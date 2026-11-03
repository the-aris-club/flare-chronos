'use client';

import { useEffect, useRef } from 'react';
import { useLocale, useTranslations } from 'next-intl';
import { formatDecimal } from '@/lib/workbench/format';
import type { MapHover } from '@/lib/workbench/map-data';

export function MapTooltip({
  hover,
  container,
}: {
  hover: MapHover | null;
  container: React.RefObject<HTMLDivElement | null>;
}) {
  const t = useTranslations('Map');
  const locale = useLocale();
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!hover || !ref.current || !container.current) return;
    const bounds = container.current.getBoundingClientRect();
    const x = Math.max(8, Math.min(hover.clientX - bounds.left + 12, bounds.width - 220));
    const y = Math.max(8, Math.min(hover.clientY - bounds.top + 12, bounds.height - 96));
    ref.current.style.setProperty('--tip-x', `${x}px`);
    ref.current.style.setProperty('--tip-y', `${y}px`);
  }, [hover, container]);

  if (!hover) return null;
  const sensor = hover.point.s === 'm' ? 'MODIS' : 'VIIRS';
  const status =
    hover.status === 'keep'
      ? t('kept')
      : hover.status === 'static'
        ? t('excludedStatic')
        : hover.status === 'saa'
          ? t('excludedSaa')
          : hover.status === 'sza'
            ? t('excludedSza')
            : t('duplicate');

  return (
    <div
      ref={ref}
      className="fc-map-tip border-line bg-panel/95 pointer-events-none absolute z-20 rounded-md border p-2"
    >
      <span className="text-meta block font-semibold">
        {sensor} · {hover.point.pf || sensor}
      </span>
      <span className="text-micro text-ink-muted mt-0.5 block font-mono">
        {hover.point.dn === 'N' ? t('night') : t('day')} ·{' '}
        {t('scan', { value: formatDecimal(hover.point.ang, locale) })} ·{' '}
        {formatDecimal(hover.point.sc * hover.point.tr, locale)} km²
      </span>
      <span className="text-micro text-ink-subtle mt-0.5 block">{status}</span>
    </div>
  );
}
