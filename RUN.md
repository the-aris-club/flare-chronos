# Design zip → `apps/workbench` — Region Globe, Workbench + Review run

> **Superseded in part (2026-11-02, ADR-0016).** Review and the briefing rail no longer use design fixtures, the service simulator, `/api/review/decisions` or `CALENDAR_FIXTURE`; they read the real `ai-service`. The fixture-era decisions below (D17, D19, D23, the `TODO(api)` table) are kept as history.


**Date:** 2026-11-01
**Start:** 11:19 +07 (scaffold present; design intake followed)
**End:** 17:54 +07
**Base:** `main` at `e24c57ed134561905ecf64280d9123923de7c066`
**Method:** contract-first, one arm. No markup-first arm was run.
**Status:** Region Globe, the full Workbench center and the Review surface are
complete. Review and the Briefing run use the design fixture runs; the live
analysis, review and audit APIs remain later. Phase 6 complete.

## 1. Inputs and hashes

| Input | Value |
|---|---|
| Archive supplied | `/Users/xirothedev/Downloads/Workbench mobile and tablet improvements.zip` |
| Archive SHA-256 | `6c28de5fba7166058f6c8ea0218aea3e84e453c8a996f3f80bb13e078cd8f8c7` |
| Extracted (read-only) | `/private/var/folders/gs/h6f9nkc50716wx9vzfr70mt00000gn/T/opencode/fc-zip/out/` |
| Workbench HTML SHA-256 | `0b30db16e588f356c08131edbf51259b0dcdc191c4f86f62fb0468babe4d8e43` (1,321 lines) |
| Review HTML SHA-256 | `0ac5f9864d7ca6989f1b9a2441be3a23bd49556af2829bc7faf238c182178c35` (678 lines) |
| Parity fixture | `docs/design/fixtures/design-calendar.json` — `b738d4a319d5c5d1604738d6b831baacca5b9b8ba695acca42da4f232d86794b` |
| Real calendar artifact | `data/processed/burning_calendar.json` — `6963c775a46cdf871116a98d51fc8ce571fd082cf00110df5761e9a44ed7bab5` |
| Empirical series | `data/processed/empirical_results.json` — annual counts, epochs, physics |
| Map data | `apps/workbench/src/data/map-data.json` — `1269ba8ee2a34159fb9650f53ef676247ef3f905423aaa2e26771dd6dcd2aef8` (physics flags + sorted inputs; reproducible) |
| Globe data | `apps/workbench/src/data/globe-data.json` — `0ddcb1d95bd0f6a4d14f695a0bcc085e64d18358533da3635508ee6182be8e8e` |
| Earth imagery | `apps/workbench/public/globe/earth.jpg` — `0c34a26960a9fea39a7b864e10f01b5261d13b24029c05d769f13aa6b67c4eb4` (NASA Blue Marble, 2048 × 1024) |
| Globe prototype | `globe.html` — `ef41d70224f79f7510b34c09c52f200bad2b697848a6523369bfb9e5780cfb07` |
| Map prototype | `map.html` — `a535f06dc1b1ecb309cf4f3ad27a622503161d896cab8518137dabfdd9e067a2` |
| Logo | `docs/figures/flare-chronos-logo.png` = `apps/workbench/public/logo.png` = `apps/workbench/src/app/icon.png` — `b3aa1c9b36e915bd9ac343f2308bc3f9291c095174999b2eb758aad6edd990bd` |

**Archive mismatch.** The prompt cites `FlareChronos.zip` at SHA-256
`07018cad…`, 1,339 Workbench lines, `R-0412`, `RUN-B`, and PNG figure downloads.
That archive is not on disk. The supplied archive is newer: period
`2001–2026`, native SVG figure builders, a read-only Workbench decision card,
unified `RUN-0412`, no figure download links, and a Review urgency column plus
search. The port follows the supplied archive. `docs/design/port-inventory.md`
records the full file, token, and screen inventory.

## 2. What shipped

- One Next.js 16.4.3 app, App Router, React 19.3.0, Tailwind v4, React Compiler,
  Turbopack, Bun 1.4.4. No re-scaffold.
- `/` is the Region Globe landing. `/workbench` is the center. `/icon.png` is the
  brand icon.
- Landing: a rotating 3D Earth (three.js, NASA Blue Marble), merged focus-country
  silhouettes, 110m country borders, real measured-epoch counts, a computed
  growth headline, two region cards, a real four-step loading screen, labelled
  illustrative orbits, and a flat SVG map fallback when WebGL is unavailable.
- Landing entry opens the region's last measured epoch and deep-links to
  `/workbench/<id>?epoch=<year>`; `tour=1` opens the walkthrough.
- Header: brand mark, Globe, region select (Mekong / Amazon), period, Walkthrough,
  Evidence, Briefing, EN/VI, dark/light, service status, mobile menu.
- The Workbench map epoch selector scrolls the selected epoch into view.
- Briefing rail: the full design service simulator over the RUN-0412 sample:
  Up/Degraded/Down, token handshake, resolving principal, run stream (classify,
  tools, reasoning, verification), number chips that verify one by one, a
  rewritten figure, paused handoff to Review, retry and reset. Audience switch,
  sources and the compact timeline remain.
- Review surface: `/review` queue with filters and status tabs; `/review/runs/[id]`
  run with evidence summary, full briefing, verification table, decision rail,
  timeline and briefing/citation/confirmation dialogs; `/review/audit` read-only
  records with CSV/JSON export. Decisions move a run between Needs decision,
  Published and Withheld and add an audit row for the session.
- Map: interactive physics filters (SZA, SAA, static, 60-minute de-dup), H3
  heatmap at Res 4–8, static-source and SAA/SZA exclusion layers, SAA display
  ellipse, and a scale bar derived from the projection's pixels per kilometre.
- Globe: hover tooltip with the epoch tick strip and open hint; the earth peeks
  toward the hovered region.
- Five `TODO(api)` markers replace the remaining review run, briefing-connect and
  run fixtures with HTTP endpoints; decisions and audit persist through
  `/api/review/decisions`.
