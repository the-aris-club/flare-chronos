# Prompt for Claude Design — Native Evidence Figures

Rework the Evidence drawer so the UI draws the scientific figures itself. Do not use PNGs or image slots for the five figures. Keep the existing mock data, sample runs, layout and palette. The only image allowed in the drawer is the logo.

The UI-native figures are the app view. The published PNGs remain available only as “Download published figure” links for the paper and the judges; they are not the primary display.

## Why

- The same figure must work in dark and light, at 1440, tablet and mobile.
- The numbers must stay tied to the data, not frozen in a bitmap.
- The calendar, comparator and polar clock are already native; reuse them instead of duplicating them as images.
- A native figure can expose the data table and an accessible summary; a PNG cannot.

## Data strategy

Design with sampled data. Do not wait for a full empirical export in this pass.

- Put every series in one `figureData` object. The chart components read `data` / `series`; the SVG paths are generated from those arrays, never hand-drawn.
- Use the sampled values in this brief for layout. Keep the published summary values exact: 9.69 km², 74.23×, KS 0.1166 → 0.0348, 70.2%, N = 11,553, +1,324%, +714%.
- Use one source note per figure: “Sample data · full series at implementation.” Do not add a warning badge to every chart.
- Later implementation replaces `figureData` with the exported calendar and empirical artifacts. The chart components must not change.
- The prototype banner “Prototype · synthetic data except published figures” stays.

## Figure set

Use the canonical five figures. Drop the static “phenology” slot; the Polar Phenology Clock is the phenology view.

### Figure 1 — Footprint physics

- Two panels.
- A: footprint area (km²) vs scan angle (0–55°). MODIS curve in amber, VIIRS curve in blue. Mark 0°, 31.7°, 44.9°, 55°. Reference lines for H3 Res 7 (5.16 km²) and Res 8 (0.74 km²). End labels: MODIS edge 9.69 km², VIIRS edge 0.62 km². Use 12–16 sampled points per curve; no full empirical scatter is needed.
- B: FRP limit (MW) vs scan angle. MODIS day and night curves, VIIRS day curve; shaded “unobserved sub-pixel fire zone”. Annotate 8.2 → 41.2 MW (MODIS day), 3.7 → 38.6 MW (MODIS night), 1.15 → 3.4 MW (VIIRS). Use the same sampled angle grid as panel A.
- Caption: “At 55°, a MODIS pixel covers 9.69 km², 74.23× a VIIRS nadir pixel; the detection limit rises from 8.2 to 41.2 MW.”
- `aria-label`: “MODIS footprint area reaches 9.69 square kilometres at 55 degrees, 74 times VIIRS; the detection limit rises to 41.2 megawatts.”

### Figure 2 — Overpass deduplication and effort

- Two panels.
- A: satellites and effective observation effort Ω vs year 2000–2026. Step lines; annotate 2002 Aqua, 2012 Suomi-NPP, 2018/20 NOAA-20, 2024 NOAA-21. Satellites 1 → 5; Ω 1.0 → 2.0.
- B: grouped bars, raw detections vs deduplicated episodes for six 5-day windows: 33,017 / 16,304; 43,342 / 22,847; 42,869 / 21,065; 50,988 / 22,950; 33,484 / 9,351; 112,405 / 19,542. Annotate the multipliers 2.03×–5.75×. The arrays are small; no sampling is needed.
- Caption: “Raw counts inflate with sensor multiplicity; deduplicated episodes grow far less.”
- `aria-label`: “Raw detections rise in steps as satellites are added; deduplicated episodes grow much more slowly.”

### Figure 3 — Coincident-pair calibration

- Two panels.
- A: parity scatter of MODIS vs VIIRS FRP with the 1:1 line. Use about 40–60 sampled points; show R² 0.733 → 0.764 and RMSE 149.1 → 140.2 MW.
- B: ECDF curves for raw MODIS (amber), VIIRS target (blue), harmonized (teal). Use about 24–40 sampled points per curve. Show KS 0.1166 → 0.0348 and the 70.2% reduction; N = 11,553.
- Caption: “Coincident-pair calibration reduces the KS distance by 70.2%.”
- Do not invent density beyond the sampled points. The source note says “Sample data · full series at implementation.”

