'use client';

import { useLocale, useTranslations } from 'next-intl';
import { formatCount } from '@/lib/workbench/format';
import type { MapLayers } from '@/lib/workbench/types';

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

export function MapLegend({
  layers,
  saa,
  islands,
  grid,
  resolution,
}: {
  layers: MapLayers;
  saa: boolean;
  islands: boolean;
  grid: number;
  resolution: number;
}) {
  const t = useTranslations('Map');
  return (
    <div className="border-line bg-panel/95 text-micro text-ink-muted absolute inset-x-0 bottom-0 flex flex-wrap items-center gap-x-3 gap-y-1 border-t px-3 py-1.5">
      <span className="inline-flex items-center gap-1.5">
        <svg width={9} height={6} aria-hidden="true">
          <ellipse cx={4.5} cy={3} rx={4} ry={2.4} fill="var(--amber)" fillOpacity={0.9} />
        </svg>
        {t('modis')}
      </span>
      <span className="inline-flex items-center gap-1.5">
        <svg width={8} height={8} aria-hidden="true">
          <circle cx={4} cy={4} r={3.5} fill="var(--raw)" />
        </svg>
        {t('viirs')}
      </span>
      <span className="inline-flex items-center gap-1.5">
        <svg width={14} height={8} aria-hidden="true">
          <rect
            x={0.5}
            y={0.5}
            width={13}
            height={7}
            fill="var(--amber)"
            fillOpacity={0.16}
            stroke="var(--amber)"
          />
        </svg>
        {t('coverage')}
      </span>
      {layers.overlay && (
        <>
          <span className="inline-flex items-center gap-1.5">
            <svg width={12} height={10} aria-hidden="true">
              <path
                d="M6,0.8L11.2,5L6,9.2L0.8,5Z"
                fill="var(--purple)"
                stroke="var(--map-ocean)"
                strokeWidth={1.1}
              />
            </svg>
            {t('staticSource')}
          </span>
          <span className="inline-flex items-center gap-1.5">
            <svg width={12} height={10} aria-hidden="true">
              <path
                d="M6,0.8L11.2,5L6,9.2L0.8,5Z"
                fill="none"
                stroke="var(--purple)"
                strokeWidth={1.2}
              />
            </svg>
            {t('excludedStatic')}
          </span>
          <span className="inline-flex items-center gap-1.5">
            <svg width={10} height={10} aria-hidden="true">
              <path
                d="M1,1L9,9M9,1L1,9"
                stroke="var(--grey)"
                strokeWidth={1}
                strokeDasharray="1.5 1"
              />
            </svg>
            {t('excludedNoise')}
          </span>
        </>
      )}
      {islands && (
        <span className="inline-flex items-center gap-1.5">
          <svg width={14} height={8} aria-hidden="true">
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
          {t('islands')}
        </span>
      )}
      {layers.overlay && (
        <span className="inline-flex items-center gap-1.5">
          <svg width={14} height={8} aria-hidden="true">
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
          {t('saaZone')}
          {saa ? '' : ` · ${t('na')}`}
        </span>
      )}
      <span className="inline-flex items-center gap-1.5">
        <svg width={14} height={8} aria-hidden="true">
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
        {t('queryBox')}
      </span>
      {layers.hex && (
        <span className="inline-flex items-center gap-1.5">
          <span aria-hidden="true" className="fc-hex-ramp h-2 w-14 rounded-xs" />
          {t('hexes')} · {t('hexShown', { grid, resolution })}
        </span>
      )}
      <span className="ml-auto font-mono">{t('scaleNote')}</span>
    </div>
  );
}
