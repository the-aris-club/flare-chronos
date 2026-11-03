'use client';

import { useCallback, useId, useState } from 'react';
import { useTranslations } from 'next-intl';
import { Icon, ICON } from '@/components/ui/icon';
import type { Epoch, MapFilters, MapPhysics } from '@/lib/workbench/types';
import { FootprintLens } from './footprint-lens';
import { PhysicsFilters, useFiltersOff } from './physics-filters';

type MapGuideProps = {
  physics: MapPhysics;
  epoch: Epoch | undefined;
  filters: MapFilters;
  onFilterAction: (key: keyof MapFilters) => void;
  /** The Static & SAA layer: the hatched zone, static heat sources and what they exclude. */
  overlay: boolean;
  onOverlayAction: () => void;
  hex: boolean;
  grid: number;
  resolution: number;
  saa: boolean;
  islands: boolean;
};

function Item({ mark, children }: { mark: React.ReactNode; children: React.ReactNode }) {
  return (
    <li className="flex items-center gap-2">
      <span aria-hidden="true" className="flex w-4 shrink-0 justify-center">
        {mark}
      </span>
      <span>{children}</span>
    </li>
  );
}

function Heading({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="text-label text-ink-subtle font-mono tracking-widest uppercase">{children}</h3>
  );
}

const DIAMOND = 'M6,0.8L11.2,5L6,9.2L0.8,5Z';

const MARK_0 = (
  <svg width={9} height={6}>
    <ellipse cx={4.5} cy={3} rx={4} ry={2.4} fill="var(--amber)" fillOpacity={0.9} />
  </svg>
);
const MARK_1 = (
  <svg width={8} height={8}>
    <circle cx={4} cy={4} r={3.5} fill="var(--raw)" />
  </svg>
);
const MARK_2 = (
  <svg width={14} height={8}>
    <rect
      x={0.5}
      y={0.5}
      width={13}
      height={7}
      fill="var(--amber)"
      fillOpacity={0.08}
      stroke="var(--amber)"
    />
  </svg>
);
const MARK_3 = (
  <svg width={14} height={8}>
    <rect
      x={0.5}
      y={0.5}
      width={13}
      height={7}
      fill="none"
      stroke="var(--cyan)"
      strokeDasharray="4 2"
    />
  </svg>
);
const MARK_4 = (
  <svg width={14} height={8}>
    <rect
      x={0.5}
      y={0.5}
      width={13}
      height={7}
      fill="none"
      stroke="var(--map-border)"
      strokeDasharray="3 2"
    />
    <circle cx={7} cy={4} r={1.4} fill="#fff" stroke="#3a4458" />
  </svg>
);
const MARK_5 = <span className="fc-hex-ramp block h-2 w-4 rounded-xs" />;
const MARK_6 = (
  <svg width={12} height={10}>
    <path d={DIAMOND} fill="var(--purple)" stroke="var(--map-ocean)" strokeWidth={1.1} />
  </svg>
);
const MARK_7 = (
  <svg width={12} height={10}>
    <path d={DIAMOND} fill="none" stroke="var(--purple)" strokeWidth={1.2} />
  </svg>
);
const MARK_8 = (
  <svg width={10} height={10}>
    <path d="M1,1L9,9M9,1L1,9" stroke="var(--grey)" strokeWidth={1} strokeDasharray="1.5 1" />
  </svg>
);
const MARK_9 = (
  <svg width={14} height={8}>
    <rect
      x={0.5}
      y={0.5}
      width={13}
      height={7}
      fill="none"
      stroke="var(--grey)"
      strokeDasharray="2 2"
    />
  </svg>
);

/**
 * One collapsible frame for everything that explains the map: the symbols, the Static & SAA
 * layer with the symbols it adds, and the true-scale footprint lens. Closed by default so
 * it never covers detections.
 */
export function MapGuide({
  physics,
  epoch,
  filters,
  onFilterAction,
  overlay,
  onOverlayAction,
  hex,
  grid,
  resolution,
  saa,
  islands,
}: MapGuideProps) {
  const t = useTranslations('Map');
  const [open, setOpen] = useState(false);
  const filtersOff = useFiltersOff(filters).length;
  const panel = useId();

  const handleToggle = useCallback(() => setOpen((value) => !value), []);

  return (
    <div className="tablet:bottom-9 absolute bottom-12 left-2 flex max-h-[calc(100%-4.5rem)] w-[min(19rem,calc(100%-1rem))] flex-col">
      {open && (
        <div
          id={panel}
          className="border-line bg-panel/95 text-micro text-ink-muted mb-1 flex min-h-0 flex-col gap-3 overflow-y-auto rounded-md border p-3"
        >
          <PhysicsFilters epoch={epoch} filters={filters} onFilter={onFilterAction} />

          <section className="border-line flex flex-col gap-1.5 border-t pt-3">
            <Heading>{t('symbols')}</Heading>
            <ul className="flex flex-col gap-1.5">
              <Item mark={MARK_0}>{t('modis')}</Item>
              <Item mark={MARK_1}>{t('viirs')}</Item>
              <Item mark={MARK_2}>{t('coverage')}</Item>
              <Item mark={MARK_3}>{t('queryBox')}</Item>
              {islands && <Item mark={MARK_4}>{t('islands')}</Item>}
              {hex && (
                <Item mark={MARK_5}>
                  {t('hexes')} · {t('hexShown', { grid, resolution })}
                </Item>
              )}
            </ul>
          </section>

          <section className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between gap-2">
              <Heading>{t('staticSaa')}</Heading>
              <button
                type="button"
                role="switch"
                aria-checked={overlay}
                aria-label={t('staticSaa')}
                onClick={onOverlayAction}
                className={`inline-flex h-5 w-9 shrink-0 items-center rounded-full border px-0.5 transition-colors ${
                  overlay ? 'border-cyan bg-seg justify-end' : 'border-line-strong justify-start'
                }`}
              >
                <span
                  className={`size-3.5 rounded-full ${overlay ? 'bg-cyan' : 'bg-ink-subtle'}`}
                />
              </button>
            </div>
            <ul className={`flex flex-col gap-1.5 ${overlay ? '' : 'opacity-50'}`}>
              <Item mark={MARK_6}>{t('staticSource')}</Item>
              <Item mark={MARK_7}>{t('excludedStatic')}</Item>
              <Item mark={MARK_8}>{t('excludedNoise')}</Item>
              <Item mark={MARK_9}>
                {t('saaZone')}
                {saa ? '' : ` · ${t('na')}`}
              </Item>
            </ul>
          </section>

          <FootprintLens physics={physics} />
        </div>
      )}

      <button
        type="button"
        aria-expanded={open}
        aria-controls={open ? panel : undefined}
        onClick={handleToggle}
        className="border-line-strong bg-panel/95 text-meta text-ink-muted hover:text-ink inline-flex h-8 items-center gap-1.5 self-start rounded-md border px-2.5 font-medium"
      >
        <Icon icon={ICON.filter} size="sm" />
        {t('guide')}
        {filtersOff > 0 && (
          <span
            role="img"
            aria-label={t('filtersOff', { count: filtersOff })}
            className="bg-warn size-2 rounded-full"
          />
        )}
        <Icon icon={ICON.chevron} size="xs" className={open ? '' : 'rotate-180'} />
      </button>
    </div>
  );
}
