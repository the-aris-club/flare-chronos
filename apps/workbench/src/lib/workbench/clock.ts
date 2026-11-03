import type { CalendarRegionData } from '@/lib/calendar/types';

export type ClockPoint = {
  pentad: number;
  hfd: number;
  q25: number;
  q75: number;
};

export type ClockData = {
  points: ClockPoint[];
  peak: ClockPoint;
  max: number;
};

const BASELINE_START = 2001;
const BASELINE_END = 2025;

function quantile(values: number[], q: number): number {
  const sorted = [...values].sort((a, b) => a - b);
  const position = (sorted.length - 1) * q;
  const lower = Math.floor(position);
  const upper = Math.ceil(position);
  const weight = position - lower;

  return sorted[lower] + (sorted[upper] - sorted[lower]) * weight;
}

export function buildClock(region: CalendarRegionData, year: number): ClockData {
  const baselineIndices = region.years
    .map((value, index) => ({ value, index }))
    .filter(({ value }) => value >= BASELINE_START && value <= BASELINE_END)
    .map(({ index }) => index);

  const yearIndex = region.years.indexOf(year);
  const points: ClockPoint[] = [];

  for (let pentadIndex = 0; pentadIndex < 73; pentadIndex += 1) {
    const values = baselineIndices.map((index) => region.hfd[index][pentadIndex]);

    points.push({
      pentad: pentadIndex + 1,
      hfd: region.hfd[yearIndex]?.[pentadIndex] ?? 0,
      q25: quantile(values, 0.25),
      q75: quantile(values, 0.75),
    });
  }

  const peak = points.reduce((best, point) => (point.hfd > best.hfd ? point : best));
  const max = Math.max(...points.map((point) => Math.max(point.hfd, point.q75)));

  return {
    points,
    peak,
    max: max > 0 ? max : 1,
  };
}
