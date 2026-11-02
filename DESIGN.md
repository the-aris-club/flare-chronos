# DESIGN.md — Flare Chronos UI/UX specification

The single source of truth for aesthetic direction, tokens, shared primitives, icon
vocabulary, layout rules, and user-facing copy. Domain terms live in `GLOSSARY.md`;
this file owns presentation and copy only.

Linked from `AGENTS.md` and `GLOSSARY-MAP.md`. A string or colour that contradicts
this file is a defect even when it looks right in isolation.

## 1. Aesthetic direction

A dark, instrument-panel workspace for scientists: near-black ground, hairline
borders, dense mono numerals, one warm fire accent, one cool cyan accent. Light
theme is the same instrument read on paper — not an inversion, a re-ink.

- Density over decoration. A 1 px hairline separates regions; no drop shadows
  except the floating header, the fixed readout card and dialogs.
- The Review surface is the same instrument in a different mode: a queue, a run
  evidence column, a decision rail and a read-only audit trail. It uses the same
  header, tokens and type; it does not get a separate visual language.
- Data carries the colour. Chrome is grey; HFD uses a sequential warm ramp, SFAI a
  diverging cool/warm ramp. Severe anomalies get a cyan ring, never a new hue.
- Mono for numbers, dates, pentads, units, and axes. Sans for prose and labels.
- No gradients as decoration, no glassmorphism beyond the sticky header, the
  landing sheet and the briefing rail. The Region Globe is the one atmospheric
  surface: a radial field behind the 3D Earth, a translucent sheet on small
  screens, and a sky (NASA SVS Deep Star Map, decorative, credited in the footer,
  dimmed behind the landing copy, dark theme only). It is imagery, not chrome.
- Motion is feedback only: 120–180 ms colour/opacity transitions; no entrance
  animations; respect `prefers-reduced-motion`. The landing globe is the one
  continuous motion, and it stops for reduced motion.

## 2. Token system

Tokens are CSS custom properties on `:root` and `[data-theme="light"]` in
`apps/workbench/src/app/globals.css`, exposed to Tailwind through `@theme inline`.
Components use token utilities (`bg-panel`, `text-ink-muted`, `border-line`) — never
a raw hex value, never an arbitrary `[Npx]` size.

### 2.1 Colour

| Token | Dark | Light | Use |
|---|---|---|---|
| `--bg` | `#070b14` | `#f2f4f8` | page |
| `--surface` | `#0b111c` | `#ffffff` | header, secondary surface |
| `--panel` | `#0c121e` | `#ffffff` | card |
| `--raised` | `#121a29` | `#f5f7fa` | raised row, unscored cell |
| `--seg` | `rgba(150,170,210,.16)` | `rgba(20,30,60,.08)` | segmented control |
| `--glass` | `rgba(10,15,26,.74)` | `rgba(255,255,255,.82)` | sticky header |
| `--line` | `rgba(150,170,210,.13)` | `rgba(20,30,60,.10)` | hairline |
| `--line-strong` | `rgba(150,170,210,.26)` | `rgba(20,30,60,.20)` | control border |
| `--text` | `#eef2f8` | `#121a2b` | primary |
| `--text-muted` | `#b4bfd0` | `#3d485d` | secondary |
| `--text-subtle` | `#8e9ab0` | `#5a6579` | tertiary |
| `--brand` | `#8fb0ff` | `#0d3a8c` | brand secondary |
| `--fire` | `#ff8a3d` | `#c4520f` | fire accent |
| `--raw` | `#ff5a36` | `#cf3a1c` | raw series |
| `--amber` | `#f5b23a` | `#9a5a00` | MODIS |
| `--teal` | `#3cc9b0` | `#0b7d6c` | harmonized series |
| `--cyan` | `#57e3ff` | `#0a6f8c` | severe-anomaly outline |
| `--purple` | `#b195ea` | `#7650c4` | secondary annotation |
| `--grey` | `#8f99ab` | `#68728a` | static / excluded |
| `--ok` | `#5fd394` | `#1b7f49` | pass |
| `--warn` | `#f5b23a` | `#9a5a00` | caution |
| `--bad` | `#ff7070` | `#bf3030` | fail |
| `--hatch` | `rgba(150,170,210,.30)` | `rgba(20,30,60,.24)` | modelled overlay |
| `--focus` | `#eef2f8` | `#121a2b` | focus ring |
| `--scrim` | `rgba(3,6,12,.70)` | `rgba(18,26,43,.46)` | modal scrim |
| `--chip` | `rgba(150,170,210,.07)` | `rgba(20,30,60,.04)` | chip fill |

