"""
Rate Limiting and Quota Management for AI Resume Assistant

Redis-based rate limiting and cost quota enforcement for API usage control.
"""

import os
import time
import json
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import redis
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateLimitError(Exception):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str, retry_after: int = 60):
        self.message = message
        self.retry_after = retry_after
        super().__init__(message)

class QuotaExceededError(Exception):
    """Raised when monthly cost quota is exceeded"""
    def __init__(self, message: str, current_cost: float, limit: float):
        self.message = message
        self.current_cost = current_cost
        self.limit = limit
        super().__init__(message)

class RateLimiter:
    """
    Redis-based rate limiter and quota manager

    Features:
    - Per-user request rate limiting (requests per time window)
    - Monthly cost quotas per user
    - Admin bypass for allowed email addresses
    - Sliding window rate limiting
    """

    def __init__(self, redis_url: str = None):
        """Initialize Redis connection for rate limiting"""
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")

        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {self.redis_url}")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

        # Configuration
        self.requests_per_window = 60  # requests per 5-minute window
        self.window_seconds = 300  # 5 minutes
        self.monthly_cost_cap_usd = float(os.getenv("MONTHLY_COST_CAP_USD", "10"))
        self.allowed_emails = set(
            email.strip().lower()
            for email in os.getenv("ALLOWED_EMAILS", "").split(",")
            if email.strip()
        )

    def _get_user_key(self, user_id: str, key_type: str) -> str:
        """Generate Redis key for user-specific data"""
        return f"rate_limit:{user_id}:{key_type}"

    def _is_admin_user(self, email: str) -> bool:
        """Check if user is admin (bypass restrictions)"""
        return email.lower() in self.allowed_emails

    def check_rate_limit(self, user_id: str, email: str) -> Dict[str, Any]:
        """
        Check if user is within rate limits

        Args:
            user_id: User's unique identifier
            email: User's email address

        Returns:
            Dict with rate limit status and metadata

        Raises:
            RateLimitError: If rate limit exceeded
        """
        # Admin bypass
        if self._is_admin_user(email):
            return {
                "allowed": True,
                "admin_bypass": True,
                "requests_remaining": float('inf'),
                "window_reset": None
            }

        current_time = int(time.time())
        window_start = current_time - (current_time % self.window_seconds)

        # Redis keys for this user
        request_key = self._get_user_key(user_id, "requests")
        window_key = self._get_user_key(user_id, f"window:{window_start}")

        # Use Redis pipeline for atomic operations
        with self.redis_client.pipeline() as pipe:
            pipe.multi()

            # Get current request count for this window
            pipe.get(window_key)

            # Increment request count (expires after window)
            pipe.incr(window_key, 1)
            pipe.expire(window_key, self.window_seconds)

            # Track total requests across windows (for cleanup)
            pipe.sadd(request_key, window_key)
            pipe.expire(request_key, self.window_seconds * 2)  # Keep for 2 windows

            results = pipe.execute()

        current_count = int(results[0]) if results[0] else 0
        new_count = results[1]

        # Check if over limit
        if new_count > self.requests_per_window:
            reset_time = window_start + self.window_seconds
            retry_after = reset_time - current_time

            raise RateLimitError(
                f"Rate limit exceeded. Maximum {self.requests_per_window} requests per {self.window_seconds//60} minutes.",
                retry_after=max(1, retry_after)
            )

        return {
            "allowed": True,
            "admin_bypass": False,
            "requests_remaining": self.requests_per_window - new_count,
            "window_reset": window_start + self.window_seconds,
            "current_count": new_count
        }

    def check_cost_quota(self, user_id: str, email: str, additional_cost: float = 0.0) -> Dict[str, Any]:
        """
        Check if user is within monthly cost quota

        Args:
            user_id: User's unique identifier
            email: User's email address
            additional_cost: Cost of the operation being checked

        Returns:
            Dict with quota status and metadata

        Raises:
            QuotaExceededError: If quota would be exceeded
        """
        # Admin bypass
        if self._is_admin_user(email):
            return {
                "allowed": True,
                "admin_bypass": True,
                "current_cost": 0.0,
                "quota_remaining": float('inf'),
                "monthly_limit": self.monthly_cost_cap_usd
            }

        current_month = datetime.now().strftime("%Y-%m")
        cost_key = self._get_user_key(user_id, f"cost:{current_month}")

        # Get current monthly cost
        current_cost = float(self.redis_client.get(cost_key) or 0.0)

        # Check if adding this cost would exceed quota
        if current_cost + additional_cost > self.monthly_cost_cap_usd:
            raise QuotaExceededError(
                f"Monthly cost quota exceeded. Current: ${current_cost".2f"}, Limit: ${self.monthly_cost_cap_usd".2f"}",
                current_cost,
                self.monthly_cost_cap_usd
            )

        return {
            "allowed": True,
            "admin_bypass": False,
            "current_cost": current_cost,
            "quota_remaining": self.monthly_cost_cap_usd - current_cost,
            "monthly_limit": self.monthly_cost_cap_usd,
            "projected_cost": current_cost + additional_cost
        }

    def record_cost(self, user_id: str, cost_usd: float) -> bool:
        """
        Record API usage cost for user

        Args:
            user_id: User's unique identifier
            cost_usd: Cost in USD to record

        Returns:
            True if recorded successfully
        """
        if cost_usd <= 0:
            return True

        current_month = datetime.now().strftime("%Y-%m")
        cost_key = self._get_user_key(user_id, f"cost:{current_month}")

        # Increment monthly cost
        new_cost = self.redis_client.incrbyfloat(cost_key, cost_usd)

        # Set expiration for next month
        next_month = datetime.now().replace(day=1) + timedelta(days=32)
        next_month = next_month.replace(day=1)
        expire_seconds = int((next_month - datetime.now()).total_seconds())

        self.redis_client.expire(cost_key, expire_seconds)

        logger.info(f"Recorded cost ${cost_usd".4f"} for user {user_id}. Total: ${new_cost".4f"}")
        return True

    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive user statistics

        Args:
            user_id: User's unique identifier

        Returns:
            Dict with user usage statistics
        """
        # Get current month cost
        current_month = datetime.now().strftime("%Y-%m")
        cost_key = self._get_user_key(user_id, f"cost:{current_month}")
        current_cost = float(self.redis_client.get(cost_key) or 0.0)

        # Get recent request windows
        request_key = self._get_user_key(user_id, "requests")
        window_keys = self.redis_client.smembers(request_key)

        total_requests = 0
        for window_key in window_keys:
            count = self.redis_client.get(window_key)
            if count:
                total_requests += int(count)

        return {
            "user_id": user_id,
            "current_month": current_month,
            "monthly_cost_usd": current_cost,
            "monthly_limit_usd": self.monthly_cost_cap_usd,
            "cost_remaining_usd": max(0, self.monthly_cost_cap_usd - current_cost),
            "total_requests": total_requests,
            "is_over_quota": current_cost >= self.monthly_cost_cap_usd,
            "quota_utilization_percent": (current_cost / self.monthly_cost_cap_usd) * 100 if self.monthly_cost_cap_usd > 0 else 0
        }

    def reset_user_quota(self, user_id: str) -> bool:
        """
        Reset user's monthly cost quota (admin function)

        Args:
            user_id: User's unique identifier

        Returns:
            True if reset successfully
        """
        current_month = datetime.now().strftime("%Y-%m")
        cost_key = self._get_user_key(user_id, f"cost:{current_month}")

        # Reset cost to zero
        self.redis_client.set(cost_key, 0)

        logger.info(f"Reset cost quota for user {user_id}")
        return True

    def cleanup_old_windows(self, user_id: str) -> int:
        """
        Clean up old rate limit windows for user

        Args:
            user_id: User's unique identifier

        Returns:
            Number of windows cleaned up
        """
        request_key = self._get_user_key(user_id, "requests")
        window_keys = self.redis_client.smembers(request_key)

        current_time = int(time.time())
        current_window = current_time - (current_time % self.window_seconds)

        cleaned = 0
        for window_key in window_keys:
            # Extract timestamp from key
            try:
                window_timestamp = int(window_key.split(":")[-1])
                if window_timestamp < current_window - self.window_seconds:
                    # Delete old window
                    self.redis_client.delete(window_key)
                    self.redis_client.srem(request_key, window_key)
                    cleaned += 1
            except (ValueError, IndexError):
                # Invalid key format, remove it
                self.redis_client.srem(request_key, window_key)
                cleaned += 1

        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} old rate limit windows for user {user_id}")

        return cleaned

    def health_check(self) -> Dict[str, Any]:
        """Check Redis connection and configuration"""
        try:
            # Test Redis connection
            self.redis_client.ping()

            # Get Redis info
            info = self.redis_client.info()

            return {
                "redis": {
                    "connected": True,
                    "version": info.get("redis_version", "unknown"),
                    "uptime_days": info.get("uptime_in_days", 0),
                    "memory_used_mb": info.get("used_memory_human", "0B"),
                    "rate_limiter_config": {
                        "requests_per_window": self.requests_per_window,
                        "window_seconds": self.window_seconds,
                        "monthly_cost_cap_usd": self.monthly_cost_cap_usd,
                        "allowed_emails_count": len(self.allowed_emails)
                    }
                }
            }
        except Exception as e:
            return {
                "redis": {
                    "connected": False,
                    "error": str(e)
                }
            }

# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None

def get_rate_limiter() -> RateLimiter:
    """Get or create global rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter

# FastAPI dependency functions
async def check_rate_limit(user_id: str, email: str) -> Dict[str, Any]:
    """FastAPI dependency for rate limit checking"""
    rate_limiter = get_rate_limiter()
    return rate_limiter.check_rate_limit(user_id, email)

async def check_cost_quota(user_id: str, email: str, cost: float = 0.0) -> Dict[str, Any]:
    """FastAPI dependency for cost quota checking"""
    rate_limiter = get_rate_limiter()
    return rate_limiter.check_cost_quota(user_id, email, cost)

async def record_api_cost(user_id: str, cost_usd: float) -> bool:
    """Record API usage cost"""
    rate_limiter = get_rate_limiter()
    return rate_limiter.record_cost(user_id, cost_usd)