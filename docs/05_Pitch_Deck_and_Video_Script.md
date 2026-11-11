<p align="center">
  <img src="figures/flare-chronos-logo.png" alt="Flare-Chronos Official Logo" width="220" />
</p>

# 05. Global Judging Pitch Deck & Second-by-Second Main Submission Video Script

**Project:** **Flare-Chronos** — *26-Year Cross-Sensor Harmonized Active Fire Intelligence & Phenology Calendar*  
**Challenge:** 2026 NASA Space Apps Challenge — *Harmonization of MODIS and VIIRS Hot Spots*  
**Related documents:** [01_NASA_SpaceApps_Proposal.md](01_NASA_SpaceApps_Proposal.md) | [02_Cross_Sensor_Harmonization_Spec.md](02_Cross_Sensor_Harmonization_Spec.md) | [GLOSSARY.md](../GLOSSARY.md)

---

## 1. Score-Maximization Strategy Against the 5 NASA Space Apps Global Judging Criteria

| NASA Space Apps Criterion | Judges' Evaluation Focus | **Flare-Chronos**' Exclusive Winning Edge |
| :--- | :--- | :--- |
| **1. Validity (Scientific Validity)** | Is the solution grounded in sensor physics and sound mathematics? Does it have empirical validation? | Validated directly on **$1.609.182$ real hotspots from NASA LANCE FIRMS**; solves the spherical scan-swath equation $\Delta S(\theta)\times\Delta T(\theta)$, the $4\,\mu\text{m}$ radiative observation operator (*Wooster et al., 2005; Sofiev & Kouznetsov, 2026*) and calibrates on **$20.786$ co-incident Aqua–SNPP cell pairs**, reducing the Kolmogorov-Smirnov distribution error by **$69,4\%$** ($D_{\text{KS}}$ from $0.1153 \to 0.0353$). |
| **2. Relevance (Alignment with the Challenge)** | Does it fully solve the MODIS–VIIRS disagreement problem to build a *Burning Activity Calendar*? | Solves all **5 cross-sensor barriers** comprehensively (Footprint Bow-tie, FRP Sensitivity, Confidence Scale & SAA noise, 5-satellite overpass duplication, NRT/Standard SZA flags) to produce a **26 Years × 73 Pentads** matrix with the **$\text{SFAI Z-Score}$** anomaly index. |
| **3. Creativity (Breakthrough Creativity)** | Is the approach new, and does it go beyond simple lat-lon gridding or linear scaling? | Replaces the scalar point with **oriented elliptical area weighting onto the dual-resolution Uber H3 hexagonal grid (Res 7 & Res 8)**, combined with **spatio-temporal fire episode deduplication ($\tau = 60\text{ minutes}$)** and normalization by **effective observation effort $\Omega(y, \phi)$**. |
| **4. Impact (Practical Impact)** | How does the solution help firefighters, forest managers and climate change research when MODIS and Suomi-NPP stop operating? | Prevents policy errors caused by the "+1,311.2% artificial step-jump trap" of raw multi-sensor aggregation; cleanly separates periodic agricultural residue burning seasons from out-of-season El Niño forest fire crises in **Vietnam / the Mekong subregion** and the **Amazon Rainforest**. |
| **5. Presentation (Presentation & Visualization)** | Is the story concise and clear, and is there a working product? | A set of 5 publication-quality scientific figures rendered directly from the Python Engine, plus a synchronized four-pane interface (Footprint Ellipse + H3 Grid + 26×73 Pentad Matrix + Polar Phenology Clock). |

---

## 2. 7-Slide Global Final Pitch Deck Blueprint

### Slide 1 — Title & The 26-Year Sensor Transition Crisis (Context & Mission)
* **Main title:** **FLARE-CHRONOS: Unifying 26 Years of Spaceborne Fire Intelligence Across MODIS & VIIRS**
* **Core message (Hook):** In October 2026, the legendary satellite pair **Terra/Aqua (MODIS)** and **Suomi-NPP (VIIRS)** are reaching the end of their life after more than two decades guarding Earth, and hand the mission to **NOAA-20 and NOAA-21**. But these two sensor generations "speak two different physical languages" — which breaks the 26-year global wildfire record.
* **Visuals:** A timeline diagram of the five-satellite constellation (`2000–2026+`) and the **Flare-Chronos** logo.