Data ramps are computed in `src/lib/calendar/ramp.ts`, not tokenised:

- HFD sequential: `oklch(.25 + .68t  .05 + .13t  25 + 65t)` with `t = sqrt(hfd / maxHfd)`.
- SFAI diverging: hue `255` below zero, hue `35` above zero, alpha `min(3, |z|) / 3`.

### 2.2 Type

IBM Plex Sans (`--font-sans`) and IBM Plex Mono (`--font-mono`) via `next/font`,
`display: swap`, self-hosted. Sizes are named utilities; a design size maps to the
nearest token with at most 1 px drift.

| Token | Size | Use |
|---|---|---|
| `text-micro` | 9 px | year axis, ramp ends |
| `text-label` | 10 px | eyebrow, legend |
| `text-meta` | 11 px | mono readout, chip |
| `text-body` | 12 px | body, controls |
| `text-body-lg` | 13 px | panel title |
| `text-subhead` | 14 px | section head |
| `text-title` | 15 px | page title |
| `text-base` | 16 px | prose |
| `text-display` | 20 px | metric |
| `text-metric` | 22 px | hero metric |
| `text-hero-sm` | 24 px | landing headline, mobile |
| `text-hero-md` | 30 px | landing headline, tablet |
| `text-hero` | 40 px | landing headline, desktop |

Weights: 400 body, 500 controls, 600 titles and numerals, 700 wordmark.

### 2.3 Spacing, radius, layout

- Spacing unit `0.25rem`. Tailwind v4's dynamic scale covers every 1 px step
  (`p-0.5`, `p-1.5`, `p-2.5`, `p-3.5`, …). No arbitrary `[Npx]` values.
- Radius: `rounded-sm` 4 px inner segments, `rounded-md` 6 px chips and controls,
  `rounded-lg` 8 px panes. The design's 5/7/9 px radii snap to these with ≤ 1 px drift.
- Header: 52 px desktop, 56 px tablet and mobile, sticky, opaque `bg-surface`.
- Physics filter bar: 31 px at every breakpoint, directly below the header; it
  scrolls horizontally on narrow screens.
- Briefing rail: 392 px open / 36 px collapsed on desktop; full-width overlay on
  tablet and mobile, above the mobile tab bar.
- Region Globe panel: 440 px wide, 56 px from the inline start, vertically
  centred on desktop. On tablet and mobile it is a 58dvh bottom sheet that
  collapses to a 52 px handle.
- Loader: a centred 300 px column, 72 px ring, 2 px progress bar.
- Calendar cell: 9 px desktop, 12 px tablet, 14 px mobile, inside a 10/13/15 px
  row pitch that includes the 1 px gap.
- Calendar minimum width: 1150 px below 720 px only, inside an `overflow-auto`
  scroller. Above 720 px the 73 columns fit the pane. The year column is sticky at
  the inline start with the panel background.
- Content is full-bleed with a 12 px gutter mobile / 16 px tablet / 20 px desktop;
  no max width, so the 73-pentad grid uses the available instrument width.

## 3. Responsive rules

CSS-first. Breakpoints are Tailwind v4 theme values: `tablet` 720 px, `xl` 1280 px.
No `window.innerWidth` state, no user-agent sniffing.

| Range | Name | Behaviour |
|---|---|---|
| `< 720px` | mobile | 56 px header; brand mark only; bottom tabs (Map, Trend, Calendar, Briefing); calendar rows 14 px; grid and epoch selector scroll horizontally; readout wraps; Region Globe is a 58dvh sheet |
| `720–1279px` | tablet | 56 px header; full wordmark; icon-only header actions; calendar rows 12 px; grid fits the pane; briefing is an overlay; Region Globe is a 58dvh sheet |
| `≥ 1280px` | desktop | 52 px header; calendar rows 9 px; the 73-pentad grid fits; Region Globe panel is 440 px; Review queue is a table, Review run is three columns |

