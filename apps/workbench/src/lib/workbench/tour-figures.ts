import type { CalendarDataset, RegionId } from '@/lib/calendar/types';
import type { WorkbenchData } from './types';

export type TourFigures = {
  /** Measured Epochs of the region. */
  measured: number;
  /** Years the calendar covers, including Interpolated Years. */
  total: number;
  first: number;
  last: number;
  /** Raw growth ratio between the two growth-window epochs, rounded as on the landing. */
  growth: number;
  growthFrom: number;
  growthTo: number;
  /** The highest SFAI of any observed cell, and its year. */
  peakSfai: number;
  peakYear: number;
};

export function tourFigures(
  calendar: CalendarDataset,
  workbench: WorkbenchData,
  region: RegionId,
): TourFigures {
  const cal = calendar.regions[region];
  const series = workbench.series[region];

  let peakSfai = Number.NEGATIVE_INFINITY;
  let peakYear = cal.years[0] ?? 0;
  cal.sfai.forEach((row, yearIndex) => {
    for (const value of row) {
      if (value !== null && value > peakSfai) {
        peakSfai = value;
        peakYear = cal.years[yearIndex] ?? peakYear;
      }
    }
  });

  return {
    measured: cal.observedYears.length,
    total: cal.years.length,
    first: cal.years[0] ?? 0,
    last: cal.years.at(-1) ?? 0,
    growth: Math.round(1 + series.rawGrowthPct / 100),
    growthFrom: series.growthWindow[0],
    growthTo: series.growthWindow[1],
    peakSfai,
    peakYear,
  };
}
