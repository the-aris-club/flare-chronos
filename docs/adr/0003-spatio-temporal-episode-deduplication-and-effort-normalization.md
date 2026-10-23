---
status: accepted
---

# Spatio-Temporal Fire Episode Deduplication and Observation Effort Normalization

We group multi-satellite Thermal Detections occurring within an elliptical footprint overlap and a $\tau = 60\text{ min}$ overpass window into unified Fire Episodes, and normalize daily rates by the constellation's Effective Observation Effort $\Omega(y, \phi)$, rather than summing raw hotspot counts per day.

## Consequences

- Prevents the afternoon VIIRS train (`Suomi-NPP`, `NOAA-20`, `NOAA-21`, separated by $\sim 25\text{–}50\text{ minutes}$ around `12:40–13:30 MLT`) and `Aqua-MODIS` from triple- or quadruple-counting the same persistent fire within a single diurnal peak.
- Eliminates the artificial step-function jumps in raw fire trends at 2002 (+Aqua), 2012 (+Suomi-NPP), 2020 (+NOAA-20), and 2024 (+NOAA-21).
- Recomputes astronomical Solar Zenith Angle ($\text{SZA} < 85^\circ$) for every detection from UTC timestamp and coordinates so that NRT orbital-node flags (`1.0NRT`/`2.0NRT`) match Standard Processing (`MODIS_SP`/`VIIRS_SNPP_SP`) across all 26 years.

## Amendment (reviewer feedback)

- The overpass window is **60 minutes**, anchored on the first detection of an episode. The afternoon train spans 50 minutes, so 60 holds it; a longer window only risked chaining. It is the constant `FIRE_EPISODE_WINDOW_MINUTES`.
- The effective observation effort is **weighted by the epoch's clear-sky share** (ERA5 total cloud cover, relative to the region's mean over Measured Epochs). A cloudier-than-usual epoch earns less effort. The weight is linear, a stated assumption, and moves individual epochs by up to about 35%. ERA5 is a reanalysis field, not an observation at overpass time.
- The MODIS-only **omission factor** is fitted, not hand-set. It is the median, over multi-sensor epochs up to 2020, of the factor that would make the epoch's `sensor_invariance_ratio` equal 1 (the same fires scored with MODIS alone against all sensors). It moved from 3.65 to 3.35 (Mekong) and from 2.55 to 1.82 (Amazon). On the held-out epochs (2023 onward) the Amazon ratios improve from 0.61–0.65 to 0.85–0.91; Mekong was already near 1 and does not improve (0.84–1.05 before, 0.92–1.14 after). The held-out gate allows a gap of 0.20; the all-epoch 0.10 gate stays a strict xfail. The overlap gain (0.24) and the era Omega ladder are still hand-set.
