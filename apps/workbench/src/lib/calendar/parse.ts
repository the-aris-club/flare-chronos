import { ALERT_SIGMA, CRISIS_SIGMA } from './constants';
import {
  REGION_IDS,
  type CalendarDataset,
  type CalendarRegionData,
  type Provenance,
  type RegionId,
} from './types';

const ROWS = 26;
export const PENTADS = 73;

export type Json = Record<string, unknown>;

export function fail(message: string): never {
  throw new Error(`Calendar data: ${message}`);
}

export function record(value: unknown, name: string): Json {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    fail(`${name} must be an object`);
  }

  return value as Json;
}

function rowsOf(value: unknown, name: string): unknown[][] {
  if (!Array.isArray(value) || value.length !== ROWS) {
    fail(`${name} must have ${ROWS} rows`);
  }

  return value.map((row, index) => {
    if (!Array.isArray(row) || row.length !== PENTADS) {
      fail(`${name}[${index}] must have ${PENTADS} pentads`);
    }

    return row;
  });
}

function numbersOf(value: unknown, name: string): number[][] {
  return rowsOf(value, name).map((row, yearIndex) =>
    row.map((cell, pentadIndex) => {
      if (typeof cell !== 'number' || !Number.isFinite(cell) || cell < 0) {
        fail(`${name}[${yearIndex}][${pentadIndex}] must be a finite, non-negative number`);
      }

      return cell;
    }),
  );
}

function nullableNumbersOf(value: unknown, name: string): (number | null)[][] {
  return rowsOf(value, name).map((row, yearIndex) =>
    row.map((cell, pentadIndex) => {
      if (cell === null) return null;
      if (typeof cell !== 'number' || !Number.isFinite(cell)) {
        fail(`${name}[${yearIndex}][${pentadIndex}] must be a finite number or null`);
      }

      return cell;
    }),
  );
}

function provenanceOf(value: unknown, name: string): Provenance[][] {
  return rowsOf(value, name).map((row, yearIndex) =>
    row.map((cell, pentadIndex) => {
      if (cell !== 0 && cell !== 1 && cell !== 2) {
        fail(`${name}[${yearIndex}][${pentadIndex}] must be 0, 1, or 2`);
      }

      return cell;
    }),
  );
}

export function yearsOf(value: unknown, name: string): number[] {
  if (!Array.isArray(value) || value.length !== ROWS) {
    fail(`${name} must have ${ROWS} years`);
  }

  const years = value.map((year, index) => {
    if (typeof year !== 'number' || !Number.isInteger(year)) {
      fail(`${name}[${index}] must be an integer year`);
    }

    return year;
  });

  for (let index = 1; index < years.length; index += 1) {
    if (years[index] !== years[index - 1] + 1) {
      fail(`${name} must be consecutive`);
    }
  }

  return years;
}

function integerOf(value: unknown, name: string, min: number, max: number): number {
  if (typeof value !== 'number' || !Number.isInteger(value) || value < min || value > max) {
    fail(`${name} must be an integer between ${min} and ${max}`);
  }

  return value;
}

export function counts(
  region: Pick<CalendarRegionData, 'sfai' | 'provenance' | 'years'>,
): Pick<CalendarRegionData, 'scoredCells' | 'alertCells' | 'crisisCells'> {
  let scoredCells = 0;
  let alertCells = 0;
  let crisisCells = 0;

  for (let yearIndex = 0; yearIndex < region.years.length; yearIndex += 1) {
    for (let pentadIndex = 0; pentadIndex < PENTADS; pentadIndex += 1) {
      const sfai = region.sfai[yearIndex][pentadIndex];

      if (region.provenance[yearIndex][pentadIndex] === 2 && sfai !== null) {
        fail(`${region.years[yearIndex]} pentad ${pentadIndex + 1} is modelled but carries SFAI`);
      }

      if (sfai === null) continue;

      scoredCells += 1;
      if (sfai >= ALERT_SIGMA) alertCells += 1;
      if (sfai >= CRISIS_SIGMA) crisisCells += 1;
    }
  }

  return { scoredCells, alertCells, crisisCells };
}

function buildRegion(id: RegionId, raw: Json): CalendarRegionData {
  const years = yearsOf(raw.years, `${id}.years`);
  const hfd = numbersOf(raw.hfd_matrix, `${id}.hfd_matrix`);
  const sfai = nullableNumbersOf(raw.sfai_matrix, `${id}.sfai_matrix`);
  const provenance = provenanceOf(raw.cell_provenance_matrix, `${id}.cell_provenance_matrix`);
  const observedPentad = integerOf(raw.observed_pentad, `${id}.observed_pentad`, 1, PENTADS);
  const signalCounts = counts({ years, sfai, provenance });

  let maxHfd = 0;
  for (const row of hfd) {
    for (const value of row) {
      maxHfd = Math.max(maxHfd, value);
    }
  }

  if (maxHfd <= 0) {
    fail(`${id}.hfd_matrix must contain a positive value`);
  }

  return {
    id,
    years,
    hfd,
    sfai,
    provenance,
    observedPentad,
    maxHfd,
    observedYears: years.filter((_, yearIndex) => provenance[yearIndex].some((value) => value < 2)),
    ...signalCounts,
  };
}

export function buildArtifact(raw: Json): CalendarDataset {
  const regions = {} as Record<RegionId, CalendarRegionData>;

  for (const id of REGION_IDS) {
    regions[id] = buildRegion(id, record(raw[id], id));
  }

  const start = regions.mekong.years[0];
  const end = regions.mekong.years[regions.mekong.years.length - 1];

  for (const id of REGION_IDS) {
    if (regions[id].years[0] !== start || regions[id].years.at(-1) !== end) {
      fail(`${id} does not share the ${start}–${end} period`);
    }
  }

  return { period: { start, end }, unit: 'density', regions };
}
