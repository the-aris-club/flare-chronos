# Claude Design → Production: Conversion Context

**Audience:** an agent or engineer who must turn the Flare-Chronos Claude Design export into production Next.js code.
**Status:** context only. The experiment protocol is in [`claude-design-to-prod-experiment.md`](./claude-design-to-prod-experiment.md).
**Rule:** this file describes what exists. It does not approve a design change. Read the source files before you edit code.

---

## 0. The short version

- The export is a **working prototype**, not a codebase. It runs on a generated runtime that fetches React 18 and Babel from a CDN at page load.
- The design is the **visual oracle** and the **interaction oracle**. It is not the source of truth for data, auth, routing, or state completeness.
- Production code must obey `rules/frontend.md`, `rules/i18n.md`, `rules/linting.md`, `rules/libraries.md`, and `rules/general.md`. Several of those rules conflict with a 1:1 pixel port. The conflicts are listed in §6 and §9–§10.
- A Next.js scaffold now exists at `apps/workbench` (Next 16.4.3, React 19.3.0, Tailwind 4, React Compiler, Bun). It is not yet aligned with the design or the team baseline. The scaffold is a prerequisite, not part of the conversion measurement.
- Do not port the synthetic data generator. Read the versioned artifacts in `data/processed/` and the live `ai-service`.
- Do not port the design's own documentation surfaces. They are not product screens.

**Product intent.** The app has two jobs. Show that 26 years of cross-sensor fire data can be harmonized into a stable calendar. Show that a human reviewer gates publication. The demo path is globe → workbench → calendar → evidence → briefing → review → decision. Optimise for that path. Do not add surfaces that are not on it. The two roles are analyst and approver. The two locales are EN and VI.

---

## 1. Source inventory

Archive used for this context: `/Users/xirothedev/Downloads/FlareChronos.zip` (SHA-256 `07018cad8150e1e50101e2e74ab1421139ac45d7285d5369ce750b0e924b2980`), extracted at
`/private/var/folders/gs/h6f9nkc50716wx9vzfr70mt00000gn/T/opencode/flare-final/`.

| File | Size | Lines | Role | Ships to production? |
|---|---:|---:|---|---|
| `Flare-Chronos Workbench.dc.html` | 189,292 B | 1,339 | Globe landing, Workbench, briefing/sign-off, connect, unavailable, tour, evidence drawer | Yes, converted |
| `Flare-Chronos Review.dc.html` | 140,239 B | 674 | Reviewer queue, run, audit, plus design-only state sheets | Partly. Queue/run/audit only |
| `Flare-Chronos Components.dc.html` | 24,845 B | 173 | Component and motion sheet | No. Reference only |
| `Flare-Chronos Screens.dc.html` | 6,045 B | 79 | Canvas of iframes for every screen | No. Reference only |
| `globe.html` | 25,238 B | 336 | Three.js region globe | No. Replace |
| `map.html` | 27,168 B | 364 | D3 equal-area map pane | No. Replace |
| `support.js` | 69,150 B | — | Generated DC runtime (`dc-runtime`) | No |
| `image-slot.js` | 65,350 B | — | Unused; the final export has no `<image-slot>` elements | No |
| `figures/fc-fig-*.png` | absent | — | Download targets for the five native figures | No. Copy from `docs/figures/` or remove the links |
| `assets/logo.png` | — | — | Logo | Yes |
| `shots/*.jpg` | — | — | Reference screenshots, including evidence captures | No |
| `uploads/*` | — | — | Design-tool leftovers; not referenced | No |

The archive has no `.image-slots.state.json` and no `<image-slot>` elements. `image-slot.js` and `uploads/` are dead. The five figure download links point to `figures/fc-fig-*.png`, which are not in the zip.

---

## 2. Runtime anatomy

`support.js` parses the `<x-dc>` element and renders it with React. It loads, at run time:

- `react@18.3.1/umd/react.production.min.js`
- `react-dom@18.3.1/umd/react-dom.production.min.js`
- `@babel/standalone@7.29.0/babel.min.js`

It also loads Google Fonts at page level. `globe.html` loads Three.js from unpkg through an import map. `map.html` loads D3 and TopoJSON from unpkg.

**Consequence:** the export does not run offline and cannot be copied into a Next.js app. Treat the markup as a template language, not as HTML.

### 2.1 Template syntax

