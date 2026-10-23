---
status: accepted
---

# The SFAI Baseline Is Computed From Measured Epochs Only

**Partially supersedes** [ADR-0009](./0009-measured-epochs-and-interpolated-years.md).

The Standardized Fire Anomaly Index is a Z-score against a multi-decade climatological baseline. Under ADR-0009 most of that baseline is modelled: fifteen of the twenty-six Mekong years and seventeen of the twenty-six Amazon years are Interpolated Years, whose scale and seasonal shape come from hand-set constants (`_EL_NINO_PEAK_AMPLITUDE`, `_AMAZON_CLIMATOLOGY_BASELINE_FRACTION`, `_TERRA_ONLY_CORRECTION`) and seeded noise. An anomaly measured against that baseline partly measures the model's own assumptions.

We compute the baseline mean, spread and every SFAI value from **Measured Epochs only**. Interpolated Years stay on the Burning Activity Calendar as a visually distinct, explicitly uncertain band, but they never feed a baseline and never earn an Anomaly Tier or a Severe Anomaly Outline.

## Considered Options

- **Keep ADR-0009 as written (all 26 years in the baseline, interpolated ones labelled)**: Preserves the 26-year headline. Rejected — a label on the output does not stop the model from shaping the statistic the output is judged by.
- **Publish only Measured Epochs**: Honest, but guts the calendar. Rejected as the end state; it is the fallback if the archive cannot be extended.
- **Extend the archive first, then compute the baseline from measured years (chosen, with the measured-only baseline as the interim rule)**: The FIRMS fetcher already exists, so each added year converts an Interpolated Year into a Measured Epoch at the cost of a download. Whatever stays missing is excluded from the baseline rather than modelled into it.

## Consequences

- A year has an Anomaly Tier only if it is a Measured Epoch. The calendar renders Interpolated Years without a tier or an outline.
- The SFAI baseline for a Pentad is computed from far fewer years than "25-year climatology" implies. Published documents state the number of measured years behind each baseline, and a Pentad with too few measured years reports no SFAI rather than a noisy one. The minimum is a named constant.
- ADR-0009's Measured Epoch / Interpolated Year vocabulary, its prohibition on a post-harmonization multiplier, and the 2026 NRT limitation all still hold.
- The ADR-0009 revisit trigger ("revisit if the archive cannot be extended to more years") is now an active work item: fetching more years is the first-choice fix, and this ADR is retired once every published year is a Measured Epoch.
- The consistency tests assert that no Interpolated Year carries a tier or outline.
