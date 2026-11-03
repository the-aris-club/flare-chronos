---
status: accepted
---

# Single Bun Toolchain

**Supersedes** ADR-0015 (package manager split).

## Context

ADR-0015 kept pnpm at the root and Bun in `apps/workbench`. Two lockfiles for one repository broke `release.yml` with `ERR_PNPM_OUTDATED_LOCKFILE` when a root dependency changed, and every dependency change had to be installed twice.

## Decision

Use Bun for every JavaScript path:

- `packageManager: bun@1.4.4` in the root `package.json` and in `apps/workbench/package.json`.
- Root `bun.lock` and `apps/workbench/bun.lock`; `pnpm-lock.yaml` is removed.
- `release.yml` and `auto-bump-version.yml` use `oven-sh/setup-bun` and `bun install --frozen-lockfile`.
- `bun run doc:version`, `bun run release` and `bun run lint-workbench` are the entry points.

## Consequences

- A root dependency change needs one `bun install`.
- Release and Workbench gates run on the same runtime.
- Documentation commands say `bun`, not `pnpm`.