| Directive | Meaning | Production mapping |
|---|---|---|
| `{{ expr }}` | Interpolation from `renderVals()` | JSX expression / props |
| `<sc-for list="{{ arr }}" as="x">` | List render | `arr.map(...)` |
| `<sc-if value="{{ cond }}">` | Conditional render | `cond && (...)` |
| `<script type="text/x-dc" data-dc-script>` | Component logic, `class Component extends DCLogic` | React component + hooks |
| `data-props` | Editor-exposed props | Typed component props |

Counts in the two product files: **1,621 interpolations, 190 loops, 216 conditionals**. The Workbench file alone has **576 inline `style="..."` attributes**; Review has 532.

### 2.2 Routing

There is no `data-screen-label` attribute in this export. The generic intake step in `workflows/claude-design-to-nextjs.md` does not apply as written. Screens are selected by query string:

- Workbench: `?screen=globe|workbench|briefing|published|connect|unavailable|tour|evidence`
- Review: `?view=queue|run|audit|states|sheet|notes|devices`
- Review run: `&run=A|B|C`
- Review overlays: `&overlay=briefing|confirm|citation`
- Shared: `&theme=dark|light`, `&lang=en|vi`
- Workbench forced breakpoint: `&bp=desktop|tablet|mobile`
- Workbench mobile tab: `&tab=map|cal|brief`

Use these parameters to capture the parity fixtures. Do not keep this router in production.

---

## 3. What ships and what does not

### 3.1 Ship

Workbench surfaces:

- Region globe landing, including the two region cards and the hand-over to the flat map.
- Workbench shell: header, physics filters, KPI strip, map pane, comparator, polar clock, calendar, evidence drawer, mobile tabs.
- Briefing and sign-off: run timeline, verification chips, Decision Basis, full-result dialog, citation detail, approve/reject, published and withheld outcomes.
- Connect and service-unavailable states.
- Six-step demo walkthrough.

Reviewer surfaces:

- Queue with tabs, filters, and row selection.
- Run view: evidence rail, verification table, sentence-level citations, decision form.
- Confirmation, full-briefing dialog, citation dialog.
- Audit trail.

### 3.2 Do not ship

- `Flare-Chronos Components.dc.html` and `Flare-Chronos Screens.dc.html`.
- Review `view=states`, `view=sheet`, `view=notes`, `view=devices`. These are design documentation.
- `DEMO · SIMULATE SERVICE`, the demo token `fc_demo_…`, and the service-state simulator.
- `apps/ai-service/src/ai_service/demo/index.html` and the `GET /` `FileResponse` route. The Workbench is the web client.
- `image-slot.js` and the `uploads/` leftovers. The final export has no `<image-slot>` elements.
- The prototype banner text as hard-coded chrome. Keep the ability to show it behind a flag for the demo build.
- The `REGIONS` mock generator and every number it synthesizes. See §5.1.

### 3.3 Replace

| Prototype | Production |
|---|---|
| `<iframe src="globe.html">` | Client island with a real globe library or a static SVG fallback |
| `<iframe src="map.html">` | Client island with a real map renderer, or a native SVG map |
| `?screen=` routing | Next.js App Router routes |
| `window.innerWidth` breakpoints | CSS-first Tailwind breakpoints |
| Unicode glyph icons | `ICON` registry + `<Icon>` |
| Inline `style="..."` | Tailwind utilities + `@theme` tokens |
| Google Fonts `<link>` | `next/font` |
| `image-slot` figures | Native SVG / chart components |

---

## 4. Screen and state inventory

### 4.1 Workbench

| Design screen | Content | Proposed route | Notes |
|---|---|---|---|
| `globe` | 3D globe, region cards, loader | `/` | Client-only; needs a no-WebGL fallback |
| `workbench` | Analysis workspace | `/workbench` | Main surface |
| `briefing` | Briefing + sign-off, paused run | `/workbench/runs/[runId]` or panel | Must not be a second approval path |
| `published` | Approved outcome | Run state `approved` | Not a route |
| `connect` | Token entry | `/connect` or auth dialog | Paste-token is a demo stopgap |
| `unavailable` | Service down, Tier 3 | Service state | Not a route |
| `tour` | 6-step overlay | `?tour=1` overlay | Not a route |
| `evidence` | Evidence drawer open | Drawer state | Not a route |

Run state machine in the Workbench panel: `idle → running → paused → done`. Production needs two more states that the panel does not implement: `clarification_requested` and `run_failed`. The API already emits both.