- Physics filter bar: four toggles with the real raw → episode, removed, and SAA
  counts for the selected measured epoch.
- Map: equal-area pre-projected country paths, region box, real sampled MODIS
  and VIIRS detections with physics flags, measured-epoch selector,
  footprints/H3/static & SAA/lens toggles, H3 Res 7/8, zoom in/out/reset, and the
  real footprint lens.
- KPI strip: raw detections, fire episodes, and peak SFAI for the selected epoch.
- Comparator: raw vs MODIS-equivalent annual detections, measured/interpolated
  dots, El Niño markers, both/raw/harmonized modes, tooltip and OLS trend.
- Phenology clock: selected epoch HFD against the 2001–2025 IQR, El Niño 2016
  dashed, peak marker and month letters.
- Burning Activity Calendar: hand-written SVG grid, 26 years × 73 pentads, HFD
  and SFAI, observed/modelled/alerts/crisis, keyboard and pointer paths, live
  readout. Selecting a measured year also updates the epoch.
- Evidence drawer: five published scientific figures with captions, source lines
  and generated data tables; the tablet/mobile trend tab has the evidence
  quick-look.
- Walkthrough: six-step card with target spotlight, progress bar and figure callout.
- Mobile tabs: Map, Trend, Calendar, Briefing; page never scrolls sideways.
- Artifact loader with strict shape validation; design fixture behind
  `CALENDAR_FIXTURE=design` for parity only.
- Continuous globe→map morph: the settled globe frame is captured, stored for
  the route, and shrunk into the Workbench map pane.
- Root `DESIGN.md`, `docs/design/design-contract.json`, EN/VI catalogs (541
  keys), and the full run record here.
- ai-service demo HTML page removed; `GET /` returns 404; docs and PDFs updated.

## 3. Gates

Run in this order. All green.

| Gate | Command / check | Result |
|---|---|---|
| Format | `bun run format` (Bun native, root `.oxfmtrc.json`) then `bun run format:check` | 103 files formatted; check clean |
| Lint | `bun run lint` → `bun lint --no-script --max-warnings=0 --allow-unsupported apps/workbench` | 0 errors, 0 warnings |
| Types | `bun run typecheck` → `tsc --noEmit` | clean |
| Build | `bun run build` (Turbopack) | compiled; `/` and `/workbench/[zone]` dynamic; `/icon.png` static |
| Tokens | grep `style={{`, hex literals, `[Npx]` in `apps/workbench/src` | none |
| Icons | `lucide-react` import only in `components/ui/icon.tsx`; every icon-only control has `aria-label` | pass |
| Boundaries | one app; no barrel files; internal imports via `@/` | pass |
| 3D boundary | `three` imported only by `src/lib/globe`; the canvas is a client island | pass |
| Max lines | largest file `review-queue.tsx` 291; `globe/scene.ts` 290; `fixtures/review-facts.ts` 252 | all ≤ 300 |
| API markers | `rg 'TODO\(api\)' apps/workbench/src` | 7, listed below |
| Console | `rg 'console\.|debugger' apps/workbench/src` | 0 hits |
| Accessibility | axe-core 4.10.2 calendar checks, 1440/390; Lighthouse on `/` and `/workbench/mekong`, desktop and mobile | 0 violations; 100 accessibility everywhere |
| Landing a11y | region cards are the keyboard path; canvas is `role=img`, not a tab stop; loader is `role=status` | pass |
| Review a11y | queue table/cards, run headings, dialogs, verification table, audit export, compact timeline target size | pass |
| Review lighthouse | `/review`, `/review/runs/RUN-0412`, `/review/audit` at 1440 and 390 | Accessibility, Best Practices, SEO and Agentic Browsing 100; 0 failed |
| Keyboard | calendar application: arrows, Home/End, PageUp/PageDown, Enter; tab order | active cell and live region update |
| Locales | 541 keys in `en.json` and `vi.json`; key-set diff empty; both render; landing, service simulator, Review and audit included | pass |
| Data swap | default artifact vs `CALENDAR_FIXTURE=design` | component unchanged; period, unit, and scored counts change from data |
| Production | `next start` on 3102; Chrome DevTools/Playwright pass at 1440/834/390 on `/`, `/workbench/mekong`, `/review`, `/review/runs/RUN-0412`, `/review/audit` | 200; 0 console errors, warnings, or issues |
| Globe data | `WORLD_ATLAS_PATH=… bun scripts/build-globe-data.mjs` repeated | 172 KB, hash stable |
| WebGL fallback | Chromium with `--disable-webgl --disable-webgl2` | flat SVG map, cards and loader still work |
| Python | `uv run ruff format --check`, `uv run ruff check`, `uv run pytest`, `python3 scripts/check-docs.py --scan` | 97 formatted, checks pass, 152 passed / 6 deselected / 1 xfailed, docs pass |

## 4. Evidence

### 4.1 Calendar parity (design vs pilot component)

The design oracle is served from the extracted archive on port 8777. The pilot
is served from the production build on port 3102. The calendar crop is the
component under parity test; the full page layout is not a parity claim.

| Case | Design crop SHA-256 (prefix) | Pilot crop SHA-256 (prefix) |
|---|---|---|
| 1440 dark EN | `0125fb83c644ca4c` | `70b92646611f30f3` |
| 1440 dark VI | `93d14120a0564e7e` | `c5c8b1031b14e4cf` |
| 1440 light VI | `e2b91b7b3d04ad01` | `d6533d1592c46508` |
| 834 dark EN | `fe6972246c177183` | `0608918f5d84c7d4` |
| 390 dark EN | `f1f88df666137be7` | `002ec03ae5867b3d` |
| 390 light VI | `2c90ca1a2ee1f019` | `91334fae36ba96bd` |

Computed-style pass at 834 and 390:

