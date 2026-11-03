# Prompt — Design Zip → `apps/workbench`

**Use:** fill the inputs, paste this file into a fresh agent session.
**Generic procedure:** `workflows/claude-design-to-nextjs.md` in `The-Resonance-Team/skills` (section 0 zip intake and the conversion method check).
**Project facts:** [`claude-design-to-prod-context.md`](./claude-design-to-prod-context.md).
**Pilot method:** [`claude-design-to-prod-experiment.md`](./claude-design-to-prod-experiment.md).

---

## Inputs

Replace the values before starting. Do not guess a path.

| Variable | Value |
|---|---|
| `DESIGN_ZIP` | `/Users/xirothedev/Downloads/FlareChronos.zip` |
| `APP` | `@flare/workbench` |
| `TARGET` | `apps/workbench` |
| `SPEC` | `docs/04_UI_UX_Burning_Calendar_Wireframe.md` |
| `DATA` | `data/processed/burning_calendar.json`, `data/processed/empirical_results.json`, `docs/openapi/ai-service.json` |
| `LOCALES` | `en`, `vi` |
| `BASE` | `main` at the current commit |

**Preconditions.** `apps/workbench` is scaffolded (D1). The URL and locale shape is chosen (D2), and the map/globe approach is chosen (D3). If D2 or D3 is open, stop and ask. Do not re-scaffold.

---

## Prompt

