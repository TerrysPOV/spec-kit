# ADR 001: Model Picker Enforcement and Google Drive Integration

## Context

The AI Resume Assistant required three upgrades to enable end-to-end staging demos:

1. A curated AI model picker with predictable pricing so we can enforce cost guardrails from the gateway.
2. Reliable Google Drive persistence with separate consent, matching the product spec for storing generated resumes.
3. Observability hooks and contract updates to validate that `/v1/apply` now orchestrates the full pipeline instead of returning generic responses.

## Decision

- Establish a strict allowlist of four production-ready models (`anthropic/claude-3-5-sonnet`, `openai/o4-mini`, `qwen/qwen-3.5-32b`, `deepseek/deepseek-chat`). The gateway estimates cost per run using model pricing and rejects unknown models with a structured 400 response. When projected cost exceeds the per-run or monthly budget we return HTTP 402 and surface cheaper alternatives.
- Replace the ad-hoc OpenRouter call path with a deterministic composition pipeline that always logs correlation IDs, cost, tokens, and per-step timings.
- Add `DriveManager` which stores OAuth tokens (encrypted via Fernet + Redis/memory fallback), exposes `POST /integrations/google/drive/connect` and `GET /integrations/google/drive/status`, uploads PDFs to Drive when connected, and returns `persist_warning=true` with a data URL fallback when Drive is unavailable.
- Extend the Next.js UI with a dedicated model picker, estimated cost hint, creativity slider, and Drive connect button surfaced in both the header and Position Description card. The Result card now highlights persisted model, costs, and Drive state.
- Ship supporting assets: JSON schema updates, HTTP smoke scripts, unit tests for cost limiting/Drive adapter/UI guards, and a Drive OAuth callback page.

## Consequences

- Cost validation happens before any downstream calls, so users immediately see budget issues and suggested cheaper models.
- Logs and saved artefacts capture the final Drive URL or fallback data URL, allowing support to audit whether a run persisted to Google Drive.
- Adding new models now requires updating a single allowlist structure rather than scattered constants.
- The UI requires environment variables for both backend and frontend pieces of the Google OAuth flow (`GOOGLE_*` and `NEXT_PUBLIC_GOOGLE_*`), which has been documented in `.env.example`.
- Future Drive features (refresh, disconnect, folder management) can build on the central `DriveManager` instead of duplicating OAuth logic inside the request handler.
