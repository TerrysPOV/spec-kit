# Orchestrator Plugin Policy

## Overview

This policy defines mandatory plugin invocations at each development phase to ensure security, compliance, and quality standards are met throughout the development lifecycle.

## Plugin-Phase Mapping

### 1. Spec Phase (`/spec`)

**Required Plugins:**

- `security-guidance` - Generate security requirements and threat model
- `backend-api-security` - API-specific security guidance (if APIs present)

**Output Artifacts:**

- `reports/security/spec-findings.md`

**Purpose:** Identify security requirements and threats early in the design phase.

### 2. Plan Phase (`/plan`)

**Required Plugins:**

- `security-scanning --mode=sast,deps` - Static analysis and dependency scanning

**Output Artifacts:**

- `reports/security/plan-scan.md`

**Purpose:** Validate architecture and dependencies for known vulnerabilities before implementation.

### 3. Tasks Phase (`/tasks`)

**Required Plugins:**

- `unit-testing --mode=scaffold` - Generate unit test scaffolds (Python projects only)

**Output Artifacts:**

- `reports/tests/tasks-unit-help.md` (Python only)

**Purpose:** Ensure test infrastructure is planned before implementation begins.

### 4. Implement Phase (`/implement`)

**Required Plugins:**

- `security-scanning --mode=sast,deps` - Continuous security validation

**Output Artifacts:**

- `reports/security/implement-scan.md`

**Purpose:** Catch security issues during active development.

### 5. Analyze Phase (`/analyze`)

**Required Plugins:**

- `security-scanning` - Comprehensive security analysis with delta tracking
- `security-compliance` - Compliance validation

**Output Artifacts:**

- `reports/security/analyze-deltas.md` (appended to `docs/CHANGELOG.md`)
- `reports/compliance/analyze-compliance.md`

**Purpose:** Final security validation and compliance certification before deployment.

## Gating Rules

### Artifact Requirements

Each phase MUST produce the required artifact files before proceeding to the next phase.

**Enforcement Location:** `orchestrator/hooks/lint_phase.sh`

### Severity-Based Blocking

**CRITICAL and HIGH severity findings:**

- **BLOCK** phase transition by default
- **ALLOW** only if:
  1. Mitigation plan exists in `plans/plan.md` with explicit reference to finding ID, OR
  2. Waiver ADR (Architecture Decision Record) exists in `DECISIONS.md` with justification

**MEDIUM and LOW severity findings:**

- **WARN** but allow phase transition
- Must be tracked in backlog

### Mitigation Documentation Format

In `plans/plan.md`:

```markdown
## Security Mitigations

### [FINDING-ID] Finding Title

- **Severity:** CRITICAL/HIGH
- **Status:** Mitigated | Accepted Risk | Waived
- **Mitigation:** Detailed description of fix or compensating controls
- **Verification:** How mitigation will be verified
```

### Waiver ADR Format

In `DECISIONS.md`:

```markdown
## ADR-XXX: Security Finding Waiver - [FINDING-ID]

**Status:** Accepted
**Date:** YYYY-MM-DD
**Decision Makers:** [Names/Roles]

**Context:** Description of the security finding

**Decision:** Accept the risk because [justification]

**Consequences:**

- Risk accepted: [description]
- Compensating controls: [if any]
- Review date: [when to reassess]
```

## Plugin Invocation Examples

### Spec Phase

```bash
# Security guidance
/security-guidance --phase=spec --output=reports/security/spec-findings.md

# API security (if applicable)
/backend-api-security --mode=threat-model --output=reports/security/spec-findings.md --append
```

### Plan Phase

```bash
# SAST + dependency scanning
/security-scanning --mode=sast,deps --output=reports/security/plan-scan.md --severity=all
```

### Tasks Phase

```bash
# Python unit test scaffolding (conditional)
if [[ -f "requirements.txt" ]] || [[ -f "pyproject.toml" ]]; then
  /unit-testing --mode=scaffold --output=reports/tests/tasks-unit-help.md
fi
```

### Implement Phase

```bash
# Continuous security scanning
/security-scanning --mode=sast,deps --output=reports/security/implement-scan.md --diff=reports/security/plan-scan.md
```

### Analyze Phase

```bash
# Full security analysis with delta tracking
/security-scanning --mode=full --output=reports/security/analyze-deltas.md
cat reports/security/analyze-deltas.md >> docs/CHANGELOG.md

# Compliance validation
/security-compliance --frameworks=OWASP,CWE --output=reports/compliance/analyze-compliance.md
```

## Enforcement Mechanism

The `orchestrator/hooks/lint_phase.sh` hook validates:

1. **Artifact Existence:** Required report files exist for the phase
2. **Finding Severity:** No unmitigated CRITICAL/HIGH findings
3. **Mitigation Documentation:** Valid mitigation plans or waivers exist

**Exit Codes:**

- `0` - All checks passed
- `1` - Missing artifacts
- `2` - Unmitigated CRITICAL/HIGH findings
- `3` - Invalid mitigation documentation

## Directory Structure

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

plans/
└── plan.md              # Mitigation plans

DECISIONS.md             # Security waivers and ADRs
docs/CHANGELOG.md        # Includes security deltas
```

## Exceptions

**Emergency Hotfixes:**

- May skip some plugin phases with explicit approval
- Must run full `analyze` phase validation before deployment
- Require post-deployment security audit

**Non-Production Environments:**

- Development/staging may use `--severity=medium` threshold
- Production MUST use `--severity=high` threshold

## Audit Trail

All plugin invocations and their outputs are tracked in:

- `reports/` directory (version controlled)
- Git commit history with plugin outputs
- CHANGELOG.md with security deltas

---

**Last Updated:** 2025-10-14
**Status:** Active
**Enforcement:** Mandatory via `lint_phase.sh`
