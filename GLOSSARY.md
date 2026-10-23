<p align="center">
  <img src="docs/figures/flare-chronos-logo.png" alt="Flare-Chronos Official Logo" width="220" />
</p>

# Flare-Chronos

**Full name (abbreviation note):** *Fire Long-term Archive Resolution & Cross-sensor Harmonization for Operational Near-real-time Observation System*

Cross-sensor harmonization of multi-decadal satellite active fire observations (MODIS and VIIRS) into a unified, physics-calibrated Burning Activity Calendar.

## Name & Acronym Meaning

- **FLARE** — evokes the image of a flame (ngọn lửa): the fire signal the system detects, harmonizes, and tracks.
- **CHRONOS** — emphasizes the core deliverable, the *Burning Activity Calendar* (Lịch hoạt động cháy), spanning more than 25 years of active-fire history (2000–2026+).
- The system connects and harmonizes data from the **NASA FIRMS** (Fire Information for Resource Management System) archive and near-real-time streams into one sensor-invariant, physics-calibrated record.

> Reusable one-liner for reports, presentations, and proposals:
> "Flare-Chronos — Fire Long-term Archive Resolution & Cross-sensor Harmonization for Operational Near-real-time Observation System: a 26-year, cross-sensor (MODIS + VIIRS) harmonized Burning Activity Calendar built on NASA FIRMS data."

## Language

### Sensor & Radiometric Physics

**Thermal Detection**:
A single raw active-fire or thermal-anomaly observation reported by a spaceborne radiometer during an orbital overpass.
_Avoid_: Fire point, hotspot row, raw fire

**Instantaneous Footprint**:
The actual ground-projected elliptical area ($\Delta S \times \Delta T$, in $\text{km}^2$) swept by a detector element at its instantaneous scan angle $\theta$ and orbital track azimuth $\alpha_{\text{track}}$.
_Avoid_: Pixel size, point buffer, nominal resolution

**Bow-Tie Distortion**:
The geometric expansion and scan-to-scan overlap of detector footprints toward the swath edges caused by Earth curvature and off-nadir viewing geometry.
_Avoid_: Edge stretching, pixel blur

**Aggregation Zone**:
One of the three discrete across-track scan-angle intervals on the VIIRS instrument ($0^\circ\text{–}31.72^\circ$, $31.72^\circ\text{–}44.86^\circ$, $44.86^\circ\text{–}56.28^\circ$) where native detectors are aggregated $3:1$, $2:1$, or $1:1$ to constrain footprint growth.
_Avoid_: Scan band, swath sector

**Fire Radiative Power (FRP)**:
The instantaneous rate of radiant heat output emitted by an active fire (measured in megawatts, $\text{MW}$), retrieved from middle-infrared ($4\,\mu\text{m}$) excess spectral radiance above the non-fire background.
_Avoid_: Fire intensity, fire temperature, heat energy

**Detection Limit ($\text{FRP}_{\text{lim}}$)**:
The minimum Fire Radiative Power required for a sub-pixel fire to exceed the contextual background threshold at a given Instantaneous Footprint and Solar Zenith Angle.
_Avoid_: Sensitivity cutoff, minimum brightness

**Observation Operator**:
The physical transfer function relating the true sub-pixel radiative flux distribution on the ground to the truncated, footprint-modulated FRP distribution observed by a specific sensor at scan angle $\theta$.
_Avoid_: Scaling factor, correction multiplier

### Spatio-Temporal Harmonization

**Solar Zenith Angle (SZA)**:
The astronomical angle between the local zenith at the Thermal Detection location and the center of the solar disk at the exact UTC acquisition time, where $\text{SZA} < 85^\circ$ defines daytime radiative regime.
_Avoid_: Day/night flag, local time indicator

**Detection Probability ($P_{\text{fire}}$)**:
The unified calibrated probability in $[0, 1]$ that a Thermal Detection represents a true vegetation or biomass fire rather than solar glint, cosmic-ray noise, or a static industrial heat source.
_Avoid_: Confidence score, quality flag

**South Atlantic Anomaly (SAA)**:
The geomagnetic field depression region ($11^\circ\text{E–}110^\circ\text{W}, 7^\circ\text{N–}55^\circ\text{S}$) where trapped high-energy protons induce spurious nighttime middle-infrared spikes in satellite detectors.
_Avoid_: Atlantic noise zone

**Static Thermal Source**:
A persistent non-biomass heat emitter—such as a gas flare, steel mill, cement kiln, refinery, or active volcano—that repeatedly triggers Thermal Detections within the same spatial cell across seasons.
_Avoid_: False fire, stationary hotspot

**Static Source Registry**:
The versioned set of Iso-Area Cells (Resolution 8) that the archive shows to be hot in nearly every month of the year, derived from the detections themselves and passed into harmonization so that a Static Thermal Source is rejected rather than counted as a Fire Episode.
_Avoid_: Blocklist, exclusion mask, static cell list

**Fire Episode**:
A unique, physical burning event reconstructed by clustering spatially overlapping and temporally proximate Thermal Detections acquired across multiple satellite overpasses within a single diurnal window.
_Avoid_: Deduplicated point, merged hotspot, fire cluster

**Effective Observation Effort ($\Omega$)**:
The normalized diurnal sensing capacity of the active satellite constellation at a given epoch and latitude, accounting for satellite count, swath overlap, and orbital revisit spacing.
_Avoid_: Overpass count, satellite multiplier

