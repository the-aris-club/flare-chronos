import { formatSigma } from '@/lib/calendar/format';
import type { CalendarRegionData } from '@/lib/calendar/types';
import { formatCount, formatDecimal } from '@/lib/workbench/format';
import type { AnnualSeries, Calibration, Epoch, MapPhysics } from '@/lib/workbench/types';

type Translate = (key: string, values?: Record<string, string | number>) => string;

export type EvidenceColumn = {
  label: string;
  align?: 'left' | 'right';
};

export type EvidenceTableSpec = {
  caption: string;
  columns: EvidenceColumn[];
  rows: string[][];
};

type Args = {
  series: AnnualSeries;
  epochs: Epoch[];
  physics: MapPhysics;
  calibration: Calibration;
  calendar: CalendarRegionData;
  locale: string;
  t: Translate;
};

export function buildEvidenceTables({
  series,
  epochs,
  physics,
  calibration,
  calendar,
  locale,
  t,
}: Args): Record<number, EvidenceTableSpec | null> {
  const metric = (value: number | null) => (value === null ? '—' : formatSigma(value, locale));

  return {
    1: {
      caption: t('table1'),
      columns: [{ label: t('item') }, { label: t('value'), align: 'right' }],
      rows: [
        ['MODIS nadir', `${formatDecimal(physics.modisNadir, locale)} km²`],
        ['MODIS edge 55°', `${formatDecimal(physics.modisEdge, locale)} km²`],
        ['VIIRS nadir', `${formatDecimal(physics.viirsNadir, locale)} km²`],
        ['VIIRS edge 56°', `${formatDecimal(physics.viirsEdge, locale)} km²`],
        ['MODIS edge / VIIRS nadir', `${formatDecimal(physics.ratio, locale)}×`],
      ],
    },
    2: {
      caption: t('table2'),
      columns: [
        { label: t('year') },
        { label: t('raw'), align: 'right' },
        { label: t('episodes'), align: 'right' },
        { label: t('harmonized'), align: 'right' },
        { label: t('sensors'), align: 'right' },
      ],
      rows: epochs.map((epoch) => [
        String(epoch.year),
        formatCount(epoch.raw, locale),
        epoch.episodes === null ? '—' : formatCount(epoch.episodes, locale),
        formatCount(epoch.harmonized, locale),
        String(epoch.sensors),
      ]),
    },
    3: {
      caption: t('table3'),
      columns: [
        { label: t('statistic') },
        { label: t('raw'), align: 'right' },
        { label: t('harmonized'), align: 'right' },
      ],
      rows: [
        [
          t('r2'),
          formatDecimal(calibration.r2Raw, locale, 3),
          formatDecimal(calibration.r2Harmonized, locale, 3),
        ],
        [
          t('rmse'),
          formatDecimal(calibration.rmseRaw, locale, 1),
          formatDecimal(calibration.rmseHarmonized, locale, 1),
        ],
        [
          t('ks'),
          formatDecimal(calibration.ksBefore, locale, 4),
          formatDecimal(calibration.ksAfter, locale, 4),
        ],
        [
          t('pairsLabel'),
          formatCount(calibration.pairs, locale),
          formatCount(calibration.pairs, locale),
        ],
      ],
    },
    4: {
      caption: t('table4'),
      columns: [
        { label: t('year') },
        { label: t('raw'), align: 'right' },
        { label: t('harmonized'), align: 'right' },
        { label: t('measured') },
      ],
      rows: series.years.map((year, index) => [
        String(year),
        formatCount(series.raw[index], locale),
        formatCount(series.harmonized[index], locale),
        series.measured.includes(year) ? t('measured') : t('interpolated'),
      ]),
    },
    5: {
      caption: t('table5'),
      columns: [
        { label: t('year') },
        { label: t('observedPentads'), align: 'right' },
        { label: t('peakSfai'), align: 'right' },
        { label: t('alerts'), align: 'right' },
        { label: t('crisis'), align: 'right' },
      ],
      rows: calendar.years.map((year, yearIndex) => {
        const scores = calendar.sfai[yearIndex];
        const observed = calendar.provenance[yearIndex].filter((value) => value !== 2).length;
        const scored = scores.filter((value): value is number => value !== null);
        const peak = scored.length > 0 ? Math.max(...scored) : null;

        return [
          String(year),
          String(observed),
          metric(peak),
          String(scores.filter((value) => value !== null && value >= 2.2).length),
          String(scores.filter((value) => value !== null && value >= 2.5).length),
        ];
      }),
    },
  };
}