```markdown
You are a senior frontend engineer. Convert a Claude Design zip export into a production Next.js app under apps/workbench. The app is already scaffolded with Next 16.4.3, React 19.3.0, Tailwind 4, React Compiler, and Bun. Do not re-scaffold it.

Read first, in this order:
1. docs/design/claude-design-to-prod-context.md
2. docs/design/claude-design-to-prod-experiment.md
3. workflows/claude-design-to-nextjs.md from The-Resonance-Team/skills (section 0 zip intake, step 6 gates, and the conversion method check)
4. The rule modules linked from CONTEXT.md: rules/frontend.md, rules/linting.md, rules/libraries.md, rules/general.md, rules/i18n.md
5. docs/04_UI_UX_Burning_Calendar_Wireframe.md §3
6. docs/adr/0011-web-facing-ai-service.md and docs/adr/0012-workbench-single-mode-real-data-and-api.md

Inputs:
- DESIGN_ZIP: /Users/xirothedev/Downloads/FlareChronos.zip
- APP: @flare/workbench
- TARGET: apps/workbench
- SPEC: docs/04_UI_UX_Burning_Calendar_Wireframe.md
- DATA: data/processed/burning_calendar.json, data/processed/empirical_results.json, docs/openapi/ai-service.json
- LOCALES: en, vi
- BASE: main

Final design facts (checked 2026-11-01):
- SHA-256: 07018cad8150e1e50101e2e74ab1421139ac45d7285d5369ce750b0e924b2980.
- Workbench 1,339 lines, Review 674, Screens 79, Components 173.
- The Evidence drawer already draws five figures natively from figureData (fig1..fig5) plus the Polar Phenology Clock. Port those builders; do not replace them with PNGs or image slots.
- No <image-slot> elements remain. image-slot.js and uploads/ are dead files; ignore them.
- The Review mini-map is native SVG and says "Schematic · H3 search area, Mekong 2024". Do not invent the 13 H3 cell IDs.
- The five "Download published figure" links point to figures/fc-fig-*.png, which are not in the zip. Copy the repo PNGs to public/figures/ with these names, or remove the links:
  docs/figures/fig1_scan_angle_footprint_physics.png -> figures/fc-fig-1-footprint-physics.png
  docs/figures/fig2_overpass_deduplication_sza.png -> figures/fc-fig-2-overpass-deduplication.png
  docs/figures/fig3_cross_sensor_frp_quantile_mapping.png -> figures/fc-fig-3-coincident-pair-calibration.png
  docs/figures/fig4_regime_shift_elimination.png -> figures/fc-fig-4-regime-shift-elimination.png
  docs/figures/fig5_harmonized_burning_calendar.png -> figures/fc-fig-5-burning-activity-calendar.png
  In the app, serve them at /figures/fc-fig-*.png; the prototype writes figures/... relative to its root.
- The prototype console logs SVG parse errors from {{ }} placeholders. They are not product errors. Production must render numeric SVG attributes from React values.
- The Workbench still has its own approve/reject card. D5 default: Review owns the decision; make the Workbench card read-only and link to Review. If the team has not accepted D5, stop and ask.
- The Workbench shows Run R-0412; Review shows RUN-B. Do not hard-code either. One run ID comes from the service.
- The queue has an urgency filter but no urgency column, and no run/principal search. Port the design as-is and log both as design gaps; add them only if the reviewer prompt is accepted.

Phase 0 — Sandbox and scan:
1. Record git status and the base commit.
2. Copy the zip to the approved temp directory. Do not unzip inside the repo.
3. Hash the zip and every .dc.html file.
4. Run the intake scan from the workflow. Record inline style count, sc-if count, sc-for count, interpolation count, off-grid px count, fractional type sizes, glyph count, iframe count, CDN imports, and image-slot count.
5. Do not edit the archive.

Phase 1 — Inventory:
1. List every screen, query parameter, route, overlay, and state.
2. Classify each as product or design-only. Product ships. Design-only does not.
3. Map each product screen to an App Router path.
4. List components, data sources, assets, external runtime dependencies, roles, and missing states.
5. Stop and present the inventory and the route map. Do not write app code yet. If the session cannot ask a human, write the inventory to a file, record assumptions, and continue.

Phase 2 — Contract:
1. Write design-contract.json: tokens, type scale, spacing map, copy keys, icon map, screen map, data shapes, state machine.
2. Write the data-source map. For each surface, record: current source (design fixture, static artifact, or endpoint), target source, and contract. Mark every mock that a real HTTP call will replace. Do not mark a static artifact as a mock.

   | Surface | Current | Target | Contract |
   |---|---|---|---|
   | Calendar | data/processed/burning_calendar.json | static artifact, CDN later | ADR-0011 |
   | Briefing run | sample events | GET /api/v1/analysis/stream | docs/openapi/ai-service.json |
   | Sign-off | local decision handler | POST /api/v1/analysis/resume | docs/openapi/ai-service.json |
   | Use cases | static list | GET /api/v1/analysis/use-cases | docs/openapi/ai-service.json |
   | Review queue, run, audit | mock runs | no endpoint yet | missing |

   Sign-off and audit are never TODO(api) candidates. Wire them live in the slice that builds them.

3. Update DESIGN.md with tokens, icon rules, breakpoints, component naming, and the EN/VI term table.
4. Extract the pilot copy into src/i18n messages (or packages/i18n when a shared package exists).
5. Stop and present the contract. Do not write components yet. If the session cannot ask a human, write the contract to design-contract.json, record assumptions, and continue.

Phase 3 — Align the scaffold:
1. apps/workbench already exists. Do not re-scaffold. Confirm Next 16.4.3, React 19.3.0, Tailwind 4, React Compiler, and Bun in package.json.
2. Read apps/workbench/AGENTS.md and the version-matched docs in apps/workbench/node_modules/next/dist/docs/ before using a Next API. The installed version differs from training data.
3. Keep the App Router, TypeScript, Tailwind v4, React Compiler, and Turbopack. Do not switch to Webpack, the Pages Router, or another package manager.
4. Add packages/ui and packages/i18n only if the repo already has a workspace or a second app needs them. For one app, keep primitives in src/components/ui and catalogs in src/i18n.
5. Add @source "../"; to globals.css; add the UI package source path when it exists.
6. Prove lint, tsc --noEmit, and build are green before any design code.
7. If Turbopack reports multiple lockfiles, set turbopack.root to the app directory. Do not delete the repo lockfile.
8. If the scaffold fails, fix the scaffold. Do not charge it to the port.

Phase 4 — Pilot slice:
1. Build the shell and the Burning Activity Calendar pane. Do not build the map, globe, KPI strip, comparator, clock, evidence drawer, briefing, review, or tour yet.
2. Use the design fixture for parity and the real artifact for the swap. Keep both behind one typed loader.
3. Use the design's data for pixel parity. Use data/processed/burning_calendar.json for the swap.
4. If a loader still reads a design fixture that a real HTTP call will replace, add a TODO(api) marker at that loader. Do not put markers in JSX. Do not mark the calendar artifact or the parity fixture; they are not mocks.
5. Pass every gate before presenting the slice.

Phase 5 — Verify:
1. Run the gates in this order: format, lint, types, build, tokens, icons, boundaries, max-lines, api markers, console, accessibility, keyboard, locales, data swap.
2. Verify live parity at 1440, 834, and 390, dark and light, EN and VI.
3. Confirm zero console errors and zero hydration warnings.
4. Run the TODO(api) gate. Copy every marker into the RUN.md inventory with file:line, surface, current source, target endpoint, contract, and phase.
5. Write RUN.md with start and end time, every gate run, rework cycles, files and lines changed, dependencies added, decisions, deviations, and evidence paths.

Phase 6 — Remove the ai-service demo page:
1. Delete apps/ai-service/src/ai_service/demo/index.html and the demo/ directory.
2. In apps/ai-service/src/ai_service/api.py, remove DEMO_PAGE, the GET / FileResponse route, and the now-unused FileResponse import. Keep the analysis endpoints unchanged.
3. Do not serve HTML from the API. If the deployment needs a health check, add a minimal JSON GET /health; otherwise let / return 404.
4. Update apps/ai-service/src/ai_service/serve.py text that refers to the removed HTML page. Keep the AI_SERVICE_AUTH=disabled loopback warning.
5. Update source docs that claim the page exists: README.md, docs/05_Pitch_Deck_and_Video_Script.md, exports/MODEL_FLOW.md, exports/REPORT.md, and exports/PROPOSAL.md. Regenerate generated exports; do not hand-edit them.
6. From apps/ai-service, run ruff format --check, ruff check, and pytest.
7. Confirm the package no longer ships demo/, and no test asserts that GET / returns HTML.

TODO(api) convention:
- Use exactly TODO(api): in a single-line comment at the data boundary (loader, API module, hook). Never put it in JSX.
- TODO(api) is API wiring debt, tracked in RUN.md. Do not also add a ponytail: marker.
- State the surface, the replacement, and the contract.
- If no endpoint exists, say "no endpoint yet" and name the expected path. Do not invent a live call.
- One marker per boundary. Do not mark static artifacts, design-only data, or the parity fixture.
- Never use TODO(api) for a write or a trust gate (sign-off, approval, audit). Wire those live in the same slice; a local stand-in is a defect.
- List every marker in RUN.md with file:line, surface, current source, target endpoint, contract, and phase. Use this table: | File:line | Surface | Current | Target | Contract | Phase |.
- Remove the marker when the API is wired. Production has zero.
- Grep gate: rg -n 'TODO\(api\)' apps/workbench/src. Every hit must match this format and appear in RUN.md.

Later API-wiring phase (not in this prompt): use the RUN.md inventory as the checklist. Wire the endpoint, delete the fixture, remove the marker, and update the contract test. Do not keep both paths.

Examples:
// TODO(api): briefing run — replace SAMPLE_EVENTS with GET /api/v1/analysis/stream; contract: docs/openapi/ai-service.json
// TODO(api): review queue — no endpoint yet; replace REVIEW_RUNS when GET /api/v1/review/runs lands

Coding rules (Next 16.4.3 + React 19.3):
Next.js:
- Server Components by default. Add "use client" at the smallest interactive leaf. Never mark a page or layout client unless the whole surface needs it.
- Use the global PageProps and LayoutProps helpers. Await params and searchParams. Do not hand-type route props.
- Use next/font, next/image, and next/link. No Google Fonts link, no raw img for content, no a for an internal route.
- Use next/navigation and the route files page, layout, loading, error, not-found. No Pages Router.
- Name request hooks proxy.ts, not middleware.ts. Turbopack is the default. Do not pass --webpack.
- React Compiler is on. Do not add useMemo, useCallback, or React.memo by default. Add them only for a measured cost or a third-party API that requires referential stability.
- Metadata is per route. Server Components do not use browser APIs. Client Components do not import server-only modules.

React and components:
- One component per file, named by domain role: calendar-pane.tsx, run-timeline.tsx. Never step-1.tsx or panel-a.tsx.
- Keep files <=250 lines after formatting; 300 is the hard cap. Split by responsibility, not by markup block.
- Props are typed and explicit. No any, no type-bypass casts. No boolean prop proliferation; use composition, children, and slots.
- Container components own data and state. Presentational components take props and render. Do not fetch inside a presentational component.
- Keep state close to its use. Lift it only when shared. Derive values during render; do not mirror them in state.
- Hooks run unconditionally before early returns. Do not fetch or derive state in useEffect. Use a server loader, React Query, or an event handler.
- Stable keys. No array index keys. No useEffect for a value you can compute.
- Use cn for conditional classes when it lands. Do not hand-concatenate long class strings.

Team rules:
- Tailwind v4 utilities only. No inline style={{}}. No raw hex or [Npx]. Use @theme tokens. Custom classes go in @layer components.
- No Unicode glyphs in JSX. Add concept keys to the ICON registry (lucide-react) and render with Icon. Text labels are acceptable until the registry exists.
- No machinery leaks or raw enums in copy. All copy goes through the locale catalog. EN and VI.
- Accessibility: semantic elements first, label every control, keyboard path for every interaction, visible focus, never colour alone.
- Imports: workspace packages through package.json#exports; app files by path; no export * barrels.
- Check the team library baseline before adding a dependency. Do not add a chart, icon, or state library without a decision.
- The scaffold ships ESLint; the team baseline is Oxlint. Do not add or customize ESLint rules. Keep bun run lint green until the root Oxlint baseline lands, then remove eslint.config.mjs and use the root lint.
- Keep the scaffold's Bun scripts. Do not introduce pnpm commands or a second lockfile.
- Read apps/workbench/AGENTS.md, then delete it before the final commit per the team rule. The versioned docs stay in node_modules/next/dist/docs/.
- Before done: bun run lint, bunx tsc --noEmit, bun run build. All green.

Hard rules for Flare-Chronos:
- The design calendar covers 2000–2025. The artifact covers 2001–2026. Align by year, not row index.
- sfai_matrix has 10 non-null values, all at pentad 15. A null SFAI renders as "not scored", never zero.
- cell_provenance_matrix: 0 and 1 are observed, 2 is modelled. Do not use the design's obs window as the production rule.
- Do not port REGIONS, getData(), or any synthetic number. The 2024 Mekong raw count is 50,988, not 319,549.
- Run and audit IDs come from the service. Do not port R-0412, RUN-B, or A-0193.
- One approval gate. Unless D5 says otherwise, Review owns the decision and Workbench links to it read-only.
- Remove the demo token, the service simulator, and the prototype banner from the product surface. Keep the banner behind a build flag.
- The ai-service has no browser UI. Delete the demo HTML page; the Workbench is the only web client.
- Every mock that a real HTTP call will replace carries TODO(api) at its loader. A bare TODO, or a marker in JSX, is a defect. The calendar artifact and the parity fixture are not mocks.
- TODO(api) never defers a trust gate. Sign-off and audit writes call the real endpoint in the same slice.
- Five native figures. No static phenology figure. The Polar Phenology Clock is the phenology view.
- Use recharts for xy charts. Use hand-written SVG for the calendar grid, polar clock, mini-map, and footprint lens. D4 must approve any deviation.
- EN and VI. next-intl with a cookie locale. No path segment unless D2 says otherwise.
- No inline style={{}}. No raw hex or [Npx]. No Unicode glyph in JSX. No file over 300 lines after format.

Non-goals:
- Do not convert the whole archive in one pass.
- Do not port Components.dc.html, Screens.dc.html, or the Review states/notes/devices views.
- Do not edit apps/ai-service except the demo-page removal in Phase 6. Do not edit packages/*.py, data/processed/*, or the design archive.
- Do not add a replay path or mock the sign-off gate.
- Do not merge.

Stop conditions:
- SPEC is missing, or D1–D3 are unresolved.
- The scaffold is red after two fix attempts.
- The data swap needs a component change that contradicts the contract.
- The ai-service tests fail after the demo-page removal.
- Parity is outside tolerance after two rework cycles.

Output:
- The working pilot slice on a branch.
- design-contract.json, DESIGN.md updates, i18n catalogs.
- The ai-service demo page removed, with its Python gates green.
- RUN.md includes the TODO(api) inventory; every row has a contract or an explicit "no endpoint yet".
- fixture hashes and the real artifact path.
- RUN.md and the parity evidence.
- A short list of rule or scaffold changes you recommend.

Do not continue to the next slice. Present the pilot and stop.
```

---

## What the agent must not do

- Do not treat the archive as the source of truth for data, auth, routing, or state completeness.
- Do not copy the design's inline styles, glyphs, iframes, query router, or mock generator.
- Do not weaken a gate to make the slice pass.
- Do not merge the branch or continue to a second slice without a review.
