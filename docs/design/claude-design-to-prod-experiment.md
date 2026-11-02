# Claude Design → Production: Conversion Experiment

**Companion:** [`claude-design-to-prod-context.md`](./claude-design-to-prod-context.md). Read it first.
**Generic method:** `workflows/claude-design-to-nextjs.md` in `The-Resonance-Team/skills` (zip intake and the conversion method check). This file is the Flare-Chronos instantiation.
**Status:** ready to run once decisions D1–D3 in the context are accepted. No web app exists yet; Stage 0 creates the shared scaffold.
**Decision this experiment informs:** which conversion method agents must use for the rest of the Workbench and Review port, and which gates prove a slice is production-ready.

---

## 0. Why this experiment exists

The repository has a working design prototype and no TypeScript web app. A large port is about to start. Two methods are plausible:

- **Markup-first:** translate the `.dc.html` markup to JSX, then clean up tokens and primitives when a gate fails.
- **Contract-first:** extract the design contract (tokens, type scale, spacing map, copy keys, data mapping) first, then write components against it.

Both can reach the same pixels. The difference is rework. The design has 1,108 inline styles, 1,555 off-grid pixel occurrences, and 15 unique Unicode icon glyphs across the two product files. Those are the defects the gates will catch. The experiment measures which method catches them earlier and cheaper.

Do not run the whole app. Run one vertical slice that contains the same defect classes.

---

## 1. Questions

| ID | Question | Type |
|---|---|---|
| Q1 | Which method produces a gate-green, parity-matching calendar slice with fewer rework cycles? | Primary |
| Q2 | Which gate catches which defect class first? | Secondary |
| Q3 | Is 4 px snapping enough for parity, or does the slice need odd-value spacing tokens? | Secondary |
| Q4 | Does a native calendar (SVG or CSS grid) match the design's CSS-grid calendar within tolerance? | Secondary |
| Q5 | Does the component survive the swap from the design fixture to the real artifact without edits? | Secondary |

---

## 2. Hypotheses

| ID | Hypothesis | Falsified if |
|---|---|---|
| H1 | Contract-first reaches first green in fewer rework cycles | Markup-first has equal or fewer cycles |
| H2 | Markup-first reaches first visual parity sooner | Contract-first is equal or faster |
| H3 | The dominant rework class is spacing and type tokens, not colour | Most rework is colour or layout structure |
| H4 | 4 px snapping fails parity on the calendar pane | Snapped layout stays within tolerance |
| H5 | The real artifact forces a component change because SFAI is sparse | The component handles nulls with no edit |

A hypothesis is accepted only with the recorded evidence in §11. A verbal impression is not evidence.

---

## 3. Design

| Element | Choice |
|---|---|
| Unit of work | One vertical slice: Workbench header + Burning Activity Calendar pane |
| Arms | A = markup-first, B = contract-first |
| Control | The `.dc.html` at the same viewport, theme, locale, and data |
| Runs | One per arm. Repeat both if the arms differ by fewer than 2 rework cycles or less than 20% in time to parity |
| Timebox | 6 hours per arm, hard stop, or the session budget, whichever comes first |
| Environment | One git worktree per arm, same base commit, same scaffold |
| Agent | Same model, same prompt, fresh session, no access to the other arm |
| Evaluation | Blind screenshot labels; a separate evaluator session |
| Merge | Neither arm merges. The winning method becomes an ADR and a fresh branch |

**Fairness rules**

- Both arms receive the same fixture, the same route, the same gates, and the same timebox.
- The scaffold is prepared once by the operator and is identical in both worktrees.
- An arm may add a runtime dependency only from `rules/libraries.md`. Any other dependency is recorded as a finding, not blocked. Test tooling is exempt.
- No human code edits during the run. The operator may restart a crashed session and must record it.

---

## 4. Stage 0 — shared scaffold (not measured)

Do this once, before either arm starts. Commit it. Both arms branch from this commit. The scaffold is infrastructure, not a result.

### 4.1 Workspace