| Element | Design | Pilot | Drift |
|---|---|---|---|
| Title | 12 px / 600 / IBM Plex Sans | 12 px / 600 / IBM Plex Sans | none |
| Period | 10 px / 400 / IBM Plex Mono, `rgb(142,154,176)` | same | none |
| Legend | 10.5 px | 10 px | 0.5 px |
| Readout | 11.5 px, padding 7/12/9 | 11 px, padding 8/12 | ≤ 1 px |
| Grid height 834 | 338 px | 338 px | none |
| Grid cell width 834 | 10.25 px | 10.1 px | 0.15 px |
| Grid cell width 390 | 14.85 px | 14.88 px | 0.03 px |

The design's calendar is 1,019 px in its two-column shell; the full Workbench
calendar uses the width left by the 392 px briefing rail (1,024 px at 1440). The
cell geometry matches at 834 and 390.

### 4.2 Full Workbench screenshots

`docs/design/experiments/fixtures/workbench-*.png`.

| Case | File | SHA-256 (prefix) |
|---|---|---|
| 1440 dark EN, top | `workbench-1440-dark-en-top.png` | `e4e2eeddbc24906d` |
| 1440 dark EN, H3 heatmap | `workbench-h3-1440-dark-en.png` | `83fcf1ceaac84b8d` |
| 1440 dark EN, static & SAA overlay | `workbench-overlay-1440-dark-en.png` | `64fd36cd7d1f81be` |
| 1440 dark EN, filters off | `workbench-filters-1440-dark-en.png` | `0a5f0442bf01aacc` |
| 1440 dark EN, comparator + clock | `workbench-1440-dark-en-mid.png` | `13a7c13515710327` |
| 1440 dark EN, calendar | `workbench-1440-dark-en-cal.png` | `a7c29c3dcd64011c` |
| 1440 light VI, top | `workbench-1440-light-vi-top.png` | `3060d6e49a3db763` |
| 1440 dark EN, service paused | `workbench-paused-1440-dark-en.png` | `3dc85a86b0eb2b63` |
| 1440 dark EN, service down | `workbench-down-1440-dark-en.png` | `70351d8f03bbc600` |
| 1440 dark EN, globe morph | `workbench-morph-1440-dark-en.png` | `6f8f5b1661068df8` |
| 834 dark EN, top | `workbench-834-dark-en-top.png` | `6a968a806f82878a` |
| 390 dark EN, map | `workbench-390-dark-en-map.png` | `69d488ab06e657cb` |
| 390 dark EN, trend + quick-look | `workbench-390-dark-en-trend.png` | `382807b8cff01b4b` |
| 390 dark EN, calendar | `workbench-390-dark-en-cal.png` | `81f4c9cdbc4be6b3` |
| 390 light VI, map | `workbench-390-light-vi-map.png` | `67fe23109f898bc5` |
| Amazon 2024, H3 + static & SAA | `workbench-amazon-2024-1440-dark-en.png` | `e3faeaf35256f965` |
| Evidence drawer + first table | `workbench-evidence-1440.png` | `66208d946e583c2b` |
| Walkthrough spotlight | `workbench-tour-1440.png` | `57cd7da7ea833aac` |

The Workbench shots were captured after the map data was regenerated with the
physics flags, the service simulator and the interactive layers landed.

### 4.3 Region Globe landing screenshots

`docs/design/experiments/fixtures/landing-*.png`.

| Case | File | SHA-256 (prefix) |
|---|---|---|
| 1440 dark EN | `landing-1440-dark-en.png` | `f0fa1ec965c048dc` |
| 1440 dark EN, Amazon hover + tooltip | `landing-hover-1440-dark-en.png` | `4b1053fea30f18c9` |
| 1440 dark EN, loader 3/4 | `landing-loader-1440-dark-en.png` | `ea3e87a33bd687b1` |
| 1440 light VI | `landing-1440-light-vi.png` | `6392a37b672bf698` |
| 834 dark EN | `landing-834-dark-en.png` | `d63d2937c9cb9c60` |
| 390 dark EN | `landing-390-dark-en.png` | `e2558ff8413c29c9` |
| 390 dark EN, collapsed | `landing-390-dark-en-collapsed.png` | `28935e5723316c0c` |
| 390 light VI | `landing-390-light-vi.png` | `56e071e188433a75` |

### 4.4 Review screenshots

`docs/design/experiments/fixtures/review-*.png`.

| Case | File | SHA-256 (prefix) |
|---|---|---|
| 1440 dark EN, queue | `review-queue-1440-dark-en.png` | `18b8dd25b38cfd33` |
| 1440 dark EN, run | `review-run-1440-dark-en.png` | `e7973c3ee3727a90` |
| 1440 dark EN, briefing dialog | `review-briefing-1440-dark-en.png` | `c3ef6896fee2299c` |
| 1440 dark EN, citation dialog | `review-citation-1440-dark-en.png` | `fb049a215ec550a5` |
| 1440 dark EN, confirm dialog | `review-confirm-1440-dark-en.png` | `d266c82283fda694` |
| 1440 dark EN, audit | `review-audit-1440-dark-en.png` | `f4f8d35fd620a758` |
| 390 dark EN, queue | `review-queue-390-dark-en.png` | `732778c15e67eb28` |
| 390 dark EN, run | `review-run-390-dark-en.png` | `a66cde4dc6b28d02` |

## 5. Decisions

