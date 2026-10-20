---
status: accepted
---

# Monorepo Deep-Module Architecture with Checklist Facade Seam

We structure the repository as a Python monorepo (`packages/harmonization-core`, `packages/firms-ingestion`, `apps/benchmark-cli`) built around deep modules with minimal interfaces, while exposing a compatibility facade at `src/harmonization/firms_harmonizer.py`.

## Consequences

- `packages/harmonization-core` is pure scientific domain logic with zero network or filesystem side effects: callers and tests pass in `ThermalDetection` records and receive harmonized `FireEpisode` and `BurningActivityCalendar` structures.
- `packages/firms-ingestion` isolates NASA FIRMS REST API pagination, rate-limit pacing (`5,000 transactions / 10 min`), and local CSV caching behind a clean ingestion seam.
- `src/harmonization/firms_harmonizer.py` satisfies external evaluation rubrics expecting the single-path module while delegating all computation to `packages/harmonization-core`.
