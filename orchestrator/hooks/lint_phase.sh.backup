#!/usr/bin/env bash
set -euo pipefail

PHASE="${1:-implement}"
EXIT_CODE=0

echo "🔍 Running lint_phase hook for: ${PHASE}"

# Plugin artifact validation
validate_plugin_artifacts() {
  local phase=$1
  local missing_artifacts=()
  local artifact_exit_code=0

  echo "→ Validating plugin artifacts for phase: ${phase}"

  case "$phase" in
    spec)
      if [[ ! -f "reports/security/spec-findings.md" ]]; then
        missing_artifacts+=("reports/security/spec-findings.md")
      fi
      ;;
    plan)
      if [[ ! -f "reports/security/plan-scan.md" ]]; then
        missing_artifacts+=("reports/security/plan-scan.md")
      fi
      ;;
    tasks)
      # Conditional: only required for Python projects
      if [[ -f "requirements.txt" ]] || [[ -f "pyproject.toml" ]]; then
        if [[ ! -f "reports/tests/tasks-unit-help.md" ]]; then
          missing_artifacts+=("reports/tests/tasks-unit-help.md")
        fi
      fi
      ;;
    implement)
      if [[ ! -f "reports/security/implement-scan.md" ]]; then
        missing_artifacts+=("reports/security/implement-scan.md")
      fi
      ;;
    analyze)
      if [[ ! -f "reports/security/analyze-deltas.md" ]]; then
        missing_artifacts+=("reports/security/analyze-deltas.md")
      fi
      if [[ ! -f "reports/compliance/analyze-compliance.md" ]]; then
        missing_artifacts+=("reports/compliance/analyze-compliance.md")
      fi
      ;;
  esac

  if [[ ${#missing_artifacts[@]} -gt 0 ]]; then
    echo "  ❌ Missing required plugin artifacts:"
    for artifact in "${missing_artifacts[@]}"; do
      echo "     - ${artifact}"
    done
    return 1
  fi

  # Check for unmitigated CRITICAL/HIGH findings
  check_security_findings "$phase"
  artifact_exit_code=$?

  if [[ $artifact_exit_code -eq 0 ]]; then
    echo "  ✅ Plugin artifacts validated"
  fi

  return $artifact_exit_code
}

check_security_findings() {
  local phase=$1
  local report_files=()

  # Determine which reports to check based on phase
  case "$phase" in
    spec)
      report_files+=("reports/security/spec-findings.md")
      ;;
    plan)
      report_files+=("reports/security/plan-scan.md")
      ;;
    implement)
      report_files+=("reports/security/implement-scan.md")
      ;;
    analyze)
      report_files+=("reports/security/analyze-deltas.md")
      ;;
  esac

  for report in "${report_files[@]}"; do
    if [[ -f "$report" ]]; then
      # Look for CRITICAL or HIGH severity markers
      # This is a simplified check - actual format depends on plugin output
      if grep -qi "severity.*critical\|severity.*high" "$report" 2>/dev/null; then
        echo "  ⚠️  CRITICAL/HIGH findings detected in ${report}"

        # Check for mitigation documentation
        if [[ -f "plans/plan.md" ]] && grep -q "Security Mitigations" "plans/plan.md" 2>/dev/null; then
          echo "  ℹ️  Mitigation plan found in plans/plan.md"
        elif [[ -f "DECISIONS.md" ]] && grep -q "Security Finding Waiver" "DECISIONS.md" 2>/dev/null; then
          echo "  ℹ️  Security waiver found in DECISIONS.md"
        else
          echo "  ❌ No mitigation plan or waiver found"
          echo "     Required: Mitigation in plans/plan.md OR waiver in DECISIONS.md"
          return 2
        fi
      fi
    fi
  done

  return 0
}

# Run plugin artifact validation for applicable phases
if [[ "$PHASE" =~ ^(spec|plan|tasks|implement|analyze)$ ]]; then
  validate_plugin_artifacts "$PHASE" || EXIT_CODE=$?
fi

# Node/TypeScript checks
if [[ -f "package.json" ]]; then
  echo "→ Node/TypeScript workspace detected"

  case "$PHASE" in
    implement)
      echo "  • Running ESLint..."
      pnpm run lint || npm run lint || EXIT_CODE=$?

      echo "  • Running Prettier..."
      pnpm exec prettier --check apps packages || npx prettier --check apps packages || EXIT_CODE=$?

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
