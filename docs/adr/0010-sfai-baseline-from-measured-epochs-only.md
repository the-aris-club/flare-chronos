---
status: accepted
---

# The SFAI Baseline Is Computed From Measured Epochs Only

**Partially supersedes** [ADR-0009](./0009-measured-epochs-and-interpolated-years.md).

The Standardized Fire Anomaly Index is a Z-score against a multi-decade climatological baseline. Under ADR-0009 most of that baseline is modelled: fifteen of the twenty-six Mekong years and seventeen of the twenty-six Amazon years are Interpolated Years, whose scale and seasonal shape come from hand-set constants (`_EL_NINO_PEAK_AMPLITUDE`, `_AMAZON_CLIMATOLOGY_BASELINE_FRACTION`, `_TERRA_ONLY_CORRECTION`) and seeded noise. An anomaly measured against that baseline partly measures the model's own assumptions.

We compute the baseline mean, spread and every SFAI value from **Measured Epochs only**. Interpolated Years stay on the Burning Activity Calendar as a visually distinct, explicitly uncertain band, but they never feed a baseline and never earn an Anomaly Tier or a Severe Anomaly Outline.

## The unit is the cell, not the year

A Measured Epoch is one 5-day FIRMS window, so only **one pentad per measured year is observed**. The other 72 pentads of that year are still built from the seasonal envelope and seeded noise. The calendar therefore carries a three-state provenance per cell: *observed*, *modelled in a measured year*, and *interpolated*. SFAI, Anomaly Tier and Severe Anomaly Outline exist only on observed cells, and a pentad reports an SFAI only with at least `MIN_MEASURED_YEARS` observed years behind it. Before this change 79 Mekong and 117 Amazon cells crossed the display threshold and only one cell in each region was observed; the rest came from the model, including a hand-set peak amplitude on 2007, 2010 and 2024.

## Considered Options

- **Keep ADR-0009 as written (all 26 years in the baseline, interpolated ones labelled)**: Preserves the 26-year headline. Rejected — a label on the output does not stop the model from shaping the statistic the output is judged by.
- **Publish only Measured Epochs**: Honest, but guts the calendar. Rejected as the end state; it is the fallback if the archive cannot be extended.
- **Extend the archive first, then compute the baseline from measured years (chosen, with the measured-only baseline as the interim rule)**: The FIRMS fetcher already exists, so each added year converts an Interpolated Year into a Measured Epoch at the cost of a download. Whatever stays missing is excluded from the baseline rather than modelled into it.

## Consequences

- A cell has an Anomaly Tier only if it is observed. On the current archive that is one pentad (Mekong 15, Amazon 47) in each Measured Epoch, and the only observed cell at or above +2.2 sigma is Mekong 2007 (+2.9). The hand-set peak amplitude now shapes interpolated years only.
- The SFAI baseline for a Pentad is computed from far fewer years than "25-year climatology" implies. Published documents state the number of measured years behind each baseline, and a Pentad with too few measured years reports no SFAI rather than a noisy one. The minimum is a named constant.
- ADR-0009's Measured Epoch / Interpolated Year vocabulary, its prohibition on a post-harmonization multiplier, and the 2026 NRT limitation all still hold.
- The ADR-0009 revisit trigger ("revisit if the archive cannot be extended to more years") is now an active work item: fetching more years is the first-choice fix, and this ADR is retired once every published year is a Measured Epoch.
- `data/processed/burning_calendar.json` exports the calendar with the per-cell provenance, and the provenance tests assert that no modelled cell carries an SFAI.
