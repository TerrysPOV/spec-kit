# Reports Directory

This directory contains plugin-generated security, testing, and compliance reports for each development phase.

## Structure

```
reports/
├── security/           # Security scan results
│   ├── spec-findings.md      # Spec phase security requirements
│   ├── plan-scan.md          # Plan phase SAST & deps scan
│   ├── implement-scan.md     # Implement phase security validation
│   └── analyze-deltas.md     # Analyze phase security deltas
├── tests/              # Test-related reports
│   └── tasks-unit-help.md    # Unit test scaffolding (Python)
└── compliance/         # Compliance validation
    └── analyze-compliance.md # OWASP/CWE compliance check
```

## Phase-Artifact Mapping

See `orchestrator/plugins.policy.md` for complete policy.

### Spec Phase

- `security/spec-findings.md` - Security requirements and threat model

### Plan Phase

- `security/plan-scan.md` - SAST and dependency scan results

### Tasks Phase

- `tests/tasks-unit-help.md` - Unit test scaffolding (Python only)

### Implement Phase

- `security/implement-scan.md` - Continuous security validation

### Analyze Phase

- `security/analyze-deltas.md` - Security changes (appended to CHANGELOG)
- `compliance/analyze-compliance.md` - Compliance framework validation

## Gating Rules

**CRITICAL/HIGH findings block phase transitions unless:**

- Mitigation plan exists in `plans/plan.md`, OR
- Waiver ADR exists in `DECISIONS.md`

**MEDIUM/LOW findings:**

- Warn but allow phase transition
- Must be tracked in backlog

## Version Control

All reports are version controlled to provide audit trail of security and compliance evolution.

---

**Last Updated:** 2025-10-14
**Status:** Active
