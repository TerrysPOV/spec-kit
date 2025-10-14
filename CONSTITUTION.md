# Spec Kit Constitution

## Project Vision

Spec Kit is a polyglot monorepo orchestrator that coordinates development workflows across TypeScript/Node.js and Rust workspaces using Turborepo and Cargo.

## Core Principles

### 1. Polyglot First

- **TypeScript/Node.js**: Managed via Turborepo and pnpm workspaces
- **Rust**: Managed via Cargo workspace
- All languages are first-class citizens with equal support

### 2. Phase-Based Development

Development follows explicit phases with automated validation:

- **spec**: Requirements and design specification
- **implement**: Code implementation with full validation
- **review**: Code review and quality checks
- **deploy**: Production deployment

### 3. Atomic Commits

- One logical change per commit
- Conventional Commit format: `type(scope): description`
- Types: feat, fix, chore, docs, refactor, test, perf
- All commits must pass phase validation

### 4. Automated Quality Gates

Every phase enforces quality through hooks:

- **Linting**: ESLint (TS), Clippy (Rust)
- **Formatting**: Prettier (TS), rustfmt (Rust)
- **Type checking**: TypeScript, Cargo check
- **Testing**: Vitest (TS), Cargo test (Rust)

### 5. Zero Tolerance for Broken Builds

- All changes must pass validation before commit
- CI/CD pipelines enforce the same checks
- No exceptions for "quick fixes"

## Repository Structure

```
spec-kit/
├─ apps/                    # Applications
│  └─ web/                  # Next.js app
├─ packages/                # Shared libraries
│  └─ ui/                   # UI components
├─ rust/                    # Rust workspace
│  └─ svc_api/              # Axum API service
├─ orchestrator/            # Orchestrator tooling
│  └─ hooks/                # Phase validation hooks
├─ turbo.json               # Turborepo config
├─ Cargo.toml               # Rust workspace
└─ package.json             # Root package
```

## Development Workflow

1. **Start**: Create feature branch from `main`
2. **Spec**: Document requirements and design
3. **Implement**: Write code with continuous validation
4. **Review**: Pass all quality gates
5. **Merge**: Conventional commit to main
6. **Deploy**: Automated deployment

## Non-Negotiables

- ✅ All code must be formatted before commit
- ✅ All tests must pass before commit
- ✅ All type checks must pass before commit
- ✅ All lints must pass before commit
- ❌ No direct commits to main (PR required)
- ❌ No skipping validation hooks
- ❌ No placeholder/TODO code in main

---

**Last Updated**: 2025-10-14
**Status**: Active
