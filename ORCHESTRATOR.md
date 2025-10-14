# Orchestrator Documentation

## Overview

The Spec Kit Orchestrator coordinates development workflows across polyglot workspaces using a phase-based validation system.

## Architecture

```
orchestrator/
└─ hooks/
   └─ lint_phase.sh    # Phase validation hook
```

## Phase Hook System

### lint_phase.sh

**Purpose**: Validate code quality at each development phase

**Usage**:

```bash
bash orchestrator/hooks/lint_phase.sh <phase>
```

**Phases**:

- `spec` - Specification/design phase (docs validation)
- `implement` - Implementation phase (full validation)
- `review` - Review phase (quality gates)
- `deploy` - Deployment phase (build validation)

### Implementation Phase Checks

#### TypeScript/Node.js Workspace

When `package.json` exists:

1. **ESLint**: Code quality and style

   ```bash
   pnpm run lint
   ```

2. **Prettier**: Code formatting

   ```bash
   pnpm exec prettier --check .
   ```

3. **TypeScript**: Type checking

   ```bash
   pnpm run typecheck
   ```

4. **Vitest**: Unit tests
   ```bash
   pnpm run test
   ```

#### Rust Workspace

When `Cargo.toml` exists:

1. **rustfmt**: Code formatting

   ```bash
   cargo fmt --all -- --check
   ```

2. **Clippy**: Linting and best practices

   ```bash
   cargo clippy --all-targets -- -D warnings
   ```

3. **Tests**: Unit and integration tests
   ```bash
   cargo test --quiet --all
   ```

## Integration with CI/CD

### Local Development

```bash
# Before committing
bash orchestrator/hooks/lint_phase.sh implement

# If checks pass, commit
git add .
git commit -m "feat(api): add user endpoint"
```

### Git Hooks (Optional)

Add to `.git/hooks/pre-commit`:

```bash
#!/usr/bin/env bash
bash orchestrator/hooks/lint_phase.sh implement
```

### CI Pipeline (GitHub Actions Example)

```yaml
name: Validate
on: [pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: bash orchestrator/hooks/lint_phase.sh implement
```

## Exit Codes

- `0`: All checks passed
- `non-zero`: At least one check failed

The hook fails fast - stops on first error for quick feedback.

## Extending the Orchestrator

### Adding New Language Support

1. Detect language in `lint_phase.sh`:

   ```bash
   if [[ -f "go.mod" ]]; then
     echo "→ Go workspace detected"
     # Add Go validation commands
   fi
   ```

2. Add validation commands for the phase
3. Update documentation

### Adding New Phases

1. Add phase case in `lint_phase.sh`:

   ```bash
   case "$PHASE" in
     myPhase)
       echo "  • Running custom checks..."
       ./my-validator || EXIT_CODE=$?
       ;;
   esac
   ```

2. Document the phase contract in `APPROACH.md`

### Custom Validators

Place custom validation scripts in `orchestrator/hooks/`:

```bash
orchestrator/
└─ hooks/
   ├─ lint_phase.sh
   └─ custom_validator.sh
```

Call from `lint_phase.sh`:

```bash
bash orchestrator/hooks/custom_validator.sh || EXIT_CODE=$?
```

## Plugin Governance

### Overview

The orchestrator enforces security and compliance through mandatory plugin invocations at each phase. See `orchestrator/plugins.policy.md` for complete policy.

### Plugin Invocation Per Phase

#### Spec Phase (`/spec`)

**Required Plugins:**

```bash
# Security guidance
/security-guidance --phase=spec --output=reports/security/spec-findings.md

# API security (if APIs present)
/backend-api-security --mode=threat-model --output=reports/security/spec-findings.md --append
```

**Output:** `reports/security/spec-findings.md`

#### Plan Phase (`/plan`)

**Required Plugins:**

```bash
# SAST + dependency scanning
/security-scanning --mode=sast,deps --output=reports/security/plan-scan.md --severity=all
```

**Output:** `reports/security/plan-scan.md`