```
pnpm-workspace.yaml          # apps/workbench, packages/ui, packages/i18n
.oxfmtrc.json                # from skills configs
.oxlintrc.json               # from skills configs
DESIGN.md                    # stub: tokens, icons, breakpoints, term table
apps/workbench/                    # Next.js 16, App Router, TS, Tailwind v4
packages/ui/                 # tokens.css, icon.tsx, primitives
packages/i18n/               # messages/en.json, messages/vi.json
```

`pnpm-workspace.yaml` must list the three packages explicitly. Do not glob `apps/*`; the Python apps have no `package.json`. Root `package.json` must expose `format`, `format:check`, and `lint` scripts, because the gate commands call them.

### 4.2 `apps/workbench` minimum

- `src/app/layout.tsx` with `next/font` for IBM Plex Sans and IBM Plex Mono.
- `src/app/globals.css` with `@import "tailwindcss";`, `@source "../";`, `@source "../../../../packages/ui/src";`.
- `src/app/workbench/page.tsx` rendering the slice.
- `src/lib/data/calendar.ts` with one typed loader. It reads a JSON fixture path from an environment variable or a constant.
- `src/proxy.ts` only if auth is needed. The pilot does not need it.
- No API calls. The pilot is a static surface.

### 4.3 `packages/ui` minimum

- `tokens.css` with `@theme inline` mappings for the §6.1 tokens. Name them by role, not by hex.
- `icon.tsx` with `ICON` and `<Icon>`; `lucide-react` is the only icon dependency.
- `cn` from `cn`; do not write a wrapper.
- No app-specific components yet.

### 4.4 `packages/i18n` minimum

- `messages/en.json` and `messages/vi.json`.
- Keys for the pilot only: header labels, calendar title, legend, metric names, tooltip, month names, weekday names, empty and error text.
- `next-intl` with a cookie locale and no path segment.

### 4.5 Scaffold gate

The empty scaffold must pass `build`, `tsc`, `lint`, and `fmt` before either arm starts. If it does not, fix the scaffold. Do not charge the failure to an arm.

---

## 5. Fixtures

Store under `docs/design/experiments/fixtures/`. Hash every file and record the hash in the run sheet.

### 5.1 Design screenshots (the visual oracle)

Capture from a local static server. The design needs network access for React, Babel, Three, D3, and Google Fonts. Confirm that access before the run; without it, the fixtures cannot be captured.

```sh
cd <extracted-design-dir>
python3 -m http.server 8765
```

Capture with Playwright at these URLs:

| Fixture | URL suffix | Viewport |
|---|---|---|
| `design-1440-dark-en.png` | `?screen=workbench&bp=desktop&theme=dark&lang=en` | 1440 × 900 |
| `design-1440-light-vi.png` | `?screen=workbench&bp=desktop&theme=light&lang=vi` | 1440 × 900 |
| `design-834-dark-en.png` | `?screen=workbench&bp=tablet&theme=dark&lang=en` | 834 × 1194 |
| `design-390-dark-en.png` | `?screen=workbench&bp=mobile&tab=cal&theme=dark&lang=en` | 390 × 844 |
| `design-1440-dark-vi.png` | `?screen=workbench&bp=desktop&theme=dark&lang=vi` | 1440 × 900 |
| `design-390-light-vi.png` | `?screen=workbench&bp=mobile&tab=cal&theme=light&lang=vi` | 390 × 844 |

Rules:

- Wait for `document.fonts.ready` and for the loader to reach opacity 0.
- Use `page.screenshot({ animations: 'disabled' })`.
- Do not hover, focus, or click. The fixture is the resting state.
- At 834 and 390, scroll the calendar pane into view before capture.
- Crop the calendar pane by screenshotting the nearest section ancestor of the `role="grid"` element. Add `data-testid="calendar-pane"` in production for a stable selector.
- Keep the full page for layout reference.

### 5.2 Design calendar fixture (the parity data)

The design synthesizes its calendar data in `getData()`. The production component must receive the **same data** for parity, so extract it once. This is a fixture, not a data source.

