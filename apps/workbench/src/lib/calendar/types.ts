export const REGION_IDS = ['mekong', 'amazon'] as const;

export type RegionId = (typeof REGION_IDS)[number];

export type Provenance = 0 | 1 | 2;

export type HfdUnit = 'density' | 'detections';

export type CalendarRegionData = {
  id: RegionId;
  years: number[];
  hfd: number[][];
  sfai: (number | null)[][];
  provenance: Provenance[][];
  observedPentad: number;
  maxHfd: number;
  observedYears: number[];
  scoredCells: number;
  alertCells: number;
  crisisCells: number;
};

export type CalendarDataset = {
  period: { start: number; end: number };
  unit: HfdUnit;
  regions: Record<RegionId, CalendarRegionData>;
};

export type Metric = 'hfd' | 'sfai';

export type CellRef = {
  yearIndex: number;
  pentadIndex: number;
};