### 4.2 Review

| Design view | Content | Proposed route | Ships |
|---|---|---|---|
| `queue` | Needs decision / Published / Withheld tabs, filters | `/review` | Yes |
| `run` | Evidence rail, verification, decision | `/review/runs/[runId]` | Yes |
| `audit` | Append-only decision log | `/review/audit` | Yes |
| `states` | State catalogue | — | No |
| `sheet` | Component sheet | — | No |
| `notes` | Interaction notes | — | No |
| `devices` | Device frames | — | No |

Decision rules visible in the design:

- Approve is blocked while any Decision Basis item fails.
- Every decision requires a reason: approve and reject.
- Reject withholds publication. Approve publishes.
- Every decision records the principal, time, reason, and audit ID.

The design currently has **two approval paths**: a compact card in the Workbench and the full rail in Review. Production must have one. See D5 in §13.

---

## 5. Data contracts

### 5.1 Design mock — do not port

`Flare-Chronos Workbench.dc.html` defines `REGIONS` (Mekong, Amazon) with `peak`, `width`, `amp`, `base`, `frp`, `seed`, `epochs`, `anom`, `over`. `getData()` expands that into 26 years × 73 pentads of synthetic `z`, `hfd`, `hrf`, observation flags, and KPI numbers.

The mock exists to hold a visual ratio (for example `+1,324%`). It is not measured data. The real 2024 Mekong raw count is **50,988**, not **319,549**. Do not copy the generator or its constants.

### 5.2 Burning Activity Calendar artifact

**Domain offset.** The design calendar covers **2000–2025** (`YEARS` in the Workbench script). The artifact covers **2001–2026**. Both have 26 years, but they are shifted by one year. Do not align them by row index. Decide the production period and the label before the swap test (D7).

`data/processed/burning_calendar.json`, keyed by region (`mekong`, `amazon`):

| Field | Shape | Meaning |
|---|---|---|
| `years` | `number[26]` | 2001–2026. Not 2000–2025 |
| `hfd_matrix` | `number[26][73]` | Human Footprint Density per pentad. No nulls |
| `sfai_matrix` | `Array<number or null>`, 26 × 73 | SFAI. **Only 10 non-null values, all at pentad 15** |
| `cell_provenance_matrix` | values 0, 1, or 2, 26 × 73 | 0 = scored observed cell, 1 = observed cell, 2 = modelled/no direct observation |
| `observed_pentad` | `number` | 15 |
| `measured_years` | `number[11]` | 2005, 2007, 2010, 2012, 2016, 2019, 2020, 2023, 2024, 2025, 2026 |
| `interpolated_years` | `number[15]` | The remaining years |
| `summary_caption` | `string` | Peak window, scoring rule, severe anomaly |

**Do not assume a full SFAI matrix.** The design paints SFAI on every observed cell. The artifact scores one pentad for ten years. A full-matrix SFAI view needs a pipeline change, not a UI change. This is an open decision (D6).

2026 is listed as measured but its whole row is provenance `2` (modelled). Treat the near-real-time year separately.

### 5.3 Empirical artifact

`data/processed/empirical_results.json`:

| Key | Use |
|---|---|
| `scan_angle_physics` | Fig. 1: MODIS 1.0 → 9.6875 km² at 55°, VIIRS 0.1305 → 0.6154 km², ratio 74.23 |
| `coincident_calibration` | Fig. 3: N = 11,553, R² 0.733 → 0.7641, RMSE 149.104 → 140.154, KS 0.1166 → 0.0348 |
| `mekong_empirical_epochs`, `amazon_empirical_epochs` | 11 and 9 measured epochs with dedup, Ω, FRP, SAA |
| `regime_shift_series` | Fig. 4: raw and harmonized index, 2005 = 100, 26 years |
| `omission_factor_fit` | Omission correction per region |
| `saa_and_sza_nrt_audit` | SAA audit windows |

### 5.4 AI service

OpenAPI: `docs/openapi/ai-service.json` (3.1.0).

| Method | Path | Notes |
|---|---|---|
| `GET` | `/api/v1/analysis/use-cases` | Bearer auth |
| `GET` | `/api/v1/analysis/stream?query=&use_case_id=&thread_id=` | SSE. Bearer auth |
| `POST` | `/api/v1/analysis/resume` | SSE. Bearer auth. Owner or approver only |

