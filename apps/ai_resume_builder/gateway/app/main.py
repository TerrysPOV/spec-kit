from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx, os

INTEL_URL = os.getenv("INTEL_URL", "http://intel-svc:8081/intel/lookup_company")
RENDER_URL = os.getenv("RENDER_URL", "http://render-svc:8082/render/resume")

app = FastAPI(title="AI Resume Assistant Gateway", version="0.1.0")

class ApplyRequest(BaseModel):
    user_id: str
    cv_json: dict
    pd_text: str
    company_domain: str
    role_family: str | None = None
    style: str | None = None
    constraints: list[str] | None = None
    budget_gbp: float | None = 0.5

class ApplyResponse(BaseModel):
    pdf_url: str
    cover_letter: str
    brief: str
    tokens_in: int = 0
    tokens_out: int = 0
    cost_gbp: float = 0.0

@app.get("/healthz")
async def health():
    return {"ok": True}

@app.post("/v1/apply", response_model=ApplyResponse)
async def apply(req: ApplyRequest):
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            intel = (await client.post(INTEL_URL, json={
                "domain": req.company_domain, "role_family": req.role_family
            })).json()
        except Exception as e:
            raise HTTPException(502, f"intel-svc error: {e}")
        cover_letter = f"Dear Hiring Team at {intel.get('domain')},\nI am excited to apply..."
        brief = f"Company signals: {', '.join(intel.get('signals', []))}"
        try:
            rend = (await client.post(RENDER_URL, json={"cv_json": req.cv_json})).json()
        except Exception as e:
            raise HTTPException(502, f"render-svc error: {e}")
    return ApplyResponse(pdf_url=rend.get("pdf_url","s3://bucket/fake.pdf"),
                         cover_letter=cover_letter, brief=brief)
