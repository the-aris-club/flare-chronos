# Design Zip → `apps/workbench` — Phase 1 Inventory

**Archive:** `/Users/xirothedev/Downloads/Workbench mobile and tablet improvements.zip`
**SHA-256:** `6c28de5fba7166058f6c8ea0218aea3e84e453c8a996f3f80bb13e078cd8f8c7`
**Extracted at:** `/private/var/folders/gs/h6f9nkc50716wx9vzfr70mt00000gn/T/opencode/fc-zip/out/` (read-only)
**Base commit:** `e24c57ed134561905ecf64280d9123923de7c066` (`main`)
**Pilot:** Workbench shell + Burning Activity Calendar.

> **Scope update (2026-11-01):** the pilot was expanded to the full Workbench
> center at the user's request: map, physics-filter summary, KPI strip,
> comparator, phenology clock, calendar, briefing rail, evidence drawer,
> walkthrough, and mobile tabs. A second pass added the Region Globe landing
> (`/`) with a Three.js Earth, the four-step loading screen, region cards, deep
> links, and the Workbench Globe button. A third pass added the full Briefing
> rail (fixture run) and the Review queue/run/dialogs/audit pages from the
> design's `RUNS` and `INIT_DEC` fixtures, plus the map scale bar, evidence
> tables and quick-look, tour spotlight and globe tooltip/peek. `RUN.md` §2 and
> §12 are the current record. The tables below remain the original Phase 1
> inventory; the built components are marked in the table.

> **Archive mismatch (recorded assumption).** The task prompt cites `FlareChronos.zip` at SHA-256 `07018cad…`, 1,339 Workbench lines, `R-0412`, `RUN-B`, and figure PNG downloads. That archive is not on disk. The supplied `Workbench mobile and tablet improvements.zip` is newer: period `2001–2026`, native SVG figure builders, a read-only Workbench decision card, unified `RUN-0412`, no figure download links, and a Review urgency column plus search. This port follows the supplied archive. Where the prompt's facts describe the older export, the newer export wins and the difference is recorded in `RUN.md`.

## 1. Archive contents and hashes

| File | Lines | SHA-256 (prefix) | Ships |
|---|---:|---|---|
| `Flare-Chronos Workbench.dc.html` | 1,321 | `0b30db16e588f356…` | Converted (pilot: shell + calendar) |
| `Flare-Chronos Review.dc.html` | 678 | `0ac5f9864d7ca698…` | Ported with the design fixture runs |
| `Flare-Chronos Screens.dc.html` | 79 | `e1a5420ff8714ee4…` | No |
| `Flare-Chronos Components.dc.html` | 173 | `e5d5668acf6c44f9…` | No |
| `globe.html` | 336 | `ef41d70224f79f75…` | Ported to `three.js` (`lib/globe`); no iframe |
| `map.html` | 364 | `a535f06dc1b1ecb3…` | Pre-projected SVG (`map-pane.tsx`) |
| `support.js` | — | — | No (DC runtime) |
| `assets/logo.png` | — | `b3aa1c9b36e915bd…` | Yes (same file as `docs/figures/flare-chronos-logo.png`) |
| `shots/*.jpg` | — | — | Reference only |

## 2. Intake scan

| Metric | Workbench | Review |
|---|---:|---:|
| Inline `style="…"` attributes | 553 | 535 |
| `sc-if` | 48 | 58 |
| `sc-for` | 32 | 47 |
| `{{ }}` interpolations | 764 | 741 |
| `px` values in inline styles | 1,033 | 1,150 |
| Off-grid `px` values (not ÷4) | 773 | 761 |
| Fractional type sizes | 8.5, 9.5, 10.5, 11.5, 12.5 | 6 values |
| Unicode icon glyphs | 51 | 113 |
| `<iframe>` | 2 | 1 |
| `<image-slot>` | 0 | 0 |
| CDN imports | Google Fonts only (React/Babel via `support.js`) | Google Fonts only |

## 3. Screens, query parameters, overlays, states

### 3.1 Workbench (`Flare-Chronos Workbench.dc.html`)

Query: `?screen=`, `&theme=dark|light`, `&lang=en|vi`, `&region=mekong|amazon`, `&bp=desktop|tablet|mobile`, `&tab=map|trend|cal|brief`, `&step=1..6`.