Every control stays reachable at 390 px. Icon-only controls carry an `aria-label`.
The calendar, the map epoch selector and the physics filter bar are the
horizontal scrollers on mobile; each scrolls inside its pane, never the page.

## 4. Shared UI primitives

Location `apps/workbench/src/components/ui`. One concern per file, flat.

| Primitive | Contract |
|---|---|
| `icon.tsx` | `ICON` concept registry and `Icon`. Renders `lucide-react`; sets `aria-hidden` and `focusable="false"`; `size` is `xs \| sm \| md \| lg \| xl`. |
| `segmented-control.tsx` | `role="group"`, `aria-pressed` buttons, mono labels, 2 px inset track. |
| `brand-mark.tsx` | CSS crop of `/logo.png` plus the `FLARE CHRONOS` wordmark; decorative image, `alt=""`. |
| `theme-toggle.tsx` | Icon button; flips the theme cookie and `data-theme` without a reload. |
| `locale-toggle.tsx` | Two-state EN/VI control; flips the locale cookie and refreshes server copy. |

Domain components live in `apps/workbench/src/components/workbench` and are named by
role, never by sequence: `app-header`, `filter-bar`, `map-pane`, `workbench-map`,
`kpi-strip`, `comparator-pane`, `clock-pane`, `burning-calendar`, `calendar-grid`,
`calendar-legend`, `calendar-summary`, `briefing-rail`, `briefing-run`,
`briefing-events`, `service-panel`, `map-controls`, `map-legend`, `evidence-drawer`,
`tour`.
The Region Globe island lives in `apps/workbench/src/components/globe`:
`globe-landing`, `landing-header`, `landing-panel`, `region-card`, `boot-overlay`,
`globe-canvas`, `globe-fallback`, `globe-morph`. The Review surface lives in
`apps/workbench/src/components/review`: `review-shell`, `review-queue`,
`review-run`, `review-decision`, `review-timeline`, `review-dialog`,
`briefing-dialog`, `citation-dialog`, `confirm-dialog`, `verification-table`,
`run-summary`, `mini-map`, `review-bits`, `review-select`. The Workbench adds
`evidence-quick-look` and `evidence-table`. A `step-1.tsx` name is a defect.

`three` is imported only by `src/lib/globe` (`scene`, `earth`, `orbits`, `stars`,
`picking`, `textures`). The canvas is a client island; the page stays a server
component.

Files stay at or below 300 lines after format; target 250. Split by concern, not by
line count.

## 5. Icon vocabulary

One concept-keyed registry in `components/ui/icon.tsx`. App code imports `ICON` and
`Icon`; app code never imports `lucide-react` directly and never draws a Unicode
glyph, emoji, or fullwidth symbol in JSX.

| Concept | Glyph | Use |
|---|---|---|
| `theme` | `Contrast` | theme toggle |
| `language` | `Languages` | locale toggle |
| `external` | `ArrowUpRight` | link out to Review |
| `alert` | `TriangleAlert` | alert legend, error panel |
| `close` | `X` | evidence and walkthrough close |
| `chevron` | `ChevronDown` | select and rail collapse |
| `tour` | `Play` | walkthrough |
| `evidence` | `FileText` | evidence drawer |
| `briefing` | `MessagesSquare` | briefing rail |
| `service` | `CircleDot` | service status |
| `pause` | `Pause` | paused run and human approval |
| `plus` / `minus` / `reset` | `Plus` / `Minus` / `Maximize2` | map zoom |
| `menu` | `Menu` | mobile header menu |
| `check` | `Check` | applied physics filters |
| `checkCircle` / `xCircle` | `CircleCheck` / `CircleX` | verified and excluded states |
| `globe` | `Globe` | return to the Region Globe |
| `arrow` | `ArrowRight` | region card affordance |
| `review` | `ClipboardCheck` | Review queue and run |
| `audit` | `History` | audit trail |
| `search` | `Search` | queue search |
| `filter` | `SlidersHorizontal` | filter controls |
| `download` | `Download` | audit export |
| `back` | `ArrowLeft` | queue and globe return |
| `next` | `ChevronRight` | row affordance |
| `dot` | `CircleDot` | pending and needs-decision states |
| `rewrite` | `RefreshCw` | rewritten value |
| `clock` | `Clock` | timeline pending |