1. Copy the extracted design to a temp directory outside the repo, for example the approved temp dir. Do not commit the design source and do not edit the original archive.
2. Append this line at the end of the `data-dc-script` block in the copy:
   ```js
   window.__fcData = { getData, REGIONS, YEARS };
   ```
3. Serve the copy and run:
   ```js
   const data = await page.evaluate(() => window.__fcData.getData('mekong'));
   ```
4. Save `fixtures/design-calendar-mekong.json` and `fixtures/design-calendar-amazon.json`.
5. Record the SHA-256 of each file.

The object shape is `{ R, z, hfd, hrf, obs, H, raw, S, q25, q75, ep, vmaxF, vmaxR, trend }`. `R` holds the region config.

Design-to-component mapping for parity:

| Visual | Design source | Real artifact source |
|---|---|---|
| HFD fill | `seqC(Math.sqrt(hfd[y][p] / vmaxF), light)` | normalized `hfd_matrix[y][p]` |
| SFAI fill | `divC(z[y][p], light)` | `sfai_matrix[y][p]`, null-aware |
| Observed vs modelled | `obs[y][p]` (epoch window) | `cell_provenance_matrix[y][p]`: 0/1 observed, 2 modelled |
| Selected cell | `active {y,p}` | component state |
| Alert ring | observed and `z ≥ 2.2`: inset 1.5 px cyan | observed and `sfai ≥ 2.2` |
| Crisis mark | observed and `z ≥ 2.5`: 4 px cyan corner gradient | observed and `sfai ≥ 2.5` |

The design's `obs` is a synthetic epoch window. The artifact's provenance is per cell. The component must accept a provenance matrix, not hard-code the design's window.

**Year offset.** The design fixture covers 2000–2025. The real artifact covers 2001–2026. Both have 26 rows, but the rows are shifted by one year. For parity, use the design fixture. For the swap test, align by year label and check rendering, null handling, and layout only. Do not expect the same pixels.

### 5.3 Real artifact (the swap fixture)

`data/processed/burning_calendar.json`, region `mekong`. Copy it to `fixtures/real-calendar-mekong.json` and hash it. The swap test loads this file with no component edit.

### 5.4 Copy fixture

Extract the pilot strings from `I18N.en` and `I18N.vi` in the Workbench file into `fixtures/copy-en.json` and `fixtures/copy-vi.json`. Keys only for the pilot. Do not copy the full catalog.

---

## 6. Pilot task

### 6.1 Scope

Build `/workbench` with:

1. A header: logo, region label (static), period label, theme toggle, language toggle.
2. A calendar pane: title, metric toggle (HFD / SFAI), 26 × 73 grid, month and pentad axis, legend, selected-cell summary, tooltip.
3. Responsive layout at 1440, 834, and 390.
4. Dark and light themes.
5. EN and VI copy.

The parity fixture covers 2000–2025. The real artifact covers 2001–2026. Build the component so the year list is a prop, not a constant.

### 6.2 Behaviour

- Arrow keys move the active cell. Home/End jump to pentad 1/73. Page Up/Down move by five years.
- Enter or Space selects the active cell and updates the summary.
- Hover or focus shows a tooltip with year, pentad, date, HFD, SFAI (if observed), and provenance.
- The metric toggle switches the fill scale and the legend.
- The theme toggle switches tokens without a flash.
- The language toggle switches copy without a reload.
- Null SFAI renders as an empty cell with a "not scored" tooltip. It never renders as zero.

### 6.3 Non-goals

- No map, globe, KPI strip, comparator, polar clock, evidence drawer, briefing, review, or tour.
- No API calls, auth, SSE, or database.
- No changes to `apps/ai-service`, `packages/*.py`, `data/processed/*`, or the design archive.
- No new chart library for the calendar. It is a grid, not a chart.

### 6.4 Acceptance

The slice is accepted only when every gate in §7 passes and the parity report in §8 is within tolerance.

---

## 7. Gates

Run in this order. `bun fmt` first, always.

