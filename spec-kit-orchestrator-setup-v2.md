# Spec Kit Orchestrator – Polyglot Setup Guide (v2)

This version adds a **Turborepo + Cargo workspace** scaffold and optional **Claude Code plugin marketplace** usage.

## Turborepo + Cargo Workspace

- **Turborepo** orchestrates JS/TS package tasks with caching (root `turbo.json`, `pnpm-workspace.yaml`, root `package.json` scripts).
- **Cargo workspace** manages Rust crates under `rust/*` with root `Cargo.toml`.

**Added paths**
- `turbo.json`, `pnpm-workspace.yaml`, root `package.json`
- `apps/web` (Next/TS), `packages/ui` (TS lib)
- `Cargo.toml` (workspace), `rust/svc_api` (Axum service)

**Quick run**
```bash
# js/ts
pnpm install -w || npm install -w
pnpm build || npm run build
# rust
cargo fmt -- --check && cargo test --quiet
```

## Claude Code Plugin Marketplace (optional)

- Add a marketplace:  
  `/plugin marketplace add https://www.aitmpl.com/plugins`  
  `/plugin marketplace add https://claudecodemarketplace.com`
- Install essentials:  
  `/plugin install code-formatter`  
  `/plugin install testing-helpers`  
  `/plugin install security-scanner`
- Persist repo-scoped preferences in `.claude/settings.json` so teammates auto-adopt the same set when trusting the folder.

The rest of the guide remains the same as v1 (constitution, phase contracts, lint hooks, CI).