SSE event types (`apps/ai-service/src/ai_service/events.py`):

`run_started`, `node_completed`, `tool_result`, `reasoning`, `message`, `sign_off_required`, `clarification_requested`, `verification`, `briefing`, `run_paused`, `run_completed`, `run_failed`.

Each SSE frame is `event: <type>` plus a JSON `data:` line. `EventSource` cannot send the bearer header, so the client must read the stream with `fetch` and a `ReadableStream` reader. ADR-0012 records this.

Errors: `400` missing query, `401` bad token, `403` thread owned by another principal, `404` no such run, `409` no sign-off waiting.

The service also serves a demo HTML page at `/` (`include_in_schema=False`). Remove it when the Workbench ships. It is not part of the API contract.

### 5.5 Provenance rule

Every displayed number needs a source. The Review design already models this with `facts`: value, unit, tool, raw value, provenance, verification state, and a sentence mapping. Production must preserve that chain. A number without a tool or artifact source is a defect, not a design detail.

### 5.6 Native figures

The Evidence drawer must draw five figures natively. It must not use image slots or PNGs as the primary display. Full specification: `docs/design/workbench-native-figures-prompt.md`.

The final export already implements this: `figureData` plus `fig1..fig5` in the Workbench file. Port the builders; do not re-create them from PNGs.

| Figure | Content | Data source | Sample size |
|---|---|---|---|
| 1 | Footprint area and FRP limit vs scan angle | sample curves now; `scan_angle_physics` for the endpoints | 12–16 points per curve |
| 2 | Overpass deduplication and observation effort Ω | sample bars now; `mekong_empirical_epochs` for Ω and counts | small; no sampling |
| 3 | Coincident-pair parity and ECDF/KS | sample points now; `coincident_calibration` for the summary values | 40–60 parity points; 24–40 ECDF points per curve |
| 4 | Raw vs harmonized regime shift | `regime_shift_series` | 26 years; no sampling |
| 5 | 26-year Burning Activity Calendar | `burning_calendar.json` | full matrix |

- The Polar Phenology Clock is the phenology view. Do not add a static phenology figure.
- Every chart reads one `figureData` object. Later implementation replaces that object with the full export; the chart components do not change.
- Source note: “Sample data · full series at implementation.”
- Published PNGs stay available as “Download published figure” links only.
- Use `recharts` for xy charts; use hand-written SVG for the calendar grid, polar clock, mini-map, and footprint lens.

---

## 6. Design system

### 6.1 Theme tokens

The design defines 26 CSS variables on `:root, [data-theme="dark"]` and overrides them on `[data-theme="light"]`.

| Token | Dark | Light | Semantic use |
|---|---|---|---|
| `--bg` | `#070b14` | `#f2f4f8` | Page |
| `--bg2` | `#0b111c` | `#ffffff` | Header, secondary surface |
| `--panel` | `#0c121e` | `#ffffff` | Card |
| `--raised` | `#121a29` | `#f5f7fa` | Raised row |
| `--seg` | `rgba(150,170,210,.16)` | `rgba(20,30,60,.08)` | Segmented control |
| `--glass` | `rgba(10,15,26,.74)` | `rgba(255,255,255,.82)` | Floating bar |
| `--line` | `rgba(150,170,210,.13)` | `rgba(20,30,60,.10)` | Hairline |
| `--line2` | `rgba(150,170,210,.26)` | `rgba(20,30,60,.20)` | Strong border |
| `--text` | `#eef2f8` | `#121a2b` | Primary text |
| `--text2` | `#b4bfd0` | `#3d485d` | Secondary text |
| `--text3` | `#8e9ab0` | `#5a6579` | Tertiary text |
| `--brand2` | `#8fb0ff` | `#0d3a8c` | Brand secondary |
| `--fire` | `#ff8a3d` | `#c4520f` | Fire accent |
| `--raw` | `#ff5a36` | `#cf3a1c` | Raw series |
| `--amber` | `#f5b23a` | `#9a5a00` | MODIS |
| `--teal` | `#3cc9b0` | `#0b7d6c` | Harmonized |
| `--cyan` | `#57e3ff` | `#0a8fb3` / `#0a6f8c` | Severe Anomaly Outline |
| `--purple` | `#b195ea` | `#7650c4` | Secondary annotation |
| `--grey` | `#8f99ab` | `#68728a` / `#5f6982` | Static / excluded |
| `--ok` | `#5fd394` | `#1b7f49` | Pass |
| `--warn` | `#f5b23a` | `#9a5a00` | Caution |
| `--bad` | `#ff7070` | `#bf3030` | Fail |
| `--hatch` | `rgba(150,170,210,.30)` | `rgba(20,30,60,.24)` | Modelled cells |
| `--focus` | `#eef2f8` | `#121a2b` | Focus ring |
| `--scrim` | `rgba(3,6,12,.70)` | `rgba(18,26,43,.46)` | Modal scrim |
| `--chipbg` | `rgba(150,170,210,.07)` | `rgba(20,30,60,.04)` | Chip fill |

