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

