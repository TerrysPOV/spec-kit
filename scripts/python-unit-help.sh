#!/usr/bin/env bash
set -euo pipefail
mkdir -p reports/tests
outfile="reports/tests/tasks-unit-help.md"
cat > "$outfile" <<'MD'
# Python Unit Testing Help

- Suggested structure: `tests/` with `test_*.py`
- Coverage goal: >= 80%
- Commands:
  - `pytest -q`
  - `pytest --maxfail=1 --disable-warnings -q`
- Add CI target to enforce coverage threshold.

MD
echo "[python-unit-help] Wrote $outfile" >&2
