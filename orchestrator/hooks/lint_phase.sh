#!/usr/bin/env bash
set -euo pipefail

PHASE="${1:-implement}"
EXIT_CODE=0

echo "🔍 Running lint_phase hook for: ${PHASE}"

# Node/TypeScript checks
if [[ -f "package.json" ]]; then
  echo "→ Node/TypeScript workspace detected"

  case "$PHASE" in
    implement)
      echo "  • Running ESLint..."
      pnpm run lint || npm run lint || EXIT_CODE=$?

      echo "  • Running Prettier..."
      pnpm exec prettier --check . || npx prettier --check . || EXIT_CODE=$?

      echo "  • Running TypeScript..."
      pnpm run typecheck || npm run typecheck || EXIT_CODE=$?

      echo "  • Running tests..."
      pnpm run test || npm run test || EXIT_CODE=$?
      ;;
    *)
      echo "  ℹ Phase '$PHASE' - skipping Node checks"
      ;;
  esac
fi

# Rust checks
if [[ -f "Cargo.toml" ]]; then
  echo "→ Rust workspace detected"

  case "$PHASE" in
    implement)
      echo "  • Running cargo fmt check..."
      cargo fmt --all -- --check || EXIT_CODE=$?

      echo "  • Running cargo clippy..."
      cargo clippy --all-targets -- -D warnings || EXIT_CODE=$?

      echo "  • Running cargo test..."
      cargo test --quiet --all || EXIT_CODE=$?
      ;;
    *)
      echo "  ℹ Phase '$PHASE' - skipping Rust checks"
      ;;
  esac
fi

if [[ $EXIT_CODE -ne 0 ]]; then
  echo "❌ Lint phase failed with code: $EXIT_CODE"
  exit $EXIT_CODE
fi

echo "✅ Lint phase passed"
exit 0
