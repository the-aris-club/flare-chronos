'use client';

import { useTranslations } from 'next-intl';
import { Icon, ICON } from '@/components/ui/icon';
import type { RegionId } from '@/lib/calendar/types';
import { RegionCard, type RegionCardData } from './region-card';

type LandingPanelProps = {
  regions: RegionCardData[];
  growth: Record<RegionId, number>;
  period: { start: number; end: number };
  yearStart: number;
  total: number;
  collapsed: boolean;
  hovered: RegionId | null;
  onToggle: () => void;
  onHover: (region: RegionId | null) => void;
  onSelect: (region: RegionId) => void;
  onExplore: () => void;
  onTour: () => void;
};

export function LandingPanel({
  regions,
  growth,
  period,
  yearStart,
  total,
  collapsed,
  hovered,
  onToggle,
  onHover,
  onSelect,
  onExplore,
  onTour,
}: LandingPanelProps) {
  const t = useTranslations('Globe');
  const ratio = Math.max(growth.mekong, growth.amazon);

  return (
    <section
      aria-label={t('choose')}
      data-collapsed={collapsed}
      className="fc-landing-panel border-line bg-panel/90 absolute inset-x-3 bottom-3 z-20 flex flex-col gap-4 overflow-y-auto rounded-xl border p-4 backdrop-blur-md xl:inset-x-auto xl:top-1/2 xl:bottom-auto xl:left-14 xl:max-h-none xl:w-110 xl:gap-5 xl:overflow-visible xl:border-0 xl:bg-transparent xl:p-0 xl:backdrop-blur-none"
    >
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={!collapsed}
        aria-label={collapsed ? t('showPanel') : t('hidePanel')}
        className="text-meta text-ink-muted border-line bg-panel/95 sticky -top-4 z-10 -mx-4 -mt-4 flex h-11 shrink-0 items-center justify-center gap-2 rounded-t-xl border-b px-4 backdrop-blur-md xl:hidden"
      >
        <span className="bg-line-strong h-1 w-9 rounded-full" />
        <span className="inline-flex items-center gap-1.5">
          <Icon icon={ICON.chevron} size="sm" className={collapsed ? 'rotate-180' : ''} />
          {collapsed ? t('showPanel') : t('hidePanel')}
        </span>
      </button>

      <div className="flex flex-col gap-3">
        <span className="text-label text-ink-subtle font-mono tracking-widest uppercase">
          {t('eyebrow', { start: period.start, end: period.end })}
        </span>
        <h1 className="text-hero-sm tablet:text-hero-md xl:text-hero max-w-lg leading-none font-semibold tracking-tight text-balance">
          {t('title', { ratio })}
        </h1>
        <p className="text-subhead text-ink-muted max-w-md leading-relaxed text-pretty">
          {t('body', {
            mekong: growth.mekong,
            amazon: growth.amazon,
          })}
        </p>
      </div>

      <div className="flex flex-col gap-2">
        <span className="text-label text-ink-subtle font-mono tracking-widest uppercase">
          {t('choose')}
        </span>
        {regions.map((region) => (
          <RegionCard
            key={region.id}
            region={region}
            yearStart={yearStart}
            total={total}
            highlighted={hovered === region.id}
            onHover={onHover}
            onSelect={onSelect}
          />
        ))}
        <div className="text-label text-ink-subtle flex gap-4">
          <span className="inline-flex items-center gap-1.5">
            <span className="bg-ink h-2 w-2 rounded-xs" />
            {t('measured')}
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="border-line-strong h-2 w-2 rounded-xs border" />
            {t('interpolated')}
          </span>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <button
          type="button"
          onClick={onTour}
          className="bg-ink text-canvas text-body inline-flex h-10 w-full items-center justify-center gap-2 rounded-lg px-3 font-semibold whitespace-nowrap"
        >
          <Icon icon={ICON.tour} size="sm" />
          {t('tour')}
        </button>
        <button
          type="button"
          onClick={onExplore}
          className="border-line-strong text-ink hover:bg-chip text-body inline-flex h-10 w-full items-center justify-center rounded-lg border px-3 font-medium whitespace-nowrap"
        >
          {t('explore')}
        </button>
      </div>
    </section>
  );
}
