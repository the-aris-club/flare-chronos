import { describe, expect, test } from 'bun:test';
import calendarJson from '../../../../../data/processed/burning_calendar.json';
import results from '../../../../../data/processed/empirical_results.json';
import { loadCalendar } from '@/lib/calendar/load';
import { loadWorkbench } from './series';
import { tourFigures } from './tour-figures';

const calendar = await loadCalendar();
const workbench = await loadWorkbench(calendar);

describe('tour figures come from the data', () => {
  for (const region of ['mekong', 'amazon'] as const) {
    test(`${region}: epochs, growth and peak match the published artifacts`, () => {
      const figures = tourFigures(calendar, workbench, region);
      const measured = results.regime_shift_series[region].measured_years;
      const epochs =
        region === 'mekong' ? results.mekong_empirical_epochs : results.amazon_empirical_epochs;
      const first = epochs.find((epoch) => epoch.year === 2005);
      const last = epochs.find((epoch) => epoch.year === 2024);
      if (!first || !last) throw new Error('growth epochs missing');

      expect(figures.measured).toBe(measured.length);
      expect(figures.total).toBe(results.regime_shift_series[region].years.length);
      expect(figures.growth).toBe(
        Math.round(last.total_raw_detections / first.total_raw_detections),
      );

      const cal = calendarJson[region];
      let best = -Infinity;
      let bestYear = 0;
      cal.sfai_matrix.forEach((row, r) => {
        row.forEach((value) => {
          if (value !== null && value > best) {
            best = value;
            bestYear = cal.years[r] ?? 0;
          }
        });
      });
      expect(figures.peakSfai).toBeCloseTo(best, 6);
      expect(figures.peakYear).toBe(bestYear);
    });
  }
});
