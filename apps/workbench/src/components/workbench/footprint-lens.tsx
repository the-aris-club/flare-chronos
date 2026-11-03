'use client';

import { useLocale, useTranslations } from 'next-intl';
import { formatDecimal } from '@/lib/workbench/format';
import type { MapPhysics } from '@/lib/workbench/types';

const SCALE = 10.5;

export function FootprintLens({ physics }: { physics: MapPhysics }) {
  const t = useTranslations('Map');
  const locale = useLocale();
  const edgeMinor = Math.sqrt((4 * physics.modisEdge) / (Math.PI * 2.4));
  const edgeMajor = 2.4 * edgeMinor;
  const viirsRadius = Math.sqrt(physics.viirsNadir / Math.PI) * SCALE;
  const modisRadius = Math.sqrt(physics.modisNadir / Math.PI) * SCALE;
  const spacing = 3.94;

  return (
    <div className="border-line bg-panel/95 text-micro text-ink-muted tablet:bottom-9 max-tablet:hidden absolute bottom-16 left-2 w-44 rounded-md border p-2">
      <div className="flex items-baseline justify-between gap-2">
        <span className="text-micro text-ink-subtle font-mono tracking-widest uppercase">
          {t('lensTitle')}
        </span>
        <span className="text-micro font-mono">12 km</span>
      </div>
      <svg
        viewBox="0 0 160 112"
        role="img"
        aria-label={t('lensTitle')}
        className="mt-1 block h-auto w-full"
      >
        <rect width={160} height={112} fill="var(--map-ocean)" opacity={0.55} />
        <ellipse
          cx={86}
          cy={58}
          rx={(edgeMajor / 2) * SCALE}
          ry={(edgeMinor / 2) * SCALE}
          transform="rotate(-8 86 58)"
          fill="var(--amber)"
          fillOpacity={0.16}
          stroke="var(--amber)"
          strokeWidth={1}
        />
        <circle
          cx={26}
          cy={26}
          r={modisRadius}
          fill="var(--amber)"
          fillOpacity={0.16}
          stroke="var(--amber)"
          strokeWidth={1}
        />
        {[-1, 0, 1].map((column) =>
          [-1, 0, 1].map((row) => (
            <circle
              key={`v-${column}-${row}`}
              cx={90 + column * spacing}
              cy={58 + row * spacing}
              r={viirsRadius}
              fill="var(--raw)"
              fillOpacity={0.85}
            />
          )),
        )}
        {[0, 1, 2, 3].map((index) => (
          <circle
            key={`edge-${index}`}
            cx={118 + index * spacing}
            cy={86 + (index % 2) * spacing}
            r={viirsRadius}
            fill="var(--raw)"
            fillOpacity={0.85}
          />
        ))}
        <text
          x={34}
          y={20}
          fontSize={8}
          fill="var(--text-subtle)"
          fontFamily="var(--font-plex-mono)"
        >
          {t('modisNadir')} {formatDecimal(physics.modisNadir, locale)}
        </text>
        <text x={44} y={38} fontSize={8} fill="var(--text)" fontFamily="var(--font-plex-mono)">
          {t('modisEdge')} {formatDecimal(physics.modisEdge, locale)}
        </text>
        <text
          x={100}
          y={104}
          fontSize={8}
          fill="var(--text)"
          fontFamily="var(--font-plex-mono)"
          textAnchor="middle"
        >
          {t('viirsNadir')} {formatDecimal(physics.viirsNadir, locale)}
        </text>
        <line x1={6} x2={6 + 2 * SCALE} y1={104} y2={104} stroke="var(--text)" strokeWidth={1.2} />
        <text
          x={6}
          y={99}
          fontSize={8}
          fill="var(--text-subtle)"
          fontFamily="var(--font-plex-mono)"
        >
          2 km
        </text>
      </svg>
      <div className="border-line text-label mt-1 border-t pt-1 font-mono">
        {t('ratio', { ratio: formatDecimal(physics.ratio, locale) })}
      </div>
    </div>
  );
}
