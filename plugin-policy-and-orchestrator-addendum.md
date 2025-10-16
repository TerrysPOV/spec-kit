# Plugin-Enforced Governance Addendum (Turborepo + Cargo + Spec Kit Orchestrator)

This addendum wires your **global Claude Code plugins** into the Spec Kit orchestrator so they run at the **right phase**, produce **auditable reports**, and **gate progress** via the linter.

## Objectives
- Invoke **security** and **testing** plugins deterministically during `/spec`, `/plan`, `/tasks`, `/implement`, `/analyze`.
- Persist results under `reports/` (markdown) for easy review and diffs.
- **Fail the phase** if critical findings exist or required artifacts are missing.
- Only require Python-specific helpers when a Python stack is present.

---

## 1) Add Plugin Policy

Create `orchestrator/plugins.policy.md`:

```md
# Plugin Policy (global/user plugins)

## Invocation rules by phase
- /spec:
  - Run: `security-guidance` to prompt for threats/auth/crypto reminders.
  - Run: `backend-api-security` (design review) if any APIs are proposed.
  - Save notes → `reports/security/spec-findings.md`.

- /plan:
  - Run: `security-scanning` to scan manifests and any early code (SAST + deps).
  - Save full report → `reports/security/plan-scan.md`.
  - If any HIGH/CRITICAL findings, propose mitigations and block until mitigated or risk accepted in `plans/plan.md#Risks`.

- /tasks:
  - If Python present (pyproject/requirements.txt), run: `unit-testing` to generate/augment tests or guidance.
  - Save a short summary → `reports/tests/tasks-unit-help.md`.

- /implement:
  - Run: `security-scanning` again (SAST + deps).
  - Save full report → `reports/security/implement-scan.md`.
  - Block on HIGH/CRITICAL unless waived in `docs/ADR-XXXX.md` with justification.

- /analyze:
  - Run: `security-scanning` final pass; append delta to `docs/CHANGELOG.md`.
  - Run: `security-compliance` (SOC2/GDPR posture check).
  - Save compliance report → `reports/compliance/analyze-compliance.md`.
```

---

## 2) Update ORCHESTRATOR.md (plugin invocation + file outputs)

Append under **Phase Loop**:

```md
## Plugin Invocation (global)
- Invoke plugins via slash commands. If a plugin is unavailable, proceed but record a note in the report.
- Save outputs under `reports/` as markdown files so results are reviewable and gating is enforceable in lint.

## Phase Loop
PHASES = [/spec, /plan, /tasks, /implement, /analyze]

For each PHASE:
1) Planner mode → checklist from contract + plugin policy preview. Ask "Proceed?"
2) Agent mode → load preamble, phase prompt, and phase contract.
3) Produce contract outputs only.
4) **Run plugins per `orchestrator/plugins.policy.md`**:
   - /spec:
     - `/plugin run security-guidance`
     - `/plugin run backend-api-security` (if APIs in scope)
     - Save summary → `reports/security/spec-findings.md`
   - /plan:
     - `/plugin run security-scanning --mode=sast,deps`
     - Save → `reports/security/plan-scan.md`
   - /tasks:
     - If Python present: `/plugin run unit-testing --mode=scaffold`
     - Save → `reports/tests/tasks-unit-help.md`
   - /implement:
     - `/plugin run security-scanning --mode=sast,deps`
     - Save → `reports/security/implement-scan.md`
   - /analyze:
     - `/plugin run security-scanning --mode=sast,deps`
     - Append deltas to `docs/CHANGELOG.md`
     - `/plugin run security-compliance`
     - Save → `reports/compliance/analyze-compliance.md`
