'use client';

import { useLocale, useTranslations } from 'next-intl';
import { formatDecimal, formatPercent } from '@/lib/workbench/format';
import type { AnnualSeries, Calibration } from '@/lib/workbench/types';

export function ConclusionStrip({
  series,
  calibration,
  measured,
  total,
}: {
  series: AnnualSeries;
  calibration: Calibration;
  measured: number;
  total: number;
}) {
  const t = useTranslations('Conclusion');
  const locale = useLocale();

  return (
    <p
      className="border-line bg-panel text-meta text-ink-muted max-tablet:hidden mb-2.5 rounded-md border px-3 py-1.5 font-mono"
      data-testid="conclusion-strip"
    >
      <span className="text-ink-subtle uppercase">{t('label')}</span>{' '}
      {t('text', {
        from: series.growthWindow[0],
        to: series.growthWindow[1],
        raw: formatPercent(series.rawGrowthPct, locale),
        trend: formatPercent(series.trendPct, locale, 1),
        ksBefore: formatDecimal(calibration.ksBefore, locale, 4),
        ksAfter: formatDecimal(calibration.ksAfter, locale, 4),
        measured,
        total,
      })}
    </p>
  );
}
