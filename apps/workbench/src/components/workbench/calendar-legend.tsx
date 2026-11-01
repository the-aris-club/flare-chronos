'use client';

import { useTranslations } from 'next-intl';
import { useTheme } from '@/components/ui/theme-provider';
import { divColor, seqColor } from '@/lib/calendar/ramp';
import type { Metric } from '@/lib/calendar/types';

type CalendarLegendProps = {
  metric: Metric;
  scoredCells: number;
};

export function CalendarLegend({ metric, scoredCells }: CalendarLegendProps) {
  const t = useTranslations('Calendar.legend');
  const tStatus = useTranslations('Calendar.status');
  const { theme } = useTheme();

  const stops =
    metric === 'hfd'
      ? [0, 0.25, 0.5, 0.75, 1].map((value) => seqColor(value, theme))
      : [-3, -1.5, 0, 1.5, 3].map((value) => divColor(value, theme));

  const observedFill = metric === 'hfd' ? seqColor(0.6, theme) : divColor(1.2, theme);

  return (
    <div className="text-label text-ink-muted flex flex-wrap items-center gap-x-3 gap-y-1">
      <span className="inline-flex items-center gap-1.5 whitespace-nowrap">
        <span className="text-micro text-ink-subtle font-mono">
          {t(metric === 'hfd' ? 'hfdLow' : 'sfaiLow')}
        </span>
        <svg width={70} height={8} aria-hidden="true" className="rounded-sm">
          {stops.map((fill, index) => (
            <rect key={fill} x={index * 14} y={0} width={14} height={8} fill={fill} />
          ))}
        </svg>
        <span className="text-micro text-ink-subtle font-mono">
          {t(metric === 'hfd' ? 'hfdHigh' : 'sfaiHigh')}
        </span>
      </span>

      <LegendItem label={t('observed')}>
        <svg width={14} height={9} aria-hidden="true">
          <rect width={14} height={9} rx={1} fill={observedFill} />
        </svg>
      </LegendItem>

      {metric === 'sfai' && (
        <LegendItem label={tStatus('notScored')}>
          <svg width={14} height={9} aria-hidden="true">
            <rect width={14} height={9} rx={1} fill="var(--raised)" />
          </svg>
        </LegendItem>
      )}

      <LegendItem label={t('modelled')}>
        <svg width={14} height={9} aria-hidden="true">
          <rect width={14} height={9} rx={1} fill="var(--panel)" />
          <rect width={14} height={9} rx={1} fill="url(#fc-hatch)" />
        </svg>
      </LegendItem>

      <LegendItem label={t('alert')}>
        <svg width={14} height={9} aria-hidden="true">
          <rect width={14} height={9} rx={1} fill={observedFill} />
          <rect
            x={0.75}
            y={0.75}
            width={12.5}
            height={7.5}
            rx={0.5}
            fill="none"
            stroke="var(--cyan)"
            strokeWidth={1.5}
          />
        </svg>
      </LegendItem>

      <LegendItem label={t('crisis')}>
        <svg width={14} height={9} aria-hidden="true">
          <rect width={14} height={9} rx={1} fill={observedFill} />
          <path d="M0 0h4L0 4z" fill="var(--cyan)" />
          <rect
            x={0.75}
            y={0.75}
            width={12.5}
            height={7.5}
            rx={0.5}
            fill="none"
            stroke="var(--cyan)"
            strokeWidth={1.5}
          />
        </svg>
      </LegendItem>

      {metric === 'sfai' && (
        <span className="text-micro text-ink-subtle font-mono">
          {t('sfaiScored', { count: scoredCells })}
        </span>
      )}
    </div>
  );
}

function LegendItem({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center gap-1.5 whitespace-nowrap">
      {children}
      {label}
    </span>
  );
}
