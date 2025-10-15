#!/usr/bin/env bash
set -euo pipefail
mkdir -p reports/security
outfile="reports/security/plan-scan.md"
echo -e "\n# Plan Scan – Rust\n" >> "$outfile"
if ! command -v cargo >/dev/null 2>&1; then
  echo "- cargo not found; skipping Rust audit" >> "$outfile"
  exit 0
fi
if ! command -v cargo-audit >/dev/null 2>&1; then
  echo "(tip) Install cargo-audit: cargo install cargo-audit" >> "$outfile"
else
  cargo audit -q --json || true >> "$outfile"
fi
echo "[audit-rust] Appended to $outfile" >&2
