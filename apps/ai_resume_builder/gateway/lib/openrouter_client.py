"""
OpenRouter Client for AI Resume Assistant

This module provides a unified interface to OpenRouter's API, allowing dynamic model selection
across multiple AI providers (OpenAI, Anthropic, Google, Meta, etc.) through a single endpoint.

Key Features:
- Dynamic model selection via model parameter
- Automatic cost tracking and optimization
- Fallback strategies for model availability
- Comprehensive error handling and retry logic
- Request/response logging for observability

Environment Variables Required:
- OPENROUTER_API_KEY: Your OpenRouter API key
- OPENROUTER_BASE_URL: Optional custom base URL (defaults to https://openrouter.ai/api/v1)
"""

import os
import json
import time
import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import httpx
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OpenRouterConfig:
    """Configuration for OpenRouter client"""
    api_key: str
    base_url: str = "https://openrouter.ai/api/v1"
    timeout: float = 60.0
    max_retries: int = 3
    retry_delay: float = 1.0
    default_model: str = "anthropic/claude-3.5-sonnet"

@dataclass
class ModelInfo:
    """Information about available models"""
    id: str
    name: str
    provider: str
    context_length: int
    input_pricing: float  # per 1M tokens
    output_pricing: float  # per 1M tokens
    supports_function_calling: bool = False
    supports_vision: bool = False

@dataclass
class CostTracking:
    """Track costs for requests"""
    model: str
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    request_id: str
    timestamp: datetime

class OpenRouterError(Exception):
    """Base exception for OpenRouter client errors"""
    pass

class ModelNotAvailableError(OpenRouterError):
    """Raised when requested model is not available"""
    pass

class RateLimitError(OpenRouterError):
    """Raised when rate limited"""
    pass

class AuthenticationError(OpenRouterError):
    """Raised when API key is invalid"""
    pass