**Drift:** `--cyan` and `--grey` differ between the Workbench and Review light themes. Unify them in `tokens.css`. Do not carry two values.

### 6.2 Typography

- IBM Plex Sans: 400, 500, 600, 700.
- IBM Plex Mono: 400, 500, 600.
- Observed sizes run from 8 to 22 px: 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15, 15.5, 16, 17, 18, 20, 22.
- Eight of those values are fractional: 8.5, 9.5, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5.
- Numerals are tabular throughout.

A 1:1 port would create a token for every fraction. Define a scale, accept at most 1 px drift where the scale cannot hold, and record the drift in the parity report. Do not use `text-[10.5px]`; `lint:tokens` rejects it.

### 6.3 Spacing and geometry

The Workbench has **1,072 px values in 576 inline styles**; 807 occurrences use values that are not multiples of 4. Review has **1,130 px values in 532 inline styles**; 748 off-grid.

This is the main friction between the design and the Tailwind/token baseline. Choose one policy per slice:

1. **Snap** to the 4 px scale. Fastest, cleanest, visible drift.
2. **Tokenise** the recurring odd values (`--space-1-5`, `--space-2-5`, `--space-7`, `--space-9`…). Slower, closer parity.
3. **Allow arbitrary values** for geometry only. Rejected: `lint:tokens` rejects `[Npx]`.

The experiment in the companion file measures which policy holds.

### 6.4 Breakpoints

| Surface | Desktop | Tablet | Mobile |
|---|---|---|---|
| Workbench | ≥ 1280 | ≥ 720 | < 720 |
| Review | ≥ 1180 | ≥ 700 | < 700 |

These do not match Tailwind (`sm` 640, `md` 768, `lg` 1024, `xl` 1280). Unify to Tailwind and document the drift, or the mobile and tablet layouts will change at the wrong width. Do not use `window.innerWidth`.

### 6.5 Colour semantics

- Raw series: orange. Harmonized series: teal. MODIS: amber. VIIRS: blue.
- Cyan is reserved for the Severe Anomaly Outline at ≥ +2.2σ.
- +2.5σ crisis uses the same outline plus a corner flag and its own label.
- Never encode state by colour alone. The design already pairs colour with text or shape. Keep that.

---

## 7. Component inventory and port mapping

| Component | Source | Interaction | Production target |
|---|---|---|---|
| App shell / header | Workbench | Region, period, grid, filters, language, theme, principal | `AppHeader` + route shell |
| KPI strip | Workbench | Epoch changes values | `KpiStrip` (server data) |
| Region globe | `globe.html` iframe | Drag, zoom, region select, fly-out | `RegionGlobe` client island + static fallback |
| Map pane | `map.html` iframe | Pan, zoom, H3 layer, footprint lens, tooltip | `FireMap` client island |
| Footprint lens | Workbench SVG | Compare MODIS edge / nadir / VIIRS | `FootprintLens` SVG |
| Calendar | Workbench `role="grid"` | Arrow keys, hover, click, tooltip, metric switch | `BurningCalendar` SVG/CSS grid |
| Polar clock | Workbench SVG | Hover, select pentad | `PhenologyClock` SVG |
| Comparator | Workbench SVG | Raw/harmonized/both | `ComparatorChart` (recharts) |
| Evidence drawer | Workbench | Open, close, figure tabs, download | `EvidenceDrawer` |
| Briefing panel | Workbench | Run, stream, verify, decide | `BriefingPanel` client island |
| Tour | Workbench | 6 steps, spotlight, gating | `DemoTour` overlay |
| Review queue | Review | Tabs, filters, search, select | `ReviewQueue` |
| Review run | Review | Rail, verification, citation, decision | `ReviewRun` |
| Audit trail | Review | Filter, expand | `AuditTable` |
| Dialogs | Both | Briefing, confirmation, citation | `Dialog` primitives |

