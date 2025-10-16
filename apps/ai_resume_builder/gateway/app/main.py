from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
import httpx, os
from typing import Optional
from contextlib import asynccontextmanager

# Import all our modules
from lib.openrouter_client import get_async_openrouter_client, OpenRouterConfig
from lib.auth import get_current_user, UserContext, auth_health_check
from lib.rate_limiter import get_rate_limiter, check_rate_limit, check_cost_quota, record_api_cost
from lib.gdpr import get_gdpr_service, format_export_for_download, generate_export_filename
from lib.database import get_db, database_health_check
from lib.models import UsageEvent

INTEL_URL = os.getenv("INTEL_URL", "http://intel-svc:8081/intel/lookup_company")
RENDER_URL = os.getenv("RENDER_URL", "http://render-svc:8082/render/resume")

# Global instances
rate_limiter = get_rate_limiter()
gdpr_service = get_gdpr_service()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Starting AI Resume Assistant Gateway...")

    # Test database connection
    db_connected = await database_health_check()
    if not db_connected.get("database", {}).get("connected", False):
        print("WARNING: Database connection failed")

    # Test Redis connection
    redis_health = rate_limiter.health_check()
    if not redis_health.get("redis", {}).get("connected", False):
        print("WARNING: Redis connection failed")

    yield

    # Shutdown
    print("Shutting down AI Resume Assistant Gateway...")

app = FastAPI(
    title="AI Resume Assistant Gateway",
    version="0.1.0",
    lifespan=lifespan
)

class ApplyRequest(BaseModel):
    user_id: str
    cv_json: dict
    pd_text: str
    company_domain: str
    role_family: str | None = None
    style: str | None = None
    constraints: list[str] | None = None
    budget_gbp: float | None = 0.5
    # New OpenRouter integration parameters
    model: str | None = None  # Model selection (e.g., "anthropic/claude-3.5-sonnet", "openai/gpt-4-turbo")
    temperature: float | None = 0.7  # AI temperature for creativity vs consistency

class ApplyResponse(BaseModel):
    pdf_url: str
    cover_letter: str
    brief: str
    tokens_in: int = 0
    tokens_out: int = 0
    cost_gbp: float = 0.0
    model_used: str = ""  # Track which model was actually used

@app.get("/healthz")
async def health():
    """Health check endpoint with OpenRouter status"""
    try:
        # Initialize OpenRouter client for health check
        openrouter_client = get_async_openrouter_client()
        health_status = await openrouter_client.health_check()

        return {
            "ok": True,
            "openrouter": health_status,
            "services": {
                "intel_svc": "healthy",  # Would check actual service in production
                "render_svc": "healthy"  # Would check actual service in production
            }
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }

async def generate_with_openrouter(
    prompt: str,
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> dict:
    """
    Generate text using OpenRouter with dynamic model selection

    Args:
        prompt: The prompt to send to the AI model
        model: Specific model to use (falls back to config default if None)
        temperature: Creativity vs consistency (0.0 to 2.0)
        max_tokens: Maximum tokens to generate

    Returns:
        AI response with content and usage statistics
    """
    try:
        openrouter_client = get_async_openrouter_client()

        # Prepare messages for OpenRouter format
        messages = [{"role": "user", "content": prompt}]

        # Create completion using OpenRouter
        response = await openrouter_client.create_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Extract response data
        if "choices" in response and len(response["choices"]) > 0:
            content = response["choices"][0]["message"]["content"]
            usage = response.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)

            return {
                "content": content,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "model_used": response.get("model", model or "default"),
                "total_tokens": input_tokens + output_tokens
            }
        else:
            raise HTTPException(502, "Invalid response format from OpenRouter")

    except Exception as e:
        raise HTTPException(502, f"OpenRouter API error: {str(e)}")