| Design screen | Content | Product? | App Router path |
|---|---|---|---|
| `globe` | Three.js region globe, two region cards, loader | Yes (later) | `/` (deferred; pilot redirects `/` → `/workbench`) |
| `workbench` | Analysis workspace | Yes | `/workbench/[zone]` |
| `briefing` | Briefing + sign-off, paused run | **Yes (rail)** | `/workbench` (rail) → `/review/runs/RUN-0412` |
| `published` | Approved outcome | Yes | Run state `approved`, not a route |
| `connect` | Token entry | No (ADR-0012: token issued out of band) | — |
| `unavailable` | Service down, Tier 3 | Yes | Panel state, not a route |
| `tour` | Six-step walkthrough | Yes (later) | Overlay state `?tour=1`; no route |
| `evidence` | Evidence drawer | Yes (later) | Drawer state; no route |

**Pilot states:** theme (dark/light), locale (EN/VI), breakpoint (desktop ≥1280 / tablet ≥720 / mobile <720), calendar metric (HFD/SFAI), active cell, hover cell, data source (artifact / parity fixture), load error.

**Later states:** run `idle → running → paused → done`, plus the missing `clarification_requested` and `run_failed`; service `up|degraded|down`; connection `none|resolved|connected`; evidence drawer open/closed and figure tab; briefing rail open/collapsed; mobile tab; tour step 1–6.

### 3.2 Review (`Flare-Chronos Review.dc.html`)

Query: `?view=`, `&run=A|B|C`, `&overlay=briefing|confirm|citation`, `&theme=`, `&lang=`.

| Design view | Content | Product? | App Router path |
|---|---|---|---|
| `queue` | Needs decision / Published / Withheld tabs, filters, search, urgency column | Yes (later) | `/review` |
| `run` | Evidence rail, verification, citations, decision form | Yes (later) | `/review/runs/[runId]` |
| `audit` | Append-only decision log | Yes (later) | `/review/audit` |
| `states` | State catalogue | No | — |
| `sheet` | Component sheet | No | — |
| `notes` | Interaction notes | No | — |
| `devices` | Device frames | No | — |

**Overlays:** full briefing dialog, confirmation dialog, citation detail. **Product:** yes, later slice.

## 4. Components

