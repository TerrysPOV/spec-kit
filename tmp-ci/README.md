# Orchestrator CI (CLI fallback)

This workflow runs on PRs and pushes to main and enforces Spec Kit gates without Claude plugins.
It uses the cross-assistant layer:
- `orchestrator/plugins.runtime.sh` (writes required report files in CLI mode)
- `orchestrator/hooks/lint_phase.sh` (enforces file presence and severity rules)

## What it does
1. Installs Node (pnpm), Rust, and optional Python.
2. Builds JS and Rust.
3. Runs phase gates for PLAN, IMPLEMENT, and ANALYZE:
   - Generates reports via CLI scripts
   - Lints/enforces gates via `lint_phase.sh`
4. Uploads `reports/` as CI artifacts.

## Local dry run
```bash
export ORCHESTRATOR_PLUGIN_MODE=cli
bash ci/run_phase_checks.sh plan
bash ci/run_phase_checks.sh implement
bash ci/run_phase_checks.sh analyze
```