Keep the design's domain names. Do not create `step-1.tsx`, `panel-a.tsx`, or other sequence names.

---

## 8. Target architecture (proposed)

The scaffold exists at `apps/workbench`. This is the target shape; align it rather than re-scaffold.

```
apps/workbench/
  src/app/layout.tsx
  src/app/globals.css
  src/app/page.tsx                    # globe landing
  src/app/workbench/page.tsx
  src/app/review/page.tsx
  src/app/review/runs/[runId]/page.tsx
  src/app/review/audit/page.tsx
  src/features/workbench/...
  src/features/review/...
  src/lib/data/calendar.ts            # reads the versioned artifact
  src/lib/data/figures.ts             # one figureData source
  src/lib/api/client.ts               # axios
  src/lib/api/stream.ts               # fetch + SSE reader
  src/components/ui/                  # primitives, ICON + Icon
  src/i18n/                           # en.ts, vi.ts
```

One app: keep primitives and catalogs local. Extract to `packages/ui` and `packages/i18n` when a second app needs them.

Rules for this shape:

- Server Components render static surfaces. Client islands own the map, globe, calendar interaction, drawers, and dialogs.
- One `figureData` module feeds every native figure. Replace the data source later; do not edit chart components.
- `next-intl` with a cookie locale, to match the design's toggle. Do not add a locale path segment unless routing requires it.
- `axios` for request/response. `fetch` only for SSE, sharing the base URL and auth header.
- The API exists. Wire it. Do not add Ponytail mock hooks for briefing or sign-off.
- Mark every temporary fixture with `TODO(api): <surface> — replace <fixture> with <METHOD> <path>; contract: <source>` at the loader boundary. Keep the inventory in the run record. The calendar artifact is not a mock. Never use the marker for sign-off or audit writes; those call the real endpoint in the same slice.
- Calendar and figures read the artifact at build time now; a CDN fetch later. Keep one loader boundary.

---

## 9. Binding rules

Read the modules, not this summary. The rule modules live in `The-Resonance-Team/skills`, not in this repository. Fetch them from the URLs in `CONTEXT.md`. The rules that decide most conversion findings:

| Rule | Application here |
|---|---|
| `rules/frontend.md` #4 | Tailwind v4 utilities only. No inline `style={{}}` |
| #5 | Put element resets in `@layer base`, custom classes in `@layer components`, add `@source "../"` and the UI package path |
| #6 | No raw hex or `[Npx]`; tokens in `tokens.css`. SVG `fill`/`stroke` and chart-series maps are the only hex exception |
| #7 | Import workspace packages through `package.json#exports`; no `export *` barrels |
| #8 | ≤ 300 lines per file; target ≤ 250 after `bun fmt` |
| #12 | `@tanstack/react-query`; no `useEffect` fetching |
| #14 | Escape JSX entities; data-drive repeated rows |
| #15 | Hooks before early returns |
| #17 | `ICON` registry, no Unicode glyphs, `aria-label` on icon-only controls |
| #19–#20 | Port motion by script; verify `getComputedStyle` and both locales live |
| #21 | Co-locate UI rules in root `DESIGN.md`. **This file does not exist yet** |
| `rules/libraries.md` #12 | `recharts` for static/dashboard charts; `uPlot` only for ≥30 Hz streams |
| `rules/linting.md` #9 | Run `bun fmt` before lint; 300-line cap after formatting |
| `rules/general.md` #5–#6 | Ponytail ladder; every `ponytail:` marker needs an upgrade trigger |
| `rules/i18n.md` | EN/VI catalogs, no machinery leaks, term table in `DESIGN.md` |

**Chart conflict.** `docs/design/workbench-native-figures-prompt.md` says “do not add a chart library if the existing SVG/React components are enough.” `rules/libraries.md` #12 fixes `recharts` for static charts. Resolution: the design prompt governs the `.dc.html` prototype; production uses `recharts` for xy charts, and hand-written SVG only for the calendar grid, the polar clock, the mini-map, and the footprint lens. Amend the prompt before the port so an agent does not read the two documents as contradictory.

---

## 10. Conversion traps

Each trap is observed in the export, not hypothetical.

