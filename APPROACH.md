# Spec Kit Development Approach

## Philosophy

Spec Kit embraces a **polyglot-native, phase-driven** approach to software development:

1. **Language Agnostic**: Each language has its own best practices and tooling
2. **Explicit Phases**: Development follows clear, validated phases
3. **Fast Feedback**: Automated checks catch issues immediately
4. **Progressive Enhancement**: Build features incrementally with confidence

## Phase Contracts

### 1. Spec Phase

**Goal**: Define what we're building and why

**Deliverables**:

- Requirements documented
- Architecture decisions recorded
- API contracts defined
- Success criteria established

**Plugin Artifacts**:

- `reports/security/spec-findings.md` - Security requirements and threat model
  - Plugin: `/security-guidance --phase=spec`
  - Plugin: `/backend-api-security --mode=threat-model` (if APIs present)
- **Gating**: Artifact must exist; CRITICAL/HIGH findings require mitigation plan

**Validation**: Documentation review, stakeholder approval, security requirements validated

### 2. Plan Phase

**Goal**: Design implementation approach and architecture

**Deliverables**:

- Implementation plan documented
- Technical design decisions
- Dependency analysis
- Risk assessment

**Plugin Artifacts**:

- `reports/security/plan-scan.md` - SAST and dependency scan results
  - Plugin: `/security-scanning --mode=sast,deps`
- **Gating**: Artifact must exist; CRITICAL/HIGH findings block implementation start

**Validation**: Plan reviewed, dependencies validated, security risks assessed

### 3. Tasks Phase

**Goal**: Break down implementation into trackable tasks

**Deliverables**:

- Task breakdown documented
- Acceptance criteria defined
- Test strategy outlined
- Effort estimates

**Plugin Artifacts**:

- `reports/tests/tasks-unit-help.md` - Unit test scaffolding (Python projects only)
  - Plugin: `/unit-testing --mode=scaffold` (conditional)
- **Gating**: Artifact required for Python projects; test infrastructure validated

**Validation**: Tasks reviewed, test strategy approved

### 4. Implement Phase

**Goal**: Write production-quality code

**Deliverables**:

- Feature implementation
- Unit tests
- Integration tests
- Documentation updates

**Plugin Artifacts**:

- `reports/security/implement-scan.md` - Continuous security validation
  - Plugin: `/security-scanning --mode=sast,deps --diff=reports/security/plan-scan.md`
- **Gating**: Artifact must exist; CRITICAL/HIGH findings block review

**Validation**: All automated checks pass

- TypeScript: eslint, prettier, tsc, vitest
- Rust: cargo fmt, cargo clippy, cargo test
- Security: no unmitigated CRITICAL/HIGH findings

### 5. Analyze Phase

**Goal**: Comprehensive security and compliance analysis

**Deliverables**:

- Security delta analysis
- Compliance validation
- Risk assessment update
- Changelog updated

**Plugin Artifacts**:

- `reports/security/analyze-deltas.md` - Security changes since last analysis
  - Plugin: `/security-scanning --mode=full`
  - Appended to `docs/CHANGELOG.md`
- `reports/compliance/analyze-compliance.md` - Compliance framework validation
  - Plugin: `/security-compliance --frameworks=OWASP,CWE`
- **Gating**: Both artifacts required; CRITICAL/HIGH findings block deployment

**Validation**: Security validated, compliance confirmed, changes documented

### 6. Review Phase

**Goal**: Ensure code quality and maintainability

**Deliverables**:

- Peer review completed
- Performance validated
- Security reviewed
- Documentation updated

**Validation**: PR approved by maintainers, all plugin artifacts validated

### 7. Deploy Phase

**Goal**: Ship to production safely

**Deliverables**:

- Production build created
- Deployment automation executed
- Monitoring configured
- Rollback plan verified

**Plugin Artifacts**:

- All analyze phase artifacts must be validated
- No unmitigated CRITICAL/HIGH findings
- Compliance attestation documented

**Validation**: Deployment succeeds, health checks pass, security gates cleared

## Turborepo Integration

Turborepo orchestrates TypeScript/Node.js workspaces with intelligent caching:

```bash
# Run tasks across all workspaces
pnpm build     # Build all apps and packages
pnpm dev       # Run all dev servers in parallel
pnpm lint      # Lint all workspaces
pnpm test      # Test all workspaces
pnpm typecheck # Type-check all workspaces
```

**Task Dependencies**:

- `build` depends on upstream package builds
- Tasks are cached based on inputs (smart rebuilds)
- Parallel execution where possible

## Cargo Workspace Integration

Cargo manages Rust crates with shared dependencies:

```bash
# Workspace-level commands
cargo build --all           # Build all crates
cargo test --all            # Test all crates
cargo clippy --all-targets  # Lint all crates
cargo fmt --all             # Format all crates
```

**Benefits**:

- Shared dependency resolution
- Unified build artifacts
- Cross-crate refactoring support

## Orchestrator Hook System

The orchestrator validates code at each phase using `orchestrator/hooks/lint_phase.sh`:

```bash
# Triggered by phase transition
bash orchestrator/hooks/lint_phase.sh implement
```

**Hook Behavior**:

- Auto-detects languages (Node/Rust)
- Runs appropriate validators
- Fails fast on first error
- Reports clear failure reasons

## Best Practices

### TypeScript/Node.js

- Use strict TypeScript configuration
- Prefer named exports over default exports
- Write tests alongside implementation
- Use Prettier for consistent formatting

### Rust

- Follow Rust idioms (rustfmt defaults)
- Enable Clippy warnings in CI
- Use `cargo fmt` before commit
- Write doc tests for public APIs

### Git Workflow

- Branch naming: `feature/description`, `fix/description`
- Commit format: `type(scope): description`
- Small, focused commits
- Keep commits atomic and reversible

### Documentation

- Keep docs close to code
- Update docs in the same commit as code
- Use inline comments for complex logic
- Maintain high-level architecture docs

## Tooling Decisions

**Package Manager**: pnpm (faster, disk-efficient)
**Monorepo Tool**: Turborepo (caching, parallelization)
**Build Tool**: Native tooling (tsc, cargo)
**Test Framework**: Vitest (TS), built-in (Rust)
**Linting**: ESLint 9 (flat config), Clippy
**Formatting**: Prettier, rustfmt

---

**Last Updated**: 2025-10-14
**Status**: Active