| Gate | Command | Pass condition |
|---|---|---|
| Format | `bun fmt --check` | Zero changes |
| Lint | `bun lint --no-script --max-warnings=0 --allow-unsupported` | Zero findings |
| Types | `pnpm --filter @flare/workbench exec tsc --noEmit` | Zero errors |
| Build | `pnpm --filter @flare/workbench build` | Exit 0 |
| Tokens (experiment) | `rg -n -e '#[0-9a-fA-F]{3,8}\b' -e '\[[0-9.]+px\]' apps/workbench/src packages/ui/src` | Zero hits outside token files, SVG attributes, and chart-series maps |
| Icons (experiment) | `rg -n '[‹←→↓↻⊘⌃▶▸▾◆◐✓✕❙]' apps/workbench/src` | Zero hits in JSX text. Arrows inside sentence strings are allowed |
| Inline styles | `rg -n 'style=\{\{' apps/workbench/src` | Zero hits |
| File size | `find apps/workbench/src packages/ui/src -type f \( -name '*.tsx' -o -name '*.ts' \) -exec wc -l {} +` | No file > 300 lines after format. Sort the output by line count |
| Console | Playwright: collect `console` errors and `pageerror` | Zero errors, zero hydration warnings |
| Accessibility | `@axe-core/playwright` | Zero serious or critical violations |
| Keyboard | Playwright: tab to the grid, arrows, Enter | All §6.2 actions work without a mouse |
| Locales | Screenshot EN and VI; scan rendered text | No leaked strings from the other locale |
| Data swap | Load `real-calendar-mekong.json` | Renders; null SFAI is empty; no crash; layout shift ≤ 2 px |

The token and icon gates are grep checks for the experiment. Replace them with the repo's `lint:tokens` and `lint:icons` when those scripts land. Do not weaken them to pass.

---

## 8. Metrics and parity

### 8.1 Process metrics

| Metric | Definition | Source |
|---|---|---|
| `first_green` | Minutes from prompt start to the first run where all gates pass | Run sheet |
| `rework_cycles` | Gate runs that fail, followed by a code change, before `first_green`. Cap at 5 | Git log + run sheet |
| `gate_failures_first_run` | Which gates fail on the first complete run | Run sheet |
| `time_to_parity` | Minutes to the first screenshot within tolerance | Run sheet |
| `files` | Files created or changed | `git diff --stat` |
| `loc` | Added lines of TS/TSX/CSS | `git diff --numstat` |
| `deps` | Runtime dependencies added | `package.json` diff |
| `restarts` | Crashed or restarted sessions | Run sheet |

### 8.2 Quality metrics (after `first_green`)

| Metric | Pass |
|---|---|
| Inline `style={{}}` | 0 |
| Raw hex / `[Npx]` | 0 outside token files and allowed SVG/chart maps |
| Unicode icon glyphs in JSX | 0 |
| `any` | 0 |
| Files > 300 lines | 0 |
| Duplicate primitives | 0. One button, one chip, one panel |
| a11y violations | 0 serious, 0 critical |

### 8.3 Parity

Measure the calendar pane, not the whole page.

**Layout:** compare `getBoundingClientRect()` for these regions against the design:

1. Header.
2. Calendar pane outer box.
3. Title block.
4. Metric toggle.
5. Grid box.
6. Month axis.
7. Legend.
8. Selected-cell summary.
9. Source note.
10. Page padding box.

Pass: each dimension within **±2 px**.

**Computed style:** for the header, title, axis label, legend label, cell, and selected summary, compare `fontFamily`, `fontSize`, `fontWeight`, `color`, `backgroundColor`, `borderRadius`, and `padding`. Pass: same primary font family and weight; fontSize and padding within ±1 px; colours within ΔE2000 ≤ 2 after converting both to sRGB. The design writes some colours as `oklch()` and others as hex, so compare resolved values, not strings.

**Pixels:** crop the calendar pane and compare with ImageMagick:

```sh
magick compare -metric RMSE -fuzz 2% design-calendar.png prod-calendar.png diff.png
```

Pass: normalized RMSE ≤ **1.5%**. ImageMagick prints the normalized value in parentheses. If the check fails, inspect `diff.png`. Do not raise the threshold without recording why.

