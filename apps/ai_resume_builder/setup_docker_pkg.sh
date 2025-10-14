#!/usr/bin/env bash
set -euo pipefail

PKG="AI_Resume_Assistant_Package_DockerOnly"
rm -rf "$PKG" "$PKG.zip"
mkdir -p "$PKG"/{schemas,rust/intel-svc/src,rust/render-svc/src,gateway/app,agent}

# ---------- Schemas ----------
cat > "$PKG/schemas/user_manifest.schema.json" << 'JSON'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "UserManifest",
  "type": "object",
  "properties": {
    "user_id": { "type": "string" },
    "summary": { "type": "string" },
    "roles": { "type": "array", "items": { "type": "string" } },
    "skills": { "type": "array", "items": { "type": "string" } },
    "achievements": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "impact": { "type": "string" },
          "metric": { "type": "string" },
          "value": { "type": "number" }
        },
        "required": ["impact"]
      }
    },
    "education": { "type": "array", "items": { "type": "string" } },
    "last_updated": { "type": "string", "format": "date-time" }
  },
  "required": ["user_id", "skills", "roles"]
}
JSON

cat > "$PKG/schemas/company_dossier.schema.json" << 'JSON'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "CompanyDossier",
  "type": "object",
  "properties": {
    "domain": { "type": "string" },
    "name": { "type": "string" },
    "products": { "type": "array", "items": { "type": "string" } },
    "role_family": { "type": "string" },
    "people": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "title": { "type": "string" },
          "linkedin": { "type": "string" }
        }
      }
    },
    "signals": { "type": "array", "items": { "type": "string" } },
    "sources": { "type": "array", "items": { "type": "string" } },
    "indexed_at": { "type": "string", "format": "date-time" }
  },
  "required": ["domain", "role_family"]
}
JSON

cat > "$PKG/schemas/compose_request.schema.json" << 'JSON'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ComposeRequest",
  "type": "object",
  "properties": {
    "manifest": { "$ref": "./user_manifest.schema.json" },
    "dossier": { "$ref": "./company_dossier.schema.json" },
    "pd_text": { "type": "string" },
    "style": { "type": "string" },
    "constraints": { "type": "array", "items": { "type": "string" } },
    "budget_gbp": { "type": "number" }
  },
  "required": ["manifest", "dossier", "pd_text"]
}
JSON

cat > "$PKG/schemas/compose_response.schema.json" << 'JSON'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ComposeResponse",
  "type": "object",
  "properties": {
    "cv_json": { "type": "object" },
    "cover_letter": { "type": "string" },
    "brief": { "type": "string" },
    "tokens_in": { "type": "integer" },
    "tokens_out": { "type": "integer" },
    "cost_gbp": { "type": "number" },
    "logs": { "type": "array", "items": { "type": "string" } }
  },
  "required": ["cv_json", "cover_letter", "brief"]
}
JSON

# ---------- Rust: intel-svc ----------
cat > "$PKG/rust/intel-svc/Cargo.toml" << 'TOML'
[package]
name = "intel-svc"
version = "0.1.0"
edition = "2021"