| # | Trap | Evidence | Required action |
|---|---|---|---|
| T1 | Inline styles are the whole design system | 576 Workbench, 532 Review | Convert to Tailwind utilities and tokens. Do not ship `style={{}}` |
| T2 | Off-grid spacing dominates | 807 / 748 occurrences not divisible by 4 | Pick snap or tokenise per §6.3; record drift |
| T3 | Fractional type sizes | 8.5–15.5 px in eight fractional values | Define a scale; do not emit `[10.5px]` |
| T4 | Unicode glyphs used as icons | 15 glyphs: `‹ ← → ↓ ↻ ⊘ ⌃ ▶ ▸ ▾ ◆ ◐ ✓ ✕ ❙` | Map to `ICON`; keep arrows only inside sentence strings |
| T5 | Iframes and CDN modules | globe/map import maps; React/Babel from unpkg | Replace with npm dependencies and client islands |
| T6 | Synthetic data generator | `REGIONS`, `getData()`, 319,549 vs real 50,988 | Do not port. Read `data/processed/` |
| T7 | SFAI matrix is mostly null | 10 non-null values, all pentad 15 | Do not promise a full SFAI calendar. Decide D6 |
| T8 | Route state lives in the query string | `?screen=`, `?view=`, `?run=` | Move to routes; drawers/dialogs become state |
| T9 | Breakpoints drift between files | 1280/720 vs 1180/700 | Unify to Tailwind; no JS width hooks |
| T10 | Two approval paths | Workbench card + Review rail | Choose one. D5 |
| T11 | Design-only views look like product screens | Review `states/sheet/notes/devices` | Do not route them |
| T12 | Missing run states | Workbench panel has no clarification or failure state | Add both from the SSE contract |
| T13 | Demo chrome | `DEMO · SIMULATE SERVICE`, demo token | Remove. Keep the banner behind a flag |
| T14 | Image slots for scientific figures | `image-slot` in the evidence drawer | Native SVG / recharts; PNG only as download |
| T15 | Two light-theme token values | `--cyan`, `--grey` | Unify in `tokens.css` |
| T16 | Numbers are formatted with `+`/`−` glyphs and thin spaces | `+2.25σ`, `−3σ`, `+1,324%` | Format with `Intl.NumberFormat` and a shared formatter |
| T17 | Focus and disabled states are inconsistent | `aria-disabled` without `disabled` | Use native `disabled`; keep `aria-disabled` only for explanation |
| T18 | Fonts load from Google at run time | `<link>` in `<helmet>` | `next/font` with the same families |
| T19 | Design and artifact calendar years are offset | Design 2000–2025; artifact 2001–2026 | Align by year, not row index. Decide D7 before the swap |
| T20 | Run identity is inconsistent across surfaces | Workbench `R-0412`; Review `RUN-B`; audit `A-0193` missing from Review | Generate run and audit IDs from the service. Do not port the mock IDs |
| T21 | The AI service still serves a browser demo | `GET /` returns `demo/index.html` | Delete the page and the route. Serve no HTML from the API |
| T22 | A mock fixture looks like production data | Design runs, sample events, static lists | Mark the loader with `TODO(api)` and list it. Remove the mock when the endpoint lands |

---

## 11. Slice map

Build in this order. Each slice must pass the gates before the next starts.

| Slice | Content | Depends on | Risk |
|---|---|---|---|
| S0 | Scaffold: exists at `apps/workbench`; align tokens, fonts, lint, and the route shell | — | Low |
| S1 | Tokens, primitives, icon registry, locale catalogs | S0 | Medium. Token policy decides the rest |
| S2 | App shell, header, theme and locale switch, responsive frame | S1 | Medium |
| S3 | Calendar pane: grid, legend, tooltip, keyboard, artifact binding | S1–S2 | **High. Pilot slice** |
| S4 | KPI strip, comparator, polar clock | S3 | Medium |
| S5 | Evidence drawer, five native figures, `View data` | S3–S4 | High. Chart library decision |
| S6 | Review queue: tabs, filters, search, selection | S1–S2 | Low |
| S7 | Review run: rail, verification, citation, decision, dialogs | S6 | High. Trust surface |
| S8 | Audit trail | S7 | Low |
| S9 | Briefing: SSE, timeline, clarification, failure, sign-off | S7 | **High. Auth and stream** |
| S10 | Globe and map islands, fallbacks | S2 | **High. WebGL and CDN** |
| S11 | Tour | S3–S9 | Low |
| S12 | Responsive, accessibility, EN/VI sweep | S3–S11 | Medium |
| S13 | Real-data swap and deletion of sample fixtures | S3–S5 | Medium |

