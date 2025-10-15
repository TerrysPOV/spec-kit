#!/usr/bin/env bash
set -euo pipefail
mkdir -p reports/security
outfile="reports/security/plan-scan.md"
: > "$outfile"

PKG_MGR=""
if command -v pnpm >/dev/null 2>&1; then PKG_MGR="pnpm"
elif command -v npm >/dev/null 2>&1; then PKG_MGR="npm"
fi

echo "# Plan Scan – JS/TS" >> "$outfile"
if [[ -n "$PKG_MGR" ]]; then
  if [[ "$PKG_MGR" == "pnpm" && -f "pnpm-workspace.yaml" ]]; then
    echo "(workspace mode)" >> "$outfile"
    pnpm audit --json || true >> "$outfile"
  else
    $PKG_MGR audit --json || true >> "$outfile"
  fi
else
  echo "- Package manager not found; skipping JS audit" >> "$outfile"
fi
echo "[audit-js] Wrote $outfile" >&2
