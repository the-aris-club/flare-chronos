'use client';

import { useLocale, useTranslations } from 'next-intl';
import { formatCount } from '@/lib/workbench/format';

export function MapScale({ pxPerKm }: { pxPerKm: number }) {
  const t = useTranslations('Map');
  const locale = useLocale();
  const target = 90 / pxPerKm;
  const power = 10 ** Math.floor(Math.log10(target));
  const barKm =
    [1, 2, 5, 10]
      .map((step) => step * power)
      .filter((value) => value <= target)
      .at(-1) ?? power;
  const barPx = Math.max(24, Math.round(barKm * pxPerKm));

  return (
    <div className="border-line bg-panel/95 text-micro text-ink-muted tablet:bottom-9 absolute right-2 bottom-16 rounded-md border px-2 py-1">
      <svg width={barPx} height={8} aria-hidden="true">
        <line x1={0} y1={4} x2={barPx} y2={4} stroke="currentColor" strokeWidth={1} />
        <line x1={0.5} y1={0} x2={0.5} y2={8} stroke="currentColor" strokeWidth={1} />
        <line
          x1={barPx - 0.5}
          y1={0}
          x2={barPx - 0.5}
          y2={8}
          stroke="currentColor"
          strokeWidth={1}
        />
      </svg>
      <span className="font-mono">{t('scale', { km: formatCount(barKm, locale) })}</span>
    </div>
  );
}

export function MapFooter() {
  const t = useTranslations('Map');
  return (
    <div className="border-line bg-panel/95 text-micro text-ink-muted absolute inset-x-0 bottom-0 flex flex-wrap items-center gap-x-3 gap-y-0.5 border-t px-3 py-1.5">
      <span className="text-ink-subtle font-mono">{t('borderCredit')}</span>
      <span className="ml-auto font-mono">{t('scaleNote')}</span>
    </div>
  );
}
