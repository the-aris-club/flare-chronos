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
`bun run lint-workbench`.

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
- `src/components/service/service-provider.tsx` — holds the pasted bearer token (memory plus an `fc_token` cookie)
  and calls `ai-service` directly (`NEXT_PUBLIC_AI_SERVICE_URL`, default
  `http://127.0.0.1:5901`). Review and the briefing rail read the real service;
  there are no fixtures and no fixture mode (ADR-0016).

The loaders check `CALENDAR_DATA_PATH` /
`EMPIRICAL_DATA_PATH` first, then the repo-relative paths. Run the app from this
directory so `process.cwd()` resolves those paths.

## Scripts

- `bun dev` — development server.
- `bun build` — production build.
- `bun start` — production server.
- `bun run typecheck` — `bun check`.
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

## Rebuilding the map base layers

The map's countries, rivers, lakes and shaded relief are Natural Earth 1:10m (public domain).
Inputs live in `.cache/ne` (git-ignored); the exact download commands are at the top of
`scripts/build-map-data.mjs` and `scripts/build-map-relief.py`.

```bash
bun scripts/build-map-data.mjs                          # vectors + lon/lat grid for the relief
../../.venv/bin/python -I scripts/build-map-relief.py   # public/map/relief-<region>.webp
```

The points in `map-data.json` come from `scripts/flag-map-points.py` and are unaffected.

## Running against the analysis service

Review and the briefing rail need a running `ai-service`; the map, charts and Calendar do not.

```bash
# service (live System 1 / System 2 models read the workspace .env)
AI_SERVICE_JWT_KEY=<32+ byte secret> AI_SERVICE_CORS_ORIGINS=http://localhost:5900 \
  uv run python -m ai_service.serve --mode live
# a token for a reviewer; the approver role may decide sign-offs
AI_SERVICE_JWT_KEY=<same secret> uv run python scripts/mint_demo_token.py --sub examiner --roles approver
# optional: fill Review with real runs
AI_SERVICE_TOKEN=<token> uv run python scripts/seed_runs.py
```

Paste the token into the briefing rail or the Review page. It is also stored in an `fc_token` cookie (SameSite=Strict, expiring with the token), so a
reload reconnects; Disconnect clears it. Tokens for the dev team and the examiner come from
`AI_SERVICE_JWT_KEY=<key> bun credentials` (`fc-dev-…`, `fc-examiner-…` in `.credentials`). `NEXT_PUBLIC_AI_SERVICE_URL` overrides the service address.

Replace `public/globe/earth.jpg` only with a public-domain NASA Blue Marble
frame at the same 2:1 aspect. The globe falls back to a flat vector map when
WebGL is unavailable.