Rules: a new concept adds a key here in the same change. An icon-only `<button>` or
`<a>` must carry `aria-label` or `aria-labelledby`. Decorative icons always
`aria-hidden`. Text arrows are `Icon icon={ICON.external}`, not `→`.

## 6. Copy voice

- Analyst-facing, declarative, present tense. Say what the data shows and what the
  reader can do. No marketing adjectives.
- EN and VI are peers. VI is drafted first for a new string, EN mirrors it in the
  same commit. `en.json` and `vi.json` have identical key sets; a parity test fails
  the build otherwise.
- No machinery leaks: no `provenance`, `matrix`, `SFAI pipeline`, raw enum, HTTP
  status, or English original in parentheses. The term table is the exemption
  register.
- The Region Globe headline is computed from the empirical series (raw 2005→2024
  growth); the sensor names and years are data, not copy written by hand.
- Numbers use `Intl.NumberFormat` with the active locale. The calendar's 73-column
  axis uses the compact month table below, not `Intl` month names.
- A null score reads "not scored" / "chưa chấm điểm". It never reads `0`, `—`, or
  `N/A`.
- VI copy is written for a Vietnamese analyst, not translated word by word. Dates are
  `dd/MM` (`15/03`, `12/03–16/03`), never `15 thg 3`. Counts of epochs are `n/total`
  (`10/26`), never `10 trên 26`.
- Chart axes keep `k` for thousands (`15k`, `30k`) or write `nghìn`. Never use `N`,
  which reads as north latitude.
- The artifact's `summary_caption` is English data, not UI copy. It is not rendered
  while the interface is Vietnamese.

### 6.1 Term table

