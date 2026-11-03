'use client';

import { GLOBE_DATA } from '@/lib/globe/data';

type RegionKey = 'mekong' | 'amazon';

export function MiniMap({ region, caption }: { region: RegionKey; caption: string }) {
  const data = GLOBE_DATA.regions[region];
  const [west, south, east, north] = data.bbox;
  const x = ((west + 180) / 360) * GLOBE_DATA.width;
  const y = ((90 - north) / 180) * GLOBE_DATA.height;
  const width = ((east - west) / 360) * GLOBE_DATA.width;
  const height = ((north - south) / 180) * GLOBE_DATA.height;
  const pad = Math.max(width, height) * 0.18;

  return (
    <div className="border-line bg-panel relative h-36 overflow-hidden rounded-md border">
      <svg
        viewBox={`${x - pad} ${y - pad} ${width + pad * 2} ${height + pad * 2}`}
        role="img"
        aria-label={caption}
        className="size-full"
        preserveAspectRatio="xMidYMid meet"
      >
        <rect
          x={x - pad}
          y={y - pad}
          width={width + pad * 2}
          height={height + pad * 2}
          fill="var(--map-ocean)"
        />
        <path
          d={data.coverage}
          fill="var(--amber)"
          fillOpacity={0.24}
          stroke="var(--amber)"
          strokeWidth={2}
          vectorEffect="non-scaling-stroke"
        />
        <rect
          x={x}
          y={y}
          width={width}
          height={height}
          fill="none"
          stroke="var(--map-bbox)"
          strokeWidth={1}
          strokeDasharray="4 3"
          vectorEffect="non-scaling-stroke"
        />
      </svg>
      <span className="text-micro text-ink-subtle bg-panel/85 border-line absolute bottom-1.5 left-1.5 rounded-sm border px-1.5 py-0.5 font-mono">
        {caption}
      </span>
    </div>
  );
}
