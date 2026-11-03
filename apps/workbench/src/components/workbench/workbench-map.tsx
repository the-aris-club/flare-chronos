'use client';

import { useCallback, useEffect, useMemo, useRef } from 'react';
import { MAP_DATA, MAP_FLAGS, type MapHover, type MapPoint } from '@/lib/workbench/map-data';
import { binDetections, displayResolution, hexEdge, hexOpacity, hexPath } from '@/lib/workbench/h3';
import { panView, zoomAt, type MapView } from '@/lib/workbench/map-view';
import { screenToViewBox } from '@/lib/workbench/map-dom';
import { MapIslands } from './map-islands';
import type { MapFilters, MapLayers } from '@/lib/workbench/types';
import type { RegionId } from '@/lib/calendar/types';

type WorkbenchMapProps = {
  region: RegionId;
  year: number;
  view: MapView;
  grid: number;
  filters: MapFilters;
  layers: MapLayers;
  label: string;
  onView: (view: MapView) => void;
  onHover: (hover: MapHover | null) => void;
};

function statusOf(point: MapPoint, filters: MapFilters): 'keep' | 'sza' | 'saa' | 'static' | 'dup' {
  if (point.f & MAP_FLAGS.static && filters.static) return 'static';
  if (point.f & MAP_FLAGS.saa && filters.saa) return 'saa';
  if (point.f & MAP_FLAGS.sza && filters.sza) return 'sza';
  if (point.f & MAP_FLAGS.dup && filters.dedup) return 'dup';
  return 'keep';
}

