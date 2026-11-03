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
});
