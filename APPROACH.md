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

**Validation**: Documentation review, stakeholder approval

### 2. Implement Phase
**Goal**: Write production-quality code

**Deliverables**:
- Feature implementation
- Unit tests
- Integration tests
- Documentation updates

**Validation**: All automated checks pass
- TypeScript: eslint, prettier, tsc, vitest
- Rust: cargo fmt, cargo clippy, cargo test

### 3. Review Phase
**Goal**: Ensure code quality and maintainability

**Deliverables**:
- Peer review completed
- Performance validated
- Security reviewed
- Documentation updated

**Validation**: PR approved by maintainers

### 4. Deploy Phase
**Goal**: Ship to production safely

**Deliverables**:
- Production build created
- Deployment automation executed
- Monitoring configured
- Rollback plan verified

**Validation**: Deployment succeeds, health checks pass

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