**Co-Incident Overpass Pair**:
Simultaneous or near-simultaneous observations of the same Iso-Area Cell by Aqua-MODIS and Suomi-NPP VIIRS within their shared $\sim 13\text{:}30 / 01\text{:}30\text{ MLT}$ orbital plane during the 2012–2026 overlap era.
_Avoid_: Matched points, overlapping passes

### Spatial Grid & Phenology Calendar

**Iso-Area Cell**:
A geodesic hexagonal cell on the Uber H3 discrete global grid (Resolution 7 for regional phenology, Resolution 8 for tactical field resolution) onto which Instantaneous Footprints are fractionally allocated.
_Avoid_: Grid square, pixel bin, lat-lon box

**Pentad**:
A standard 5-day climatological time step ($73\text{ pentads per year}$) used to structure seasonal fire phenology without calendar-month length distortion.
_Avoid_: 5-day bin, mini-week

**Harmonized Fire Density (HFD)**:
The sensor-invariant, effort-normalized rate of Fire Episodes per $100\text{ km}^2$ per day, calibrated to a unified VIIRS-equivalent reference baseline across the 2000–2026+ record.
_Avoid_: Normalized fire count, adjusted hotspot density

**Harmonized Radiative Flux (HRF)**:
The sensor-invariant areal density of Fire Radiative Power (in $\text{MW}\cdot\text{km}^{-2}$) allocated across Iso-Area Cells after Observation Operator and Quantile Mapping calibration.
_Avoid_: Calibrated FRP, total heat flux

**Standardized Fire Anomaly Index (SFAI)**:
The robust seasonal Z-score measuring how many median absolute deviations (or standard deviations) a Pentad's Harmonized Radiative Flux departs from its 25-year climatological baseline for that exact Pentad.
_Avoid_: Fire risk score, anomaly percent

**Burning Activity Calendar**:
The two-dimensional phenological matrix ($\text{Year} \times \text{Pentad}$) and polar seasonal clock displaying Harmonized Fire Density, Harmonized Radiative Flux, and Standardized Fire Anomaly Index for an Area of Interest.
_Avoid_: Fire heatmap, hotspot timeline

**Anomaly Tier**:
The operational severity band of a Standardized Fire Anomaly Index value, assigned in five ordered bands — QUIET ($< -0.5$), BASELINE ($-0.5 \le \text{SFAI} < 1.0$), ELEVATED ($1.0 \le \text{SFAI} < 1.75$), SEVERE ($1.75 \le \text{SFAI} < 2.5$), and CRISIS ($\ge 2.5$). SEVERE mobilises patrols; CRISIS raises an out-of-season crisis alarm.
_Avoid_: Risk level, alert level, severity score, crisis threshold

**Measured Epoch**:
A year for which the archive holds a real NASA FIRMS slice set — the harmonized count for that year is computed from observed detections. Eleven of the twenty-six Mekong years and nine of the twenty-six Amazon years are Measured Epochs.
_Avoid_: Real year, hard data, ground truth, anchor year

**Interpolated Year**:
A year with no archived slice set, whose annual scale is modelled from the observed MODIS-only count and the region's empirical seasonal envelope. The interpolation is deterministic but it is a model, not an observation, and published documents mark these years as such.
_Avoid_: Estimated year, synthetic year, filled year, projection

**Severe Anomaly Outline**:
The cyan frame drawn on a Burning Activity Calendar cell whose Standardized Fire Anomaly Index reaches the display threshold of $+2.2\sigma$. It is a rendering convention for a *display* threshold, deliberately below the CRISIS Anomaly Tier so the calendar highlights severe anomalies before a crisis alarm is raised.
_Avoid_: Crisis anomaly, crisis outline, alarm outline, threshold

### Visual Communication Artifacts

**Scientific Figure**:
A publication-grade chart rendered directly from the empirical results by `benchmark_cli.figure_renderer`, carrying measured values, units and axis labels. It is a build artifact — regenerated from code, never hand-edited, never re-labelled for narrative effect.
_Avoid_: Chart, plot, graph, illustration

**Narrative Asset**:
A hand-authored visual — motion graphic, 3D scene, title card or map animation — produced for the pitch video to explain the science. It may depict a concept truthfully but it never substitutes for a Scientific Figure, and it is never labelled as a measurement.
_Avoid_: Figure, chart, data viz, screenshot, mock-up

**Workbench**:
The Flare-Chronos interactive analysis surface — the Deck.gl / MapLibre application specified in `docs/04_UI_UX_Burning_Calendar_Wireframe.md` that renders the harmonization engine's output on demand rather than pre-rendering it. Specified but not yet implemented.
_Avoid_: Dashboard, UI, app, interactive demo, live visualization

**Main Submission Video**:
The 120-second primary pitch deliverable for NASA Space Apps, cut to the shot script in `docs/05_Pitch_Deck_and_Video_Script.md` §3.1.
_Avoid_: Demo, promo, trailer, explainer

**Pitch Deck**:
The 7-slide presentation mirroring the `docs/05_Pitch_Deck_and_Video_Script.md` §2 blueprint — the still counterpart of the Main Submission Video, carrying the same argument in slide form.
_Avoid_: Slide deck, slides, presentation, deck

Rendered deliverables, their release tags, and the naming convention they share are indexed in [`docs/media/SOURCES.md`](docs/media/SOURCES.md).
