# Detailed Reference of Symbols, Formulas & Terms (Symbols, Formulas & Terms Reference)

**Project:** **Flare-Chronos** — *26-Year Cross-Sensor Harmonized Active Fire Intelligence & Phenology Calendar*
**Purpose:** A detailed explanation of each symbol, formula, and term that appears in the project documents (`docs/*`, `GLOSSARY.md`, `exports/PROPOSAL.md`, `exports/REPORT.md`, `exports/export_pdf.py`, source code `packages/*`, `apps/*`, `src/*`, `tests/*`).
**Audience:** Scientists, engineers, judges, and anyone who needs a quick lookup of the meaning of a symbol or term.

> **Reading conventions:** Italic symbols ($\theta$) are mathematical variables; `monospace` symbols are function or variable names in the source code. Units follow after a comma. Implementation references use the form `file.py::function_name`.

---

## 1. Notation Conventions

| Convention | Meaning | Example |
| :--- | :--- | :--- |
| Lowercase Greek letters ($\theta, \phi, \lambda, \omega, \delta, \gamma, \tau, \kappa, \alpha, \beta, \sigma$) | Physical quantity / angle / parameter | $\theta$ = scan angle |
| Uppercase Latin letters ($A, R, N, P, D, L, T, S$) | Set, area, count, probability, distance | $A_p$ = pixel area |
| Subscripts ($p, k, i, j, y$) | Element / year / period index | $E_k$ = $k$-th fire event |
| Hat notation ($\hat{X}, \tilde{X}, \bar{X}, \widetilde{X}$) | Estimate / correction / mean | $\widehat{\text{FRP}}_{\text{VIIRS-eq}}$ = VIIRS-equivalent corrected FRP |
| Delta notation ($\Delta X$) | Difference / magnitude of change | $\Delta S$ = across-track pixel width |
| $|x|$ | Absolute value of $x$ | $|\theta|$, for example $|-3| = 3$ |
| $\max(a,b)$, $\min(a,b)$ | Max/min function | $\max(0, \cos\text{SZA})$ |
| $\text{clip}(x, lo, hi)$ | Clamp the value to $[lo, hi]$ | $\text{clip}(\Delta T_{45}-18, -10, 40)$ |
| $\ln$, $\log$ | Natural logarithm | $\ln(\max(1, A_p))$ |
| $\arccos$, $\arcsin$, $\arctan$ | Inverse trigonometric functions | $\arccos(\cos\text{SZA})$ |
| $\sum$, $\prod$ | Sum / product | $\sum_{E_k} \text{FRP}$ |
| $\text{Median}$, $\text{MAD}$, $\text{Std}$ | Median / median absolute deviation / standard deviation | $\text{MAD}_{y'}(\text{HRF})$ |
| $F^{-1}$ | Inverse quantile function | $F_{\text{VIIRS}}^{-1}(\cdot)$ |
| $\mathbb{E}$ / $\bar{X}$ | Expectation / sample mean | $\bar{N}_{\text{VIIRS}}$ |

---

## 2. Physical & Orbital Constants

| Symbol | Value | Unit | Meaning | Location |
| :--- | :--- | :--- | :--- | :--- |
| $R_e$ | $6378.137$ | km | Earth radius (WGS-84 semi-major axis) | `geometry_h3.py::R_EARTH_KM` |
| $h_{\text{MODIS}}$ | $705$ | km | Nominal orbital altitude of MODIS (Terra/Aqua) | `geometry_h3.py::MODIS_ALTITUDE_KM` |
| $r_{\text{MODIS}}$ | $7083.137$ | km | MODIS orbital radius = $R_e + h_{\text{MODIS}}$ | `geometry_h3.py::MODIS_ORBIT_RADIUS_KM` |
| $s_{\text{MODIS}}$ | $0.0014184397$ | rad/sample | MODIS sampling angular step (1 km nominal) | `geometry_h3.py::MODIS_SAMPLING_RAD` |
| $\theta_{\max,\text{MODIS}}$ | $55.0$ | deg | Maximum MODIS scan angle | `geometry_h3.py::MODIS_MAX_SCAN_DEG` |
| $h_{\text{VIIRS}}$ | $829$ | km | Nominal orbital altitude of VIIRS (S-NPP/JPSS) | `geometry_h3.py::VIIRS_ALTITUDE_KM` |
| $r_{\text{VIIRS}}$ | $7207.137$ | km | VIIRS orbital radius | `geometry_h3.py::VIIRS_ORBIT_RADIUS_KM` |
| $s_{\text{native},S}$ | $0.0001458$ | rad | Native VIIRS across-track detector angular step (~121 m) | `geometry_h3.py::VIIRS_NATIVE_SCAN_RAD` |
| $s_{\text{native},T}$ | $0.0004340$ | rad | Native VIIRS along-track detector angular step (~360 m) | `geometry_h3.py::VIIRS_NATIVE_TRACK_RAD` |
| $\theta_{z1}$ | $31.72$ | deg | VIIRS Zone 1 limit (3:1 aggregation) | `geometry_h3.py::VIIRS_ZONE1_MAX_DEG` |
| $\theta_{z2}$ | $44.86$ | deg | VIIRS Zone 2 limit (2:1 aggregation) | `geometry_h3.py::VIIRS_ZONE2_MAX_DEG` |
| $\theta_{z3}$ | $56.28$ | deg | VIIRS Zone 3 limit (1:1 aggregation, max swath) | `geometry_h3.py::VIIRS_ZONE3_MAX_DEG` |
| $i_{\text{Terra/Aqua}}$ | $98.2$ | deg | MODIS orbital inclination | `geometry_h3.py::compute_orbital_track_azimuth` |
| $i_{\text{S-NPP/JPSS}}$ | $98.7$ | deg | VIIRS orbital inclination | `geometry_h3.py::compute_orbital_track_azimuth` |
| $\sigma_{\text{SB}}$ | $5.6704\times10^{-8}$ | W·m⁻²·K⁻⁴ | Stefan-Boltzmann constant | `docs/02` §3.1 |
| $a$ (Planck coeff.) | $\approx 3.0\times10^{-9}$ | W·m⁻²·sr⁻¹·μm⁻¹·K⁻⁴ | Empirical spectral constant of the sensor (4 μm) | `docs/02` §3.1 |
| $\lambda_{\text{MODIS},4}$ | $\approx 3.96$ | μm | MODIS middle-infrared channel (Ch21/22) | `domain.py::ThermalDetection.bright_t4_k` |
| $\lambda_{\text{VIIRS},4}$ | $3.55$–$3.93$ | μm | VIIRS I-4 channel | `domain.py::ThermalDetection.bright_t4_k` |
| $\lambda_{\text{MODIS},11}$ | $\approx 11.0$ | μm | MODIS long-wave channel (Ch31) | `domain.py::ThermalDetection.bright_t5_k` |
| $\lambda_{\text{VIIRS},11}$ | $10.5$–$12.4$ | μm | VIIRS I-5 channel | `domain.py::ThermalDetection.bright_t5_k` |
| $T_{\text{sat,I-4}}$ (day/night) | $367/320$ | K | VIIRS I-4 channel saturation temperature | `docs/02` §1 |
| $T_{\text{sat,M13}}$ | $380$ | K | VIIRS M13 channel saturation temperature | `docs/02` §1 |
| $\bar{A}_7$ (H3 Res 7) | $5.16129336$ | km² | H3 Resolution 7 hexagon cell area | `geometry_h3.py::H3_RES7_AREA_KM2` |
| $\bar{A}_8$ (H3 Res 8) | $0.73732760$ | km² | H3 Resolution 8 hexagon cell area | `geometry_h3.py::H3_RES8_AREA_KM2` |
| $A_{\text{VIIRS,nadir,nominal}}$ | $0.140625$ | km² | $0.375\times0.375$ km² nominal VIIRS footprint | `radiometric_calibrator.py` |
| $P_{\text{thresh}}$ | $85.0$ | deg | SZA threshold separating day from night | `solar_sza.py::DAYNIGHT_SZA_THRESHOLD_DEG` |
| $\tau_{\text{cluster}}$ | $60.0$ | minutes | Multi-satellite clustering time window | `deduplication.py::cluster_fire_episodes` |
| $P_{\text{min}}$ | $0.20$ | — | Minimum detection probability to enter a cluster | `deduplication.py::cluster_fire_episodes` |
| $\text{SAA}$ bounds | $\phi\in[-55,7]$, $\lambda\in[-110,11]$ | deg | South Atlantic Anomaly bounding box | `confidence_filter.py` |
| $\Omega_0$ baseline | $1.00$ | — | Baseline epoch: Terra+Aqua equatorial standard, 2003–2011 | `deduplication.py::compute_effective_observation_effort` |

---

## 3. Variables & Symbols

### 3.1. Scan Geometry

| Symbol | Name | Unit | Meaning |
| :--- | :--- | :--- | :--- |
| $\theta$ | Scan angle | rad / deg | Angular offset of the pixel from nadir |
| $\Delta S(\theta)$ | Across-track width | km | Pixel dimension perpendicular to the flight track |
| $\Delta T(\theta)$ | Along-track length | km | Pixel dimension along the flight track |
| $A_p$ | Instantaneous pixel area | km² | $\Delta S \times \Delta T$ |
| $\alpha_{\text{track}}$ | Orbital track azimuth | deg | Satellite flight direction (clockwise from North) |
| $i$ | Orbital inclination | deg | Inclination (98.2 / 98.7) |
| $\phi$ | Latitude | deg | Latitude |
| $\lambda$ | Longitude | deg | Longitude |
| $z$ / zone | Aggregation zone | — | 1, 2, 3 (VIIRS) or 0 (MODIS) |
| $N_{\text{agg}}$ | Aggregation factor | — | 3, 2, 1 by zone |
| $\text{scan}$ | scan field in CSV | km | Measured $\Delta S$ |
| $\text{track}$ | track field in CSV | km | Measured $\Delta T$ |

### 3.2. Radiance & FRP

| Symbol | Name | Unit | Meaning |
| :--- | :--- | :--- | :--- |
| $\text{FRP}$ | Fire Radiative Power | MW | Instantaneous fire radiative power |
| $\text{FRP}_{\text{lim}}$ | Detection limit | MW | Minimum detection threshold |
| $\widetilde{\text{FRP}}_{\text{MODIS}}$ | Scan-angle corrected FRP | MW | After Stage 1 (scan-angle operator) |
| $\widehat{\text{FRP}}_{\text{VIIRS-eq}}$ | VIIRS-equivalent FRP | MW | After Stage 2 (calibration) |
| $\text{FRP}_{\text{raw}}$ | Raw FRP | MW | Original value from FIRMS |
| $\text{scan\_corrected\_frp\_mw}$ | Scan-corrected FRP | MW | Field in `HarmonizedDetection` |
| $\text{calibrated\_viirs\_eq\_frp\_mw}$ | VIIRS-eq FRP | MW | Field in `HarmonizedDetection` |
| $\Delta T_{45}$ | Thermal contrast | K | $T_4 - T_5$ |
| $T_4$ | 4 μm brightness temperature | K | `bright_t4_k` |
| $T_5$ | 11 μm brightness temperature | K | `bright_t5_k` |
| $\tau_4(\theta)$ | Atmospheric transmittance | — | Atmospheric transmittance at 4 μm |
| $L_4$ | 4 μm radiance | W·m⁻²·sr⁻¹·μm⁻¹ | Spectral radiance |
| $\bar{L}_{4,\text{bg}}$ | Background radiance | same | Background radiance |
| $\text{FRP}_p$ | FRP per pixel | MW | $A_p \cdot \sigma_{\text{SB}} / (a \tau_4) \cdot (L_4 - \bar{L}_{4,\text{bg}})$ |

### 3.3. Probability & Noise Filtering

| Symbol | Name | Unit | Meaning |
| :--- | :--- | :--- | :--- |
| $P_{\text{fire}}$ | Detection probability | [0,1] | Probability that a detection is a true fire |
| $C_{\text{MODIS}}$ | MODIS confidence | % | `raw_confidence` 0–100 |
| $P_0(\text{class})$ | VIIRS probability anchor | [0,1] | 0.94 (high), 0.78/0.84 (nominal D/N), 0.28/0.38 (low D/N) |
| $P_{\text{episode}}$ | Fire episode probability | [0,1] | $1 - \prod(1 - 0.85 P_i)$ |
| $\text{is\_saa\_anomaly}$ | SAA flag | bool | Nighttime proton contamination |
| $\text{is\_static\_source}$ | Static source flag | bool | Gas flare / volcano / background |
| $P_{\text{combined}}$ | Combined evidence probability | [0,1] | Bayesian combination |

### 3.4. Astronomy & SZA

| Symbol | Name | Unit | Meaning |
| :--- | :--- | :--- | :--- |
| $\text{SZA}$ | Solar Zenith Angle | deg | Solar zenith angle |
| $\text{DOY}$ | Day of Year | 1–366 | Day of the year |
| $t_{\text{UTC}}$ | UTC time | decimal hours | UTC time |
| $\gamma$ | Fractional year | rad | $2\pi/365.25 \cdot (\text{DOY}-1 + (t_{\text{UTC}}-12)/24)$ |
| $\Delta t_{\text{EoT}}$ | Equation of Time | minutes | Equation of time |
| $\delta$ | Solar declination | rad | Solar declination |
| $\omega$ | Solar hour angle | deg | Solar hour angle |
| $\phi$ | Latitude | deg | Latitude |
| $\lambda$ | Longitude | deg | Longitude |

### 3.5. Cross-Calibration & Model Parameters

| Symbol | Name | Value / unit | Meaning |
| :--- | :--- | :--- | :--- |
| $\alpha$ (day/night) | Power-law intercept | — | `day_power_alpha`, `night_power_alpha` |
| $\beta$ (day/night) | Power-law exponent | — | `day_power_beta`, `night_power_beta` |
| $\kappa$ | Scan-tail compensation | — | `scan_tail_kappa` |
| $\gamma$ | Parametric blend weight | 0.8969 | Parametric weight in the blend, fitted by least squares on the training pairs (≤2019); default 0.65 before fitting |
| $1-\gamma$ | EQM blend weight | 0.1031 | EQM weight in the blend |
| $\text{base\_count\_mult}$ | Nadir count multiplier | 2.85 (day), 3.40 (night) | Equivalent hotspot count multiplier |
| $\kappa_{\text{grid}}$ | Grid search kappa | [0.10, 0.55] | Search for the optimal $\kappa$ |
| $\alpha_{\text{track}}$ | Track azimuth | deg | Orbital track azimuth |

### 3.6. Observation Effort & Clustering

| Symbol | Name | Unit | Meaning |
| :--- | :--- | :--- | :--- |
| $\Omega(y, \phi)$ | Effective observation effort | — | Normalized to 1.00 at Terra+Aqua equatorial 2003–2011 |
| $\Omega_0(y)$ | Baseline effort by year | — | 0.52, 0.76, 1.00, 1.48, 1.78, 1.92, 2.08 |
| $\text{lat\_convergence}$ | Latitude convergence | — | $1 + 0.18(1/\cos\phi - 1)$, bounded [1.0, 1.65] |
| $\tau_{\text{cluster}}$ | Clustering window | minutes | 60 |
| $d_{\text{Haversine}}$ | Great-circle distance | km | Haversine distance |
| $r_{\text{eff}}$ | Effective footprint radius | km | $\sqrt{A_p/\pi}$ |
| $m$ | Number of detections in the cluster | — | raw_detection_count |

### 3.7. Burning Activity Calendar

| Symbol | Name | Unit | Meaning |
| :--- | :--- | :--- | :--- |
| $\text{HFD}_{y,p}$ | Harmonized Fire Density | episodes / 100 km² / day | Normalized fire density |
| $\text{HRF}_{y,p}$ | Harmonized Radiative Flux | MW / km² | Normalized radiative flux |
| $\text{SFAI}_{y,p}$ | Standardized Fire Anomaly Index | Z-score | Robust anomaly index |
| $\text{H3}_7, \text{H3}_8$ | H3 hexagon cell | — | Resolution 7 / 8 |
| $p$ | Pentad | 1–73 | 5-day period |
| $y$ | Year | 2000–2026 | Year |
| $A_{\text{AOI}}$ | Area of interest | km² | Area of interest |
| $\psi_{\text{regime}}(y)$ | Sensor regime coefficient | — | (in the HFD formula) |
| $\text{Median}_{y'}$ | Median HRF by pentad | MW/km² | Baseline by pentad |
| $\text{MAD}$ | Median absolute deviation | MW/km² | Median absolute deviation |
| $\text{Std}$ | Standard deviation | MW/km² | Standard deviation |
| $E_k$ | Fire Episode | — | Cluster of detections |
| $\mathcal{E}_{y,p}$ | Set of fire episodes in (y,p) | — | Set of episodes |
| $\text{episode\_count}$ | Fire episode count | — | Deduplicated count |

### 3.8. Validation Statistics

| Symbol | Name | Meaning |
| :--- | :--- | :--- |
| $N_{\text{pairs}}$ | Number of co-incident grid cell pairs | 11,553 |
| $R^2$ | Coefficient of determination | Variance explained |
| $\text{RMSE}$ | Root mean square error | MW/cell |
| $D_{\text{KS}}$ | Kolmogorov-Smirnov distance | Distribution distance |
| $\text{ECDF}$ | Empirical CDF | Empirical cumulative distribution |
| $\text{CDF}_v, \text{CDF}_m$ | CDF of VIIRS / MODIS | — |
| $\text{max\_axis\_mw}$ | Maximum axis | MW |
| $\text{alpha}, \text{beta}$ | Fitted parameters | — |
| $\text{raw\_r2}, \text{harm\_r2}$ | R² before/after | — |
| $\text{ks\_before}, \text{ks\_after}$ | KS before/after | — |

---

## 4. Formulas

Each formula includes its name, expression, variables, and implementation location.

### F1. MODIS across-track $\Delta S(\theta)$
$$\Delta S_{\text{MODIS}}(\theta) = r \cdot s \left( \cos\theta - \sqrt{(R_e / r)^2 - \sin^2\theta} \right) \cdot \frac{R_e}{r} \cdot \frac{1}{\sqrt{(R_e / r)^2 - \sin^2\theta}}$$

That is, $\Delta S = \frac{R_e}{r} \cdot \frac{\Delta T}{\sqrt{(R_e / r)^2 - \sin^2\theta}}$: the across-track dimension is the along-track dimension $\Delta T$ multiplied by the Earth curvature factor $\frac{R_e}{r}$ and the oblique-view stretching factor $1/\sqrt{(R_e / r)^2 - \sin^2\theta}$. This form is algebraically equivalent to $R_e \cdot s \left( \frac{\cos\theta}{\sqrt{(R_e / r)^2 - \sin^2\theta}} - 1 \right)$ (numerical check: same value $1.000$, $1.159$, $1.943$, $4.830\text{ km}$ at $0^\circ, 20^\circ, 40^\circ, 55^\circ$) and gives $\Delta S(0^\circ) = s\,h = 1.000\text{ km}$.
Variables: $R_e=6378.137$, $r=7083.137$, $s=0.0014184397$, $\theta$ rad.
Location: `geometry_h3.py::modis_dimensions_from_scan_angle`.

### F2. MODIS along-track $\Delta T(\theta)$
$$\Delta T_{\text{MODIS}}(\theta) = r \cdot s \left( \cos\theta - \sqrt{(R_e/r)^2 - \sin^2\theta} \right)$$
Location: same as F1.

### F3. VIIRS dimensions (3-zone)
$$\Delta S = R_e \cdot (N_{\text{agg}}\cdot s_{\text{native},S}) \cdot \left(\frac{\cos\theta}{\sqrt{(R_e/r)^2-\sin^2\theta}}-1\right)$$
$$\Delta T = r \cdot s_{\text{native},T} \cdot (\cos\theta - \sqrt{(R_e/r)^2-\sin^2\theta})$$
$N_{\text{agg}} = 3/2/1$ by zone. Location: `geometry_h3.py::viirs_dimensions_from_scan_angle`.

### F4. VIIRS zone
$$N_{\text{agg}}(\theta_{\deg}) = \begin{cases}3 & |\theta|<31.72\\2 & 31.72\le|\theta|<44.86\\1 & 44.86\le|\theta|\le56.28\end{cases}$$
Location: `geometry_h3.py::viirs_aggregation_zone`.

### F5. MODIS scan angle inversion (bisection)
Solve $\Delta S(\theta)=\text{scan}$ on $[0, 55.5^\circ]$, 45 iterations, error $<10^{-9}$ rad.
Location: `geometry_h3.py::invert_modis_scan_angle`.

### F6. VIIRS scan angle inversion
Bisection on track, then refine by scan. Location: `geometry_h3.py::invert_viirs_scan_angle`.

### F7. Orbital track azimuth
$$\sin\alpha_{\text{track}} = \frac{\cos i}{\cos\phi},\quad \cos\phi \ge 0.15$$
Ascending node logic by platform/daynight. Location: `geometry_h3.py::compute_orbital_track_azimuth`.

### F8. H3 fractional allocation (13-point stencil)
$$w_{p,h} = \sum_{k: \text{H3}(\phi_k,\lambda_k)=h} \omega_k,\quad \sum_h w_{p,h}=1.0$$
Stencils: center 0.28, inner ring 4×0.09, outer ring 8×0.045. Location: `geometry_h3.py::allocate_footprint_to_h3`.

### F9. FRP detection limit
$$\text{FRP}_{\text{lim,MODIS}} = (3.70 + 4.50\cos^{0.75}\text{SZA})\cdot A_p^{1.04}$$
$$\text{FRP}_{\text{lim,VIIRS}} = (0.50 + 0.65\cos^{0.75}\text{SZA})\cdot (A_p/0.1406)^{0.94}$$
Location: `radiometric_calibrator.py::compute_frp_detection_limit`.

### F10. Stage 1 scan-angle tail compensation
$$\widetilde{\text{FRP}}_{\text{MODIS}} = \text{FRP}_{\text{raw}} \cdot [1 + \kappa\cdot \ln(\max(1, A_p))]$$
Location: `radiometric_calibrator.py::apply_two_stage_frp_calibration`.

### F11. Stage 2 parametric + EQM blend
$$\widehat{\text{FRP}}_{\text{VIIRS-eq}} = \gamma\cdot(\alpha\cdot \widetilde{\text{FRP}}^\beta + 0.35(\text{FRP}_{\text{lim}}-1.15)) + (1-\gamma)\cdot \text{EQM}(\widetilde{\text{FRP}})$$
Location: `radiometric_calibrator.py::apply_two_stage_frp_calibration`.

### F12. VIIRS equivalent count
$$\text{viirs\_eq\_count} = \text{base\_count\_mult}\cdot A_p^{0.38}$$
Location: `radiometric_calibrator.py::apply_two_stage_frp_calibration`.

### F13. EQM interpolation
$$\text{EQM}(x) = \text{interp}(x, Q_{\text{MODIS}}, Q_{\text{VIIRS}})$$
Location: `numpy.interp` in the calibrator.

### F14. SZA computation (Spencer 1971)
$$\gamma = \frac{2\pi}{365.25}\left(\text{DOY}-1+\frac{t_{\text{UTC}}-12}{24}\right)$$
$$\Delta t_{\text{EoT}} = 229.18(0.000075 + 0.001868\cos\gamma - 0.032077\sin\gamma - 0.014615\cos2\gamma - 0.040849\sin2\gamma)$$
$$\delta = 0.006918 - 0.399912\cos\gamma + 0.070257\sin\gamma - 0.006758\cos2\gamma + 0.000907\sin2\gamma - 0.002697\cos3\gamma + 0.001480\sin3\gamma$$
$$\omega = \frac{(60t_{\text{UTC}}+\Delta t_{\text{EoT}}+4\lambda)\bmod 1440}{4}-180$$
$$\text{SZA} = \arccos(\sin\phi\sin\delta + \cos\phi\cos\delta\cos\omega)$$
Location: `solar_sza.py::compute_solar_zenith_angle`.

### F15. Day/night flag
$$\text{DayNight} = \begin{cases}\text{'D'} & \text{SZA}<85.0\\ \text{'N'} & \text{SZA}\ge85.0\end{cases}$$
Location: `solar_sza.py::harmonize_daynight_flag`.

### F16. Unified detection probability (MODIS)
$$P_{\text{fire}} = \frac{1}{1+\exp\left[-\left(\frac{C-38}{19}+0.015\cdot\text{clip}(\Delta T_{45}-18,-10,40)\right)\right]}$$
Location: `confidence_filter.py::compute_unified_detection_probability`.

### F17. Unified detection probability (VIIRS)
$$P_{\text{fire}} = \text{clip}\left(P_0 + 0.06\tanh\left(\frac{\Delta T_{45}-20}{15}\right), 0.05, 0.99\right)$$
$P_0$: high=0.94, nominal D/N=0.78/0.84, low D/N=0.28/0.38.
Location: `confidence_filter.py::compute_unified_detection_probability`.

### F18. SAA false alarm
If $\phi\in[-55,7]$, $\lambda\in[-110,11]$, night, and ($\Delta T_{45}<16.5$ & FRP<2.2) or (base_prob<0.45 & $\Delta T_{45}<19.5$): is_saa=True, prob×=0.12.
Location: `confidence_filter.py::compute_unified_detection_probability`.

### F19. Episode combined probability
$$P_{\text{episode}} = 1 - \prod_{i=1}^{m}(1 - 0.85 P_i)$$
Location: `deduplication.py::cluster_fire_episodes`.

### F20. Haversine distance
$$d = 2R_e \arcsin\sqrt{\sin^2(\Delta\phi/2)+\cos\phi_1\cos\phi_2\sin^2(\Delta\lambda/2)}$$
Location: `deduplication.py::haversine_km`.

### F21. Effective observation effort
$$\Omega(y,\phi)=\Omega_0(y)\cdot[1+0.18(1/\max(0.55,\cos\phi)-1)]$$
$\Omega_0$: 0.52 (≤2001), 0.76 (2002), 1.00 (2003–2011), 1.48 (2012–2017), 1.78 (2018–2022), 1.92 (2023), 2.08 (≥2024).
Location: `deduplication.py::compute_effective_observation_effort`.

### F22. Cluster condition
$$d_{\text{Haversine}} \le \max(1.35, r_{\text{eff},i}+r_{\text{eff},j}+0.65) \quad \text{or} \quad \text{H3}_8(x_i)=\text{H3}_8(x_j)$$
with $\Delta t \le 95$ minutes. Location: `deduplication.py::cluster_fire_episodes`.

### F23. HFD
$$\text{HFD}_{y,p} = \frac{100}{5 A_{\text{AOI}}}\sum_{E_k\in\mathcal{E}_{y,p}} \frac{P_{\text{episode}}(E_k)\psi_{\text{regime}}(y)}{\Omega(y,\phi_k)}$$
Location: `calendar_engine.py::build_burning_activity_calendar` (simplified: harm_ep_sum).

### F24. HRF
$$\text{HRF}_{y,p} = \frac{1}{A_{\text{AOI}}}\sum_{E_k\in\mathcal{E}_{y,p}} \frac{\widehat{\text{FRP}}_{\text{VIIRS-eq}}(E_k)}{\Omega(y,\phi_k)}$$
Location: `calendar_engine.py::build_burning_activity_calendar`.

### F25. SFAI
$$\text{SFAI}_{y,p} = \frac{\text{HRF}_{y,p}-\text{Median}_{y'\in\mathcal{Y}_{\text{obs}}(p)}(\text{HRF}_{y',p})}{0.65(1.4826\cdot\text{MAD})+0.35\cdot\text{Std}}$$
Location: `calendar_engine.py::build_burning_activity_calendar`.

### F26. Pentad mapping
$$\text{pentad} = \min(73, \max(1, \lfloor(\text{doy}-1)/5\rfloor+1))$$
Location: `calendar_engine.py::day_of_year_to_pentad`.

### F27. Pentad DOY range
$$\text{start}=(p-1)\cdot5+1,\quad \text{end}=365 \text{ if } p=73 \text{ else } p\cdot5$$
Location: `calendar_engine.py::pentad_to_doy_range`.

### F28. SFAI tier
$$\text{Tier} = \begin{cases}\text{QUIET} & \text{SFAI}<-0.5\\\text{BASELINE} & -0.5\le\text{SFAI}<1.0\\\text{ELEVATED} & 1.0\le\text{SFAI}<1.75\\\text{SEVERE} & 1.75\le\text{SFAI}<2.5\\\text{CRISIS} & \text{SFAI}\ge2.5\end{cases}$$
Location: `calendar_engine.py::classify_sfai_tier`.

### F29. Calibration fit (least squares / grid search)
Grid search $\kappa\in[0.10,0.55]$ (19 steps) minimizing the MSE between predicted and VIIRS. Then a log-log polyfit to obtain $\alpha,\beta$. KS statistic via ECDF.
Location: `radiometric_calibrator.py::fit_coincident_aqua_snpp_model`.

### F30. Coincident cell grouping
Group by (acq_date, daynight, lat_bin, lon_bin) with lat_bin = round(lat×18), lon_bin = round(lon×18) (~0.05°). Filter: m_frp≥5, v_frp≥5, 0.65≤v/m≤4.2.
Location: `run_experiments.py::run_coincident_overpass_calibration`.

---

## 5. Domain Terms

Extracted from `GLOSSARY.md` (root). Each term includes its definition and the words to avoid.

### 5.1. Sensor Physics

- **Thermal Detection**: A single raw active-fire or thermal-anomaly observation from MODIS/VIIRS. Avoid: Fire point, hotspot row, raw fire.
- **Instantaneous Footprint**: The elliptical area $\Delta S \times \Delta T$ at scan angle $\theta$ and azimuth $\alpha_{\text{track}}$. Avoid: Pixel size, point buffer, nominal resolution.
- **Bow-Tie Distortion**: The expansion and overlap of pixels toward the edge of the scan swath. Avoid: Edge stretching, pixel blur.
- **Aggregation Zone**: The 3 VIIRS scan-angle zones (0–31.72, 31.72–44.86, 44.86–56.28) with 3:1, 2:1, and 1:1 aggregation. Avoid: Scan band, swath sector.
- **FRP**: Instantaneous fire radiative power (MW). Avoid: Fire intensity, fire temperature, heat energy.
- **Detection Limit (FRP_lim)**: The minimum FRP required to exceed the background threshold at $A_p$ and SZA. Avoid: Sensitivity cutoff, minimum brightness.
- **Observation Operator**: The transfer function that relates the sub-pixel flux to the observed FRP. Avoid: Scaling factor, correction multiplier.

### 5.2. Spatio-Temporal Harmonization

- **SZA**: Solar zenith angle; SZA < 85° = daytime. Avoid: Day/night flag, local time indicator.
- **Detection Probability (P_fire)**: The probability [0,1] that a hotspot is a true fire. Avoid: Confidence score, quality flag.
- **SAA**: South Atlantic Anomaly (11°E–110°W, 7°N–55°S). Avoid: Atlantic noise zone.
- **Static Thermal Source**: A static heat source (gas flare, industrial plant, volcano). Avoid: False fire, stationary hotspot.
- **Fire Episode**: A single physical burning event assembled from multiple overpasses. Avoid: Deduplicated point, merged hotspot, fire cluster.
- **Effective Observation Effort ($\Omega$)**: Normalized observation capacity. Avoid: Overpass count, satellite multiplier.
- **Co-Incident Overpass Pair**: Simultaneous Aqua-MODIS and S-NPP VIIRS observations. Avoid: Matched points, overlapping passes.

### 5.3. Spatial Grid & Phenology Calendar

- **Iso-Area Cell**: H3 Res 7/8 hexagon cell. Avoid: Grid square, pixel bin, lat-lon box.
- **Pentad**: 5-day period (73/year). Avoid: 5-day bin, mini-week.
- **HFD**: Normalized fire density (episodes/100km²/day). Avoid: Normalized fire count, adjusted hotspot density.
- **HRF**: Radiative flux density (MW/km²). Avoid: Calibrated FRP, total heat flux.
- **SFAI**: Robust per-pentad Z-score. Avoid: Fire risk score, anomaly percent.
- **Burning Activity Calendar**: Year × Pentad matrix. Avoid: Fire heatmap, hotspot timeline.
- **Anomaly Tier**: The operational severity band of SFAI, in 5 ordered bands — QUIET ($< -0.5$), BASELINE ($-0.5 \le \text{SFAI} < 1.0$), ELEVATED ($1.0 \le \text{SFAI} < 1.75$), SEVERE ($1.75 \le \text{SFAI} < 2.5$), CRISIS ($\ge 2.5$). SEVERE mobilises patrols; CRISIS raises an out-of-season crisis alarm. Avoid: Risk level, alert level, severity score, crisis threshold.
- **Measured Epoch**: A year for which the archive holds a real FIRMS slice set — the normalized count for that year is computed from observed detections. 11/26 Mekong years and 9/26 Amazon years are Measured Epochs. Avoid: Real year, hard data, ground truth, anchor year.
- **Interpolated Year**: A year with no slice set; the annual scale is modelled from the observed MODIS count and the region's empirical seasonal envelope. The interpolation is deterministic but it is a model, not an observation, and the published documentation marks these years. Avoid: Estimated year, synthetic year, filled year, projection.
- **Severe Anomaly Outline**: The cyan frame drawn on a Burning Activity Calendar cell when SFAI reaches the display threshold of $+2.2\sigma$. This is a *display* convention, deliberately below the CRISIS Anomaly Tier, so the calendar highlights severe anomalies *before* the crisis alarm is raised. Avoid: Crisis anomaly, crisis outline, alarm outline, threshold.

### 5.4. Processing Modes & Satellites

- **ProcessingMode**: STANDARD, NRT, RT, URT.
- **SatellitePlatform**: TERRA, AQUA, SNPP, NOAA20, NOAA21.
- **SensorType**: MODIS, VIIRS.
- **AnomalyTier**: QUIET, BASELINE, ELEVATED, SEVERE, CRISIS.

### 5.5. Architecture

- **Deep Module**: A module with a small interface and a complex implementation (Ousterhout).
- **Seam**: The junction point between modules (firms-ingestion ↔ core).
- **Facade**: `FIRMSHarmonizer` compatibility layer.
- **Bounded in-memory map**: A map with MAX_ENTRIES + TTL + FIFO.
- **Encapsulated resource component**: A React component that manages an object URL.

### 5.6. Art & Communication Products

- **Scientific Figure**: A publication-grade chart rendered directly from the empirical results by `benchmark_cli.figure_renderer`, carrying measured values, units, and axis labels. It is a build artifact — regenerated from code, never hand-edited, never re-labelled for storytelling. Avoid: Chart, plot, graph, illustration.
- **Narrative Asset**: A hand-authored visual — motion graphic, 3D scene, title card, or map animation — that makes the pitch video easier to understand. It may depict a concept truthfully but never replaces a Scientific Figure, and it is never labelled as a measurement. Avoid: Figure, chart, data viz, screenshot, mock-up.
- **Workbench**: The Flare-Chronos interactive analysis surface — a Deck.gl / MapLibre application specified in `docs/04_UI_UX_Burning_Calendar_Wireframe.md`, rendering the harmonization engine's output on demand instead of pre-building it. Specified, not yet implemented. Avoid: Dashboard, UI, app, interactive demo, live visualization.
- **Main Submission Video**: The 120-second primary pitch deliverable for NASA Space Apps, cut to the shot script in `docs/05_Pitch_Deck_and_Video_Script.md` §3.1. Avoid: Demo, promo, trailer, explainer.
- **Pitch Deck**: The 7-slide set mirroring the `docs/05_Pitch_Deck_and_Video_Script.md` §2 blueprint — the still counterpart of the Main Submission Video, carrying the same argument in slide form. Avoid: Slide deck, slides, presentation, deck.

---

## 6. Acronyms

| Acronym | Full form |
| :--- | :--- |
| ADR | Architecture Decision Record |
| AOI | Area of Interest |
| CDF / ECDF | Cumulative Distribution Function / Empirical CDF |
| DOY | Day of Year |
| EoT | Equation of Time |
| EQM | Empirical Quantile Mapping |
| FIRMS | Fire Information for Resource Management System |
| FRP | Fire Radiative Power |
| HFD | Harmonized Fire Density |
| HRF | Harmonized Radiative Flux |
| H3 | Uber H3 Hexagonal Hierarchical Spatial Index |
| KS | Kolmogorov-Smirnov |
| MLT | Mean Local Time |
| MODIS | Moderate Resolution Imaging Spectroradiometer |
| MW | Megawatt |
| NRT / RT / URT | Near-Real-Time / Real-Time / Ultra-Real-Time |
| RMSE | Root Mean Square Error |
| SAA | South Atlantic Anomaly |
| SFAI | Standardized Fire Anomaly Index |
| SP | Standard Processing (Science Quality) |
| SZA | Solar Zenith Angle |
| UTC | Coordinated Universal Time |
| VIIRS | Visible Infrared Imaging Radiometer Suite |
| WGS-84 | World Geodetic System 1984 |

---

## 7. Units

| Unit | Meaning |
| :--- | :--- |
| km | Kilometer |
| km² | Square kilometer |
| MW | Megawatt |
| MW/km² | Megawatt per square kilometer |
| episodes/100km²/day | Episodes per 100 km² per day |
| K | Kelvin |
| deg | Degree (angle) |
| rad | Radian |
| μm | Micrometer |
| sr | Steradian |
| W·m⁻²·K⁻⁴ | Watt per square meter per Kelvin to the fourth |
| min | Minute |
| % | Percent |

---


## 8. Data Consistency Notes

After the audit, the following figures were corrected to match `data/processed/empirical_results.json`:
- Total detections: **1,609,182** (not 1,609,194).
- Number of CSV slices: **134** (not 138).
- Test duration: **0.004s** (not 0.003s).
- `n_pairs`: **11,553**; R²: **0.7330 → 0.7470**; KS: **0.1166 → 0.0237**; count ratio: **3.56×**; FRP ratio: **1.371×**.
- MODIS nadir area: **1.000 km²**; edge (55°): **9.688 km²**.
- VIIRS nadir area: **0.1305 km²**; edge (56.28°): **0.615 km²**.

The claims in `PROPOSAL.md`/`REPORT.md` have been updated accordingly. The 26-year calendar contains **11/26 Measured Epochs** for the Mekong and **9/26 years** for the Amazon; the remaining years are **Interpolated Years** — the annual scale is modelled from the observed MODIS count and the region's empirical seasonal envelope (fixed-seed RNG noise, El Niño peak coefficient `1.85`, Amazon climate baseline `0.58`, single-Terra correction `1.92/1.32`). The interpolation is a **model, not an observation**, and the documentation marks it clearly. See `docs/adr/0009-measured-epochs-and-interpolated-years.md`.

The coefficient `1.55` was once multiplied into the Amazon 2024 normalized index *after* normalization with no recorded explanation; it was the only reason that year appeared to be a severe year. It has been removed — the published index is **45.6**, and the test suite blocks the multiplication of a coefficient onto a Measured Epoch.

At the same time, `docs/01_NASA_SpaceApps_Proposal.md` and `docs/05_Pitch_Deck_and_Video_Script.md` have been resynchronized with `data/processed/empirical_results.json` (they still publish figures from the earlier FIRMS pull: `775.531` records / `5.769` grid cell pairs / `$D_{KS}$ 0.1180 → 0.0205`). `tests/test_documented_claims_consistency.py` automatically checks these claims, so a later regeneration of `empirical_results.json` will make CI fail if the documents have not been updated accordingly.

---

*This document is a reference appendix. Update it when new symbols, formulas, or terms are added.*
