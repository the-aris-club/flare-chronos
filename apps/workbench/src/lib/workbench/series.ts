import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { cache } from 'react';
import type { CalendarDataset, RegionId } from '@/lib/calendar/types';
import type { AnnualSeries, Epoch, SfaiPeak, WorkbenchData } from './types';

type RawEpoch = {
  year: number;
  date_window: string;
  sources: string[];
  total_raw_detections: number;
  deduplicated_fire_episodes: number;
  harmonized_viirs_eq_episodes: number;
  saa_rejected_count: number;
  daynight_sza_reclassified_pct: number;
};

type RawPhysics = {
  modis_nadir_area_km2: number;
  modis_edge_55deg_area_km2: number;
  viirs_nadir_area_km2: number;
  viirs_edge_56deg_area_km2: number;
  max_area_ratio_modis_edge_to_viirs_nadir: number;
};

type RawCalibration = {
  raw_r2: number;
  harm_r2: number;
  raw_rmse: number;
  harm_rmse: number;
  ks_before: number;
  ks_after: number;
  n_pairs: number;
  holdout: {
    raw_rmse_mw: number;
    harmonized_rmse_mw: number;
    rmse_gain_ci95_mw: [number, number];
    train_last_year: number;
  };
};

type RawEmpirical = {
  regime_shift_series: Record<
    RegionId,
    {
      years: number[];
      raw_counts_by_year: Record<string, number>;
      modis_reference_counts_by_year: Record<string, number>;
    }
  >;
  mekong_empirical_epochs: RawEpoch[];
  amazon_empirical_epochs: RawEpoch[];
  scan_angle_physics: RawPhysics;
  coincident_calibration: RawCalibration;
};

const REGIONS: RegionId[] = ['mekong', 'amazon'];

/** The raw-growth headline is read between these two Measured Epochs, as on the landing. */
const GROWTH_WINDOW = [2005, 2024] as const;

function fail(message: string): never {
  throw new Error(`Workbench data: ${message}`);
}

function growthPct(raw: number[], start: number, end: number): number {
  const first = raw[start];
  const last = raw[end];
  if (!first) return 0;
  return (last / first - 1) * 100;
}

function trendPct(years: number[], values: number[]): number {
  const n = years.length;
  const meanX = years.reduce((sum, year) => sum + year, 0) / n;
  const meanY = values.reduce((sum, value) => sum + value, 0) / n;

  let numerator = 0;
  let denominator = 0;
  for (let index = 0; index < n; index += 1) {
    numerator += (years[index] - meanX) * (values[index] - meanY);
    denominator += (years[index] - meanX) ** 2;
  }

  if (denominator === 0 || meanY === 0) return 0;
  return (numerator / denominator / meanY) * 100;
}

function sfaiPeaks(calendar: CalendarDataset, region: RegionId) {
  const data = calendar.regions[region];
  const peaks: Record<number, SfaiPeak> = {};

  for (let yearIndex = 0; yearIndex < data.years.length; yearIndex += 1) {
    let value: number | null = null;
    let pentad: number | null = null;

    for (let pentadIndex = 0; pentadIndex < data.sfai[yearIndex].length; pentadIndex += 1) {
      const score = data.sfai[yearIndex][pentadIndex];
      if (score === null) continue;
      if (value === null || score > value) {
        value = score;
        pentad = pentadIndex + 1;
      }
    }

    peaks[data.years[yearIndex]] = { value, pentad };
  }

  return peaks;
}

async function readEmpirical(): Promise<RawEmpirical> {
  const candidates = [
    process.env.EMPIRICAL_DATA_PATH,
    path.resolve(process.cwd(), '../../data/processed/empirical_results.json'),
    path.resolve(process.cwd(), 'data/processed/empirical_results.json'),
  ].filter((value): value is string => Boolean(value));

  const found = await Promise.all(
    candidates.map(async (candidate) => {
      try {
        return JSON.parse(await readFile(candidate, 'utf8')) as RawEmpirical;
      } catch {
        return null;
      }
    }),
  );

  const data = found.find((candidate) => candidate !== null);
  if (!data) fail('no empirical_results.json found');

  return data;
}