| ID | Resolution |
|---|---|
| D1 | One app. Primitives in `src/components/ui`, catalogs in `src/i18n`; no `packages/ui` or `packages/i18n`. |
| D2 | `next-intl@4.14.9`, cookie locale (`fc-locale`), no path segment. |
| D3 | The Workbench map is a pre-projected SVG built from world-atlas and real sampled raw detections. The landing globe is a `three.js` scene with canvas textures. No iframe; `d3-geo` and `topojson-client` are build-only. |
| D4 | `recharts@3.10.1` for the comparator; hand-written SVG for the calendar, clock, map and lens. |
| D5 | Review owns the decision. The Workbench has no decision surface. |
| D6 | SFAI stays sparse. Null renders "not scored"; the grid never shows zero for a null. |
| D7 | Period is `2001–2026`, derived from the artifact, never hard-coded. |
| D8 | No prototype banner. |
| D9 | Tailwind's 0.25 rem scale; odd design pixels snap with at most 1 px drift. |
| D10 | `tablet` 720 px, `xl` 1280 px; calendar pitch 10/13/15 px; map 520 px tablet, viewport-height mobile. |
| D11 | `/` is the Region Globe landing; `/workbench/[zone]` is the center. `/workbench` redirects to `/workbench/mekong` and preserves `epoch`/`tour`. | The Globe header button returns to `/`. |
| D12 | `three@0.184.0` and a local 2048 × 1024 NASA Blue Marble JPEG. No runtime CDN; the loader waits on the local texture. |
| D13 | Entry opens the region's last measured epoch and deep-links to `/workbench/<id>?epoch=<year>`; `tour=1` opens the walkthrough. |
| D14 | The loader has four real steps (fonts, interface, satellite imagery, country borders), a 900 ms minimum and a 15 s fallback. It does not fake progress. |
| D15 | Globe region silhouettes are merged focus-country coverage from the 110m atlas. The orbit rings are decorative and carry an "illustration" label. |
| D16 | The WebGL fallback is a flat equirectangular SVG map; the region cards remain the accessible path. |
| D17 | Review is shipped from the design fixture runs (`RUN-0411/0412/0413`), facts, brief templates, decisions and audit ids. The user asked for the full UI without a fixture mode; the data boundaries carry five `TODO(api)` markers; decisions and audit rows persist through `/api/review/decisions`. |
| D18 | The Workbench briefing rail is the compact RUN-0412 run: audience, number chips with sources, verification, timeline and an "Open in Review" handoff. The Workbench never records the decision. |
| D19 | Review decisions live in a session store; a decision moves the run between Needs decision, Published and Withheld and adds A-0196+ to the audit. A reload restores the design's initial decisions. |
| D20 | The Review queue is a table at `xl`, cards below; the run is three columns at `xl` and stacks below; dialogs are modal with Escape/scrim close and body-scroll lock. |
| D21 | Evidence adds a source line and a generated data table per published figure; the PNGs remain the figure images. |
| D22 | The map gains a bbox-derived scale bar that updates with zoom; the walkthrough gains a spotlight, progress bar and figure callout; the globe gains a hover tooltip and an earth peek. |
| D23 | The live analysis stream, review endpoints and audit endpoint are the next API slice. The UI is complete; the fixture data is the only stand-in. |
| D24 | The map filters and layers are real: `flag-map-points.py` flags every sampled detection through the harmonization core, and the H3 heatmap bins those points at Res 4–8. The KPI stays the full artifact count. |
| D25 | The service state is a local simulator (Up/Degraded/Down, token handshake, run stream, retry, reset). The Workbench still hands the decision to Review; returning with a decision marks the run published or withheld. |
| D26 | The globe captures its settled frame and morphs it into the map pane on entry. The return trip remains a route change. |
| D27 | The detailed Workbench lives at `/workbench/[zone]`; `/workbench?region=…` redirects to the zone path and preserves epoch/tour. |
| D28 | The map owns client-side pan/zoom (wheel, trackpad, pinch, drag), the merged coverage polygon, true-scale footprint ellipses, and the footprint lens. |

## 6. Deviations

1. The supplied archive is newer than the prompt's archive. The newer facts win.
2. Default metric is HFD, not SFAI. The artifact scores 10 Mekong and 8 Amazon
   cells, so SFAI is the sparse anomaly view; HFD shows the full matrix.
3. HFD is a density (`events/100 km²/day`) in the artifact. The design fixture
   stores detections/pentad; the readout unit follows the dataset.
4. HRF is not in the artifact, so the calendar ships two metrics, not three.
5. Map points are sampled real MODIS/VIIRS detections, not the design's synthetic
   points. The sample count is shown. 2026 is modelled and is not a measured epoch.
6. The map has footprints, H3 hexes, static & SAA exclusions and the footprint
   lens. The H3 heatmap bins the sampled projected points at Res 4–8; the region
   box is always shown.
7. Physics filter chips are interactive. They hide their flagged sampled points;
   the raw → episode/removed/SAA counts remain the full artifact totals.
8. The briefing rail is a local service simulator over the RUN-0412 sample; the
   live analysis stream remains the later API slice. Tokens shorter than 16
   characters are rejected; a valid token resolves to the demo principal. Seven
   `TODO(api)` markers name the HTTP boundaries.
9. Evidence uses the five published PNGs rather than the design's native SVG
   builders; the drawer adds source lines and generated data tables.
10. Dates use `Intl` (`Mar 12–Mar 16`, `12 thg 3–16 thg 3`), not the design's
    fixed `DD Mon` English table.
11. The design's separate selected state is folded into the active cell.
12. The design's cursor-following tooltip becomes the fixed readout strip.
13. The artifact always has 26 × 73 cells, so an empty-grid state is unreachable.
    A load failure renders `app/workbench/error.tsx`.
14. `apps/workbench/AGENTS.md` was deleted before the final commit per the team
    rule. `next dev` regenerates it on the next local run.
15. Review is shipped with the design fixture runs; the live briefing stream
    remains a later slice. The landing globe is shipped; the Workbench Globe
    button returns to it.
16. The landing headline uses the real 2005→2024 growth (14× Mekong, 8× Amazon)
    and the artifact's sensor years (2012, 2019, 2024), not the design's older
    14× / 2000→2024 and Aqua/2018 claims.
17. The globe silhouettes are the merged 4/8 focus countries from the 110m atlas;
    the design merges 50m topology at runtime.
18. The island reference markers (Hoàng Sa, Trường Sa) in `globe.html` are not
    ported; the repo has no spatial measurement layer for them.
19. The globe surface is a local 2048 × 1024 NASA Blue Marble JPEG; the orbits
    are decorative and labelled "Illustration, not a measurement".
20. The loader is on the landing only. The Workbench is server-rendered and does
    not replay it.
