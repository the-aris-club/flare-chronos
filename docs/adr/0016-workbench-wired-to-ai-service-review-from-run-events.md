---
status: proposed
---

# Workbench Is Wired To ai-service; Review Is Derived From Stored Run Events

**Supersedes** the 2026-11-01 amendment to [ADR-0012](./0012-workbench-single-mode-real-data-and-api.md) and the "static review fixtures" and "five `TODO(api)` markers" clauses of [ADR-0013](./0013-workbench-route-map-and-demo-boundaries.md).

## Decision

Every Workbench surface that read a fixture reads the real source instead: the briefing run and sign-off call `ai-service` directly with a pasted bearer token (held in memory, CORS set for the Workbench origin, stream read with `fetch`), the Calendar reads only the exported artifact, and Review is a projection of a **Run Event Log** the service now stores. The simulator, the `data/fixtures/review*` files, the app-local `/api/review/decisions` route and `CALENDAR_FIXTURE` are deleted.

`ai-service` gains an append-only events table, `GET /api/v1/review/runs`, `GET /api/v1/review/runs/{id}` and `GET /api/v1/review/runs/{id}/audit`, and an optional `reason_code` on resume and audit (migration keeps the append-only triggers). Approvers see every Review Run; other principals see their own. Run content (briefing, fact text) is shown as authored, never machine-translated; interface chrome stays EN/VI. The reviewer shown is the principal named by the token.

The use cases that do not support the harmonization claim are removed (UC-5.1, UC-5.2, UC-5.3, UC-4.3, UC-3.2), leaving 15: five System 1 and ten System 2, with 18 registered tools. UC-3.3 was proposed for removal but kept: its tool reports the published Aqua→SNPP FRP calibration (KS 0.117 → 0.024), which is harmonization evidence, not autonomous recalibration.

## Considered Options

- **Keep the simulator for the demo**: Always works. Rejected — a reviewer cannot tell a simulated run from a real one, the failure ADR-0012 exists to prevent.
- **A separate review store in the Workbench**: Fewer service changes. Rejected — it would be a second source of truth that can drift from what the run showed.
- **Machine-translate briefings to Vietnamese**: Full bilingual parity. Rejected — it breaks the Grounded Narrative guarantee that a verified briefing is what was verified.

## Consequences

- A run must exist before Review has anything to show; `scripts/seed-runs` produces real runs through the live System 1 and System 2 chain.
- Done means a live end-to-end run in the browser, plus a check that every verified fact equals the same cell of the Calendar artifact.
- A SQLite single instance remains the upgrade path described in ADR-0011.
- Counts of "20 use cases / 23 tools" (now 15 / 18) in the README, MODEL_FLOW and ADR-0005 must be updated with the cut.