**Text:** compare visible text after whitespace normalization. Pass: identical in EN and VI, except for data values that legitimately differ in the swap test.

### 8.4 Scoring

Hard gates are pass/fail. Do not average them.

Order of comparison:

1. All hard gates pass.
2. Lower `rework_cycles`.
3. Lower `time_to_parity`.
4. Lower quality debt count.
5. Lower `loc` and `files`.

If the RMSE difference between arms exceeds **0.015**, parity wins over process metrics.

---

## 9. Procedure

1. **Freeze.** Record the base commit, the design archive SHA-256, and the fixture hashes.
2. **Scaffold.** Complete Stage 0 and prove it green. Commit.
3. **Worktrees.** Create two sibling worktrees, one per arm. Do not nest them in the repo.
4. **Brief.** Start each arm in a fresh session with the §10 prompt and the arm-specific method. Do not give either arm the other's branch or notes.
5. **Run.** Timebox 6 hours. Record gate runs as they happen. Do not coach.
6. **Stop.** At 6 hours, stop and run the gates on the current tree. A partial slice is a valid result.
7. **Capture.** Run the screenshot and parity scripts. Save all evidence under `docs/design/experiments/runs/<arm>/`.
8. **Blind.** Rename the screenshots `slice-1` and `slice-2` in random order. Give them to an evaluator session with no arm context. Record the key separately.
9. **Score.** Fill the §11 template. Compute the metrics from the evidence, not from memory.
10. **Decide.** Apply §12. Write an ADR with the result and the method the team will use.

---

## 10. Agent prompt

For the Flare-Chronos instance with the paths already filled, use [`claude-design-zip-to-apps-prompt.md`](./claude-design-zip-to-apps-prompt.md). The block below is the generic form.

Copy this prompt into each arm. Replace `{{ARM}}` with `A` or `B`, and `{{METHOD}}` with the paragraph below.

```markdown
You are a senior frontend engineer. Convert one vertical slice of a Claude Design export to production Next.js code.
Arm: {{ARM}}

Read first, in this order:
1. docs/design/claude-design-to-prod-context.md
2. docs/04_UI_UX_Burning_Calendar_Wireframe.md §3.2
3. The rule modules linked from CONTEXT.md: rules/frontend.md, rules/linting.md, rules/libraries.md, rules/general.md
4. docs/design/experiments/fixtures/design-calendar-mekong.json (shape only)
5. The design source, only the calendar, header, and I18N ranges (header ~30–140, calendar ~300–330, cell renderer ~975–995, I18N ~648–655)

Scope:
- Route /workbench with the header and the Burning Activity Calendar pane.
- 1440, 834, and 390 widths; dark and light; EN and VI.
- Keyboard, selection, tooltip, metric toggle, theme toggle, language toggle.
- Null SFAI must render as "not scored", never zero.

Non-goals:
- No map, globe, KPI strip, comparator, clock, evidence drawer, briefing, review, or tour.
- No API, auth, SSE, or database work.
- Do not edit apps/ai-service, packages/*.py, data/processed/*, or the design archive.
- Do not change the scaffold's token policy, lint config, or file budget.

Method:
{{METHOD}}

Gates, in this order:
bun fmt --check
bun lint --no-script --max-warnings=0 --allow-unsupported
pnpm --filter @flare/workbench exec tsc --noEmit
pnpm --filter @flare/workbench build
grep gates for raw hex, [Npx], inline styles, and Unicode glyphs
Playwright: console errors, a11y, keyboard, locales
Data swap to fixtures/real-calendar-mekong.json

Output:
- The working slice.
- RUN.md with: start and end time, every gate run and result, rework cycles, files and lines changed, dependencies added, decisions, deviations, and the data-swap result.
- A short note on what you would change in the scaffold or the rules.

Stop at 6 hours. Do not merge. Do not touch another worktree.
```

Arm methods:

**A — markup-first.** “Start from the `.dc.html` calendar and header markup. Translate it to JSX and make it render first. Replace inline styles and glyphs only when a gate fails. Extract primitives after the slice is green.”