21. The landing CTAs stack full width on desktop because the side-by-side pair
    wrapped at 440 px; the primary label does not wrap.
22. The landing sheet is a toggle button, not the design's drag/swipe gesture.
23. Landing region labels clamp inside the viewport instead of following the
    design's off-screen projection.
24. The landing meta title is "Region Globe"; the Workbench title is "Workbench".
25. The map epoch selector scrolls the selected epoch into view; the design's
    selector did not.
26. The map build samples and flags the raw files in Python through the
    harmonization core, then projects in Bun. The map hash is `1269…`; every
    point carries SZA/SAA/static/duplicate flags and the full-slice counts.
27. Returning to the globe is a route change to `/`; entering the Workbench now
    captures the globe frame and morphs it into the map pane. The landing still
    replays its loader.
28. Review and the Workbench briefing run use the design fixture runs
    (`RUN-0411/0412/0413`). Seven `TODO(api)` markers name the review, audit,
    briefing-connect and run boundaries. No fixture mode or prototype banner was
    added.
29. The Workbench rail shows the RUN-0412 Mekong 2024 sample. It does not
    regenerate a run from the selected map region or epoch; the target is the
    run's own.
30. Review decisions are session-only. A reload restores the design's initial
    decisions (RUN-0411 published, RUN-0413 withheld, RUN-0412 needs decision).
31. H3 hexes are binned from the sampled projected points at Res 4–8, not
    from full-resolution H3 polygons. The analysis grid stays Res 7 or 8.
32. Map filters hide flagged sampled points; the KPI and artifact counts remain
    the full measured epoch. The SAA display zone is the design ellipse, while
    the core rejects with the broader NASA FIRMS envelope.
33. The service simulator, connect steps and run stream are local. The prototype
    banner and "Demo walkthrough" label remain excluded; the "Demo · simulate
    service" control is the explicit simulator.
34. The globe captures one frame on arrival and morphs it into the map pane; the
    return trip is still a route change.
35. The tour spotlight, progress bar, figure callout, globe tooltip and earth
    peek remain shipped.
36. Evidence uses the five published PNGs; the drawer adds source lines and
    generated data tables rather than native SVG figure builders.
37. The Review queue has the three design runs only; the waiting, failed and
    stale tabs shown in the design do not have fixture rows.

## 7. Rework cycles

Counted as a red gate or a visible defect followed by a green pass.

| # | Cycle |
|---|---|
| 1 | Initial typecheck: `PENTADS_PER_YEAR` imported from the wrong module; moved to `model.ts`. |
| 2 | Lint baseline adoption: replaced per-app ESLint with root Bun native format/lint; fixed `no-await-in-loop`; scoped React Compiler event/prop override. |
| 3 | First visual pass: calendar pane stretched to the viewport; changed to content height. |
| 4 | Tablet: 1150 px min-width forced a scroll at 834; moved the min-width below 720 px. |
| 5 | Tablet legend: `ml-auto` right-aligned a wrapped legend; replaced with a flex spacer. |
| 6 | Keyboard: readout followed `selected` instead of `active`; removed the duplicate state. |
| 7 | Pointer: click at a row boundary disagreed with the hover cell; click uses hover and clears it. |
| 8 | Year axis: observed dots were too muted; active year uses teal, observed uses ink. |
| 9 | Chrome DevTools found an unused `preload` warning and two form-field issues; removed `preload`, added `id`/`name`/`autocomplete`. |
| 10 | Full center: map data pipeline from raw CSVs + world-atlas, pre-projected to SVG to avoid runtime D3. |
| 11 | Full center: Recharts warned at 0 × 0 when the trend tab was CSS-hidden; chart now mounts only when visible. |
| 12 | Full center: the rail opened after hydration and caused CLS 0.126; replaced the JS default with `data-state` CSS (desktop 392/36, tablet/mobile overlay) and CLS reached 0. |
| 13 | Full center: the language button's visible `EN` was not in its accessible name; label now includes the code. |
| 14 | Full center: the mobile map was covered by projection chips and the full lens card; hidden below 720 px, and the lens button hides with them. |
| 15 | Full center: El Niño labels collided at 390 px; labels render at tablet+, and the footer gains an El Niño legend swatch. |
| 16 | Full center: the rail's content stayed visible in the 36 px collapsed rail because utilities beat component-layer CSS; switched to `group-data` utilities. |
| 17 | Landing: the first camera direction was unset, so `resize()` defaulted to +Z (the Pacific); set the Atlantic direction before `OrbitControls`. |
| 18 | Landing: the light theme reused the dark vector texture; the vector cache is now keyed to the theme. |
| 19 | Landing: the Amazon label overflowed at 1440; labels clamp to the viewport with a cached width. |
| 20 | Landing: the CTA wrapped at 440 px; the pair is now full-width and stacked. |
| 21 | Landing: the card `aria-label` failed `label-content-name-mismatch`; the card uses its visible text and the tick row is `aria-hidden`. |
| 22 | Landing: the initial surface map leaked because it was created inline and replaced by `setTheme`; `setTheme` now owns the first texture. |
| 23 | Landing: two fast card clicks could skip the flight; a `leaving` ref guard was added. |
| 24 | Landing: the fallback copy leaked `WebGL`; it now says the 3D globe is unavailable. |
| 25 | Workbench: a deep-linked 2025 epoch was off-screen on mobile; the selected epoch scrolls into view. |
| 26 | Map build: `readdirSync` order made the output non-deterministic; the raw files are sorted. |
| 27 | Review: the mobile brand link had no accessible name; added an `sr-only` Workbench label. |
| 28 | Review: the logo link `aria-label` failed `label-content-name-mismatch`; the sr-only label includes the visible brand. |
| 29 | Workbench: the Review link's visible badge did not match its `aria-label`; the visible label is now the accessible name. |
| 30 | Workbench: compact timeline rows were 23 px; `min-h-6` reaches the target-size minimum. |
| 31 | Review: the briefing footer showed "Nothing was released" before a decision; split it into `notReleased`. |
| 32 | Review: the audit header reused "Note · optional"; added `noteShort`. |
| 33 | Review: the fixture file exceeded 300 lines; split into review, facts, briefs and runs. |
| 34 | Landing: the globe label printed the measured-year array; restored the `length` count. |
| 35 | Landing: the tooltip block did not render after the label refactor; reinserted it with the tick strip. |
| 36 | Landing: the pointer handlers moved to `picking.ts`; the scene stays under 300 lines. |
| 37 | Review: a full page reload restores the design decisions; client navigation keeps the session. Documented. |
| 38 | Review: "Not evaluated" stayed English in VI; localized via `notEvaluated`. |

