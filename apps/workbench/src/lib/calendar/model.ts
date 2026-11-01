import { ALERT_SIGMA, CRISIS_SIGMA } from './constants';
import type { CalendarRegionData, CellRef } from './types';

export const PENTADS_PER_YEAR = 73;

export type CalendarCell = {
  year: number;
  pentad: number;
  hfd: number;
  sfai: number | null;
  observed: boolean;
  alert: boolean;
  crisis: boolean;
};

export function buildCells(region: CalendarRegionData): CalendarCell[] {
  const cells: CalendarCell[] = [];

  for (let yearIndex = 0; yearIndex < region.years.length; yearIndex += 1) {
    for (let pentadIndex = 0; pentadIndex < PENTADS_PER_YEAR; pentadIndex += 1) {
      const sfai = region.sfai[yearIndex][pentadIndex];
      const observed = region.provenance[yearIndex][pentadIndex] < 2;

      cells.push({
        year: region.years[yearIndex],
        pentad: pentadIndex + 1,
        hfd: region.hfd[yearIndex][pentadIndex],
        sfai,
        observed,
        alert: observed && sfai !== null && sfai >= ALERT_SIGMA,
        crisis: observed && sfai !== null && sfai >= CRISIS_SIGMA,
      });
    }
  }

  return cells;
}

export function findInitialCell(region: CalendarRegionData): CellRef {
  let peak: { value: number; ref: CellRef } | null = null;
  let firstObserved: CellRef | null = null;

  for (let yearIndex = 0; yearIndex < region.years.length; yearIndex += 1) {
    for (let pentadIndex = 0; pentadIndex < PENTADS_PER_YEAR; pentadIndex += 1) {
      if (region.provenance[yearIndex][pentadIndex] >= 2) continue;

      firstObserved ??= { yearIndex, pentadIndex };

      const sfai = region.sfai[yearIndex][pentadIndex];
      if (sfai !== null && (peak === null || sfai > peak.value)) {
        peak = { value: sfai, ref: { yearIndex, pentadIndex } };
      }
    }
  }

  return peak?.ref ?? firstObserved ?? { yearIndex: 0, pentadIndex: 0 };
}
