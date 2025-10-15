#!/usr/bin/env bash
# ci/run_phase_checks.sh <phase>
set -euo pipefail
PHASE="${1:-}"
if [[ -z "$PHASE" ]]; then
  echo "Usage: $0 <spec|plan|tasks|implement|analyze>" >&2
  exit 2
fi
export ORCHESTRATOR_PLUGIN_MODE="${ORCHESTRATOR_PLUGIN_MODE:-cli}"
bash orchestrator/plugins.runtime.sh "$PHASE" || true
bash orchestrator/hooks/lint_phase.sh "$PHASE"
echo "[ci] Phase $PHASE OK"