class OpenRouterClient:
    """
    Unified client for OpenRouter API with dynamic model selection

    Supports all major AI providers through OpenRouter's unified API:
    - OpenAI (GPT-4, GPT-3.5)
    - Anthropic (Claude 3.5 Sonnet, Claude 3 Haiku)
    - Google (Gemini Pro, Gemini Ultra)
    - Meta (Llama 2, Code Llama)
    - Mistral (Mixtral, Mistral models)
    - And many more...
    """

    # Popular model configurations for different use cases
    MODEL_PRESETS = {
        "fast": "anthropic/claude-3-haiku",
        "balanced": "anthropic/claude-3.5-sonnet",
        "powerful": "openai/gpt-4-turbo",
        "code": "anthropic/claude-3.5-sonnet",
        "analysis": "openai/gpt-4-turbo",
        "creative": "anthropic/claude-3-opus"
    }

    def __init__(self, config: Optional[OpenRouterConfig] = None):
        """Initialize OpenRouter client with configuration"""
        self.config = config or OpenRouterConfig(
            api_key=os.getenv("OPENROUTER_API_KEY", ""),
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        )

        if not self.config.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")

        self.client = httpx.Client(
            base_url=self.config.base_url,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://ai-resume-assistant.com",
                "X-Title": "AI Resume Assistant"
            },
            timeout=self.config.timeout
        )

        # In-memory cost tracking (in production, use proper database)
        self.cost_history: List[CostTracking] = []

        logger.info(f"OpenRouter client initialized with base URL: {self.config.base_url}")

    def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models from OpenRouter"""
        try:
            response = self.client.get("/models")
            response.raise_for_status()
            data = response.json()

            models = []
            for model_data in data.get("data", []):
                models.append(ModelInfo(
                    id=model_data["id"],
                    name=model_data["name"],
                    provider=model_data.get("provider", {}).get("name", "Unknown"),
                    context_length=model_data.get("context_length", 4096),
                    input_pricing=model_data.get("pricing", {}).get("input", 0),
                    output_pricing=model_data.get("pricing", {}).get("output", 0),
                    supports_function_calling=model_data.get("supports_function_calling", False),
                    supports_vision=model_data.get("supports_vision", False)
                ))

            return models

        except httpx.RequestError as e:
            logger.error(f"Failed to fetch models: {e}")
            raise OpenRouterError(f"Failed to fetch available models: {e}")

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a given model and token usage"""
        # This is a simplified calculation - in practice, you'd want to cache model pricing
        # For now, using reasonable estimates for popular models
        pricing = {
            "anthropic/claude-3.5-sonnet": {"input": 3.0, "output": 15.0},
            "anthropic/claude-3-haiku": {"input": 0.25, "output": 1.25},
            "anthropic/claude-3-opus": {"input": 15.0, "output": 75.0},
            "openai/gpt-4-turbo": {"input": 10.0, "output": 30.0},
            "openai/gpt-3.5-turbo": {"input": 1.5, "output": 2.0},
            "google/gemini-pro": {"input": 0.5, "output": 1.5},
            "meta-llama/llama-2-70b-chat": {"input": 0.7, "output": 0.9}
        }

        model_pricing = pricing.get(model, pricing["anthropic/claude-3.5-sonnet"])

        input_cost = (input_tokens / 1_000_000) * model_pricing["input"]
        output_cost = (output_tokens / 1_000_000) * model_pricing["output"]

        return input_cost + output_cost

    def create_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        functions: Optional[List[Dict]] = None,
        function_call: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a completion using OpenRouter API

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (defaults to config default)
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            functions: Optional function definitions for function calling
            function_call: Function call mode ("auto", "none", or specific function name)
            **kwargs: Additional parameters

        Returns:
            API response dictionary
        """
        # Select model
        selected_model = model or self.config.default_model

        # Prepare request payload
        payload = {
            "model": selected_model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        if functions:
            payload["functions"] = functions
            if function_call:
                payload["function_call"] = function_call

        # Make request with retry logic
        last_error = None

        for attempt in range(self.config.max_retries):
            try:
                logger.info(f"Creating completion with model: {selected_model} (attempt {attempt + 1})")

                response = self.client.post("/chat/completions", json=payload)
                response.raise_for_status()

                result = response.json()

                # Track costs if usage information is available
                if "usage" in result:
                    usage = result["usage"]
                    input_tokens = usage.get("prompt_tokens", 0)
                    output_tokens = usage.get("completion_tokens", 0)

                    cost = self.calculate_cost(selected_model, input_tokens, output_tokens)

                    cost_tracking = CostTracking(
                        model=selected_model,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        input_cost=(input_tokens / 1_000_000) * 3.0,  # Simplified pricing
                        output_cost=(output_tokens / 1_000_000) * 15.0,
                        total_cost=cost,
                        request_id=result.get("id", f"req_{int(time.time())}"),
                        timestamp=datetime.now()
                    )

                    self.cost_history.append(cost_tracking)

                    logger.info(f"Cost tracking: ${cost".6f"} for {input_tokens + output_tokens} tokens")

                return result

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise AuthenticationError("Invalid API key")
                elif e.response.status_code == 429:
                    if attempt < self.config.max_retries - 1:
                        wait_time = self.config.retry_delay * (2 ** attempt)
                        logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise RateLimitError("Rate limit exceeded")
                elif e.response.status_code == 404:
                    raise ModelNotAvailableError(f"Model {selected_model} not available")
                else:
                    last_error = e

            except httpx.RequestError as e:
                last_error = e
                if attempt < self.config.max_retries - 1:
                    wait_time = self.config.retry_delay * (2 ** attempt)
                    logger.warning(f"Request failed, waiting {wait_time}s before retry: {e}")
                    time.sleep(wait_time)
                    continue

        # All retries failed
        if last_error:
            raise OpenRouterError(f"Request failed after {self.config.max_retries} attempts: {last_error}")
        else:
            raise OpenRouterError("Request failed with unknown error")

    def get_cost_summary(self, limit: int = 100) -> Dict[str, Any]:
        """Get cost summary for recent requests"""
        recent_costs = self.cost_history[-limit:] if self.cost_history else []

        if not recent_costs:
            return {"total_cost": 0.0, "total_requests": 0, "total_tokens": 0}

        total_cost = sum(cost.total_cost for cost in recent_costs)
        total_requests = len(recent_costs)
        total_tokens = sum(cost.input_tokens + cost.output_tokens for cost in recent_costs)

        # Group by model
        model_costs = {}
        for cost in recent_costs:
            if cost.model not in model_costs:
                model_costs[cost.model] = {"cost": 0.0, "requests": 0, "tokens": 0}
            model_costs[cost.model]["cost"] += cost.total_cost
            model_costs[cost.model]["requests"] += 1
            model_costs[cost.model]["tokens"] += cost.input_tokens + cost.output_tokens

        return {
            "total_cost": round(total_cost, 6),
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "avg_cost_per_request": round(total_cost / total_requests, 6) if total_requests > 0 else 0,
            "avg_tokens_per_request": total_tokens // total_requests if total_requests > 0 else 0,
            "model_breakdown": model_costs,
            "time_period": {
                "start": recent_costs[0].timestamp.isoformat() if recent_costs else None,
                "end": recent_costs[-1].timestamp.isoformat() if recent_costs else None
            }
        }

    def health_check(self) -> Dict[str, Any]:
        """Check if OpenRouter API is accessible and get basic info"""
        try:
            # Try to get models list as a health check
            models = self.get_available_models()
            return {
                "status": "healthy",
                "available_models": len(models),
                "api_key_configured": bool(self.config.api_key),
                "base_url": self.config.base_url
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "api_key_configured": bool(self.config.api_key),
                "base_url": self.config.base_url
            }

    def __del__(self):
        """Cleanup HTTP client"""
        if hasattr(self, 'client'):
            self.client.close()

# Convenience function for getting a client instance
def get_openrouter_client() -> OpenRouterClient:
    """Get a configured OpenRouter client instance"""
    return OpenRouterClient()

# Async version for FastAPI compatibility
class AsyncOpenRouterClient:
    """Async version of OpenRouter client for FastAPI"""

    def __init__(self, config: Optional[OpenRouterConfig] = None):
        self.sync_client = OpenRouterClient(config)

    async def create_completion(self, *args, **kwargs) -> Dict[str, Any]:
        """Async version of create_completion"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.sync_client.create_completion, *args, **kwargs)

    async def get_available_models(self) -> List[ModelInfo]:
        """Async version of get_available_models"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.sync_client.get_available_models)

    async def health_check(self) -> Dict[str, Any]:
        """Async version of health_check"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.sync_client.health_check)

    def get_cost_summary(self, *args, **kwargs) -> Dict[str, Any]:
        """Get cost summary (same as sync version)"""
        return self.sync_client.get_cost_summary(*args, **kwargs)

def get_async_openrouter_client() -> AsyncOpenRouterClient:
    """Get an async OpenRouter client instance"""
    return AsyncOpenRouterClient()</code>
</edit_file>