export function WorkbenchMap({
  region,
  year,
  view,
  grid,
  filters,
  layers,
  label,
  onView,
  onHover,
}: WorkbenchMapProps) {
  const data = MAP_DATA.regions[region];
  const points = useMemo(() => data.epochs[String(year)] ?? [], [data, year]);
  const { width, height } = MAP_DATA;
  const svgRef = useRef<SVGSVGElement>(null);
  const viewRef = useRef(view);
  const pointers = useRef(new Map<number, { x: number; y: number }>());
  const lastPointer = useRef<{ x: number; y: number } | null>(null);
  const pinch = useRef<{ distance: number } | null>(null);
  useEffect(() => {
    viewRef.current = view;
  }, [view]);

  const { kept, excluded } = useMemo(() => {
    const visible: MapPoint[] = [];
    const removed: { point: MapPoint; status: ReturnType<typeof statusOf> }[] = [];
    for (const point of points) {
      const status = statusOf(point, filters);
      if (status === 'keep') visible.push(point);
      else if (status !== 'dup') removed.push({ point, status });
    }
    return { kept: visible, excluded: removed };
  }, [points, filters]);

  const h3 = useMemo(() => {
    if (!layers.hex) return null;
    const resolution = displayResolution(view.k, grid);
    const edge = hexEdge(resolution, data.pxPerKm);
    const bins = binDetections(kept, edge);
    const max = bins.reduce((value, bin) => Math.max(value, bin.count), 0);
    return { resolution, bins, max, path: hexPath(edge) };
  }, [layers.hex, view.k, grid, data.pxPerKm, kept]);

  const toViewBox = useCallback(
    (clientX: number, clientY: number) =>
      screenToViewBox(svgRef.current, clientX, clientY, width, height),
    [width, height],
  );

  useEffect(() => {
    const svg = svgRef.current;
    if (!svg) return;
    const onWheel = (event: WheelEvent) => {
      event.preventDefault();
      const anchor = toViewBox(event.clientX, event.clientY);
      const factor = Math.exp(-event.deltaY * 0.0016);
      onView(zoomAt(viewRef.current, factor, anchor.x, anchor.y, width, height));
    };
    svg.addEventListener('wheel', onWheel, { passive: false });
    return () => svg.removeEventListener('wheel', onWheel);
  }, [onView, width, height, toViewBox]);

  function pointerDown(event: React.PointerEvent<SVGSVGElement>) {
    event.currentTarget.setPointerCapture(event.pointerId);
    pointers.current.set(event.pointerId, { x: event.clientX, y: event.clientY });
    if (pointers.current.size === 1) {
      lastPointer.current = { x: event.clientX, y: event.clientY };
      pinch.current = null;
    } else if (pointers.current.size === 2) {
      const [a, b] = [...pointers.current.values()];
      pinch.current = { distance: Math.hypot(a.x - b.x, a.y - b.y) };
      lastPointer.current = null;
    }
  }

  function pointerMove(event: React.PointerEvent<SVGSVGElement>) {
    if (!pointers.current.has(event.pointerId)) return;
    pointers.current.set(event.pointerId, { x: event.clientX, y: event.clientY });
    if (pointers.current.size === 1 && lastPointer.current) {
      const from = toViewBox(lastPointer.current.x, lastPointer.current.y);
      const to = toViewBox(event.clientX, event.clientY);
      onView(panView(viewRef.current, to.x - from.x, to.y - from.y, width, height));
      lastPointer.current = { x: event.clientX, y: event.clientY };
    } else if (pointers.current.size === 2) {
      const [a, b] = [...pointers.current.values()];
      const distance = Math.hypot(a.x - b.x, a.y - b.y);
      if (pinch.current && pinch.current.distance > 0) {
        const anchor = toViewBox((a.x + b.x) / 2, (a.y + b.y) / 2);
        onView(
          zoomAt(
            viewRef.current,
            distance / pinch.current.distance,
            anchor.x,
            anchor.y,
            width,
            height,
          ),
        );
      }
      pinch.current = { distance };
    }
  }

  function pointerUp(event: React.PointerEvent<SVGSVGElement>) {
    pointers.current.delete(event.pointerId);
    if (pointers.current.size < 2) pinch.current = null;
    if (pointers.current.size === 1) {
      const [remaining] = [...pointers.current.values()];
      lastPointer.current = { x: remaining.x, y: remaining.y };
    } else {
      lastPointer.current = null;
    }
  }

  return (
    <svg
      ref={svgRef}
      viewBox={`0 0 ${width} ${height}`}
      preserveAspectRatio="xMidYMid meet"
      role="img"
      aria-label={label}
      className="size-full cursor-grab touch-none active:cursor-grabbing"
      onPointerDown={pointerDown}
      onPointerMove={pointerMove}
      onPointerUp={pointerUp}
      onPointerCancel={pointerUp}
      onPointerLeave={() => onHover(null)}
    >
      <defs>
        <pattern
          id="fc-saa-hatch"
          width="12"
          height="12"
          patternUnits="userSpaceOnUse"
          patternTransform="rotate(45)"
        >
          <line x1="0" y1="0" x2="0" y2="12" stroke="var(--grey)" strokeWidth="1" opacity="0.14" />
        </pattern>
      </defs>

      <rect width={width} height={height} fill="var(--map-ocean)" />
      <g transform={`translate(${view.x} ${view.y}) scale(${view.k})`}>
        <path
          d={data.graticule}
          fill="none"
          stroke="var(--map-grat)"
          strokeWidth={1}
          vectorEffect="non-scaling-stroke"
        />
        {data.countries.map((country) => (
          <path
            key={country.id}
            d={country.d}
            fill={country.focus ? 'var(--map-focus)' : 'var(--map-land)'}
          />
        ))}
        <path
          d={data.coveragePath}
          fill="var(--amber)"
          fillOpacity={0.22}
          stroke="var(--amber)"
          strokeWidth={1.4}
          vectorEffect="non-scaling-stroke"
        />
        <path
          d={data.borders}
          fill="none"
          stroke="var(--map-border)"
          strokeWidth={0.8}
          vectorEffect="non-scaling-stroke"
        />
        <path
          d={data.queryBoxPath}
          fill="none"
          stroke="var(--cyan)"
          strokeWidth={1}
          strokeDasharray="6 3"
          vectorEffect="non-scaling-stroke"
          data-testid="firms-query-box"
        />
        <MapIslands islands={data.islands} zoom={view.k} />

        {region === 'amazon' && layers.overlay && (
          <path
            d={data.saaPath}
            fill="url(#fc-saa-hatch)"
            fillOpacity={0.4}
            stroke="var(--grey)"
            strokeWidth={1}
            strokeDasharray="3 3"
            vectorEffect="non-scaling-stroke"
          />
        )}

        {h3 &&
          h3.bins.map((bin) => (
            <path
              key={`${bin.x.toFixed(1)}:${bin.y.toFixed(1)}`}
              d={h3.path}
              transform={`translate(${bin.x.toFixed(2)} ${bin.y.toFixed(2)})`}
              fill="var(--amber)"
              fillOpacity={hexOpacity(bin.count, h3.max)}
              stroke="var(--map-ocean)"
              strokeWidth={0.6}
              vectorEffect="non-scaling-stroke"
              aria-hidden="true"
            />
          ))}

        {layers.overlay &&
          data.staticSources.map((source) => (
            <path
              key={source.id}
              d="M0,-5L5,0L0,5L-5,0Z"
              transform={`translate(${source.x} ${source.y}) scale(${1 / view.k})`}
              fill="var(--purple)"
              stroke="var(--map-ocean)"
              strokeWidth={1.2}
              vectorEffect="non-scaling-stroke"
              opacity={0.9}
            />
          ))}

        {layers.footprints &&
          !layers.hex &&
          kept.map((point) => (
            <ellipse
              key={`kept-${point.i}`}
              cx={point.x}
              cy={point.y}
              rx={Math.max((point.sc * data.pxPerKm) / 2, 1.7 / view.k)}
              ry={Math.max((point.tr * data.pxPerKm) / 2, 1.25 / view.k)}
              transform={`rotate(${point.dn === 'N' ? -8 : 8} ${point.x} ${point.y})`}
              fill={point.s === 'm' ? 'var(--amber)' : 'var(--raw)'}
              fillOpacity={0.9}
              onPointerEnter={(event) =>
                event.pointerType === 'mouse' &&
                onHover({ point, status: 'keep', clientX: event.clientX, clientY: event.clientY })
              }
            />
          ))}

        {layers.footprints &&
          !layers.hex &&
          layers.overlay &&
          excluded.map(({ point, status }) => (
            <circle
              key={`excluded-${point.i}-${status}`}
              cx={point.x}
              cy={point.y}
              r={status === 'static' ? 2.8 / view.k : 3.2 / view.k}
              transform={`translate(0 0) scale(1)`}
              fill="none"
              stroke={status === 'static' ? 'var(--purple)' : 'var(--grey)'}
              strokeWidth={1}
              strokeDasharray={status === 'static' ? undefined : '2 1.5'}
              vectorEffect="non-scaling-stroke"
              opacity={0.7}
              onPointerEnter={(event) =>
                event.pointerType === 'mouse' &&
                onHover({ point, status, clientX: event.clientX, clientY: event.clientY })
              }
            />
          ))}
      </g>
    </svg>
  );
}