| Component | Source | Pilot? | Target |
|---|---|---|---|
| App shell / header | Workbench | **Yes** | `app-header.tsx` in `workbench-shell.tsx` |
| Brand mark | Workbench sprite | **Yes** | `brand-mark.tsx` (CSS sprite crop of `/logo.png`) |
| Theme toggle | Workbench | **Yes** | `theme-toggle.tsx` + `theme-provider.tsx` |
| Language toggle | Workbench | **Yes** | `locale-toggle.tsx` |
| Burning Activity Calendar | Workbench `role="grid"` | **Yes** | `burning-calendar.tsx` (client container) |
| Calendar grid | Workbench CSS grid | **Yes** | `calendar-grid.tsx` (hand-written SVG) |
| Calendar legend / metric toggle | Workbench | **Yes** | `calendar-legend.tsx` |
| Calendar readout | Workbench fixed card | **Yes** | `calendar-summary.tsx` replaces the tooltip |
| Segmented control | Workbench | **Yes** | `segmented-control.tsx` |
| Icon registry | — | **Yes** | `icon.tsx` (`ICON`, `AmIcon`, lucide) |
| Map pane / equal-area map | Workbench `map.html` | **Yes** | `map-pane.tsx`, `workbench-map.tsx` (pre-projected SVG) |
| Physics filter bar | Workbench | **Yes (interactive)** | `filter-bar.tsx` |
| H3 heatmap + Res 7/8 | Workbench `map.html` | **Yes** | `workbench-map.tsx`, `lib/workbench/h3.ts` |
| Static-source / SAA / SZA layers | Workbench `map.html` | **Yes (sampled real flags)** | `workbench-map.tsx`, `scripts/flag-map-points.py` |
| Map scale bar | Workbench `map.html` | **Yes (projection px/km)** | `map-legend.tsx` |
| KPI strip | Workbench | **Yes** | `kpi-strip.tsx` |
| Comparator | Workbench | **Yes** | `comparator-pane.tsx` (recharts) |
| Polar phenology clock | Workbench | **Yes** | `clock-pane.tsx` (hand-written SVG) |
| Briefing / sign-off rail | Workbench | **Yes (service simulator)** | `briefing-rail.tsx`, `briefing-run.tsx`, `briefing-events.tsx`, `service-panel.tsx` |
| Service states / connect flow | Workbench `briefing` | **Yes (up/degraded/down; token handshake)** | `service-panel.tsx`, `lib/workbench/service.ts` |
| Globe→map entry morph | Workbench `arrive()` | **Yes (frame snapshot → map pane)** | `globe-morph.tsx`, `lib/globe/snapshot.ts`, `lib/globe/morph.ts` |
| Evidence drawer (5 figures) | Workbench | **Yes (PNGs + data tables)** | `evidence-drawer.tsx` |
| Walkthrough | Workbench | **Yes (spotlight + card)** | `tour.tsx` |
| Region Globe landing | Workbench `screen=globe` + `globe.html` | **Yes** | `globe-landing.tsx`, `globe-canvas.tsx`, `lib/globe` |
| Landing header / region cards | Workbench | **Yes** | `landing-header.tsx`, `region-card.tsx` |
| Loading screen | Workbench loader | **Yes** | `boot-overlay.tsx` (4 real steps) |
| Globe fallback | — | **Yes** | `globe-fallback.tsx` (flat SVG) |
| Review queue | Review | **Yes (fixture)** | `review-queue.tsx` |
| Review run / decision rail | Review | **Yes (fixture)** | `review-run.tsx`, `review-decision.tsx` |
| Briefing, citation, confirmation dialogs | Review | **Yes (fixture)** | `briefing-dialog.tsx`, `citation-dialog.tsx`, `confirm-dialog.tsx` |
| Audit trail / export | Review | **Yes (fixture)** | `review-audit.tsx` |
| Review fixtures | Review `RUNS` / `INIT_DEC` | **Yes** | `src/data/fixtures/review*.ts` |

## 5. Data sources

| Surface | Current (design) | Target | Contract |
|---|---|---|---|
| Calendar | `getData()` synthetic 2000–2025 | `data/processed/burning_calendar.json` (2001–2026) | ADR-0011 |
| Calendar parity | `getData('mekong')` | `docs/design/fixtures/design-calendar.json` (SHA-256 `b738d4a319d5c5d1…`), `CALENDAR_FIXTURE=design` only | experiment §5.2 |
| Evidence figures | `figureData` + `fig1..fig5` | `data/processed/empirical_results.json` + calendar artifact | native-figures prompt |
| Workbench map | `map.html` synthetic points | `src/data/map-data.json` (pre-projected; sampled real detections) | `RUN.md` §1 |
| Globe surface | `three-globe` Blue Marble CDN | `public/globe/earth.jpg` (local NASA Blue Marble) | `RUN.md` §1 |
| Globe borders / silhouettes | runtime 50m atlas + topojson | `src/data/globe-data.json` (110m, build-time) | `RUN.md` §1 |
| Landing headline | design I18N fixed `14×` | computed 2005→2024 growth (14× / 8×) + catalogs | `DESIGN.md` §6 |
| Review runs / decisions / audit | design `RUNS` / `INIT_DEC` | design fixtures in `src/data/fixtures` | `RUN.md` §9 |
| Briefing run | design sample run | RUN-0412 fixture; live stream TODO(api) | `RUN.md` §9 |
| Evidence figures | native SVG + tables | published PNGs + generated data tables | `RUN.md` §11 |
| Briefing run | sample events | `GET /api/v1/analysis/stream` | `docs/openapi/ai-service.json` |
| Sign-off | local handler | `POST /api/v1/analysis/resume` | `docs/openapi/ai-service.json` |
| Use cases | static list | `GET /api/v1/analysis/use-cases` | `docs/openapi/ai-service.json` |
| Review queue / run / audit | mock runs | No endpoint yet; fixture runs + TODO(api) | `docs/openapi/ai-service.json` |

`burning_calendar.json` facts confirmed: 26 years (2001–2026), 26 × 73 matrices, 10 non-null SFAI values (all pentad 15), provenance `0` × 10, `1` × 720, `2` × 1,168, max HFD `8.0418`, 2026 entirely modelled.