| Internal term | EN | VI |
|---|---|---|
| Workbench (product surface) | Workbench | Không gian phân tích |
| Region Globe | Region Globe | Địa cầu khu vực |
| Review | Review | Xem xét |
| Review queue | Review queue | Hàng chờ xem xét |
| Decision | Decision | Quyết định |
| Approve | Approve | Phê duyệt |
| Reject | Reject | Từ chối |
| Audit trail | Audit trail | Nhật ký kiểm toán |
| Citation | Citation detail | Chi tiết trích dẫn |
| Evidence summary | Evidence summary | Tóm tắt kiểm chứng |
| Reason | Reason | Lý do |
| Note | Note | Ghi chú |
| Review Run | Review run | Lượt chạy xem xét |
| Reason Code | Reason | Lý do |
| Reason: evidence | Evidence confirmed | Dữ liệu kiểm chứng đã xác nhận |
| Reason: stale | Stale data | Dữ liệu lỗi thời |
| Reason: duplicate | Duplicate alert | Cảnh báo trùng lặp |
| Reason: conflict | Evidence conflict | Dữ liệu kiểm chứng mâu thuẫn |
| Reason: authority | Outside authority | Ngoài thẩm quyền |
| Reason: degraded | Service degraded | Dịch vụ suy giảm |
| Reason: other | Other | Khác |
| Measured epoch | Measured epoch | Quan trắc thực tế |
| Raw | Raw | Thô |
| Harmonized | Harmonized | Đã chuẩn hóa |
| Walkthrough | Walkthrough | Hướng dẫn |
| Evidence | Evidence | Dữ liệu kiểm chứng |
| Evidence (nav label) | Evidence | Kiểm chứng |
| Briefing | Briefing | Báo cáo phân tích |
| Briefing (nav label) | Briefing | Báo cáo |
| Analysis service | Analysis service | Dịch vụ phân tích |
| Connected | Connected | Đã kết nối |
| Degraded | Degraded | Suy giảm |
| Unavailable | Unavailable | Không khả dụng |
| Tier | Tier | Cấp |
| Bearer token | Bearer token | Mã truy cập |
| Principal | Principal | Danh tính |
| H3 cell | H3 cell | Ô H3 |
| Physics filters | Physics filters | Bộ lọc vật lý |
| Static heat source | Static heat source | Nguồn nhiệt cố định |
| SAA | SAA | SAA |
| Satellite orbits | Satellite orbits | Quỹ đạo vệ tinh |
| Burning Activity Calendar | Burning Activity Calendar | Lịch hoạt động cháy |
| Region | Region | Vùng |
| Mekong | Mekong | Mê Kông |
| Amazon | Amazon | Amazon |
| Period | Period | Giai đoạn |
| Pentad | Pentad | Kỳ 5 ngày |
| Observed | Observed | Quan trắc |
| Modelled | Modelled | Mô hình hóa |
| Interpolated | Interpolated | Ước tính |
| Not scored | Not scored | Chưa chấm điểm |
| Alert | Alert | Cảnh báo |
| Crisis | Crisis | Nguy cấp |
| Selected | Selected | Đã chọn |
| Hover | Hover | Đang trỏ |
| Theme | Theme | Giao diện |
| Dark | Dark | Tối |
| Light | Light | Sáng |
| Language | Language | Ngôn ngữ |
| English | English | Tiếng Anh |
| Vietnamese | Vietnamese | Tiếng Việt |
| HFD unit (events per 100 km² per day) | events/100 km²/day | vụ/100 km²/ngày |
| Design-fixture HFD unit (detections per pentad) | detections/pentad | điểm phát hiện/kỳ |
| HFD | HFD | HFD |
| SFAI | SFAI | SFAI |
| σ (standard deviation) | σ | σ |
| Read-only | Read-only | Chế độ chỉ xem |
| Nadir | Nadir | Tâm quét |
| Edge | Edge | Rìa quét |
| Satellite footprint | Satellite footprint | Vết quét |
| Map lens | Map lens | Khung phóng đại |
| Deduplication | Deduplication | Lọc trùng |
| Equal-area projection | Equal-area projection | Bảo toàn diện tích |
| Phenology clock | Phenology clock | Chu kỳ mùa cháy |
| Baseline / IQR | Baseline / IQR | Đường cơ sở / Khoảng tứ phân vị (IQR) |
| Raw detections | Raw detections | Điểm nóng thô |
| Local only | Local only | Chỉ lưu trên trình duyệt |
| Deterministic tool calls | Deterministic tool calls | Truy vấn công cụ nhất quán |
| Human approval & audit trail | Human approval & audit trail | Phê duyệt thủ công & Nhật ký kiểm toán |

`HFD`, `SFAI`, `Mekong`, `Amazon`, and `σ` are sanctioned domain forms. Every other
row must match this table exactly across catalogs, tests, and e2e specs.

## 7. Accessibility

- Target WCAG 2.2 AA. Body text contrast ≥ 4.5:1 in both themes; non-text marks
  ≥ 3:1. The cyan ring is never the only signal — a crisis cell also carries a
  corner flag and a text status in the readout.
- The calendar is a single `role="application"` region with instructions, one
  focusable element, and a visually hidden `aria-live="polite"` readout. The SVG
  grid is `aria-hidden`; individual cells are not tab stops. Arrow keys move the
  active cell, `Home`/`End` jump pentads, `PageUp`/`PageDown` move five years,
  `Enter`/`Space` keep the active cell and clear hover. This avoids 1,898 tab
  stops and `aria-required-children` failures.
- Focus ring: 2 px `--focus` with 2 px offset. Never remove focus without a
  replacement.
- The Region Globe canvas is `role="img"` with an aria-label and is not a tab stop.
  The two region cards are the accessible selection path; the globe is a pointer
  enhancement.
- The loader is `role="status"`, `aria-live="polite"` and `aria-busy`; it never
  traps focus. It fades in 560 ms after all four steps or the 15 s fallback.
- Review dialogs are `role="dialog"`, `aria-modal`, labelled by their title, close
  on Escape and on the scrim, and lock body scroll. The queue is a table at
  desktop and a card list below `xl`; the run page stacks below `xl`. Decision
  buttons are at least 32 px high and the compact timeline rows at least 24 px.
- Respect `prefers-reduced-motion` and `forced-colors`. In forced colours, keep the
  hatch pattern and the crisis flag shape.

## 8. Data presentation rules