**B — contract-first.** “Before writing components, write `design-contract.json`: token map, type scale, spacing map, copy keys, and the data-to-fill mapping. Then write components against that contract. Use the markup only to confirm geometry. Do not copy inline styles.”

Both arms must produce the same route and the same behaviour. The method is the only variable.

---

## 11. Result template

Save as `docs/design/experiments/runs/<date>/RESULT.md`.

```markdown
# Conversion Experiment — <date>

Base commit:
Design archive SHA-256:
Fixture SHA-256:
Agent model:
Evaluator:

## Runs

| Field | Arm A (markup-first) | Arm B (contract-first) |
|---|---|---|
| Start / end | | |
| first_green (min) | | |
| time_to_parity (min) | | |
| rework_cycles | | |
| gate_failures_first_run | | |
| files / loc | | |
| deps added | | |
| restarts | | |
| Pixel RMSE | | |
| Max layout delta | | |
| a11y serious/critical | | |
| Data swap | pass / fail | pass / fail |

## Gate history

| # | Arm | Gate | Result | Fix |
|---|---|---|---|---|

## Findings

- Dominant defect class:
- Gate that caught it first:
- Spacing policy that held:
- What the real artifact broke:
- Scaffold or rule change needed:

## Blind evaluation

| Slice label | Visual match (1–5) | Interaction (1–5) | Notes |
|---|---|---|---|

## Decision

Method chosen:
Reason:
ADR:
```

---

## 12. Decision rules

| Outcome | Decision |
|---|---|
| Both pass, B has fewer rework cycles | Adopt contract-first for S1–S13 |
| Both pass, A has fewer rework cycles | Adopt markup-first; add a token cleanup pass to the runbook |
| A passes, B fails a hard gate | Adopt markup-first; record B's failure class |
| B passes, A fails a hard gate | Adopt contract-first; record A's failure class |
| Both fail | Stop the port. The finding is the blocker. Fix the scaffold, the fixture, or the rule before scaling |
| Parity RMSE differs by more than 0.015 | The more accurate arm wins, even if slower |
| Results differ by < 20% on Q1 | Repeat both arms once before deciding |

Do not adopt a method that fails a hard gate. Do not average a hard failure into a score.

---

## 13. Threats to validity

| Threat | Control |
|---|---|
| Agent skill variance | Same model, same prompt, fresh sessions. Run in parallel if possible; otherwise run A then B on the same day and record the order |
| Order effects | Run both arms from the same commit at the same time |
| Fixture drift | Hash every fixture; fail the run if a hash changes |
| Screenshot noise | Same browser, same fonts, `animations: 'disabled'`, fixed viewport |
| Font loading | Wait for `document.fonts.ready` before capture |
| Different data | Both arms use `design-calendar-mekong.json` for parity |
| Evaluator bias | Blind labels; separate evaluator session |
| Small sample | One slice is directional. Repeat if the difference is small |
| Scaffold defects | Stage 0 must be green before either arm starts |
| Hidden edits | `git diff` per arm; no human edits during the run |

---

## 14. Extension stages

Run these only after the pilot decides the method.

| Stage | Slice | Main risk |
|---|---|---|
| 2 | Review queue + run + citation + decision | Trust surface, two approval paths |
| 3 | Briefing SSE + clarification + failure + sign-off | Auth, stream, suspended state |
| 4 | Globe + map islands | WebGL, CDN removal, fallbacks |
| 5 | Full responsive, a11y, EN/VI sweep | Drift across slices |
| 6 | Real-data swap and fixture deletion | Sparse SFAI, period labels, provenance |

Each stage uses the same gates. Each stage produces a `RESULT.md` and, if it changes the method, an ADR.

---

## 15. Definition of resolved

The experiment is resolved when:

1. Both arms have a `RESULT.md` with evidence.
2. The parity report is reproducible from the saved screenshots and fixtures.
3. The data-swap result is recorded.
4. One method is chosen by §12.
5. An ADR records the method, the gates, and the rejected alternative.
6. The winning slice is either merged or scheduled as the first slice of the port.
7. The scaffold and fixtures are committed; the losing worktree is deleted.