5) Run: `bash orchestrator/hooks/lint_phase.sh <phase>`.
6) If lint fails, fix and re-run.
7) Commit with `feat(<phase>): …`
8) Advance state; after /analyze, propose next feature.
```

> Use the plugin’s built‑in help if flags differ; always capture a markdown summary file in `reports/` even when the plugin prints to chat.

---

## 3) Tighten Phase Contracts (expect plugin artifacts)

Append these sections to your existing contracts:

**`subagents/spec.contract.md`**

```md
## Plugin Artifacts
- Produce `reports/security/spec-findings.md` with a bulleted list of risks and proposed controls.
```

**`subagents/plan.contract.md`**

```md
## Plugin Artifacts
- Produce `reports/security/plan-scan.md` summarizing SAST/dependency findings + severity counts.
- If any HIGH/CRITICAL → add mitigation owner & timeline in `plans/plan.md` and block progression until addressed or risk accepted in an ADR.
```

**`subagents/tasks.contract.md`**

```md
## Plugin Artifacts (conditional)
- If Python stack present, produce `reports/tests/tasks-unit-help.md` documenting test scaffolding or coverage goals.
```

**`subagents/implement.contract.md`**

```md
## Plugin Artifacts
- Produce `reports/security/implement-scan.md` with severity counts. HIGH/CRITICAL must be zero or explicitly waived in `docs/ADR-XXXX.md`.
```

**`subagents/analyze.contract.md`**

```md
## Plugin Artifacts
- Produce `reports/compliance/analyze-compliance.md` (SOC2/GDPR posture + actions).
- Append security scan deltas to `docs/CHANGELOG.md`.
```

---

## 4) Enforce in the Linter

Append to `orchestrator/hooks/lint_phase.sh`:

```bash
# Helper near other helpers
sev() { grep -Eo 'CRITICAL|HIGH|MEDIUM|LOW' | sort | uniq -c || true; }

if [[ "$PHASE" == "spec" ]]; then
  [[ -f reports/security/spec-findings.md ]] || { echo "Missing reports/security/spec-findings.md (security-guidance/backend-api-security)"; exit 1; }
fi

if [[ "$PHASE" == "plan" ]]; then
  [[ -f reports/security/plan-scan.md ]] || { echo "Missing reports/security/plan-scan.md (security-scanning)"; exit 1; }
  if grep -Eiq 'CRITICAL|HIGH' reports/security/plan-scan.md; then
    grep -Eiq 'Mitigation|Owner|Timeline' plans/plan.md || { echo "High/critical findings require named mitigations in plans/plan.md"; exit 1; }
  fi
fi

if [[ "$PHASE" == "tasks" ]]; then
  if [[ -f pyproject.toml || -f requirements.txt ]]; then
    [[ -f reports/tests/tasks-unit-help.md ]] || { echo "Missing reports/tests/tasks-unit-help.md (unit-testing plugin)"; exit 1; }
  fi
fi

if [[ "$PHASE" == "implement" ]]; then
  [[ -f reports/security/implement-scan.md ]] || { echo "Missing reports/security/implement-scan.md (security-scanning)"; exit 1; }
  if grep -Eiq 'CRITICAL|HIGH' reports/security/implement-scan.md; then
    grep -Eiq 'ADR-[0-9]+' docs || { echo "High/critical findings require explicit ADR waiver reference"; exit 1; }
  fi
fi

if [[ "$PHASE" == "analyze" ]]; then
  [[ -f reports/compliance/analyze-compliance.md ]] || { echo "Missing reports/compliance/analyze-compliance.md (security-compliance)"; exit 1; }
fi
```

> Upgrade to JSON parsing later if your plugins can emit machine‑readable reports.

---

## 5) Paste‑Ready Prompt for Claude Code (to implement this addendum)

Use this as a single message inside your active Claude Code session at the repo root:

```md
**Addendum: Plugin-enforced governance**

1) Read `orchestrator/plugins.policy.md` (create it if missing with the rules below) and update **ORCHESTRATOR.md** to invoke plugins per phase, saving outputs in `reports/`:
   - /spec → `security-guidance` (+ `backend-api-security` if APIs) → `reports/security/spec-findings.md`
   - /plan → `security-scanning --mode=sast,deps` → `reports/security/plan-scan.md`
   - /tasks → if Python present → `unit-testing --mode=scaffold` → `reports/tests/tasks-unit-help.md`
   - /implement → `security-scanning --mode=sast,deps` → `reports/security/implement-scan.md`
   - /analyze → `security-scanning` (append deltas to `docs/CHANGELOG.md`) + `security-compliance` → `reports/compliance/analyze-compliance.md`

2) Amend phase contracts to expect these artifacts (sections titled **Plugin Artifacts**).

3) Extend `orchestrator/hooks/lint_phase.sh` with gating rules:
   - Require the artifact file for each phase.
   - Block on HIGH/CRITICAL findings unless mitigations exist in `plans/plan.md` or a waiver ADR is referenced.

4) Make atomic, conventional commits for each logical change. Show me a concise summary of changed paths when done, then proceed with the current phase.
```