### Figure 4 — Regime-shift elimination

- Two panels: Mekong and Amazon.
- Raw vs harmonized activity index (2005 = 100) from 2001 to 2026. Raw in orange, harmonized in teal.
- Mark satellite additions at 2012, 2018/20 and 2024; mark measured epochs and interpolated years distinctly.
- Raw labels: +1,324% Mekong; +714% Amazon. Harmonized series stays flat except the real El Niño peaks.
- Reuse the existing comparator data and line colours. The yearly series 2001–2026 is small; no sampling is needed.
- Caption: “The raw step jumps vanish after harmonization; the harmonized series is flat apart from real drought peaks.”

### Figure 5 — Burning Activity Calendar

- Reuse the existing calendar component in a compact read-only form.
- 26 years × 73 pentads. Observed cells solid, modelled cells hatched. SFAI only on observed cells; cyan outline at ≥ +2.2σ; crisis legend at +2.5σ.
- Do not aggregate to 12 monthly columns. Use the existing calendar data; no sampling is needed.
- Caption: “26 years × 73 pentads; SFAI shown for observed cells only.”

### Phenology

Use the existing Polar Phenology Clock. If it appears in the Evidence drawer, make it a sixth card and label it “Derived from the 26-year calendar”. Do not create a static phenology image.

## Review map thumbnail

Replace the `review-map-uc22` image slot with a native `MiniMap` SVG.

- Simplified Mekong outline.
- Ellipse at 12.4° azimuth, 4.83 km scan × 2.01 km track.
- Draw the ellipse now. Add the 13 H3 Res 8 cells only when the cell geometry is supplied; do not fake cell IDs.
- If the exact cells are not supplied, caption the card “Schematic · H3 search area, Mekong 2024” and do not imply the 13 cells are drawn.
- Keep the 132 px height and the map aspect ratio.
- No PNG and no iframe.

## Layout

- Evidence drawer: full-width panel, minimum 900 px at 1440.
- Two-column grid. The two-panel figures span both columns; the calendar spans both columns; the phenology clock can be one column.
- Each figure card: title, subtitle, chart, caption, source note, and a “View data” toggle.
- On tablet, keep two columns if the chart remains legible; otherwise one column. On mobile, one column.
- Charts must never shrink below a readable axis size; allow the drawer to scroll.

## Visual rules

- Reuse the Workbench palette: raw orange, harmonized teal, MODIS amber, VIIRS blue; cyan only for the Severe Anomaly Outline; neutral text and grid.
- Tabular numerals for axes and values; IBM Plex Mono for numbers, IBM Plex Sans for labels.
- Legends inside the plot; units on every axis; zero line where relevant.
- No decorative glow, no 3D, no chart animation. Respect `prefers-reduced-motion`.
- Dark and light themes; contrast at least 4.5:1; never colour alone.

## Accessibility

- Each chart has `role="img"` and an `aria-label` that states the finding, not just “chart”.
- Provide a visually hidden summary and a “View data” table with the plotted values.
- Hover tooltips are optional; the axes and values must be readable without hovering.
- Keyboard focus reaches the “View data” toggle and the table.

## Data

- Design with the sampled arrays in this brief. The full empirical export is not required for this pass.
- Keep the published summary values exact: 9.69 km², 74.23×, KS 0.1166 → 0.0348, 70.2%, N = 11,553, +1,324%, +714%.
- Every chart is data-driven: `figureData` → chart component → SVG. Later implementation swaps `figureData` for the exported calendar and empirical artifacts without changing layout.
- The published PNGs stay as “Download published figure” links; do not render them as the primary chart.
- Do not invent numbers beyond the sample arrays and the published summaries.

## Do not

- Do not use image slots for the five scientific figures.
- Do not attach the five PNGs as the primary figures.
- Do not add a static phenology PNG.
- Do not change the mock KPI strip, the reviewer flow, or the decision records.
- Do not add a chart library if the existing SVG/React components are enough.
