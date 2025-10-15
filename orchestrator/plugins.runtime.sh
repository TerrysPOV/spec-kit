#!/usr/bin/env bash
set -euo pipefail
PHASE="${1:-}"
MODE="${ORCHESTRATOR_PLUGIN_MODE:-cli}"

mkdir -p reports/security reports/tests reports/compliance

log() { printf "[plugins.runtime] %s\n" "$*" >&2; }

run_claude_spec() {
  log "Expecting Claude to run: /plugin run security-guidance (+ backend-api-security if APIs)"
  : > reports/security/spec-findings.md || true
  printf "# Spec Findings (from Claude plugins)\n\n" >> reports/security/spec-findings.md
  printf "_Claude plugins should append their outputs here._\n" >> reports/security/spec-findings.md
}

run_claude_plan() {
  : > reports/security/plan-scan.md || true
  printf "# Plan Scan (from Claude plugins)\n\n" >> reports/security/plan-scan.md
  printf "_Claude plugins should append their outputs here._\n" >> reports/security/plan-scan.md
}

run_claude_tasks() {
  : > reports/tests/tasks-unit-help.md || true
  printf "# Python Unit Testing Help (from Claude plugins)\n\n" >> reports/tests/tasks-unit-help.md
  printf "_Claude plugins should append their outputs here._\n" >> reports/tests/tasks-unit-help.md
}

run_claude_implement() {
  : > reports/security/implement-scan.md || true
  printf "# Implement Scan (from Claude plugins)\n\n" >> reports/security/implement-scan.md
  printf "_Claude plugins should append their outputs here._\n" >> reports/security/implement-scan.md
}

run_claude_analyze() {
  : > reports/compliance/analyze-compliance.md || true
  printf "# Compliance Report (from Claude plugins)\n\n" >> reports/compliance/analyze-compliance.md
  printf "_Claude plugins should append their outputs here._\n" >> reports/compliance/analyze-compliance.md
}

# CLI fallbacks
run_cli_spec() { scripts/generate-threat-model.sh; }
run_cli_plan() { scripts/audit-js.sh; scripts/audit-rust.sh; scripts/audit-python.sh; scripts/merge-audits.sh; }
run_cli_tasks() {
  if [[ -f "pyproject.toml" || -f "requirements.txt" ]]; then
    scripts/python-unit-help.sh
  else
    printf "[plugins.runtime] No Python detected; skipping tasks unit help\n" >&2
  fi
}
run_cli_implement() { run_cli_plan; mv -f reports/security/plan-scan.md reports/security/implement-scan.md; }
run_cli_analyze() { scripts/generate-compliance-report.sh; }

case "$MODE" in
  claude)
    case "$PHASE" in
      spec) run_claude_spec ;;
      plan) run_claude_plan ;;
      tasks) run_claude_tasks ;;
      implement) run_claude_implement ;;
      analyze) run_claude_analyze ;;
      *) echo "Unknown phase: $PHASE" >&2; exit 1;;
    esac
    ;;
  cli|*)
    case "$PHASE" in
      spec) run_cli_spec ;;
      plan) run_cli_plan ;;
      tasks) run_cli_tasks ;;
      implement) run_cli_implement ;;
      analyze) run_cli_analyze ;;
      *) echo "Unknown phase: $PHASE" >&2; exit 1;;
    esac
    ;;
esac