#### Tasks Phase (`/tasks`)

**Required Plugins:**

```bash
# Python unit test scaffolding (conditional)
if [[ -f "requirements.txt" ]] || [[ -f "pyproject.toml" ]]; then
  /unit-testing --mode=scaffold --output=reports/tests/tasks-unit-help.md
fi
```

**Output:** `reports/tests/tasks-unit-help.md` (Python only)

#### Implement Phase (`/implement`)

**Required Plugins:**

```bash
# Continuous security scanning
/security-scanning --mode=sast,deps --output=reports/security/implement-scan.md --diff=reports/security/plan-scan.md
```

**Output:** `reports/security/implement-scan.md`

#### Analyze Phase (`/analyze`)

**Required Plugins:**

```bash
# Full security analysis with delta tracking
/security-scanning --mode=full --output=reports/security/analyze-deltas.md
cat reports/security/analyze-deltas.md >> docs/CHANGELOG.md

# Compliance validation
/security-compliance --frameworks=OWASP,CWE --output=reports/compliance/analyze-compliance.md
```

**Outputs:**

- `reports/security/analyze-deltas.md`
- `reports/compliance/analyze-compliance.md`
- Appends to `docs/CHANGELOG.md`

### Artifact Gating

The `lint_phase.sh` hook enforces artifact requirements:

1. **Artifact Existence:** Required report files must exist
2. **Severity Blocking:** CRITICAL/HIGH findings block progression
3. **Mitigation Required:** Unmitigated findings require:
   - Mitigation plan in `plans/plan.md`, OR
   - Waiver ADR in `DECISIONS.md`

**Exit Codes:**

- `0` - All checks passed
- `1` - Missing artifacts
- `2` - Unmitigated CRITICAL/HIGH findings
- `3` - Invalid mitigation documentation

### Mitigation Documentation

**In `plans/plan.md`:**

```markdown
## Security Mitigations

### [FINDING-ID] Finding Title

- **Severity:** CRITICAL/HIGH
- **Status:** Mitigated | Accepted Risk | Waived
- **Mitigation:** Detailed description of fix or compensating controls
- **Verification:** How mitigation will be verified
```

**Waiver ADR in `DECISIONS.md`:**

```markdown
## ADR-XXX: Security Finding Waiver - [FINDING-ID]

**Status:** Accepted
**Date:** YYYY-MM-DD

**Context:** Description of the security finding

**Decision:** Accept the risk because [justification]

**Consequences:**

- Risk accepted: [description]
- Compensating controls: [if any]
- Review date: [when to reassess]
```

### Reports Directory Structure

```
reports/
├── security/
│   ├── spec-findings.md
│   ├── plan-scan.md
│   ├── implement-scan.md
│   └── analyze-deltas.md
├── tests/
│   └── tasks-unit-help.md
└── compliance/
    └── analyze-compliance.md
```

## Troubleshooting

### "command not found: pnpm"

Install pnpm globally:

```bash
npm install -g pnpm
```

Or use npm fallback (already in hook):

```bash
npm run lint
```

### "cargo: command not found"

Install Rust toolchain:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### Hook Permission Denied

Make hook executable:

```bash
chmod +x orchestrator/hooks/lint_phase.sh
```

### Tests Failing in CI but Pass Locally

- Check environment differences (Node/Rust versions)
- Verify all dependencies installed
- Check for flaky tests or timing issues

## Configuration

### Skipping Specific Checks (Not Recommended)

Modify `lint_phase.sh` to add skip flags:

```bash
# Only for temporary debugging - remove before commit
SKIP_TESTS=true

if [[ "$SKIP_TESTS" != "true" ]]; then
  pnpm run test || EXIT_CODE=$?
fi
```

### Adjusting Clippy Strictness

Modify Clippy command in hook:

```bash
# Current (strict)
cargo clippy --all-targets -- -D warnings

# Relaxed (warnings only)
cargo clippy --all-targets
```

---

**Last Updated**: 2025-10-14
**Status**: Active
