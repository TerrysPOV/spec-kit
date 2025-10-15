#!/usr/bin/env bash
set -euo pipefail
mkdir -p reports/security
outfile="reports/security/plan-scan.md"
echo -e "\n# Plan Scan – Python\n" >> "$outfile"
if [[ ! -f "pyproject.toml" && ! -f "requirements.txt" ]]; then
  echo "- No Python project detected; skipping" >> "$outfile"
  exit 0
fi
if ! command -v pip-audit >/dev/null 2>&1; then
  echo "(tip) Install pip-audit: pip install pip-audit" >> "$outfile"
else
  pip-audit -f json || true >> "$outfile"
fi
echo "[audit-python] Appended to $outfile" >&2