## 8. Dependencies

Added to `apps/workbench`:

- `next-intl@4.14.9` — cookie locale, no path segment.
- `lucide-react@1.66.0` — only `components/ui/icon.tsx` imports it.
- `recharts@3.10.1` — comparator chart.
- `three@0.184.0` — the landing globe scene; only `src/lib/globe` imports it.
- `@types/three@0.184.0` — dev-only.
- `d3-geo@3.1.1`, `topojson-client@3.1.0` — dev-only, used by
  `scripts/build-map-data.mjs` and `scripts/build-globe-data.mjs`; the runtime
  map and globe use pre-projected paths and canvas textures.

Removed: `eslint`, `eslint-config-next`, `apps/workbench/eslint.config.mjs`.
Root `.oxfmtrc.json` and `.oxlintrc.json` use Bun 1.4.4's native
`bun fmt` / `bun lint`; no formatter or linter package is installed. The root
config adds scoped overrides for `apps/workbench/src/**/*.tsx`
(`react-perf` function/array/object/JSX props; React Compiler memoizes them) and
`apps/workbench/scripts/**/*.mjs` (`no-console` for the build script). All other
rules, including `max-lines: 300`, stay on.

## 9. TODO(api) inventory

| File:line | Surface | Current | Target | Contract | Phase |
|---|---|---|---|---|---|
| `apps/workbench/src/data/fixtures/review.ts:1` | Review run list | Design `RUNS` / `INIT_DEC` fixture | `GET /api/v1/review/runs` | Review endpoints (contract pending) | Later API |
| `apps/workbench/src/data/fixtures/review-runs.ts:1` | Review run detail | `runById` fixture | `GET /api/v1/review/runs/:id` | Review endpoints | Later API |
| `apps/workbench/src/lib/workbench/briefing.ts:3` | Briefing connect | Empty and <16-character tokens are rejected locally; the rest resolve to the demo principal | `POST /api/v1/analysis/stream` handshake; live event stream | `docs/openapi/ai-service.json` | Later API |
| `apps/workbench/src/components/workbench/briefing-rail.tsx:32` | Briefing run | Local service simulator over the RUN-0412 fixture | Live `POST /api/v1/analysis/stream` run | `docs/openapi/ai-service.json` | Later API |
| `apps/workbench/src/app/review/runs/[runId]/page.tsx:1` | Review run route | Fixture lookup | Run detail endpoint | Review endpoints | Later API |

The calendar artifact, empirical series, map data and globe data are real or
derived from the real artifacts. The landing growth headline and evidence tables
are computed at request time. The review runs, decisions, audit rows and the
briefing-run content are the design fixtures the user asked to use. Decisions and
audit rows persist through `/api/review/decisions`; the service states, connect
steps and run progress are simulated locally. Five `TODO(api)` markers remain.

## 10. Files changed

App:

- `apps/workbench/src/app/{layout.tsx,page.tsx,globals.css,globe.css,review.css,icon.png}`
- `apps/workbench/src/app/review/{layout.tsx,page.tsx,audit/page.tsx,runs/[runId]/page.tsx}`
- `apps/workbench/src/app/workbench/{page.tsx,error.tsx}`
- `apps/workbench/src/components/ui/{icon.tsx,theme-provider.tsx,theme-toggle.tsx,locale-toggle.tsx,brand-mark.tsx,segmented-control.tsx}`
- `apps/workbench/src/components/globe/{globe-landing.tsx,globe-canvas.tsx,globe-fallback.tsx,globe-morph.tsx,landing-header.tsx,landing-panel.tsx,region-card.tsx,boot-overlay.tsx}`
- `apps/workbench/src/components/workbench/{workbench-shell.tsx,app-header.tsx,filter-bar.tsx,map-pane.tsx,map-controls.tsx,map-legend.tsx,workbench-map.tsx,kpi-strip.tsx,comparator-pane.tsx,clock-pane.tsx,burning-calendar.tsx,calendar-grid.tsx,calendar-legend.tsx,calendar-summary.tsx,briefing-rail.tsx,briefing-run.tsx,briefing-events.tsx,briefing-event-row.tsx,service-panel.tsx,evidence-drawer.tsx,evidence-quick-look.tsx,evidence-table.tsx,tour.tsx}`
- `apps/workbench/src/components/review/{review-shell.tsx,review-queue.tsx,review-run.tsx,review-decision.tsx,review-timeline.tsx,review-dialog.tsx,briefing-dialog.tsx,citation-dialog.tsx,confirm-dialog.tsx,verification-table.tsx,run-summary.tsx,mini-map.tsx,review-bits.tsx,review-select.tsx,review-store.tsx}`
- `apps/workbench/src/data/fixtures/{review.ts,review-facts.ts,review-briefs.ts,review-runs.ts}`
- `apps/workbench/src/lib/calendar/{types.ts,load.ts,parse.ts,fixture.ts,model.ts,ramp.ts,format.ts,pentad.ts}`
- `apps/workbench/src/lib/workbench/{types.ts,series.ts,clock.ts,map-data.ts,h3.ts,format.ts,briefing.ts,regions.ts,service.ts,evidence-tables.ts}`
- `apps/workbench/src/lib/globe/{types.ts,data.ts,scene.ts,earth.ts,flight.ts,labels.ts,morph.ts,orbits.ts,picking.ts,snapshot.ts,stars.ts,textures.ts}`
- `apps/workbench/src/lib/{theme.ts,browser.ts,use-media.ts}`
- `apps/workbench/src/i18n/{config.ts,request.ts,messages/en.json,messages/vi.json}`
- `apps/workbench/{next.config.ts,package.json,README.md,public/logo.png,public/globe/earth.jpg}`
- `apps/workbench/public/figures/fig-1.png` … `fig-5.png`
- `apps/workbench/src/data/{map-data.json,globe-data.json}`
- `apps/workbench/scripts/{flag-map-points.py,build-map-data.mjs,build-globe-data.mjs}`
- Deleted: stock `public/*.svg`, stock `src/app/favicon.ico`, `apps/workbench/AGENTS.md`.