S3 is the pilot because it combines dense SVG, responsive layout, tokens, i18n, and a real artifact. A strategy that fails there will fail everywhere.

---

## 12. Definition of done

A slice is done only when all of these pass on the merged tree:

1. `bun fmt` (or the repo formatter) runs first.
2. `bun lint --no-script --max-warnings=0 --allow-unsupported` returns zero.
3. `tsc --noEmit` / `bun check` returns zero.
4. `lint:tokens` reports zero new raw hex or pixel literals. Until that script lands, use the experiment grep gate.
5. `lint:icons` reports zero JSX glyphs and every icon-only control has a label. Until that script lands, use the experiment grep gate.
6. `lint:boundaries` passes; no barrel imports.
7. No file exceeds 300 lines after formatting.
8. Unit tests pass; the calendar data mapper and formatter have tests.
9. The page loads with zero console errors and zero hydration errors.
10. Computed layout matches the design at 1440, 834, and 390, in dark and light.
11. EN and VI both render with no leaked strings from the other locale.
12. Keyboard-only use reaches every control; focus order is visible.
13. Replacing the sample fixture with the real artifact requires no component edit.
14. No design-only surface, demo token, or simulator is reachable.
15. Every temporary fixture has a `TODO(api)` marker and an inventory row; production has none.
16. `git status` is clean of generated files.

---

## 13. Open decisions

| ID | Decision | Why it blocks |
|---|---|---|
| D1 | Workspace shape: standalone Bun app or Bun workspace with packages? | The scaffold exists; the package split is open |
| D2 | URL shape and locale strategy | `?screen=` cannot survive; `next-intl` needs a locale decision |
| D3 | Map and globe technology | Iframes and unpkg imports cannot ship |
| D4 | Chart library for Fig. 1–4 | `recharts` baseline vs hand-written SVG |
| D5 | One approval gate: Workbench, Review, or both with one read-only | The current design has two |
| D6 | Full SFAI matrix or scored pentad only | The artifact has 10 scored cells |
| D7 | Period label: 2001–2026, 2000–2025, or 2000–2026 | Design, artifact, and docs disagree |
| D8 | Prototype banner in the production build | Keep behind a flag or remove |
| D9 | Spacing policy: snap or tokenise | Decides parity and token churn |
| D10 | Breakpoint unification | Decides tablet and mobile layout |

Resolve D2–D3 before the experiment. D1 is the workspace shape; D4–D10 can be resolved by the results.

---

## 14. Related documents and reading order

| Document | Use |
|---|---|
| [`claude-design-zip-to-apps-prompt.md`](./claude-design-zip-to-apps-prompt.md) | Ready-to-run prompt: design zip → `apps/workbench` |
| `workflows/claude-design-to-nextjs.md` in skills | Zip intake, porting gates, live parity, and the conversion method check |
| `docs/04_UI_UX_Burning_Calendar_Wireframe.md` | Product wireframe. §3.2 calendar, §3.5 briefing and sign-off |
| `docs/design/workbench-claude-design-prompt.md` | Original Workbench brief. Background only |
| `docs/design/workbench-reviewer-ui-prompt.md` | Reviewer queue, run, citation, and decision surfaces |
| `docs/design/workbench-native-figures-prompt.md` | The five native figures and the sampled-data rule |
| `docs/design/workbench-fix-pass-prompt.md` | Corrections already applied to the export. Do not re-apply |
| `docs/adr/0011-web-facing-ai-service.md` | Service contract, auth, SSE, static calendar artifact |
| `docs/adr/0012-workbench-single-mode-real-data-and-api.md` | Real data and real API only. No replay |
| `docs/openapi/ai-service.json` | Generated API contract |
| `CONTEXT.md` in `The-Resonance-Team/skills` | Rule and workflow router. Fetch the modules from here |
| `apps/workbench/AGENTS.md` and `apps/workbench/node_modules/next/dist/docs/` | Version-matched Next docs. Read before using a Next API |

Reading order by slice:

- **Calendar or figure slice:** §5, §6, §7 of this file, then the native-figures prompt.
- **Reviewer slice:** §4.2 of this file, then the reviewer prompt, then wireframe §3.5.
- **Briefing slice:** §4.1 and §5.4 of this file, then ADR-0011 and ADR-0012.
