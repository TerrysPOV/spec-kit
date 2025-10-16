"""
Authentication utilities for AI Resume Assistant Gateway

JWT token validation, user context management, and authentication middleware.
"""

import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET = os.getenv("NEXTAUTH_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60 * 24 * 7  # 7 days

# Security scheme for FastAPI
security = HTTPBearer(auto_error=False)

class AuthError(HTTPException):
    """Authentication error"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class UserContext:
    """User context for authenticated requests"""
    def __init__(self, user_id: str, email: str):
        self.user_id = user_id
        self.email = email

def create_jwt_token(user_id: str, email: str) -> str:
    """
    Create JWT token for user

    Args:
        user_id: User's unique identifier
        email: User's email address

    Returns:
        Encoded JWT token string
    """
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES),
        "iat": datetime.utcnow(),
        "type": "access"
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode JWT token

    Args:
        token: JWT token string

    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # Check if token is expired
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            logger.warning("Token expired")
            return None

        return payload

    except jwt.ExpiredSignatureError:
        logger.warning("Token signature expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return None

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[UserContext]:
    """
    Get current user from JWT token (optional authentication)

    Args:
        credentials: Bearer token credentials

    Returns:
        UserContext if authenticated, None otherwise
    """
    if not credentials:
        return None

    payload = verify_jwt_token(credentials.credentials)
    if not payload:
        return None

    return UserContext(
        user_id=payload["user_id"],
        email=payload["email"]
    )

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> UserContext:
    """
    Get current user from JWT token (required authentication)

    Args:
        credentials: Bearer token credentials

    Returns:
        UserContext if authenticated

    Raises:
        AuthError: If authentication fails
    """
    if not credentials:
        raise AuthError("Authentication credentials missing")

    payload = verify_jwt_token(credentials.credentials)
    if not payload:
        raise AuthError("Invalid or expired token")

    return UserContext(
        user_id=payload["user_id"],
        email=payload["email"]
    )

def require_admin_user(user: UserContext) -> UserContext:
    """
    Check if user is admin based on allowed emails

    Args:
        user: User context

    Returns:
        UserContext if admin

    Raises:
        AuthError: If user is not admin
    """
    allowed_emails = os.getenv("ALLOWED_EMAILS", "")
    if not allowed_emails:
        return user  # No restriction if no allowed emails configured

    admin_emails = [email.strip() for email in allowed_emails.split(",")]
    if user.email not in admin_emails:
        raise AuthError("Admin access required")

    return user

async def get_current_admin_user(
    user: UserContext = Depends(get_current_user)
) -> UserContext:
    """
    Get current admin user (requires authentication and admin privileges)

    Args:
        user: Authenticated user context

    Returns:
        UserContext if admin

    Raises:
        AuthError: If not authenticated or not admin
    """
    return require_admin_user(user)

# Utility functions for token management
def extract_token_from_header(auth_header: str) -> Optional[str]:
    """
    Extract token from Authorization header

    Args:
        auth_header: Authorization header value

    Returns:
        Token string or None
    """
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    return auth_header.split(" ", 1)[1]

def validate_user_id_format(user_id: str) -> bool:
    """
    Validate user ID format (UUID)

    Args:
        user_id: User ID to validate

    Returns:
        True if valid format
    """
    try:
        # Simple UUID validation - check if it's a valid UUID format
        parts = user_id.split("-")
        if len(parts) != 5:
            return False

        # Basic length checks for UUID parts
        if not (len(parts[0]) == 8 and len(parts[1]) == 4 and len(parts[2]) == 4 and len(parts[3]) == 4 and len(parts[4]) == 12):
            return False

        return True
    except:
        return False

# Health check for auth system
def auth_health_check() -> dict:
    """Check authentication system health"""
    return {
        "auth": {
            "jwt_secret_configured": bool(JWT_SECRET),
            "algorithm": JWT_ALGORITHM,
            "expiration_minutes": JWT_EXPIRATION_MINUTES,
            "allowed_emails": os.getenv("ALLOWED_EMAILS", "not_configured")
        }
    }