- Period is derived from the artifact (`2001–2026`), never hard-coded.
- Year status derives from cell provenance, not `measured_years`: a year whose cells
  are all provenance `2` is modelled, even when the artifact lists it as measured.
- HFD renders with two significant digits below 1, up to two decimals from 1 to 10,
  and no decimals at or above 10. The design's integer rounding is wrong for values
  in `0.0075–8.0418`.
- SFAI renders with one decimal and an explicit sign (`+2.9σ`, `−1.4σ`). A null
  SFAI renders "not scored".
- Provenance `0` and `1` are observed; `2` is modelled. Only observed cells carry a
  score, an alert ring, or a crisis flag.
- The map plots sampled real MODIS/VIIRS detections for a measured epoch. The
  sample count is shown; no synthetic points reach production. 2026 is modelled
  and is not offered as a measured epoch.
- Every map point carries a physics flag from the harmonization core: SZA night,
  SAA false alarm, static heat source, or a 60-minute overpass duplicate. The four
  filter chips toggle those flags; the points, H3 bins and legend count react
  immediately. The KPI and artifact totals stay the full measured epoch.
- The H3 layer bins the projected points in screen space at Res 4–8 as the map
  zooms, never above the selected analysis grid (Res 7 or 8). Static sources draw
  as purple diamonds; SAA and SZA exclusions as grey crosses; the SAA display zone
  is a hatched ellipse. The exclusion overlay is on by default; the Static &
  SAA button reveals it. Static-source flags are the FIRMS `type` 1–3 subset;
  the core's 12-month persistent-cell registry is not available from the
  archive's same-season 5-day slices. Footprints off also hides the H3 layer because the bins
  are built from those points.
- The map scale bar uses the projection's measured pixels per kilometre, so it
  stays true through zoom and region changes.
- The comparator plots raw annual detections against the MODIS-equivalent
  harmonized series. The trend is an OLS slope over 2001–2024, shown as %/yr.
- The phenology clock plots HFD per pentad for the selected epoch against the
  2001–2025 interquartile range; El Niño 2016 is dashed.
- The Region Globe draws the merged focus-country silhouette for each region on a
  pre-projected 3D Earth. The silhouette is a coverage mask, not a detection. The
  surface is NASA Blue Marble; the country borders are Natural Earth 110m; the
  satellite orbits are decorative and labelled as an illustration.
- Landing entry opens the last measured epoch (2025). The Workbench deep link is
  `/workbench/<id>?epoch=<year>`; `tour=1` opens the walkthrough. The Globe
  header button returns to `/`.
- The Review fixture runs (`RUN-0411`, `RUN-0412`, `RUN-0413`) carry the design's
  facts, brief templates, tool calls, decisions and audit ids. They are sample
  records, not production data; every boundary that becomes HTTP carries
  `TODO(api)`. The queue, run, dialogs and audit read the same store, so a
  decision moves the run from Needs decision to Published or Withheld and adds an
  audit row for the session.
- The Workbench briefing rail is a local service simulator over the same run
  fixture: Up / Degraded / Down, a token handshake (none, rejected, resolving,
  resolved, connected), a run stream (idle, running, paused, done), number chips
  that verify one by one, a rewritten figure, a degraded banner and a retry path.
  The Workbench never records the decision; the paused run hands off to Review.
  Returning with a decision marks the run published or withheld.
- The service chip in the header mirrors the simulator state. The rail footer
  carries the "Demo · simulate service" control and Reset run; it is present at
  every breakpoint, including the mobile briefing overlay.
- The evidence drawer carries a source line and a data table per published
  figure. The walkthrough uses a spotlight on the target
  pane, a progress bar and a figure callout. The globe label shows a tick strip
  and "Click to open" on hover, and the earth peeks toward the hovered region.
- The globe captures the settled frame when the camera arrives, stores it in
  sessionStorage and shrinks it into the map pane on the Workbench. The overlay
  uses the clicked region as its object position, so the transition reads as one
  continuous globe-to-map move. The return trip is still a route change.
- The live analysis stream, review endpoints and audit endpoint are not wired;
  the five remaining `TODO(api)` markers are the replacement checklist; decisions
and audit rows persist through `/api/review/decisions`.
