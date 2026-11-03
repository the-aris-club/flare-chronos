'use client';

import { useTranslations } from 'next-intl';
import type { MapRegion } from '@/lib/workbench/map-data';

export function MapIslands({ islands, zoom }: { islands: MapRegion['islands']; zoom: number }) {
  const t = useTranslations('Map');

  return (
    <>
      {islands.map((island) => (
        <g key={island.id}>
          <path
            d={island.boxPath}
            fill="none"
            stroke="var(--map-border)"
            strokeWidth={1}
            strokeDasharray="3 2"
            vectorEffect="non-scaling-stroke"
          />
          {island.points.map((point) => (
            <circle
              key={point.name}
              cx={point.x}
              cy={point.y}
              r={2.2 / zoom}
              fill="#fff"
              stroke="#3a4458"
              strokeWidth={0.8}
              vectorEffect="non-scaling-stroke"
            >
              <title>{point.name}</title>
            </circle>
          ))}
          {island.label && (
            <text
              x={island.label.x}
              y={island.label.y}
              textAnchor="middle"
              fill="var(--text)"
              stroke="var(--map-ocean)"
              strokeWidth={3}
              paintOrder="stroke"
              fontFamily="var(--font-plex-sans)"
              fontSize={10.5 / zoom}
              fontWeight={500}
            >
              {island.id === 'hs' ? t('islandHs') : t('islandTs')}
            </text>
          )}
        </g>
      ))}
    </>
  );
}