Repo docs and config:

- `DESIGN.md`, `GLOSSARY-MAP.md`, `AGENTS.md`, `package.json`
- `.oxfmtrc.json`, `.oxlintrc.json`
- `docs/design/{port-inventory.md,design-contract.json}`
- `docs/design/fixtures/design-calendar.json`
- `docs/design/experiments/fixtures/workbench-*.png` (18 full-center shots)
- `docs/design/experiments/fixtures/review-*.png` (8 Review shots)
- `docs/design/experiments/fixtures/landing-*.png` (8 landing shots)
- `docs/design/experiments/fixtures/calendar-*.png` (12 calendar crops)

ai-service and exports:

- `apps/ai-service/src/ai_service/api.py` (removed `DEMO_PAGE`, `GET /`, `FileResponse`)
- Deleted: `apps/ai-service/src/ai_service/demo/`
- `tests/test_ai_service_api.py` (added the `GET /` 404 regression test)
- `README.md`, `docs/05_Pitch_Deck_and_Video_Script.md`
- `exports/{MODEL_FLOW.md,REPORT.md,PROPOSAL.md}` and regenerated PDFs
- `docs/openapi/ai-service.json`

Line counts: 114 TS/TSX files under `apps/workbench/src`, 11,122 lines, plus
345 lines of `globals.css`, 128 lines of `globe.css` and 5 lines of
`review.css`. Largest file 300 lines (`components/workbench/comparator-pane.tsx`).

## 11. Known gaps

- The H3 heatmap bins the sampled points in screen space; it is not a full
  H3 polygon artifact. The SAA display zone is the design ellipse, not the
  broader core envelope.
- The briefing rail is the design RUN-0412 sample; the live stream, token
  handshake and sign-off remain the later API slice. Service states and run
  progress are simulated locally.
- Review queue/run/audit is shipped from the design fixture runs. The live
  review, decision and audit endpoints remain later; decisions are session-only.
- The Workbench rail's RUN-0412 target does not follow the selected map region
  or epoch.
- The globe has no H3, static-source or SAA layer; those layers live on the
  Workbench map. The island reference markers are not ported.
- Static-source flags use the FIRMS `type` 1–3 subset and the design source marks; see ADR-0014. The core's 12-month
  persistent-cell registry cannot be built from the archive's same-season 5-day
  slices, so the map does not claim that broader registry.
- The return from Workbench to Globe is still a route change; only the entry
  morph is continuous.
- The globe uses one Blue Marble frame, not a day/night composite.
- The loader is on the landing only; the Workbench is server-rendered.
- The globe is a pointer enhancement; the cards are the keyboard path.
- Evidence uses the published PNGs; the native SVG figure builders are a later
  task.
- Deployment: the loaders read `../../data/processed` and `../../data/raw` from
  the app's working directory. A standalone or Vercel deployment must set the
  data paths or copy/trace the artifacts into the deployment root.
- There are five `TODO(api)` markers: review run list/detail, briefing connect,
  briefing run and the review run route. Decisions and audit rows now persist
  through `/api/review/decisions`.
- The root release automation still uses pnpm because the CI workflows are
  configured for it; the Workbench app and its gates use Bun. Do not unify them
  without changing `release.yml` and `auto-bump-version.yml`. See ADR-0013, ADR-0014 and ADR-0015.
- The Burning Activity Calendar's 26x73 shape is the artifact contract, not a
  user-selected period; `ROWS`/`PENTADS` document that fixed shape.

## 12. Chrome DevTools interaction pass

Run against the production build on port 3102 with the Chrome DevTools MCP and
Playwright: 1440×900, 834×1194 and 390×844 (DPR 2, mobile, touch).

