'use client';

import { useTranslations } from 'next-intl';
import { AmIcon, ICON } from '@/components/ui/icon';
import type { RegionId } from '@/lib/calendar/types';

export type RegionCardData = {
  id: RegionId;
  name: string;
  coverage: string;
  measured: number[];
  lastEpoch: number;
};

type RegionCardProps = {
  region: RegionCardData;
  yearStart: number;
  total: number;
  highlighted: boolean;
  onHover: (region: RegionId | null) => void;
  onSelect: (region: RegionId) => void;
};

export function RegionCard({
  region,
  yearStart,
  total,
  highlighted,
  onHover,
  onSelect,
}: RegionCardProps) {
  const t = useTranslations('Globe');
  const years = Array.from({ length: total }, (_, index) => yearStart + index);

  return (
    <button
      type="button"
      onClick={() => onSelect(region.id)}
      onMouseEnter={() => onHover(region.id)}
      onMouseLeave={() => onHover(null)}
      onFocus={() => onHover(region.id)}
      onBlur={() => onHover(null)}
      className={`grid grid-cols-[minmax(0,1fr)_auto] gap-x-3 gap-y-1 rounded-lg border px-3 py-2.5 text-left backdrop-blur-sm transition-colors ${
        highlighted ? 'border-amber bg-raised' : 'border-line-strong bg-panel/60 hover:bg-raised'
      }`}
    >
      <span className="text-subhead font-semibold">{region.name}</span>
      <AmIcon icon={ICON.arrow} size="sm" className="text-ink-muted" />

      <span className="text-label text-ink-subtle col-span-2 font-mono">{region.coverage}</span>

      <span aria-hidden="true" className="col-span-2 mt-1.5 flex gap-0.5">
        {years.map((year) => {
          const measured = region.measured.includes(year);

          return (
            <span
              key={year}
              title={measured ? t('measured') : t('interpolated')}
              className={`h-2 flex-1 rounded-xs ${
                measured ? 'bg-ink' : 'border-line-strong border'
              }`}
            />
          );
        })}
      </span>

      <span className="text-meta text-ink-muted col-span-2">
        {t('epochs', { count: region.measured.length, total })}
      </span>
    </button>
  );
}
