'use client';

import { useLocale, useTranslations } from 'next-intl';
import { AmIcon, ICON } from '@/components/ui/icon';
import { formatCount, formatDecimal } from '@/lib/workbench/format';
import type { Calibration, MapPhysics } from '@/lib/workbench/types';

export function EvidenceQuickLook({
  physics,
  calibration,
  onOpen,
}: {
  physics: MapPhysics;
  calibration: Calibration;
  onOpen: () => void;
}) {
  const t = useTranslations('Evidence');
  const locale = useLocale();
  const reduction = formatDecimal(
    (1 - calibration.ksAfter / calibration.ksBefore) * 100,
    locale,
    1,
  );

  return (
    <section
      aria-label={t('quickTitle')}
      className="border-line bg-panel flex flex-col gap-2 rounded-lg border p-3 xl:hidden"
    >
      <span className="text-label text-ink-subtle font-mono tracking-widest uppercase">
        {t('quickTitle')}
      </span>
      <div className="tablet:grid-cols-2 grid grid-cols-1 gap-2">
        <div className="border-line rounded-md border p-2.5">
          <span className="text-micro text-ink-subtle font-mono uppercase">{t('quickScan')}</span>
          <span className="text-metric block font-mono font-semibold">
            {formatDecimal(physics.ratio, locale)}×
          </span>
          <span className="text-meta text-ink-muted block">
            {t('quickScanDetail', {
              modis: formatDecimal(physics.modisEdge, locale),
              viirs: formatDecimal(physics.viirsNadir, locale),
            })}
          </span>
        </div>
        <div className="border-line rounded-md border p-2.5">
          <span className="text-micro text-ink-subtle font-mono uppercase">{t('quickKs')}</span>
          <span className="text-metric block font-mono font-semibold">
            <span className="text-raw">{formatDecimal(calibration.ksBefore, locale, 4)}</span>
            {' → '}
            <span className="text-teal">{formatDecimal(calibration.ksAfter, locale, 4)}</span>
          </span>
          <span className="text-meta text-ink-muted block">
            {t('quickPairs', {
              pairs: formatCount(calibration.pairs, locale),
              pct: reduction,
            })}
          </span>
        </div>
      </div>
      <button
        type="button"
        onClick={onOpen}
        className="border-line-strong text-meta hover:bg-chip inline-flex h-8 items-center gap-1.5 self-start rounded-md border px-2.5 font-medium"
      >
        <AmIcon icon={ICON.evidence} size="sm" />
        {t('quickOpen')}
      </button>
    </section>
  );
}
