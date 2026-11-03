import { describe, expect, test } from 'bun:test';
import results from '../../../../../data/processed/empirical_results.json';
import { loadCalendar } from '@/lib/calendar/load';
import { loadWorkbench } from './series';

const calendar = await loadCalendar();
const workbench = await loadWorkbench(calendar);

describe('workbench series', () => {
  test('measured epochs are the years the archive holds, never the current year', () => {
    for (const region of ['mekong', 'amazon'] as const) {
      const published = results.regime_shift_series[region].measured_years;
      expect(workbench.epochs[region].map((epoch) => epoch.year)).toEqual(published);
      expect(calendar.regions[region].observedYears).toEqual(published);
      expect(published).not.toContain(2026);
    }
  });

  test('raw growth is read between two Measured Epochs and says which', () => {
    for (const region of ['mekong', 'amazon'] as const) {
      const [from, to] = workbench.series[region].growthWindow;
      const epochs =
        region === 'mekong' ? results.mekong_empirical_epochs : results.amazon_empirical_epochs;
      const first = epochs.find((epoch) => epoch.year === from);
      const last = epochs.find((epoch) => epoch.year === to);
      if (!first || !last) throw new Error(`${region} growth window is not measured`);

      expect(workbench.series[region].rawGrowthPct).toBeCloseTo(
        (last.total_raw_detections / first.total_raw_detections - 1) * 100,
        6,
      );
    }
  });

  test('the held-out calibration gain and its interval come from the artifact', () => {
    const holdout = results.coincident_calibration.holdout;
    const published = workbench.calibration.holdout;

    expect(published.gainMw).toBeCloseTo(holdout.raw_rmse_mw - holdout.harmonized_rmse_mw, 6);
    expect(published.ciLowMw).toBe(holdout.rmse_gain_ci95_mw[0]);
    expect(published.ciHighMw).toBe(holdout.rmse_gain_ci95_mw[1]);
    expect(published.trainLastYear).toBe(holdout.train_last_year);
  });

  test('the harmonized trend is fitted over the same window as the raw growth', () => {
    for (const region of ['mekong', 'amazon'] as const) {
      const shift = results.regime_shift_series[region];
      const [from, to] = workbench.series[region].growthWindow;
      const years = shift.years.filter((year) => year >= from && year <= to);
      const values = years.map(
        (year) =>
          (shift.modis_reference_counts_by_year as Record<string, number>)[String(year)] ?? 0,
      );
      const n = years.length;
      const meanX = years.reduce((a, b) => a + b, 0) / n;
      const meanY = values.reduce((a, b) => a + b, 0) / n;
      let num = 0;
      let den = 0;
      years.forEach((year, i) => {
        num += (year - meanX) * ((values[i] ?? 0) - meanY);
        den += (year - meanX) ** 2;
      });

      expect(workbench.series[region].trendPct).toBeCloseTo((num / den / meanY) * 100, 6);
    }
  });
});
