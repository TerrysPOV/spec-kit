Ensure `orchestrator/hooks/lint_phase.sh` calls:
  bash orchestrator/plugins.runtime.sh <phase>
before severity/file existence checks. This produces required reports in CLAUDE or CLI mode.
