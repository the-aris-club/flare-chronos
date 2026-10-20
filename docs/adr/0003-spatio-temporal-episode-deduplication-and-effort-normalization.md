---
status: accepted
---

# Spatio-Temporal Fire Episode Deduplication and Observation Effort Normalization

We group multi-satellite Thermal Detections occurring within an elliptical footprint overlap and a $\tau = 90\text{ min}$ overpass window into unified Fire Episodes, and normalize daily rates by the constellation's Effective Observation Effort $\Omega(y, \phi)$, rather than summing raw hotspot counts per day.

## Consequences

- Prevents the afternoon VIIRS train (`Suomi-NPP`, `NOAA-20`, `NOAA-21`, separated by $\sim 25\text{–}50\text{ minutes}$ around `12:40–13:30 MLT`) and `Aqua-MODIS` from triple- or quadruple-counting the same persistent fire within a single diurnal peak.
- Eliminates the artificial step-function jumps in raw fire trends at 2002 (+Aqua), 2012 (+Suomi-NPP), 2020 (+NOAA-20), and 2024 (+NOAA-21).
- Recomputes astronomical Solar Zenith Angle ($\text{SZA} < 85^\circ$) for every detection from UTC timestamp and coordinates so that NRT orbital-node flags (`1.0NRT`/`2.0NRT`) match Standard Processing (`MODIS_SP`/`VIIRS_SNPP_SP`) across all 26 years.
