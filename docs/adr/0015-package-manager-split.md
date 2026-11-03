---
status: accepted
---

# Package Manager Split: Bun for Workbench, pnpm for Release Automation

**Supersedes** the single-package-manager baseline for this repository.

## Context

The Workbench app, its install, build, formatting and lint gates run on Bun (`bun.lock`, `bun@1.4.4`). The root release automation and CI are built around pnpm: `.github/workflows/release.yml` and `auto-bump-version.yml` use `pnpm/setup`, `pnpm install --frozen-lockfile`, and `pnpm run doc:version|release`.

## Decision

Keep the split explicit:

- `apps/workbench`: Bun, `bun.lock`, `bun run dev|build|typecheck`, `bun fmt`/`bun lint` from the root.
- Root changesets/release: pnpm, `pnpm-lock.yaml`, existing workflows.

Do not change `packageManager` or remove `pnpm-lock.yaml` without migrating both workflows in the same change. A future migration must add a Bun lockfile at the root and replace `pnpm/setup` + pnpm scripts with Bun equivalents.

## Consequences

- The baseline "one package manager" rule is explicitly superseded for this repo.
- A reviewer can see which tool owns which path; `pnpm install` inside `apps/workbench` is not supported.
