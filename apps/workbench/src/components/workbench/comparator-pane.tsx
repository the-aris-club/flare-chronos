'use client';

import { useCallback, useMemo, useState } from 'react';
import { useLocale, useTranslations } from 'next-intl';
import {
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceDot,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  type TooltipContentProps,
} from 'recharts';
import { formatCompact, formatCount, formatPercent } from '@/lib/workbench/format';
import { SegmentedControl } from '@/components/ui/segmented-control';
import { useIsTablet } from '@/lib/use-media';
import { SensorTracks } from './sensor-tracks';
import type { AnnualSeries } from '@/lib/workbench/types';

type Mode = 'both' | 'raw' | 'harmonized';

const chartMargin = { top: 16, right: 18, bottom: 4, left: 2 } as const;
const tickStyle = { fill: 'var(--text-subtle)', fontSize: 10 };
const axisLineStyle = { stroke: 'var(--line)' };

type ChartRow = {
  year: number;
  raw: number;
  harmonized: number;
  measured: boolean;
};

type ChartTooltipProps = Partial<TooltipContentProps<number, string>> & {
  locale: string;
  rawLabel: string;
  harmonizedLabel: string;
};

function ChartTooltip({
  active,
  payload,
  label,
  locale,
  rawLabel,
  harmonizedLabel,
}: ChartTooltipProps) {
  if (!active || !payload?.length) return null;

  const row = payload[0]?.payload as ChartRow | undefined;
  if (!row) return null;

  return (
    <div className="border-line bg-panel text-meta rounded-md border px-2 py-1.5">
      <div className="font-mono font-semibold">{label}</div>
      <div className="text-raw flex items-center justify-between gap-4">
        <span>{rawLabel}</span>
        <span className="font-mono">{formatCount(row.raw, locale)}</span>
      </div>
      <div className="text-teal flex items-center justify-between gap-4">
        <span>{harmonizedLabel}</span>
        <span className="font-mono">{formatCount(row.harmonized, locale)}</span>
      </div>
    </div>
  );
}

