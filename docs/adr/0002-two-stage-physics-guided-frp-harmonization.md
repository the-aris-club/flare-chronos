---
status: accepted
---

# Two-Stage Physics-Guided FRP and Fire Density Harmonization

We harmonize MODIS Collection 6.1 and VIIRS 375m Collection 2 records using a two-stage physical-statistical operator—combining a Scan-Angle Observation Operator for sub-pixel detection limits ($\text{FRP}_{\text{lim}}(A_p, \text{SZA})$) with regime-stratified Hurdle Negative-Binomial and Empirical Quantile Mapping (EQM) trained on Co-Incident Overpass Pairs (`Aqua` and `Suomi-NPP` at `13:30 / 01:30 MLT`)—rather than applying a constant global scaling ratio or an unconstrained neural network.

## Considered Options

- **Global constant ratio ($\text{VIIRS} / \text{MODIS} = k$)**: Fails because the detection sensitivity ratio varies from $\sim 2.1\times$ for large crown fires at nadir to $>8.5\times$ for small agricultural burns at large scan angles ($\theta > 45^\circ$).
- **Black-box MLP / Deep Learning regressor**: Lacks physical conservation guarantees, extrapolates poorly outside training biomes, and cannot be audited by NASA fire science reviewers.
- **Two-Stage Observation Operator + Stratified Hurdle/EQM (Chosen)**: Explicitly corrects scan-angle truncation bias using Planck's $4\,\mu\text{m}$ radiance scaling law (*Wooster et al., 2005; Sofiev & Kouznetsov, 2026*) before mapping extreme fire distributions across the 90th–99th percentiles.
