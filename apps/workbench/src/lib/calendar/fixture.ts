import {
  REGION_IDS,
  type CalendarDataset,
  type CalendarRegionData,
  type Provenance,
  type RegionId,
} from './types';
import { PENTADS, counts, fail, record, yearsOf, type Json } from './parse';

type FixtureRegion = {
  hfd: Record<string, number[]>;
  z: Record<string, (number | null)[]>;
  obs: Record<string, boolean[]>;
  vmaxF: number;
};

function fixtureRow<T>(source: Record<string, T[]>, year: number, name: string): T[] {
  const row = source[String(year)];

  if (!Array.isArray(row) || row.length !== PENTADS + 1) {
    fail(`${name}[${year}] must have ${PENTADS + 1} entries`);
  }

  return row.slice(1);
}

function buildRegion(id: RegionId, raw: FixtureRegion, years: number[]): CalendarRegionData {
  const hfd = years.map((year) => fixtureRow(raw.hfd, year, `${id}.hfd`));
  const z = years.map((year) => fixtureRow(raw.z, year, `${id}.z`));
  const obs = years.map((year) => fixtureRow(raw.obs, year, `${id}.obs`));

  const provenance = obs.map((row) => row.map((value) => (value ? 0 : 2) as Provenance));
  const sfai = z.map((row, yearIndex) =>
    row.map((value, pentadIndex) => (obs[yearIndex][pentadIndex] ? value : null)),
  );

  let observedPentad = 1;
  let peakValue = Number.NEGATIVE_INFINITY;
  for (const row of sfai) {
    row.forEach((value, index) => {
      if (value !== null && value > peakValue) {
        peakValue = value;
        observedPentad = index + 1;
      }
    });
  }

  return {
    id,
    years,
    hfd,
    sfai,
    provenance,
    observedPentad,
    maxHfd: raw.vmaxF,
    observedYears: years.filter((_, yearIndex) => obs[yearIndex].some(Boolean)),
    ...counts({ years, sfai, provenance }),
  };
}

export function buildDesignFixture(raw: Json): CalendarDataset {
  const years = yearsOf(raw.years, 'fixture.years');
  const regions = {} as Record<RegionId, CalendarRegionData>;

  for (const id of REGION_IDS) {
    regions[id] = buildRegion(id, record(raw[id], id) as unknown as FixtureRegion, years);
  }

  return {
    period: { start: years[0], end: years[years.length - 1] },
    unit: 'detections',
    regions,
  };
}
