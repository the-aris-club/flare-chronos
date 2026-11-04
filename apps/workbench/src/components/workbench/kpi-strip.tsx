'use client';

import { useLocale, useTranslations } from 'next-intl';
import { formatSigma } from '@/lib/calendar/format';
import { pentadDates } from '@/lib/calendar/pentad';
import { ALERT_SIGMA, CRISIS_SIGMA } from '@/lib/calendar/constants';
import { formatCount } from '@/lib/workbench/format';
import type { AnnualSeries, Epoch, MapFilters, SfaiPeak } from '@/lib/workbench/types';
import type { MapCounts } from '@/lib/workbench/map-data';

type KpiStripProps = {
  series: AnnualSeries;
  epoch: Epoch | undefined;
  year: number;
  peak: SfaiPeak;
  filters: MapFilters;
  counts?: MapCounts;
};

function Arrow({ label }: { label: string }) {
  return (
    <div
      aria-hidden="true"
      className="text-ink-subtle tablet:flex hidden flex-col items-center justify-center gap-0.5 px-1"
    >
      <svg width={28} height={10} viewBox="0 0 28 10">
        <line x1={1} y1={5} x2={24} y2={5} stroke="currentColor" strokeWidth={1.2} />
        <path d="M21 1.5 L26 5 L21 8.5" fill="none" stroke="currentColor" strokeWidth={1.2} />
      </svg>
      <span className="text-micro font-mono">{label}</span>
    </div>
  );
}

export function KpiStrip({ series, epoch, year, peak, filters, counts }: KpiStripProps) {
  const t = useTranslations('Kpi');
  const locale = useLocale();
  const raw = epoch?.raw ?? series.raw[series.years.indexOf(year)] ?? 0;
  const episodes = epoch?.episodes ?? null;
  const sensors = epoch?.sensors ?? 0;
  const score = peak.value;
  const dates = peak.pentad ? pentadDates(peak.pentad, locale) : null;
  const alert = score !== null && score >= ALERT_SIGMA;
  const crisis = score !== null && score >= CRISIS_SIGMA;
  const filtersOff = Object.values(filters).filter((value) => !value).length;
  const added = counts
    ? (filters.sza ? 0 : counts.sza) +
      (filters.saa ? 0 : counts.saa) +
      (filters.static ? 0 : counts.static) +
      (filters.dedup ? 0 : counts.dup)
    : 0;
  const displayEpisodes = episodes === null ? null : episodes + added;

  return (
    <section
      data-tour="kpi"
      aria-label={t('title')}
      className="border-line bg-panel flex flex-wrap items-stretch rounded-lg border"
    >
      <div className="flex min-w-40 flex-1 flex-col justify-center gap-1 px-3 py-2">
        <span className="text-micro text-ink-subtle font-mono tracking-widest uppercase">
          {t('raw')}
        </span>
        <div className="flex flex-wrap items-baseline gap-2">
          <span className="text-metric text-raw font-mono font-semibold tracking-tight">
            {formatCount(raw, locale)}
          </span>
          <span className="text-meta text-ink-subtle">{t('rawSub', { year, count: sensors })}</span>
        </div>
      </div>

      <Arrow label={t('filters')} />

      <div className="flex min-w-40 flex-1 flex-col justify-center gap-1 px-3 py-2">
        <span className="text-micro text-ink-subtle font-mono tracking-widest uppercase">
          {t('episodes')}
        </span>
        <div className="flex flex-wrap items-baseline gap-2">
          <span className="text-metric font-mono font-semibold tracking-tight">
            {displayEpisodes === null ? '—' : formatCount(displayEpisodes, locale)}
          </span>
          <span className="text-meta text-ink-subtle">
            {episodes === null
              ? t('notMeasured')
              : filtersOff > 0
                ? t('filtersOff', { count: filtersOff })
                : t('afterFilters')}
          </span>
        </div>
      </div>

      <Arrow label={t('vsNorm')} />

      <div className="flex min-w-48 flex-1 flex-col justify-center gap-1 px-3 py-2">
        <span className="text-micro text-ink-subtle font-mono tracking-widest uppercase">
          {t('sfai')} · {year}
        </span>
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-metric font-mono font-semibold tracking-tight">
            {score === null ? '—' : `${formatSigma(score, locale)}σ`}
          </span>
          <span
            className={`text-label inline-flex h-5 items-center rounded-sm border px-1.5 font-mono ${
              alert ? 'border-cyan text-ink' : 'border-line-strong text-ink-subtle'
            }`}
          >
            {score === null
              ? t('notScored')
              : crisis
                ? t('crisis')
                : alert
                  ? t('alert')
                  : t('below')}
          </span>
        </div>
        <span className="text-meta text-ink-subtle truncate">
          {peak.pentad && dates ? t('peak', { pentad: peak.pentad, dates }) : t('notScored')}
        </span>
      </div>
    </section>
  );
}
