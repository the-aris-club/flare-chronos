'use client';

import { memo, useCallback, useEffect, useMemo, useRef } from 'react';
import { MAP_DATA, MAP_FLAGS, type MapHover, type MapPoint } from '@/lib/workbench/map-data';
import { binDetections, displayResolution, hexEdge, hexOpacity, hexPath } from '@/lib/workbench/h3';
import { markerScale, panView, zoomAt, type MapView } from '@/lib/workbench/map-view';
import { screenToViewBox } from '@/lib/workbench/map-dom';
import { MapIslands } from './map-islands';
import type { MapFilters, MapLayers } from '@/lib/workbench/types';
import type { RegionId } from '@/lib/calendar/types';

const RELIEF_STYLE = {
  mixBlendMode: 'var(--map-relief-blend)' as never,
  opacity: 'var(--map-relief-opacity)',
  filter: 'var(--map-relief-filter)',
};

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

// Memoised: hovering a point updates the tooltip only, never this subtree.
export const WorkbenchMap = memo(function WorkbenchMap({
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
  const { width, height, pad } = MAP_DATA;
  const svgRef = useRef<SVGSVGElement>(null);
  const groupRef = useRef<SVGGElement>(null);
  // `viewRef` is where the gesture is heading, `liveRef` what is on screen. Both move
  // outside React while a gesture runs; the parent only hears about the settled view.
  const viewRef = useRef(view);
  const liveRef = useRef(view);
  const frame = useRef(0);
  const onViewRef = useRef(onView);
  const pointers = useRef(new Map<number, { x: number; y: number }>());
  const lastPointer = useRef<{ x: number; y: number } | null>(null);
  const pinch = useRef<{ distance: number } | null>(null);
  useEffect(() => {
    onViewRef.current = onView;
  }, [onView]);
  useEffect(() => {
    // An outside change (zoom buttons, reset, region switch) wins unless we are mid-gesture.
    if (frame.current) return;
    viewRef.current = view;
    liveRef.current = view;
  }, [view]);
  useEffect(() => () => cancelAnimationFrame(frame.current), []);

  const paint = useCallback((next: MapView) => {
    liveRef.current = next;
    groupRef.current?.setAttribute('transform', `translate(${next.x} ${next.y}) scale(${next.k})`);
  }, []);

  const settle = useCallback(() => {
    cancelAnimationFrame(frame.current);
    frame.current = 0;
    paint(viewRef.current);
    onViewRef.current(viewRef.current);
  }, [paint]);

  // Ease the on-screen view toward the target once per frame (wheel zoom).
  const glide = useCallback(() => {
    if (frame.current) return;
    const step = () => {
      const live = liveRef.current;
      const goal = viewRef.current;
      const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      const t = reduce ? 1 : 0.28;
      const k = live.k * Math.pow(goal.k / live.k, t);
      const next = { k, x: live.x + (goal.x - live.x) * t, y: live.y + (goal.y - live.y) * t };
      const done =
        Math.abs(Math.log(goal.k / next.k)) < 0.002 &&
        Math.abs(goal.x - next.x) < 0.2 &&
        Math.abs(goal.y - next.y) < 0.2;
      if (done) settle();
      else {
        paint(next);
        frame.current = requestAnimationFrame(step);
      }
    };
    frame.current = requestAnimationFrame(step);
  }, [paint, settle]);

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

  const marker = markerScale(view.k);

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
      viewRef.current = zoomAt(viewRef.current, factor, anchor.x, anchor.y, width, height);
      glide();
    };
    svg.addEventListener('wheel', onWheel, { passive: false });
    return () => svg.removeEventListener('wheel', onWheel);
  }, [glide, width, height, toViewBox]);

  // Pan and pinch follow the pointer exactly: paint now, tell the parent on release.
  const follow = useCallback(
    (next: MapView) => {
      cancelAnimationFrame(frame.current);
      frame.current = -1;
      viewRef.current = next;
      paint(next);
    },
    [paint],
  );

  const release = useCallback(() => {
    if (frame.current === -1) settle();
  }, [settle]);

  const pointerDown = useCallback((event: React.PointerEvent<SVGSVGElement>) => {
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
  }, []);

  const pointerMove = useCallback(
    (event: React.PointerEvent<SVGSVGElement>) => {
      if (!pointers.current.has(event.pointerId)) return;
      pointers.current.set(event.pointerId, { x: event.clientX, y: event.clientY });
      if (pointers.current.size === 1 && lastPointer.current) {
        const from = toViewBox(lastPointer.current.x, lastPointer.current.y);
        const to = toViewBox(event.clientX, event.clientY);
        follow(panView(viewRef.current, to.x - from.x, to.y - from.y, width, height));
        lastPointer.current = { x: event.clientX, y: event.clientY };
      } else if (pointers.current.size === 2) {
        const [a, b] = [...pointers.current.values()];
        const distance = Math.hypot(a.x - b.x, a.y - b.y);
        if (pinch.current && pinch.current.distance > 0) {
          const anchor = toViewBox((a.x + b.x) / 2, (a.y + b.y) / 2);
          follow(
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
    },
    [toViewBox, width, height, follow],
  );

  const pointerUp = useCallback(
    (event: React.PointerEvent<SVGSVGElement>) => {
      pointers.current.delete(event.pointerId);
      if (pointers.current.size === 0) release();
      if (pointers.current.size < 2) pinch.current = null;
      if (pointers.current.size === 1) {
        const [remaining] = [...pointers.current.values()];
        lastPointer.current = { x: remaining.x, y: remaining.y };
      } else {
        lastPointer.current = null;
      }
    },
    [release],
  );

  const handlePointerLeave = useCallback(() => onHover(null), [onHover]);

  const handlePointerEnter = useCallback(
    (point: MapPoint, status: 'keep' | 'sza' | 'saa' | 'static' | 'dup') =>
      (event: React.PointerEvent<SVGElement>) => {
        if (event.pointerType === 'mouse') {
          onHover({ point, status, clientX: event.clientX, clientY: event.clientY });
        }
      },
    [onHover],
  );

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
      onPointerLeave={handlePointerLeave}
    >
      <defs>
        <clipPath id={`fc-land-${region}`}>
          <path d={data.landPath} />
        </clipPath>
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
      <g ref={groupRef} transform={`translate(${view.x} ${view.y}) scale(${view.k})`}>
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
        {/* Natural Earth shaded relief, already in this projection; the blend and filter
            come from the theme so flat land is unchanged and only the hills shade it. */}
        <image
          href={`/map/relief-${region}.webp`}
          x={-pad.x}
          y={-pad.y}
          width={width + 2 * pad.x}
          height={height + 2 * pad.y}
          preserveAspectRatio="none"
          clipPath={`url(#fc-land-${region})`}
          style={RELIEF_STYLE}
          aria-hidden="true"
        />
        <path
          d={data.lakes}
          fill="var(--map-ocean)"
          stroke="var(--map-border)"
          strokeWidth={0.5}
          vectorEffect="non-scaling-stroke"
        />
        <path
          d={data.rivers}
          fill="none"
          stroke="var(--map-river)"
          strokeWidth={1.3}
          strokeLinecap="round"
          strokeLinejoin="round"
          vectorEffect="non-scaling-stroke"
        />
        <path
          d={data.coveragePath}
          fill="var(--amber)"
          fillOpacity={0.05}
          stroke="var(--amber)"
          strokeWidth={1.1}
          strokeOpacity={0.7}
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
              transform={`translate(${source.x} ${source.y}) scale(${marker / view.k})`}
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
              rx={Math.max((point.sc * data.pxPerKm) / 2, (1.7 * marker) / view.k)}
              ry={Math.max((point.tr * data.pxPerKm) / 2, (1.25 * marker) / view.k)}
              transform={`rotate(${point.dn === 'N' ? -8 : 8} ${point.x} ${point.y})`}
              fill={point.s === 'm' ? 'var(--amber)' : 'var(--raw)'}
              fillOpacity={0.9}
              onPointerEnter={handlePointerEnter(point, 'keep')}
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
              r={((status === 'static' ? 2.8 : 3.2) * marker) / view.k}
              transform={`translate(0 0) scale(1)`}
              fill="none"
              stroke={status === 'static' ? 'var(--purple)' : 'var(--grey)'}
              strokeWidth={1}
              strokeDasharray={status === 'static' ? undefined : '2 1.5'}
              vectorEffect="non-scaling-stroke"
              opacity={0.7}
              onPointerEnter={handlePointerEnter(point, status)}
            />
          ))}
      </g>
    </svg>
  );
});
