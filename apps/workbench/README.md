# Region Globe, Workbench and Review

Flare Chronos has three surfaces:

- `/` — the Region Globe landing: a rotating 3D Earth with the two measured
  regions, the real 2005→2024 growth headline, and entry into either region. The
  four-step loading screen covers the first paint.
- `/workbench/mekong` and `/workbench/amazon` — the analysis workspace: map with interactive physics filters,
  H3 heatmap and static/SAA layers; key figures, comparator, phenology clock,
  Burning Activity Calendar, service-state briefing rail, evidence drawer with
  data tables, map scale bar, walkthrough and Review handoff. Entering from the
  globe captures the settled frame and morphs it into the map pane.
- `/review` — the reviewer queue, run detail, briefing/citation/decision dialogs
  and read-only audit trail. `/review/runs/[id]` and `/review/audit` are the
  nested routes.

`/` no longer redirects. Entry links carry the region and the last measured epoch:

```text
/workbench/amazon?epoch=2024
/workbench/mekong?tour=1
/review/runs/RUN-0412
/review/runs/RUN-0412?overlay=briefing
```

## Run

```sh
bun install
bun dev
```

Open `/`. Formatting and linting are repo-root gates: `bun run format`,
`bun run lint`.

## Data

- `../../data/processed/burning_calendar.json` — the production calendar:
  26 years (2001–2026) × 73 pentads for the Mekong and Amazon regions.
- `../../data/processed/empirical_results.json` — annual series, measured
  epochs, episode counts and scan-angle physics. The landing headline and the
  card tick rows are derived from this file.
- `src/data/map-data.json` — pre-projected country paths and sampled real
  detections from `../../data/raw/*.csv` for the Workbench map. Every point
  carries physics flags from the harmonization core (SZA night, SAA false alarm,
  static source, 60-minute duplicate); per-epoch counts come from the full
  slices. `scripts/flag-map-points.py` owns those flags.
- `src/data/globe-data.json` — equirectangular land, border and graticule paths
  plus the merged focus-country silhouettes for the 3D globe. The runtime draws
  these into canvas textures; no d3 or topojson ships.
- `public/globe/earth.jpg` — NASA Blue Marble, 2048 × 1024, served locally.
- `src/data/fixtures/review*.ts` — the design's review runs, facts, brief
  templates, decisions and audit rows. These are sample records; every boundary
  that must become HTTP is marked `TODO(api)`. Do not add a fixture mode: the
  Review pages and the Workbench briefing run read these records directly until
  the analysis API is wired. The Workbench rail simulates the service states,
  connect steps and run stream locally around RUN-0412.
- `../../docs/design/fixtures/design-calendar.json` — the calendar parity
  fixture (2000–2025). Enable it with `CALENDAR_FIXTURE=design`; never use it in
  production.

The loaders check `CALENDAR_DATA_PATH` / `CALENDAR_FIXTURE_PATH` /
`EMPIRICAL_DATA_PATH` first, then the repo-relative paths. Run the app from this
directory so `process.cwd()` resolves those paths.

## Scripts

- `bun dev` — development server.
- `bun build` — production build.
- `bun start` — production server.
- `bun run typecheck` — `tsc --noEmit`.
- `../../.venv/bin/python scripts/flag-map-points.py` — read the raw FIRMS
  slices, apply the core physics flags and sampling, and write
  `.cache/map-points.json` (git-ignored).
- `bun scripts/build-map-data.mjs` — project the flagged points and build the
  Workbench map data.
- `bun scripts/build-globe-data.mjs` — regenerate the globe paths and region
  silhouettes.

The map and globe builds need the Natural Earth atlas (110m):

```sh
curl -sSL -o countries-110m.json \
  https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json
../../.venv/bin/python scripts/flag-map-points.py
WORLD_ATLAS_PATH=$PWD/countries-110m.json bun scripts/build-map-data.mjs
WORLD_ATLAS_PATH=$PWD/countries-110m.json bun scripts/build-globe-data.mjs
```

The map build reads `.cache/map-points.json`; `MAP_POINTS_PATH` overrides it.
Both map and globe scripts write minified JSON. Run `bun run format` from the
repo root after regenerating so the committed files match `.oxfmtrc.json`.

The Review surface and the Workbench briefing run use the design fixtures until
the API exists. The markers are the 5 remaining `TODO(api)` comments in `src/`; decisions and
audit rows persist through `/api/review/decisions`. Replace the remaining review
run and analysis-stream boundaries with the endpoints described in
`docs/openapi/ai-service.json`.

Replace `public/globe/earth.jpg` only with a public-domain NASA Blue Marble
frame at the same 2:1 aspect. The globe falls back to a flat vector map when
WebGL is unavailable.
