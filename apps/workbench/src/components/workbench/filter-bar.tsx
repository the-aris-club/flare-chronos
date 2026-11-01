'use client';

import { useLocale, useTranslations } from 'next-intl';
import { AmIcon, ICON } from '@/components/ui/icon';
import type { Epoch, MapFilters } from '@/lib/workbench/types';
import { formatCount } from '@/lib/workbench/format';

const KEYS: (keyof MapFilters)[] = ['sza', 'saa', 'static', 'dedup'];

export function FilterBar({
  epoch,
  filters,
  onFilter,
}: {
  epoch: Epoch | undefined;
  filters: MapFilters;
  onFilter: (key: keyof MapFilters) => void;
}) {
  const t = useTranslations('Filters');
  const locale = useLocale();
  const raw = epoch?.raw ?? 0;
  const episodes = epoch?.episodes ?? 0;
  const removed = raw - episodes;
  const saa = epoch?.saa ?? 0;
  const values = {
    raw: formatCount(raw, locale),
    episodes: formatCount(episodes, locale),
    removed: formatCount(removed, locale),
    saa: formatCount(saa, locale),
  };
  const labels: Record<keyof MapFilters, string> = {
    sza: t('sza'),
    saa: t('saa'),
    static: t('static'),
    dedup: t('dedup'),
  };
  const off = KEYS.filter((key) => !filters[key]).map((key) => labels[key]);

  return (
    <div
      role="group"
      aria-label={t('title')}
      className="border-line bg-canvas text-ink-muted text-micro tablet:gap-1.5 flex items-center gap-1 overflow-x-auto border-b px-3 py-1.5"
    >
      <span className="text-micro text-ink-subtle max-tablet:hidden shrink-0 font-mono tracking-widest uppercase">
        {t('title')}
      </span>
      {KEYS.map((key) => (
        <button
          key={key}
          type="button"
          aria-pressed={filters[key]}
          onClick={() => onFilter(key)}
          className={`tablet:px-1.5 inline-flex shrink-0 items-center gap-1.5 rounded-md border px-1 py-0.5 transition-colors ${
            filters[key]
              ? 'border-line-strong text-ink-muted'
              : 'border-warn/50 text-warn hover:text-ink'
          }`}
        >
          <span
            className={`inline-flex size-3 items-center justify-center rounded-sm border ${
              filters[key]
                ? 'border-cyan bg-cyan text-canvas'
                : 'border-line-strong text-transparent'
            }`}
          >
            <AmIcon icon={ICON.check} size="xs" />
          </span>
          {labels[key]}
        </button>
      ))}
      <span className="text-micro ml-auto hidden shrink-0 font-mono xl:inline">
        {off.length ? t('off', { filters: off.join(', ') }) : t('removed', values)}
      </span>
      <span className="text-micro text-ink-subtle hidden shrink-0 font-mono xl:inline">
        {t('note')}
      </span>
    </div>
  );
}