### Slide 2 — The Hidden Physics Trap: Why Raw FIRMS Data Misleads Policy (The Unresolved Physics Trap)
* **3 real data shocks from $1.609.182$ NASA FIRMS records:**
  1. **$74,23\times$ pixel-area asymmetry**: A MODIS pixel at the swath edge ($\theta = 55^\circ$) swells to **$9,69\text{ km}^2$** ($4,83 \times 2,01\text{ km}$), **$74,23\text{ times}$** larger than a VIIRS pixel at nadir ($0,13\text{ km}^2$).
  2. **Blindness to small fires at the swath edge**: The daytime MODIS minimum detectable threshold $\text{FRP}_{\text{lim}}$ rises from $8,2\text{ MW}$ to **$41,2\text{ MW}$** at the scan edge, missing $65\text{–}85\%$ of the agricultural and under-canopy fires that VIIRS (`1,15 MW`) captures.
  3. **The artificial $+1.311,2\%$ step-jump trap**: In the Mekong subregion, the actual MODIS fire count in mid-March 2024 ($3.588$ points) is 8.3% lower than in 2005 ($3.914$ points), but a raw sum of 4 sensor streams (`MODIS + S-NPP + NOAA-20 + NOAA-21`) pushes the number to **$55.235$ points** (an artificial increase of $+1.311,2\%$) — close to the 2019 maximum of **$54.171$ points** ($+1.284,0\%$)!
* **Visuals:** Embed [fig1_scan_angle_footprint_physics.png](figures/fig1_scan_angle_footprint_physics.png).

### Slide 3 — Our 5-Stage Physics-Guided Harmonization Engine (5-Step Algorithm Architecture)
* **Diagram of the five core processing blocks of `flare_chronos_core`:**
  1. **Astronomical SZA Unification**: Compute the exact solar zenith angle $\text{SZA}(\phi, \lambda, t_{\text{UTC}}) < 85^\circ$ to unify the `DayNight` flag across `NRT` and `Standard` data.
  2. **Bayesian $P(\text{fire})$ & SAA/Static Filtering**: Convert the `0–100%` scale (MODIS) and the `low/nominal/high` scale (VIIRS) to an empirical probability $P_{\text{fire}} \in [0, 1]$; filter out nighttime proton-spike noise in the **South Atlantic Anomaly (SAA)** ($4,63\%$ of S-NPP data over South America) and static industrial heat sources.
  3. **Oriented Elliptical Footprint $\to$ Dual-Resolution Uber H3**: Integrate 13 quadrature points to allocate the ellipse area $\Delta S \times \Delta T$ along the orbital track angle $\alpha_{\text{track}}$ onto the equal-area hexagonal grid at **H3 Res 7 ($5,16\text{ km}^2$)** and **Res 8 ($0,74\text{ km}^2$)**.
  4. **Two-Stage Radiometric Operator**: Correct the scan-angle detection limit $\text{FRP}_{\text{lim}}(\theta)$ with **Empirical Quantile Mapping (EQM)** on co-incident Aqua–SNPP pairs (`13:30 / 01:30 MLT`).
  5. **Spatio-Temporal Episode Clustering ($\tau = 60\text{ minutes}$) & Effort $\Omega(y, \phi)$**: Merge duplicate afternoon satellite-train overpasses into a single **Fire Episode** and divide by the observation effort factor $\Omega(y, \phi)$.
* **On top of the physics engine, the dual cognitive tier answers the operational question without letting the model invent numbers:**
  - **Reflexive tier** (`System 1`): the **decision model** assigns the required analysis, defines the region and rates urgency with a **calibrated probability** — it runs on the project's own inference node, so it **costs no cloud credits**; it has a **fallback chain** (decision → chat → deterministic extraction), so a run does not depend on any single live service.
  - **Reporting tier**: single-step lookup through Atomic Tools, **no model call**, and **no** use of Domain Diagnostic Tools — fact cards and urgency alerts return in milliseconds.
  - **Deliberative tier** (`System 2`): the chat model **selects** tools itself from the `18` deterministic tools exposed to it (`19` `@tool` functions in total) and writes the explanation itself.
  - **Quantitative verification gate**: every number in the draft briefing is checked against the **verified facts ledger**; a number with no source sends the briefing back for rewrite, and it is never published.
  - **Human approval gate**: a briefing with a field action **pauses the run** for a decision; if rejected, **no** briefing is released.

### Slide 4 — Mathematical Validation on $N = 20,786$ Co-Incident Satellite Pairs (Quantitative Validation Evidence)
* **Empirical results from `run_experiments.py`:**
  - Match $N = 20.786$ equal-area cell pairs observed simultaneously by **Aqua-MODIS** and **Suomi-NPP VIIRS** in the same `13:30 / 01:30 MLT` window.
  - The cumulative distribution distance **Kolmogorov-Smirnov ($D_{\text{KS}}$) falls from $0,1153$ to only $0,0353$ (a $69,4\%$ reduction in distribution error)**.
  - The radiative energy correlation coefficient rises to $R^2 = 0,8048$, removing the $-27,1\%$ MODIS energy-deficit bias at the scan edge (RMSE $141,087 \to 134,077$ MW/cell).