export const loadWorkbench = cache(async (calendar: CalendarDataset): Promise<WorkbenchData> => {
  const empirical = await readEmpirical();
  const series = {} as Record<RegionId, AnnualSeries>;
  const epochs = {} as Record<RegionId, Epoch[]>;
  const sfai = {} as Record<RegionId, Record<number, SfaiPeak>>;

  for (const region of REGIONS) {
    const shift = empirical.regime_shift_series[region];
    if (!shift) fail(`${region}.regime_shift_series is missing`);

    const raw = shift.years.map((year) => shift.raw_counts_by_year[String(year)]);
    const harmonized = shift.years.map(
      (year) => shift.modis_reference_counts_by_year[String(year)],
    );

    if (raw.some((value) => typeof value !== 'number')) {
      fail(`${region}.raw_counts_by_year is incomplete`);
    }

    const measured = calendar.regions[region].observedYears;
    const rawEpochs =
      region === 'mekong' ? empirical.mekong_empirical_epochs : empirical.amazon_empirical_epochs;

    const regionEpochs = measured.map((year): Epoch => {
      const epoch = rawEpochs.find((item) => item.year === year);
      if (!epoch) {
        return {
          year,
          date: null,
          raw: shift.raw_counts_by_year[String(year)] ?? 0,
          episodes: null,
          harmonized:
            shift.modis_reference_counts_by_year[String(year)] ??
            fail(`${region} ${year} has no MODIS reference count`),
          sensors: 0,
          saa: 0,
          szaPct: 0,
        };
      }

      return {
        year,
        date: epoch.date_window,
        raw: epoch.total_raw_detections,
        episodes: epoch.deduplicated_fire_episodes,
        harmonized: epoch.harmonized_viirs_eq_episodes,
        sensors: epoch.sources.length,
        saa: epoch.saa_rejected_count,
        szaPct: epoch.daynight_sza_reclassified_pct,
      };
    });

    const start = shift.years.indexOf(GROWTH_WINDOW[0]);
    const end = shift.years.indexOf(GROWTH_WINDOW[1]);
    if (start < 0 || end < 0)
      fail(`${region} regime-shift series must span ${GROWTH_WINDOW.join(' to ')}`);
    if (!GROWTH_WINDOW.every((year) => measured.includes(year))) {
      fail(`${region} growth window ${GROWTH_WINDOW.join('–')} must be Measured Epochs`);
    }

    series[region] = {
      years: shift.years,
      raw,
      harmonized,
      measured,
      rawGrowthPct: growthPct(raw, start, end),
      growthWindow: GROWTH_WINDOW,
      trendPct: trendPct(shift.years.slice(0, end + 1), harmonized.slice(0, end + 1)),
    };
    epochs[region] = regionEpochs;
    sfai[region] = sfaiPeaks(calendar, region);
  }

  const physics = empirical.scan_angle_physics;
  if (!physics) fail('scan_angle_physics is missing');
  const calibration = empirical.coincident_calibration;
  if (!calibration) fail('coincident_calibration is missing');

  return {
    series,
    epochs,
    sfai,
    physics: {
      modisNadir: physics.modis_nadir_area_km2,
      modisEdge: physics.modis_edge_55deg_area_km2,
      viirsNadir: physics.viirs_nadir_area_km2,
      viirsEdge: physics.viirs_edge_56deg_area_km2,
      ratio: physics.max_area_ratio_modis_edge_to_viirs_nadir,
    },
    calibration: {
      r2Raw: calibration.raw_r2,
      r2Harmonized: calibration.harm_r2,
      rmseRaw: calibration.raw_rmse,
      rmseHarmonized: calibration.harm_rmse,
      ksBefore: calibration.ks_before,
      ksAfter: calibration.ks_after,
      pairs: calibration.n_pairs,
      holdout: {
        gainMw: calibration.holdout.raw_rmse_mw - calibration.holdout.harmonized_rmse_mw,
        ciLowMw: calibration.holdout.rmse_gain_ci95_mw[0],
        ciHighMw: calibration.holdout.rmse_gain_ci95_mw[1],
        trainLastYear: calibration.holdout.train_last_year,
      },
    },
  };
});
