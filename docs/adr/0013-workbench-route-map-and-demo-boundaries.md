---
status: accepted
---

# Workbench Zone Routes, Map Interaction, and Demo Boundaries

**Builds on** [ADR-0012](./0012-workbench-single-mode-real-data-and-api.md).

## Decision

- The detailed Workbench is `/workbench/[zone]` (`mekong`, `amazon`). `/workbench` and the old `?region=` links redirect to the zone path and preserve `epoch` and `tour`.
- The map is a pre-projected 1000x730 SVG with client-side pan/zoom (wheel, trackpad, pinch, drag, 1–64x), a merged focus-country coverage polygon, true-scale footprint ellipses, a true-scale footprint lens, hover tooltips, H3 bins at Res 4–8, and static/SAA/SZA layers.
- H3 bins are computed from the sampled projected detections. They are not a full-resolution H3 polygon artifact.
- Static-source flags use the FIRMS `type` 1–3 subset. The core's 12-month persistent-cell registry cannot be built from the archive's same-season 5-day slices, so the map does not claim that broader registry.
- The design's archipelago reference markers (Hoàng Sa, Trường Sa) are not ported. They are reference-only design marks, not a measurement layer.
- Static review fixtures remain for the queue and run detail. Decisions and audit rows persist through the app-local `/api/review/decisions` route. The five remaining `TODO(api)` markers name the run list/detail, briefing connect, briefing run and run detail route.
- Root release automation uses pnpm because `.github/workflows/release.yml` and `auto-bump-version.yml` are configured for it. The Workbench app and its gates use Bun. This is an explicit split, not drift to be "fixed" without changing CI.

## Consequences

- Unknown zones return 404; the zone is the route source of truth.
- The map's client transforms do not rebuild the d3 projection on resize, so the pane keeps a stable aspect and may show more ocean than a live refit.
- The static-source and archipelago limits are visible in `RUN.md` and `DESIGN.md`; they are data/design boundaries, not missing UI wiring.
- Any move to a live review service must replace the app-local decisions route and the five markers together.

> The "static review fixtures" and "five `TODO(api)` markers" clauses are superseded by [ADR-0016](./0016-workbench-wired-to-ai-service-review-from-run-events.md).
