# Prompt for Claude Design — Flare-Chronos Workbench

Paste everything below the line into Claude Design. Attach `docs/figures/flare-chronos-logo.png` and, optionally, `docs/04_UI_UX_Burning_Calendar_Wireframe.md`. The reviewer surfaces that follow a finished run are specified in the addendum `docs/design/workbench-reviewer-ui-prompt.md`; paste that addendum after this prompt.

---

## Task

Design the **Flare-Chronos Workbench**: a single-mode, data-dense analysis web app that proves a scientific claim to NASA Space Apps judges in 2–3 minutes. Deliver high-fidelity screens for desktop (1440×900) with a tablet and mobile adaptation of the key screens, in dark and light themes, plus a small component sheet.

## The claim the design must make obvious

Raw NASA FIRMS fire detections rise about 14× between 2000 and 2024 only because more satellites were added (MODIS, then Suomi-NPP 2012, NOAA-20 2018/2020, NOAA-21 2024). After physics-guided harmonization the series is flat except for real drought peaks (El Niño 2010 and 2016). A viewer must see "the raw sum jumps, the harmonized line does not" without reading anything.

## Audience

Primary: international judges, non-specialists, no setup. Secondary: forest rangers, forestry leaders, climate scientists. Tone: scientific, sober, trustworthy. Not a marketing site, not a game.

## Screens

1. **Region Globe (landing).** A full-screen, slowly rotating 3D Earth (see assets below). Two regions are marked: Mekong sub-region and Vietnam (BBOX 100.0–109.5°E, 11.0–23.5°N) and the Amazon fire arc (BBOX 62–50°W, 14–4°S). Hover shows the region name and its number of Measured Epochs (11 of 26 for Mekong, 9 of 26 for Amazon). Click flies the camera in and switches to the flat map. Any satellite-orbit animation on the globe is a **Narrative Asset** and must carry a small "Illustration, not a measurement" label.
2. **Workbench (main).** Layout from the wireframe:
   - Header: Flare-Chronos wordmark, region selector, period 2000–2026, grid (H3 Res 7 or 8), physics filter toggles (SZA < 85°, SAA night noise, static heat sources, 60-minute de-duplication), a language toggle (English / Tiếng Việt), a Globe button, and a connection status chip for the analysis service.
   - Map pane (flat, equal-area-faithful): oriented elliptical footprints for MODIS and VIIRS pixels, H3 hex layer, static and SAA overlay in purple/grey. A year picker lists **Measured Epochs only**, each showing its date window.
   - KPI strip: Raw Detections → Fire Episodes → SFAI.
   - Burning Activity Calendar matrix: 26 years × 73 pentads, three metric modes (HFD, HRF, SFAI). Observed cells and modelled cells are visibly different (for example solid vs hatched). Only Observed cells show SFAI. Cells at or above +2.2σ get a cyan **Severe Anomaly Outline**.
   - Polar Phenology Clock: 73 pentads, grey 25-year IQR band, orange dashed El Niño year, teal current year.
   - Before/After comparator: raw unharmonized sum (red-orange, step jumps in 2012, 2020, 2024) vs harmonized series (teal, flat baseline).
   - Evidence drawer: scan-angle asymmetry (MODIS edge pixel 9.69 km² vs VIIRS nadir 0.13 km², 74.23×), coincident-pair calibration (N = 11,553; KS 0.1166 → 0.0348), and the five scientific figures.
