#!/usr/bin/env bash
set -euo pipefail

if ! command -v http >/dev/null 2>&1; then
  echo "httpie (http) is required for smoke tests" >&2
  exit 1
fi

BASE="${PUBLIC_BASE_URL:-https://staging.example.com}"
COMPOSE_FILE="${COMPOSE_FILE:-infra/compose/compose.staging.yaml}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
ART_DIR="spec-kit/artifacts/staging-${TIMESTAMP}"
mkdir -p "${ART_DIR}"

curl -fsS "${BASE}/healthz" | tee "${ART_DIR}/health-gateway.json"
curl -fsS "${BASE}/integrations/google/drive/status" | tee "${ART_DIR}/drive-status-initial.json"

curl -fsS "${BASE}/v1/estimate?model=anthropic/claude-3-5-sonnet&pd_chars=2500&cv_chars=8000" \
  | tee "${ART_DIR}/estimate.json"

http --check-status POST "${BASE}/v1/apply" \
  user_id:=smoke-user \
  company_domain:=example.com \
  role_family:=Distribution \
  model:=anthropic/claude-3-5-sonnet \
  creativity:=0.7 \
  pd_text:='Sample PD text: build Dublin entity; governance; CBI; European distribution.' \
  cv_json:='{"meta":"smoke"}' \
  | tee "${ART_DIR}/apply.json"

python - "${ART_DIR}/apply.json" <<'PY'
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
data = json.loads(path.read_text())
if data.get("tokens_in", 0) <= 0 or data.get("tokens_out", 0) <= 0:
    raise SystemExit("apply response missing tokens")
if not isinstance(data.get("step_timings_ms"), dict) or not data["step_timings_ms"]:
    raise SystemExit("apply response missing step timings")
PY

curl -fsS "${BASE}/internal/proxy/intel/healthz" | tee "${ART_DIR}/health-intel.json" || true
curl -fsS "${BASE}/internal/proxy/render/healthz" | tee "${ART_DIR}/health-render.json" || true

if [ -f "${COMPOSE_FILE}" ]; then
  docker compose -f "${COMPOSE_FILE}" logs --tail=200 gateway > "${ART_DIR}/gateway.log"
  mkdir -p infra/releases
  {
    echo "TAG=${TAG:-latest}"
    docker compose -f "${COMPOSE_FILE}" ps --format '{{.Service}} {{.Image}}'
  } > infra/releases/staging.lock
fi

echo "Artifacts stored in ${ART_DIR}"