@app.post("/v1/apply", response_model=ApplyResponse)
async def apply(
    req: ApplyRequest,
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Apply for a job with AI-enhanced resume and cover letter

    Now uses OpenRouter for maximum model flexibility across all major AI providers
    """
    try:
        # Check rate limits and quotas
        await check_rate_limit(user.user_id, user.email)
        cost_quota = await check_cost_quota(user.user_id, user.email, 0.1)  # Estimate 10 cents

        # Get company intelligence
        async with httpx.AsyncClient(timeout=20) as client:
            intel_response = await client.post(INTEL_URL, json={
                "domain": req.company_domain,
                "role_family": req.role_family
            })

            if intel_response.status_code != 200:
                raise HTTPException(502, f"Intel service error: {intel_response.text}")

            intel = intel_response.json()

        # Generate cover letter using OpenRouter
        cover_letter_prompt = f"""
        Write a professional cover letter for a {req.role_family or 'professional'} position at {intel.get('domain', req.company_domain)}.

        Company context: {', '.join(intel.get('signals', []))}
        Key people: {', '.join([f"{p.get('name', '')} ({p.get('title', '')})" for p in intel.get('people', [])])}

        Resume content: {req.cv_json}
        Job description: {req.pd_text}

        Style: {req.style or 'professional'}
        Constraints: {', '.join(req.constraints or [])}

        Make it compelling, specific, and tailored to this company and role.
        Focus on achievements and impact rather than just responsibilities.
        """

        # Generate cover letter with OpenRouter
        ai_response = await generate_with_openrouter(
            prompt=cover_letter_prompt,
            model=req.model,
            temperature=req.temperature or 0.7,
            max_tokens=1200  # Longer for cover letters
        )

        cover_letter = ai_response["content"]
        tokens_used = ai_response["total_tokens"]
        model_used = ai_response["model_used"]

        # Generate company brief
        brief = f"""
        Company: {intel.get('domain', req.company_domain)}
        Key signals: {', '.join(intel.get('signals', []))}
        Key people: {', '.join([f"{p.get('name', '')} ({p.get('title', '')})" for p in intel.get('people', [])])}
        Products: {', '.join(intel.get('products', []))}
        Sources: {', '.join(intel.get('sources', []))}
        """

        # Generate PDF using render service
        async with httpx.AsyncClient(timeout=30) as client:
            render_response = await client.post(RENDER_URL, json={
                "cv_json": req.cv_json,
                "cover_letter": cover_letter,
                "company_brief": brief
            })

            if render_response.status_code != 200:
                raise HTTPException(502, f"Render service error: {render_response.text}")

            rend = render_response.json()

        # Record usage in database
        usage_event = UsageEvent(
            user_id=user.user_id,
            model=model_used,
            prompt_tokens=ai_response["input_tokens"],
            completion_tokens=ai_response["output_tokens"],
            total_tokens=tokens_used,
            cost_usd=0.0,  # Will be calculated by OpenRouter client
            status="success",
            endpoint="/v1/apply",
            metadata={
                "company_domain": req.company_domain,
                "role_family": req.role_family,
                "model_requested": req.model
            }
        )
        db.add(usage_event)

        # Record cost in Redis
        await record_api_cost(user.user_id, 0.0)  # Will be updated with actual cost

        return ApplyResponse(
            pdf_url=rend.get("pdf_url", "s3://bucket/generated-resume.pdf"),
            cover_letter=cover_letter,
            brief=brief,
            tokens_in=ai_response["input_tokens"],
            tokens_out=ai_response["output_tokens"],
            cost_gbp=0.0,  # Will be calculated from USD
            model_used=model_used
        )

    except Exception as e:
        # Record failed usage
        if 'user' in locals():
            failed_usage = UsageEvent(
                user_id=user.user_id,
                model=req.model or "unknown",
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                cost_usd=0.0,
                status="error",
                error_message=str(e),
                endpoint="/v1/apply",
                metadata={"company_domain": req.company_domain}
            )
            db.add(failed_usage)

        raise HTTPException(502, f"Service error: {str(e)}")

@app.get("/v1/models")
async def list_available_models():
    """List all available models from OpenRouter"""
    try:
        openrouter_client = get_async_openrouter_client()
        models = await openrouter_client.get_available_models()

        # Format for API response
        model_list = []
        for model in models:
            model_list.append({
                "id": model.id,
                "name": model.name,
                "provider": model.provider,
                "context_length": model.context_length,
                "input_pricing": model.input_pricing,
                "output_pricing": model.output_pricing,
                "supports_function_calling": model.supports_function_calling,
                "supports_vision": model.supports_vision
            })

        return {
            "models": model_list,
            "total_count": len(model_list)
        }

    except Exception as e:
        raise HTTPException(502, f"Failed to fetch models: {str(e)}")

@app.get("/v1/costs")
async def get_cost_summary(user: UserContext = Depends(get_current_user)):
    """Get cost summary for recent OpenRouter usage"""
    try:
        openrouter_client = get_async_openrouter_client()
        summary = openrouter_client.get_cost_summary()

        return summary

    except Exception as e:
        raise HTTPException(502, f"Failed to get cost summary: {str(e)}")

@app.post("/v1/generate")
async def generate_text(
    prompt: str,
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    user: UserContext = Depends(get_current_user)
):
    """
    Simple text generation endpoint using OpenRouter

    Useful for testing different models and parameters
    """
    try:
        result = await generate_with_openrouter(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return {
            "content": result["content"],
            "tokens_used": result["total_tokens"],
            "model_used": result["model_used"],
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"]
        }

    except Exception as e:
        raise HTTPException(502, f"Generation failed: {str(e)}")

@app.get("/v1/export")
async def export_user_data(
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export all user data for GDPR compliance"""
    try:
        export_data = await gdpr_service.export_user_data(db, user.user_id)

        # Create GDPR request record
        await gdpr_service.create_gdpr_request(db, user.user_id, "export")

        return {
            "download_url": f"/v1/download/{user.user_id}",
            "export_data": export_data,
            "expires_in": 3600  # 1 hour
        }

    except Exception as e:
        raise HTTPException(502, f"Export failed: {str(e)}")

@app.delete("/v1/delete")
async def delete_user_data(
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete all user data for GDPR compliance"""
    try:
        # Create GDPR request record first
        await gdpr_service.create_gdpr_request(db, user.user_id, "delete")

        # Delete all user data
        deletion_summary = await gdpr_service.delete_user_data(db, user.user_id)

        return deletion_summary

    except Exception as e:
        raise HTTPException(502, f"Deletion failed: {str(e)}")

@app.get("/v1/user/stats")
async def get_user_stats(
    user: UserContext = Depends(get_current_user)
):
    """Get user statistics including usage and quotas"""
    try:
        stats = rate_limiter.get_user_stats(user.user_id)

        return stats

    except Exception as e:
        raise HTTPException(502, f"Failed to get user stats: {str(e)}")