export function ComparatorPane({
  series,
  regionLabel,
  visible,
}: {
  series: AnnualSeries;
  regionLabel: string;
  visible: boolean;
}) {
  const t = useTranslations('Comparator');
  const locale = useLocale();
  const showNinoLabels = useIsTablet();
  const [mode, setMode] = useState<Mode>('both');

  const rows = useMemo<ChartRow[]>(
    () =>
      series.years.map((year, index) => ({
        year,
        raw: series.raw[index],
        harmonized: series.harmonized[index],
        measured: series.measured.includes(year),
      })),
    [series],
  );

  const measured = useMemo(() => rows.filter((row) => row.measured), [rows]);

  const modeOptions = useMemo<ReadonlyArray<{ value: Mode; label: string }>>(
    () => [
      { value: 'both', label: t('both') },
      { value: 'raw', label: t('raw') },
      { value: 'harmonized', label: t('harmonized') },
    ],
    [t],
  );

  const yearTicks = useMemo(
    () =>
      series.years.filter(
        (year, index) => index === 0 || index === series.years.length - 1 || year % 5 === 0,
      ),
    [series.years],
  );

  const formatTick = useCallback((value: number) => formatCompact(value, locale), [locale]);

  const nino2010Label = useMemo(
    () =>
      showNinoLabels
        ? {
            value: t('elnino', { year: 2010 }),
            fill: 'var(--text-subtle)',
            fontSize: 9,
            position: 'insideTopLeft' as const,
          }
        : undefined,
    [showNinoLabels, t],
  );

  const nino2016Label = useMemo(
    () =>
      showNinoLabels
        ? {
            value: t('elnino', { year: 2016 }),
            fill: 'var(--text-subtle)',
            fontSize: 9,
            position: 'insideTopRight' as const,
          }
        : undefined,
    [showNinoLabels, t],
  );

  const tooltipContent = useMemo(
    () => <ChartTooltip locale={locale} rawLabel={t('raw')} harmonizedLabel={t('harmonized')} />,
    [locale, t],
  );

  return (
    <section
      data-tour="cmp"
      aria-labelledby="comparator-title"
      className="border-line bg-panel flex h-105 flex-col overflow-hidden rounded-lg border"
    >
      <header className="border-line flex flex-wrap items-center gap-x-3 gap-y-1.5 border-b px-3 py-2">
        <h2 id="comparator-title" className="text-body font-semibold">
          {t('title')}
        </h2>
        <span className="text-label text-ink-subtle font-mono">{regionLabel}</span>
        <div className="ml-auto">
          <SegmentedControl
            label={t('mode')}
            value={mode}
            options={modeOptions}
            onChange={setMode}
          />
        </div>
      </header>

      <div className="min-h-0 flex-1 px-2 pt-2">
        {visible && (
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={rows} margin={chartMargin}>
              <CartesianGrid vertical={false} stroke="var(--line)" />
              <XAxis
                dataKey="year"
                ticks={yearTicks}
                tick={tickStyle}
                tickLine={false}
                axisLine={axisLineStyle}
              />
              <YAxis
                width={54}
                tickFormatter={formatTick}
                tick={tickStyle}
                tickLine={false}
                axisLine={false}
              />
              <ReferenceLine
                x={2010}
                stroke="var(--line-strong)"
                strokeDasharray="3 3"
                label={nino2010Label}
              />
              <ReferenceLine
                x={2016}
                stroke="var(--line-strong)"
                strokeDasharray="3 3"
                label={nino2016Label}
              />
              {mode !== 'harmonized' && (
                <Line
                  type="stepAfter"
                  dataKey="raw"
                  name={t('raw')}
                  stroke="var(--raw)"
                  strokeWidth={1.6}
                  dot={false}
                  isAnimationActive={false}
                />
              )}
              {mode !== 'raw' && (
                <Line
                  type="stepAfter"
                  dataKey="harmonized"
                  name={t('harmonized')}
                  stroke="var(--teal)"
                  strokeWidth={1.6}
                  dot={false}
                  isAnimationActive={false}
                />
              )}
              {mode !== 'raw' &&
                rows.map((row) => (
                  <ReferenceDot
                    key={row.year}
                    x={row.year}
                    y={row.harmonized}
                    r={row.measured ? 2.5 : 2}
                    fill={row.measured ? 'var(--teal)' : 'var(--panel)'}
                    stroke="var(--teal)"
                    strokeWidth={1}
                  />
                ))}
              <Tooltip content={tooltipContent} cursor={false} />
            </ComposedChart>
          </ResponsiveContainer>
        )}
      </div>

      <SensorTracks years={series.years} />

      <footer className="border-line text-micro text-ink-muted flex flex-wrap items-center gap-x-4 gap-y-1 border-t px-3 py-1.5">
        <span className="inline-flex items-center gap-1.5">
          <svg width={16} height={3} aria-hidden="true">
            <line x1={0} y1={1.5} x2={16} y2={1.5} stroke="var(--raw)" strokeWidth={2} />
          </svg>
          {t('raw')}
        </span>
        <span className="inline-flex items-center gap-1.5">
          <svg width={16} height={3} aria-hidden="true">
            <line x1={0} y1={1.5} x2={16} y2={1.5} stroke="var(--teal)" strokeWidth={2} />
          </svg>
          {t('harmonized')}
        </span>
        <span className="inline-flex items-center gap-1.5">
          <svg width={8} height={8} aria-hidden="true">
            <circle cx={4} cy={4} r={3} fill="var(--teal)" />
          </svg>
          {t('measured')}
        </span>
        <span className="inline-flex items-center gap-1.5">
          <svg width={8} height={8} aria-hidden="true">
            <circle cx={4} cy={4} r={2.5} fill="var(--panel)" stroke="var(--teal)" />
          </svg>
          {t('interpolated')}
        </span>
        <span className="inline-flex items-center gap-1.5">
          <svg width={16} height={3} aria-hidden="true">
            <line
              x1={0}
              y1={1.5}
              x2={16}
              y2={1.5}
              stroke="var(--amber)"
              strokeWidth={1.2}
              strokeDasharray="3 2"
            />
          </svg>
          {t('elninoShort')}
        </span>
        <span className="ml-auto font-mono">
          {t('summary', {
            start: series.growthWindow[0],
            end: series.growthWindow[1],
            pct: formatPercent(series.rawGrowthPct, locale),
            trend: formatPercent(series.trendPct, locale, 1),
          })}
        </span>
      </footer>

      <span className="sr-only">
        {t('aria', {
          start: series.years[0],
          end: series.years[series.years.length - 1],
          measured: measured.length,
        })}
      </span>
    </section>
  );
}