## 6. Assets

| Asset | Use |
|---|---|
| `docs/figures/flare-chronos-logo.png` → `public/logo.png` | Header brand mark |
| IBM Plex Sans / Mono | `next/font`, weights 400/500/600/700 and 400/500/600 |
| `figures/fc-fig-*.png` | Not used: the newer export removed the download links |
| `globe.html` | Ported to `three.js`; the earth photo and paths are local |
| `map.html` | Ported to a pre-projected SVG (`map-data.json`) |
| NASA Blue Marble | `public/globe/earth.jpg`, 2048 × 1024 |

## 7. External runtime dependencies

| Design dependency | Production |
|---|---|
| React 18 UMD + Babel standalone (CDN) | `next@16.4.3`, `react@19.3.0` (installed) |
| Google Fonts `<link>` | `next/font/google` |
| Three.js (unpkg, `globe.html`) | `three@0.184.0`; client island + flat SVG fallback |
| D3 + TopoJSON (unpkg, `map.html`) | Build-only (`d3-geo`, `topojson-client`); runtime paths are pre-projected |
| `recharts` | `recharts@3.10.1` for the comparator; **not** the calendar |

Pilot adds `next-intl@4.14.9`, `lucide-react@1.66.0`, `recharts@3.10.1` and `three@0.184.0`.

## 8. Roles

| Role | Capability | Pilot |
|---|---|---|
| Analyst | Read the calendar and evidence; run briefings | Read-only calendar |
| Approver | Approve or reject a briefing in Review | **Yes (fixture runs)** |

One approval gate: Review owns the decision. The Workbench is read-only and links to Review; the Review pages record the decision and audit row. The runs are design fixtures until the review API is wired.

## 9. Missing states (must be added, not copied)

| Missing state | Where | Pilot action |
|---|---|---|
| `clarification_requested` | Briefing run | Later slice |
| `run_failed` | Briefing run | Later slice |
| Null SFAI | Calendar | **Added** — "not scored" / "chưa chấm điểm", never zero |
| Empty calendar | Calendar | Not reachable: the artifact always has 26 × 73 cells. Load failure renders `error.tsx`. |
| Calendar load error | Calendar | **Add** (`error.tsx`) |
| Hydration / locale leak | All | **Gate** |
| Keyboard path for the grid | Calendar | **Add** |

## 10. Route map

```
/                         → /workbench/mekong                (pilot)
/workbench/[zone]         → shell + Burning Activity Calendar (pilot)
/workbench/runs/[runId]   → briefing + sign-off            (later)
/review                   → reviewer queue                 (later)
/review/runs/[runId]      → reviewer run                   (later)
/review/audit             → audit trail                    (later)
```

## 11. Assumptions recorded

1. The supplied archive governs; the prompt's older-archive facts are noted, not applied.
2. D1: one app. Primitives in `src/components/ui`, catalogs in `src/i18n`; no `packages/ui` or `packages/i18n`.
3. D2: `next-intl`, cookie locale, no path segment.
4. D4: `recharts` for xy charts later; hand-written SVG for the calendar now.
5. D5: accepted by the newer export — Review owns the decision.
6. D7: period is `2001–2026`, derived from the artifact, not hard-coded.
7. D9: Tailwind's 2 px spacing scale; at most 1 px drift from the design's odd values.
8. D10: Tailwind breakpoints `tablet` 720 px and `xl` 1280 px, matching the Workbench.
9. The design's default metric is SFAI on a full synthetic matrix. The artifact scores 10 Mekong and 8 Amazon cells, so the pilot defaults to HFD and keeps SFAI as the sparse anomaly view. The artifact has no HRF matrix, so the pilot ships two metrics, not three.
10. The design's cursor-following tooltip becomes the fixed readout strip in the pane. The readout content is unchanged; the floating position is a DOM-style necessity, recorded as a deviation.
11. The artifact HFD is a density (events/100 km²/day), not the design fixture's detections/pentad. The readout unit follows the dataset; the fixture is parity-only.
12. The design's separate selected state is folded into the active cell. The readout labels the active cell Selected, matching the design's `hover || active` behaviour.
