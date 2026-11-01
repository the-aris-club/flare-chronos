'use client';

import { useTranslations } from 'next-intl';
import { useTheme } from '@/components/ui/theme-provider';
import { formatHfd, formatSigma } from '@/lib/calendar/format';
import type { CalendarCell } from '@/lib/calendar/model';
import { pentadDates } from '@/lib/calendar/pentad';
import { divColor, seqColor } from '@/lib/calendar/ramp';
import type { HfdUnit, Metric } from '@/lib/calendar/types';

type CalendarSummaryProps = {
  cell: CalendarCell;
  hovering: boolean;
  metric: Metric;
  unit: HfdUnit;
  maxHfd: number;
  locale: string;
};

export function CalendarSummary({
  cell,
  hovering,
  metric,
  unit,
  maxHfd,
  locale,
}: CalendarSummaryProps) {
  const t = useTranslations('Calendar.readout');
  const tStatus = useTranslations('Calendar.status');
  const { theme } = useTheme();

  const status = cell.observed ? tStatus('observed') : tStatus('modelled');
  const when = t('when', {
    year: cell.year,
    pentad: cell.pentad,
    dates: pentadDates(cell.pentad, locale),
  });

  const value =
    metric === 'hfd'
      ? t(unit === 'density' ? 'hfd' : 'hfdDetections', {
          value: formatHfd(cell.hfd, locale),
        })
      : cell.sfai === null
        ? t('notScored')
        : t('sfai', { value: formatSigma(cell.sfai, locale) });

  const flag = cell.crisis ? t('crisis') : cell.alert ? t('alert') : null;

  const fill =
    metric === 'hfd'
      ? seqColor(Math.sqrt(cell.hfd / maxHfd), theme)
      : cell.sfai === null
        ? 'var(--raised)'
        : divColor(cell.sfai, theme);

  return (
    <div className="border-line border-t">
      <p className="sr-only" aria-live="polite">
        {[when, status, value, flag].filter(Boolean).join('. ')}
      </p>

      <div
        aria-hidden="true"
        className="text-meta flex flex-wrap items-center gap-x-4 gap-y-1 px-3 py-2"
      >
        <span className="inline-flex min-w-0 items-baseline gap-2">
          <span className="text-micro text-ink-subtle font-mono tracking-widest uppercase">
            {hovering ? t('hover') : t('selected')}
          </span>
          <span className="font-mono font-semibold whitespace-nowrap">{when}</span>
        </span>

        <span className="text-ink-muted inline-flex items-center gap-1.5 whitespace-nowrap">
          <svg width={12} height={8} aria-hidden="true" className="shrink-0">
            <rect width={12} height={8} rx={1} fill={fill} />
            {!cell.observed && <rect width={12} height={8} rx={1} fill="url(#fc-hatch)" />}
          </svg>
          {status}
        </span>

        <span className="font-mono whitespace-nowrap">{value}</span>

        <span
          className={`border-cyan text-label inline-flex h-5 items-center rounded-sm border-2 px-1.5 font-mono ${
            flag ? 'text-ink' : 'invisible'
          }`}
        >
          {flag ?? t('alert')}
        </span>

        <span className="text-label text-ink-subtle tablet:inline ml-auto hidden whitespace-nowrap">
          {t('hint')}
        </span>
        <span className="text-label text-ink-subtle tablet:hidden ml-auto whitespace-nowrap">
          {t('hintTouch')}
        </span>
      </div>
    </div>
  );
}
