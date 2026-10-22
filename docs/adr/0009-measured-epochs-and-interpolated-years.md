---
status: accepted
---

# The 26-Year Calendar Is Partly Measured and Partly Interpolated

The Burning Activity Calendar spans 2001–2026, but the archive does not hold a NASA FIRMS slice set for every one of those years. **Eleven of the twenty-six Mekong years and nine of the twenty-six Amazon years are Measured Epochs** — years whose harmonized count is computed from observed detections. The remaining years are **Interpolated Years**: their annual scale is modelled from the observed MODIS-only count, and their intra-year shape is taken from the region's empirical seasonal envelope.

We publish that distinction rather than presenting the whole series as observation. The interpolation is deterministic, so the figures are reproducible, but it is a model, and a reader who cannot tell an observation from a model output will read the modelled years as measured evidence.

## Considered Options

- **Publish all 26 years as if measured**: The full 26-year series is the product's headline claim, and every year currently reads as a real observation. Rejected — an unlabelled model output is a claim the artifact cannot support.
- **Publish only the measured epochs**: Honest, and it removes the ambiguity entirely. Rejected for now because it would gut the "26-year" claim the whole pitch rests on, and because the interpolation is sound methodology rather than fabrication. Revisit if the archive cannot be extended to more years.
- **Publish all 26 years, marking the interpolated ones (chosen)**: The series keeps its full span, every published epoch table lists measured years only, and the documents state how many years are measured and how many are interpolated.

## Consequences

- The published documents say, per region, how many years are Measured Epochs and how many are Interpolated Years, and the epoch tables list measured years only.
- `GLOSSARY.md` defines *Measured Epoch* and *Interpolated Year* so the distinction has a name.
- The pipeline records `measured_years` and `interpolated_years` in `data/processed/empirical_results.json`, and the consistency test asserts the documents' counts match.
- A measured epoch's published index must equal the artifact's own harmonized value. A post-harmonization multiplier on a measured epoch is not permitted: the published Amazon 2024 index once carried an unexplained `x1.55` applied *after* harmonization, and it was the only reason that year read as a severe anomaly — without it the index is 45.6 and the year produces no outlined cells at all. A factor that changes a conclusion cannot be reintroduced silently.
- The modelling constants are named (`_AMAZON_CLIMATOLOGY_BASELINE_FRACTION`, `_EL_NINO_PEAK_AMPLITUDE`, `_TERRA_ONLY_CORRECTION`, `_CALENDAR_NOISE_SEED`) and documented as describing a model, never a measurement.

## Known limitation

The 2026 epoch is NRT-only and the calendar anchors it to the observed MODIS count rather than the harmonized episode count, so its published index is not comparable with the other epochs. It is excluded from the measured-epoch index check for that reason.