[dependencies]
axum = { version = "0.7", features = ["macros"] }
tokio = { version = "1", features = ["rt-multi-thread", "macros"] }
reqwest = { version = "0.12", features = ["json", "gzip", "http2"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tower-http = { version = "0.5", features = ["trace", "cors"] }
tracing = "0.1"
tracing-subscriber = "0.3"
anyhow = "1"
urlencoding = "2"
TOML

cat > "$PKG/rust/intel-svc/src/main.rs" << 'RS'
use axum::{routing::get, routing::post, Router, Json};
use serde::{Deserialize, Serialize};
use tracing::info;

#[derive(Deserialize)]
struct LookupReq { domain: String, role_family: Option<String> }

#[derive(Serialize)]
struct LookupResp {
    domain: String,
    role_family: String,
    products: Vec<String>,
    people: Vec<Person>,
    signals: Vec<String>,
    sources: Vec<String>,
}

#[derive(Serialize)]
struct Person { name: String, title: String, linkedin: String }

async fn health() -> &'static str { "ok" }

async fn lookup_company(Json(req): Json<LookupReq>) -> Json<LookupResp> {
    let role = req.role_family.unwrap_or_else(|| "General".to_string());
    Json(LookupResp {
        domain: req.domain,
        role_family: role,
        products: vec!["ExampleProduct".into()],
        people: vec![Person { name: "Jane Doe".into(), title: "Hiring Manager".into(), linkedin: "https://linkedin.com/in/janedoe".into() }],
        signals: vec!["Recent funding".into(), "Hiring push".into()],
        sources: vec!["https://example.com".into()],
    })
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt().with_target(false).init();
    let app = Router::new()
        .route("/healthz", get(health))
        .route("/intel/lookup_company", post(lookup_company));
    let addr = std::net::SocketAddr::from(([0,0,0,0], 8081));
    info!("intel-svc listening on {}", addr);
    axum::serve(tokio::net::TcpListener::bind(addr).await.unwrap(), app).await.unwrap();
}
RS

# ---------- Rust: render-svc ----------
cat > "$PKG/rust/render-svc/Cargo.toml" << 'TOML'
[package]
name = "render-svc"
version = "0.1.0"
edition = "2021"

[dependencies]
axum = { version = "0.7", features = ["macros"] }
tokio = { version = "1", features = ["rt-multi-thread", "macros"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tracing = "0.1"
tracing-subscriber = "0.3"
TOML

cat > "$PKG/rust/render-svc/src/main.rs" << 'RS'
use axum::{routing::post, Router, Json, response::IntoResponse};
use serde::Deserialize;
use tracing::info;

#[derive(Deserialize)]
struct RenderReq { cv_json: serde_json::Value }

async fn render(Json(_req): Json<RenderReq>) -> impl IntoResponse {
    Json(serde_json::json!({ "pdf_url": "s3://bucket/fake.pdf" }))
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt().with_target(false).init();
    let app = Router::new().route("/render/resume", post(render));
    let addr = std::net::SocketAddr::from(([0,0,0,0], 8082));
    info!("render-svc listening on {}", addr);
    axum::serve(tokio::net::TcpListener::bind(addr).await.unwrap(), app).await.unwrap();
}
RS

# ---------- FastAPI gateway ----------
cat > "$PKG/gateway/pyproject.toml" << 'TOML'
[project]
name = "ai-resume-gateway"
version = "0.1.0"
description = "FastAPI gateway for AI Resume Assistant"
requires-python = ">=3.10"
dependencies = [
  "fastapi>=0.112",
  "uvicorn[standard]>=0.30",
  "httpx>=0.27",
  "pydantic>=2.7",
]
TOML

cat > "$PKG/gateway/Dockerfile" << 'DOCKER'
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir fastapi uvicorn[standard] httpx pydantic
COPY app /app/app
ENV PYTHONPATH=/app
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
DOCKER

cat > "$PKG/gateway/app/main.py" << 'PY'
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
PY

# ---------- Agent tools registry (Claude) ----------
cat > "$PKG/agent/claude_tool_registry.py" << 'PY'
# Claude Agent SDK - Tool registration example (outline)
from typing import Any, Dict
import requests

INTEL_URL = "http://intel-svc:8081/intel/lookup_company"
RENDER_URL = "http://render-svc:8082/render/resume"

def lookup_company_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    r = requests.post(INTEL_URL, json={
        "domain": args.get("domain", ""),
        "role_family": args.get("role_family")
    }, timeout=10)
    r.raise_for_status()
    return r.json()

def render_resume_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    r = requests.post(RENDER_URL, json={
        "cv_json": args.get("cv_json", {})
    }, timeout=20)
    r.raise_for_status()
    return r.json()

TOOLS = [
    {
        "name": "lookup_company",
        "description": "Fetch company dossier for a given domain and role family",
        "parameters": {
            "type": "object",
            "properties": {
                "domain": {"type": "string"},
                "role_family": {"type": "string"}
            },
            "required": ["domain"]
        },
        "handler": lookup_company_tool,
    },
    {
        "name": "render_resume",
        "description": "Render resumake-style JSON into a PDF",
        "parameters": {
            "type": "object",
            "properties": {
                "cv_json": {"type": "object"}
            },
            "required": ["cv_json"]
        },
        "handler": render_resume_tool,
    }
]
# Example (SDK-specific): agent.register_tools(TOOLS)
PY

# ---------- Spec (updated, references included files) ----------
cat > "$PKG/AI_Resume_Assistant_Product_Spec.md" << 'MD'
# AI Resume Assistant – Product Specification (Docker-Only Package)

**Prepared by:** Terry Yodaiken  
**Role:** Founder & CEO, POVIEW.AI  
**Audience:** Engineering, Product, and Ops teams

This package implements the FastAPI + Claude Agent SDK architecture with **Rust services** and **Docker-only** deploy files for OrbStack and containerd (nerdctl).

## Included Files (paths relative to this package)
- `schemas/` — JSON Schemas (contracts)
  - `user_manifest.schema.json`
  - `company_dossier.schema.json`
  - `compose_request.schema.json`
  - `compose_response.schema.json`
- `gateway/` — FastAPI gateway (Dockerfile, pyproject, app/main.py)
- `rust/intel-svc/` — Axum service: `POST /intel/lookup_company`
- `rust/render-svc/` — Axum service: `POST /render/resume`
- `agent/claude_tool_registry.py` — Claude Agent SDK tool registration
- `docker-compose.yml` — OrbStack-friendly compose
- `compose.nerdctl.yaml` — containerd-friendly compose

## Local Run (OrbStack)
```bash
docker compose up --build
# gateway: http://localhost:8080/healthz
# intel-svc: http://localhost:8081/healthz
# render-svc: POST http://localhost:8082/render/resume