* **Visuals:** Embed [fig3_cross_sensor_frp_quantile_mapping.png](figures/fig3_cross_sensor_frp_quantile_mapping.png) and [fig2_overpass_deduplication_sza.png](figures/fig2_overpass_deduplication_sza.png).

### Slide 5 — Eliminating the 2012/2020/2024 Step-Jump Mirage (26-Year Empirical Comparison)
* **Direct before-and-after comparison through Flare-Chronos:**
  - **Mekong Subregion & Vietnam (`2001–2026`)**: Raw data reports an artificial $14,1\times$ increase (`+1.311,2%`) in 2024; the **Flare-Chronos** harmonized line holds a stable physical baseline (`2024 Index = 90,5`, 9.5% below 2005) and precisely highlights the two **El Niño 2010 ($\text{Index} = 184,9$)** and **El Niño 2016 ($\text{Index} = 133,0$)** drought peaks.
  - **Amazon Rainforest Belt (`2001–2026`)**: Deduplication compression reaches **$5,75\times$** in 2024 (from $112.405$ raw detections to $19.542$ independent fire events, harmonized index `37,7`), faithfully reflecting the 2005, 2010 and 2024 drought cycles.
* **Visuals:** Embed [fig4_regime_shift_elimination.png](figures/fig4_regime_shift_elimination.png).

### Slide 6 — The Harmonized Burning Activity Calendar & Early Warning (Practical Application)
* **Demonstrate the Burning Activity Calendar Matrix (`26 Years × 73 Pentads`) & the $\text{SFAI}$ Anomaly Index:**
  - **In Vietnam & the Mekong Subregion**: Precisely identify the seasonal agricultural residue burning and dipterocarp forest fire window from **Pentad 11 to Pentad 22 (20/02 – 20/04)**; score SFAI only on **observed** cells (Pentad 15 of the 25 Measured Epochs `2001–2025`): 2007 exceeds the cyan-outline display threshold $+2{,}2\sigma$ (measured $+3{,}7\sigma$), while 2010 ($+1{,}8\sigma$) and 2016 ($+0{,}6\sigma$) stay below the cyan outline threshold. The remaining cells are modelled and carry no anomaly tier.
  - **In the Amazon Basin**: Precisely locate the peak fire season from **Pentad 40 to Pentad 56 (15/07 – 07/10)**, with the observed Pentad 47 cell in 2002 reaching $+3{,}8\sigma$ on a 25-year measured baseline (`2001–2025`).
* **On that calendar, the system issues grounded briefings that wait for a human decision:**
  - **Grounded Narrative briefing**: the model writes the narrative in the language of each audience (rangers / forestry leaders / climate scientists), while **every quantitative value is injected by the harness from the ledger** — the model is not allowed to compute any number itself.
  - **Accompanying feed**: every run emits a **typed event stream** (Server-Sent Events) so the interface can show each step: triage → tool call → reasoning → verification → approval → briefing.
  - **Human approval** for every briefing that contains a field action; if rejected, nothing is released, but the decision is still recorded.
* **Real runs, real views:** the bundled server streams the events of each run — the Workbench reads that stream to show triage, tool calls, verification of each number, the briefing, and the **approval button** when a run needs a human decision.
* **Visuals:** Embed [fig5_harmonized_burning_calendar.png](figures/fig5_harmonized_burning_calendar.png).

### Slide 7 — Open-Source Monorepo Architecture & 2027+ Multi-Sensor Roadmap (Open Architecture & Vision)
* **Ready for real deployment:**
  - An industry-standard monorepo (`packages/harmonization-core`, `packages/firms-ingestion`, `apps/benchmark-cli`, `apps/ai-service`, `apps/workbench`), connected directly to the NASA LANCE FIRMS API, with $O(N)$ spatio-temporal clustering that processes $50.000$ hotspots in $< 0,4\text{ seconds}$.
  - **`apps/ai-service`**: a two-tier cognitive LangGraph orchestrator — `15` use cases (`5` System 1 + `10` System 2), `18` deterministic `@tool` functions exposed to the model (`19` `@tool` functions in total), a quantitative verification gate, a human approval gate and an SSE event stream; every tier connects through an explicit **Endpoint Profile** (protocol, endpoint, model, API key), so it does **not** depend on the agent configuration on the user's machine. The test suite has `182` offline tests + `6` live-model tests (22 test files); CI **never** calls a live model.
