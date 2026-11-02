'use client';

import { useLocale, useTranslations } from 'next-intl';
import { Icon, ICON } from '@/components/ui/icon';
import type { Epoch, MapFilters } from '@/lib/workbench/types';
import { formatCount } from '@/lib/workbench/format';

const KEYS: (keyof MapFilters)[] = ['sza', 'saa', 'static', 'dedup'];

/** The names of the filters currently switched off; the numbers on screen are inflated by them. */
export function useFiltersOff(filters: MapFilters): string[] {
  const t = useTranslations('Filters');
  return KEYS.filter((key) => !filters[key]).map((key) => t(key));
}

/** The four physics filters and what they removed from the selected epoch. */
export function PhysicsFilters({
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
  const off = useFiltersOff(filters);

  return (
    <section role="group" aria-label={t('title')} className="flex flex-col gap-1.5">
      <h3 className="text-label text-ink-subtle font-mono tracking-widest uppercase">
        {t('title')}
      </h3>
      <div className="flex flex-col gap-1">
        {KEYS.map((key) => (
          <button
            key={key}
            type="button"
            aria-pressed={filters[key]}
            onClick={() => onFilter(key)}
            className={`flex items-center gap-2 rounded-md border px-2 py-1 text-left transition-colors ${
              filters[key]
                ? 'border-line-strong text-ink-muted'
                : 'border-warn/50 text-warn hover:text-ink'
            }`}
          >
            <span
              className={`inline-flex size-3 shrink-0 items-center justify-center rounded-sm border ${
                filters[key]
                  ? 'border-cyan bg-cyan text-canvas'
                  : 'border-line-strong text-transparent'
              }`}
            >
              <Icon icon={ICON.check} size="xs" />
            </span>
            {t(key)}
          </button>
        ))}
      </div>
      <p className="font-mono">
        {off.length
          ? t('off', { filters: off.join(', ') })
          : t('removed', {
              raw: formatCount(raw, locale),
              episodes: formatCount(episodes, locale),
              removed: formatCount(raw - episodes, locale),
              saa: formatCount(epoch?.saa ?? 0, locale),
            })}
      </p>
      <p className="text-ink-subtle font-mono">{t('note')}</p>
    </section>
  );
}