3. **Briefing and Sign-off panel.** One surface with three states, not a finished timeline that happens to contain an approval row.

   **Run state.** A vertical run timeline: classify (region, urgency with calibrated probability) → tool calls → reasoning → verification → approval → briefing. Show which classifier answered and the current degradation tier. Rows are expandable: a tool row reveals its arguments and returned quantity; a reasoning row reveals the text; a verification row reveals the Verification Table. Every number carries a status chip: verified, being rewritten, or no source. The briefing is published only when all numbers are verified.

   **Waiting state (sign-off gate).** When the run needs a human decision, the timeline stops at "Approval — Waiting" and must not render a "Done" approval row before a decision exists. A Decision Card appears above the proposed briefing and contains: the question ("Authorize the operational action proposed by UC-S1.4?"), the signed-in principal and role, a required reason field, and Approve / Reject buttons. A **Decision Basis** strip sits above the buttons and states what the reviewer is checking: the proposed action, region and time window, verified N/N numbers, unresolved citations (must be 0), unverified numbers (must be 0), self-correction retries, synthesis mode, classifier confidence source (calibrated vs self-reported), and the degradation tier. Rejection reasons are structured (stale NRT, duplicate alert, evidence conflict, action outside authority, degraded service) plus free text; the reason is written to the audit record. The proposed briefing is shown below the card as a read-only draft — the exact text that would be published — with its Verification Table one click away, so the reviewer authorizes the text, not a summary. The panel states that the run is paused and survives a reconnect.

   **Result state.** After a decision, or after a non-sign-off run, the timeline collapses to a Result Summary with a persistent primary action **View full briefing**. It opens a full-height dialog (right-side sheet on desktop) containing:
   - the full briefing text with the audience switch (rangers / forestry leaders / climate scientists) and the stakeholder header (tier, cognitive path, System 1 / System 2 models, synthesis mode);
   - the Verification Table: one row per number — value, unit, source tool, source field, status (verified / rewritten / no source), and the check result. Each row is a link to a **Citation Detail** popover with the sentence where the number appears, the rendered value, the fact key, the source tool, the raw value the tool returned, the unit, the provenance tag, and the verifier's verdict;
   - the Sign-off Decision record: decision, principal, UTC timestamp, reason, and the released state;
   - the run's event log and audit id.

   Approved → **Published**, with the decision stamp on the briefing. Rejected → **Withheld**: no briefing text at all, the decision record remains, and the summary says the decision was recorded. A non-sign-off run → **Published** with no decision record. The dialog must remain reachable after the run ends and after a reload of the completed run.
4. **Connect and unavailable states.** A Connect step to paste a bearer token, showing the resolved principal and role. If the service is down, the panel shows a clear unavailable state with the reason and degradation tier, never a placeholder briefing. The data surfaces stay fully usable.
5. **Demo Walkthrough.** A six-step guided overlay with a progress indicator and an Exit-to-explore control: (1) the footprint trap, 74× asymmetry; (2) the +1,324% raw illusion; (3) harmonization fixes it, KS 0.1166 → 0.0348; (4) the calendar, with the cyan outline on 2007 (+2.9σ); (5) a real briefing run; (6) real sign-off. Steps 5 and 6 must tolerate real model latency (progress states, streaming text).

## Non-negotiable honesty rules (design them visibly)

1. Interpolated Years and modelled cells are always visibly marked.
2. SFAI and the Severe Anomaly Outline appear only on Observed cells.
3. The +2.2σ **display** threshold and the +2.5σ **crisis** threshold are labelled distinctly.
4. Illustrations (orbits, 3D scenes, animations) never look like Scientific Figures and are labelled as illustrations.
5. Briefing numbers always show their verification status.
6. An approval row is never shown as Done without a recorded decision, and a Withheld run never shows briefing text.

## Visual direction

- Dark-first, deep space blue-black, with fire accents (amber to red) for activity and teal for the harmonized signal. Cyan is reserved for the Severe Anomaly Outline. Purple/grey is reserved for filtered static and SAA sources.
- Data-dense and typographically precise. Tabular numerals, restrained motion, no decorative glow on data.
- Colour-blind-safe sequential scale for HFD and HRF, a diverging scale for SFAI; legends always visible.
- Accessible: keyboard navigation for the matrix, contrast of at least 4.5:1, never colour alone to encode status.
- Use the attached logo; keep the wordmark compact.

## 3D Earth assets

Primary (verified, direct download, 18.05 MB, glTF binary):
- NASA Earth with Clouds 3D model, credit NASA Visualization Technology Applications and Development (VTAD): https://assets.science.nasa.gov/content/dam/science/psd/solar/2023/09/e/EarthClouds_1_12756.glb?emrc=6ae590cb3bbdc
- Page: https://science.nasa.gov/resource/earth-with-clouds-3d-model
- USDZ (957.57 KB, for quick previews): https://assets.science.nasa.gov/content/dam/science/psd/solar/2023/09/e/EarthClouds_1_12756.usdz

Fallback, if you prefer a plain textured sphere: NASA Blue Marble imagery collection (colour Earth textures, several resolutions): https://science.nasa.gov/earth/earth-observatory/collections/blue-marble (the older address visibleearth.nasa.gov/collection/1484/blue-marble redirects here). Wrap a chosen equirectangular texture on a UV sphere.

Licence note: the model page states no licence. Keep the credit line "Earth model: NASA VTAD" visible in the design and check NASA's usage guidelines before redistributing the files.

## Deliverables

- Screens 1–5 above in dark and light, desktop plus tablet and mobile for screens 2 and 3.
- A component sheet: calendar cell states (observed, modelled, anomaly-outlined), verification chips, run-timeline events, connection and degradation banners, Approve/Reject card (waiting, approved, rejected), the briefing result dialog (published and withheld), the Verification Table row, and the walkthrough step card.
- Notes on interaction and motion for the globe-to-map transition.