* **2027+ roadmap:**
  - Extend the observation operator to 10-minute geostationary satellites (**GOES-16/19 ABI, Himawari-9 AHI, Meteosat Third Generation**), $30\text{ m}$ thermal sensors (**Landsat 8/9/Next**) and L/S-band radar data from **NISAR (`GCOV` / `GUNW`)** to measure burned forest biomass through smoke haze.

---

## 3. Second-by-Second Main Submission Video Script (120-Second Main Submission Video)

### 3.1. Official 2-Minute Video Script (120 Seconds — NASA Space Apps Judging Standard)

| Duration | On-Screen Visuals | Voiceover (English) |
| :---: | :--- | :--- |
| **0:00 – 0:18**<br/>*(18 seconds)* | Opens on a global NASA FIRMS map glowing red with hotspots from 2000 to 2026. Quick cut to the red line chart jumping vertically in 2012, 2020 and 2024. | *"For more than a quarter of a century, NASA's MODIS and VIIRS satellites have watched every fire on Earth. But looking at this raw data chart, have wildfires in Southeast Asia and the Amazon really increased 14-fold since 2005? No. That is a dangerous physical illusion created by the sensor generation transition."* |
| **0:18 – 0:42**<br/>*(24 seconds)* | Zoom into **Figure 1**: the huge $4,83 \times 2,01\text{ km}$ MODIS ellipse at the swath edge ($\theta=55^\circ$) covering dozens of $375\text{ m}$ VIIRS points, with the blindness-threshold chart $\text{FRP}_{\text{lim}} = 41,2\text{ MW}$. | *"At the 55-degree edge of the scan swath, one MODIS pixel swells to 9.69 km², 74 times larger than a VIIRS pixel at nadir, and misses every fire below 41 megawatts. At the same time, since 2024, a train of three VIIRS and two MODIS satellites passes over the same fire only minutes apart, counting the same blaze four to five times."* |
| **0:42 – 1:12**<br/>*(30 seconds)* | Shows a live run of the **Flare-Chronos Engine** on $1.609.182$ NASA FIRMS records. Cuts to **Figure 2 & Figure 3**: tightly matched ECDF curves between calibrated MODIS and VIIRS over $20.786$ co-incident Aqua–SNPP cell pairs. | *"We introduce **Flare-Chronos** — a cross-sensor physical harmonization system. Instead of treating hotspots as scalar dots, Flare-Chronos restores the true elliptical geometry by scan angle, allocates radiative energy onto equal-area Uber H3 hexagonal grids, normalizes the solar zenith angle below 85 degrees, filters South Atlantic Anomaly particle noise, and clusters multi-satellite fire episodes. Validated on 20,786 co-incident Aqua and Suomi-NPP observation pairs, Flare-Chronos reduces Kolmogorov-Smirnov distribution error by as much as 69.4%."* |
| **1:12 – 1:34**<br/>*(22 seconds)* | Cut to the live cognitive-tier run: triage event (the decision model returns a **calibrated probability** for the region and urgency level) → tool-call event → event verifying each number against the ledger. | *"On top of that physics core, the dual cognitive tier answers the operational question: the decision model assigns the analysis and defines the region with calibrated probability, the reporting tier answers in milliseconds without calling a model, and the deliberative model chooses its own tools. But the model is never allowed to compute numbers itself: every quantitative value in a briefing is checked against the ledger, and every briefing with a field action must wait for human approval before release."* |
| **1:34 – 1:42**<br/>*(8 seconds)* | Show **Figure 4 & Figure 5**: the **Harmonized Burning Activity Calendar (`26 Years × 73 Pentads`)** matrix for the Mekong subregion/Vietnam and the Amazon Rainforest. Zoom into the cyan-outlined cells among observed cells: Mekong 2007 ($+3{,}7\sigma$) and Amazon 2002 ($+3{,}8\sigma$). | *"The result is a **26-Year Harmonized Burning Activity Calendar** by 5-day pentad. In Vietnam and the Mekong subregion, the artificial +1,311.2% jump disappears entirely, revealing the agricultural residue burning window from Pentad 11 to 22; only observed cells above the SFAI +2.2 sigma threshold (Mekong 2007 at +3.7 sigma, Amazon 2002 at +3.8 sigma) receive the cyan emergency-warning outline; modelled cells are not assigned an anomaly tier."* |
| **1:42 – 2:00**<br/>*(18 seconds)* | Return to the interactive map interface + the open-source Monorepo structure on GitHub. Ends with the mission message. | *"As MODIS and Suomi-NPP close their historic mission in 2026, **Flare-Chronos** ensures humanity's thermal data record remains unbroken — giving firefighters and climate scientists an accurate compass for the next decade."* |