| Interaction | Result |
|---|---|
| `/` | Region Globe landing; title `Flare Chronos — Region Globe`; `h1` "Raw fire counts rose up to 14×. The fires did not." |
| Loader | 4 steps; captured at 3/4 "Loading satellite imagery"; fades after 900 ms + 560 ms; 15 s fallback; `aria-busy` follows. |
| Landing theme | Dark ↔ light. Photo surface ↔ vector surface, stars, coverage, borders and orbit colours change; `fc-theme` cookie follows. |
| Landing locale | EN ↔ VI. `h1`, body, cards, labels, loader and meta title change; the globe and camera state survive `router.refresh()`. |
| Globe drag | Drag rotates the camera; labels re-project; auto-rotate pauses and resumes after 3.5 s. |
| Globe hover | Hovering the Amazon silhouette or its card sets `cursor: pointer`, turns the card border amber, shows the tick-strip tooltip and peeks the earth toward the region. |
| Globe select | Clicking the silhouette flies 1.7 s, fades out, and lands on `/workbench/amazon?epoch=2025`. |
| Region cards | Tab reaches both cards; Enter on Amazon lands on the same deep link; double-click cannot skip the flight. |
| Landing CTAs | "Start 2-minute walkthrough" → `/workbench/mekong?tour=1`, step 1/6; "Explore the workbench" → `/workbench/mekong`, Mekong 2024. |
| Landing mobile | 390: 58dvh sheet, handle collapses to 52 px, no page horizontal overflow; card entry and menu Globe link work. |
| Landing tablet | 834: globe above a 58dvh sheet; header, cards, legend and CTAs fit without page scroll. |
| Globe fallback | `--disable-webgl`: flat SVG map, cards, loader and entry still work; console logs Three's context errors only in this mode. |
| Workbench deep link | `?region=amazon&epoch=2024`: Amazon 2024 selected, KPI 112,405 raw / 19,542 episodes, 1,033 sampled detections. |
| Workbench epoch scroll | Mobile deep link to 2025 keeps the selected epoch visible in the strip. |
| Workbench Globe | Header Globe link returns to `/`; mobile menu includes "Globe". |
| Theme | Dark ↔ light on landing, Workbench and Review; `fc-theme` cookie follows. |
| Locale | EN ↔ VI on landing, Workbench and Review; region, epoch, metric and active cell survive `router.refresh()`. |
| Region | Mekong ↔ Amazon. 10/8 measured epochs, KPI 11,296/13,033 for 2007, map label and series update. |
| Map epoch | 2005 → 2007 → 2012. KPI, filter summary, map points and clock update; selected button follows. |
| Map layers | Footprints off hides points and H3; H3 hexes toggles the heatmap; Static & SAA toggles excluded markers and the zone; Lens toggles the card. |
| Map zoom | `+` sets `scale(1.5)`, reset restores `scale(1)`; focusable icon buttons with labels. |
| Comparator modes | Both = 2 lines, Raw = red only, Harmonized = teal only. |
| Comparator tooltip | Hover shows year, raw and harmonized values (2013: 35,354 / 6,734). |
| Calendar keyboard | Tab reaches the application; arrows, Home/End, PageUp/PageDown and Enter update the live readout. |
| Calendar ↔ epoch | Clicking modelled 2013 leaves epoch 2005; ArrowUp to measured 2012 sets epoch 2012; ArrowDown to 2013 leaves 2012. |
| Calendar metrics | HFD ↔ SFAI; legend, Not scored, 10/8 scored cells; crisis cell 2007 P15 reads +2.9σ with ring, corner and flag. |
| Briefing rail | Service chip mirrors Up/Degraded/Down. Desktop 392/open → 36/collapsed → 392; header `aria-pressed` follows. |
| Briefing service | Up / Degraded / Down; Down shows the retry panel; Retry restores the service and the charts keep working. |
| Briefing connect | Disconnect reveals the token form; empty and short tokens are rejected; Use demo token → resolving → resolved principal → Connect as → run target. |
| Briefing run | Start → classify, 6 tool calls, reasoning stream, number verification, paused handoff; 8/8 verified; Open in Review; a Review decision marks the run published/withheld on client return. |
| Evidence | Header button opens a 5-figure dialog; each figure has a source line and a "View data" table; body scroll locks; Escape closes and restores. |
| Walkthrough | 6 steps with spotlight, progress bar, figure callout, Back/Next/Done; closes. |
| Mobile tabs | Map, Trend, Calendar, Briefing show the right pane; Briefing opens the full-width rail above the tab bar; close returns to Map. |
| Mobile header | Logo, region, EN/VI, theme, menu; menu opens Walkthrough/Evidence; no page horizontal overflow. |
| Mobile map | Chips, full lens card and Lens button hidden below 720; points, filter bar, H3 control and zoom remain. |
| Tablet | 834: header 56, filter bar scrolls, map 810×520, chart labels fit, briefing hidden until opened. |
| Console | 0 errors, 0 warnings, 0 DevTools issues. |
| Network | All requests 200; logo, earth.jpg, globe data and fonts are local; no external CDN. |
| Map layers | Footprints off hides points and H3; H3 hexes toggles the heatmap; Static & SAA toggles excluded markers and the zone; Lens toggles the card. |
| Map filters | SAA off 331→573 points; static off 331→362; de-dup off 331→1193; SZA off 331→518 (Amazon 2024). |
| Map H3 | Res 7/8 control; zoom 1 shows Res 4, zoom 3 shows Res 5; bins follow the filters. |
| Map scale | The `≈ 200 km` bar uses the projection's pixels per kilometre and changes with zoom. |
| Review queue | 1 Needs decision / 1 Published / 1 Withheld; search, region, use case, urgency, owner, assigned-to-me filters; table at 1440 and cards at 390. |
| Review run | RUN-0412: action, region/period/mini map, thresholds, evidence status, full briefing, verification table, evidence summary, decision basis, approver, timeline. |
| Review decision | Choose reason → Approve → Confirm approval → run moves to Published, audit adds A-0196, queue needs 0 / published 2; client navigation preserves the session. |
| Review dialogs | Briefing (audience, meta, brief, verification), citation (source/raw/verdict), confirm (run/action/decision/reason/note/reviewer); Escape/scrim close and body lock. |
| Review audit | 3 rows after the decision; filters reviewer/decision/date/use case; CSV/JSON export; read-only note. |
| Review mobile | 390: queue cards and stacked run; header Review/Audit and theme/locale; no page horizontal overflow; Lighthouse 100. |
| Globe morph | Region card → 1.7 s flight → snapshot → Workbench; the overlay shrinks into the map pane and clears without console errors. |
| Lighthouse | Landing 49/49; Workbench 56/52; Review queue 54/52; Review run 55/55; Review audit 54/54. Accessibility, Best Practices, SEO and Agentic Browsing all 100; 0 failed. |

## 13. How to run

```sh
cd apps/workbench
bun install
bun dev                     # / landing, /workbench/<zone> center, /review queue
bun run typecheck
bun run build && bun start

# Regenerate map and globe data (dev-only d3-geo/topojson-client)
curl -sSL -o countries-110m.json \
  https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json
WORLD_ATLAS_PATH=$PWD/countries-110m.json bun scripts/build-map-data.mjs
WORLD_ATLAS_PATH=$PWD/countries-110m.json bun scripts/build-globe-data.mjs

# Parity fixture (never production)
CALENDAR_FIXTURE=design bun dev

# Repo gates
cd ../..
bun run format && bun run format:check
bun run lint
bun run typecheck
```

```sh
cd apps/ai-service
uv run ruff format --check
uv run ruff check
uv run pytest                 # run from the repo root to pick up testpaths
```
