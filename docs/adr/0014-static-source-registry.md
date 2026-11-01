---
status: accepted
---

# Static Source Registry Replacement

**Supersedes** the persistent-cell part of the static-source registry for this archive.

## Context

The harmonization core's `build_static_source_registry` needs observations from all 12 calendar months. The supplied archive contains one 5-day slice per measured epoch, all in the same season, so a 12-month registry cannot be built without marking seasonal burning cells as industrial.

## Decision

The Workbench uses two explicit, reviewable substitutes:

1. FIRMS `type` 1–3 flags in `apps/workbench/scripts/flag-map-points.py` identify volcano, static and offshore detections.
2. The four Mekong and three Amazon source-coordinate marks in `src/lib/workbench/regions.ts` are the design's reference static sources, drawn as diamonds.

The map does not claim a persistent H3 registry, and the UI label says "Static heat source", not "persistent source". If a 12-month archive is supplied, `flag-map-points.py` adds `persistent_static_h3_res8` from the core and the source-coordinate marks remain a design reference.

## Consequences

- The static layer is conservative and does not hide seasonal burning.
- The limitation is visible in the map/README/ADR rather than hidden in a filter.
