# Plans Directory

This directory contains implementation plans and security mitigation documentation.

## Structure

```
plans/
└── plan.md              # Implementation plan with security mitigations
```

## Security Mitigations

When plugin scans identify CRITICAL or HIGH severity findings, mitigations must be documented in `plan.md` using this format:

```markdown
## Security Mitigations

### [FINDING-ID] Finding Title

- **Severity:** CRITICAL/HIGH
- **Status:** Mitigated | Accepted Risk | Waived
- **Mitigation:** Detailed description of fix or compensating controls
- **Verification:** How mitigation will be verified
```

## Enforcement

The orchestrator hook (`orchestrator/hooks/lint_phase.sh`) checks for security mitigations before allowing phase transitions.

**Alternatives to mitigation plans:**

- Security waiver ADR in `DECISIONS.md` (for accepted risks)

See `orchestrator/plugins.policy.md` for complete policy.

---

**Last Updated:** 2025-10-14
**Status:** Active
