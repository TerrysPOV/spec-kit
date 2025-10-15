# Plugin Policy (Cross-Assistant)

This repository can run with **Claude Code plugins** or **CLI fallbacks** (Kilo Code / Code Supernova, Cline, ChatGPT-5-Codex, etc.).

Set `ORCHESTRATOR_PLUGIN_MODE` to one of:
- `claude` → use Claude plugin slash-commands
- `cli` (default) → use local CLI scripts

Required report files by phase:
- /spec → reports/security/spec-findings.md
- /plan → reports/security/plan-scan.md
- /tasks (Python only) → reports/tests/tasks-unit-help.md
- /implement → reports/security/implement-scan.md
- /analyze → reports/compliance/analyze-compliance.md
