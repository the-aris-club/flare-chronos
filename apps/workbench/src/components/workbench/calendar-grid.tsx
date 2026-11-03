'use client';

import { useCallback, memo, type MouseEvent, type PointerEvent } from 'react';
import { useTranslations } from 'next-intl';
import { useTheme } from '@/components/ui/theme-provider';
import type { Theme } from '@/lib/theme';
import { monthIndexAt } from '@/lib/calendar/pentad';
import { divColor, seqColor } from '@/lib/calendar/ramp';
import { PENTADS_PER_YEAR, type CalendarCell } from '@/lib/calendar/model';
import type { CalendarRegionData, CellRef, Metric } from '@/lib/calendar/types';

type CalendarGridProps = {
  region: CalendarRegionData;
  cells: CalendarCell[];
  metric: Metric;
  active: CellRef;
  hover: CellRef | null;
  onActive: (ref: CellRef) => void;
  onHover: (ref: CellRef | null) => void;
  onTip?: (x: number, y: number) => void;
};

function sameRef(a: CellRef | null, b: CellRef): boolean {
  return a !== null && a.yearIndex === b.yearIndex && a.pentadIndex === b.pentadIndex;
}

function refFromPoint(
  element: SVGSVGElement,
  clientX: number,
  clientY: number,
  rows: number,
): CellRef {
  const rect = element.getBoundingClientRect();
  const x = (clientX - rect.left) / rect.width;
  const y = (clientY - rect.top) / rect.height;

  return {
    yearIndex: Math.min(rows - 1, Math.max(0, Math.floor(y * rows))),
    pentadIndex: Math.min(PENTADS_PER_YEAR - 1, Math.max(0, Math.floor(x * PENTADS_PER_YEAR))),
  };
}

type CellsProps = {
  region: CalendarRegionData;
  cells: CalendarCell[];
  metric: Metric;
  theme: Theme;
};

// The ~1,900 cells never change while the pointer moves; the focus rings are drawn
// separately so a hover repaints two rects, not the grid.
const CalendarCells = memo(function CalendarCells({ region, cells, metric, theme }: CellsProps) {
  function fillFor(cell: CalendarCell): string | null {
    if (metric === 'hfd') {
      return seqColor(Math.sqrt(cell.hfd / region.maxHfd), theme);
    }

    return cell.sfai === null ? null : divColor(cell.sfai, theme);
  }

  return region.years.map((year, yearIndex) =>
    Array.from({ length: PENTADS_PER_YEAR }, (_, pentadIndex) => {
      const cell = cells[yearIndex * PENTADS_PER_YEAR + pentadIndex];
      const modelled = !cell.observed;
      const fill = fillFor(cell) ?? (modelled ? 'var(--panel)' : 'var(--raised)');

      return (
        <g key={`${year}-${pentadIndex}`}>
          <rect
            x={pentadIndex}
            y={yearIndex}
            width={0.92}
            height={0.92}
            rx={0.06}
            fill={fill}
            fillOpacity={modelled ? 0.4 : 1}
          />
          {modelled && (
            <rect
              x={pentadIndex}
              y={yearIndex}
              width={0.92}
              height={0.92}
              rx={0.06}
              fill="url(#fc-hatch)"
            />
          )}
          {cell.alert && (
            <rect
              x={pentadIndex + 0.05}
              y={yearIndex + 0.05}
              width={0.82}
              height={0.82}
              fill="none"
              stroke="var(--cyan)"
              strokeWidth={1.5}
              vectorEffect="non-scaling-stroke"
            />
          )}
          {cell.crisis && <path d={`M${pentadIndex} ${yearIndex}h0.32v0.32z`} fill="var(--cyan)" />}
        </g>
      );
    }),
  );
});

export function CalendarGrid({
  region,
  cells,
  metric,
  active,
  hover,
  onActive,
  onHover,
  onTip,
}: CalendarGridProps) {
  const t = useTranslations('Calendar');
  const { theme } = useTheme();
  const months = t.raw('months') as string[];
  const observedYears = new Set(region.observedYears);

  const handleMove = useCallback(
    (event: PointerEvent<SVGSVGElement>) => {
      if (event.pointerType !== 'mouse') return;

      const next = refFromPoint(
        event.currentTarget,
        event.clientX,
        event.clientY,
        region.years.length,
      );
      if (!sameRef(hover, next)) onHover(next);
      onTip?.(event.clientX, event.clientY);
    },
    [hover, onHover, onTip, region.years.length],
  );

  const handleClick = useCallback(
    (event: MouseEvent<SVGSVGElement>) => {
      const next =
        hover ??
        refFromPoint(event.currentTarget, event.clientX, event.clientY, region.years.length);
      onActive(next);
      onHover(null);
    },
    [hover, onActive, onHover, region.years.length],
  );

  const handlePointerLeave = useCallback(() => onHover(null), [onHover]);

  return (
    <div>
      <div className="mb-0.5 flex gap-1.5" aria-hidden="true">
        <span className="w-11 shrink-0" />
        <div className="fc-calendar-axis text-micro text-ink-subtle flex-1 font-mono">
          {Array.from({ length: PENTADS_PER_YEAR }, (_, pentadIndex) => {
            const monthIndex = monthIndexAt(pentadIndex);

            return (
              <span
                key={pentadIndex}
                className={monthIndex === null ? undefined : 'border-line-strong border-l pl-1'}
              >
                {monthIndex === null ? null : months[monthIndex]}
              </span>
            );
          })}
        </div>
      </div>

      <div className="flex gap-1.5">
        <div
          aria-hidden="true"
          className="fc-calendar-year-rows bg-panel sticky left-0 z-10 grid w-11 shrink-0"
        >
          {region.years.map((year, yearIndex) => {
            const observed = observedYears.has(year);
            const isActive = active.yearIndex === yearIndex;

            return (
              <div key={year} className="flex items-center gap-1">
                <span
                  className={`size-1.5 shrink-0 rounded-full border ${
                    isActive
                      ? 'border-teal bg-teal'
                      : observed
                        ? 'border-ink bg-ink'
                        : 'border-line-strong bg-transparent'
                  }`}
                />
                <span
                  className={`text-micro font-mono ${
                    isActive
                      ? 'text-teal font-semibold'
                      : observed
                        ? 'text-ink font-semibold'
                        : 'text-ink-subtle'
                  }`}
                >
                  {year}
                </span>
              </div>
            );
          })}
        </div>

        <svg
          viewBox={`0 0 ${PENTADS_PER_YEAR} 26`}
          preserveAspectRatio="none"
          aria-hidden="true"
          className="fc-calendar-svg block w-full cursor-crosshair"
          onPointerMove={handleMove}
          onPointerLeave={handlePointerLeave}
          onClick={handleClick}
        >
          <CalendarCells region={region} cells={cells} metric={metric} theme={theme} />
          {[
            { ref: active, inset: 0.03, size: 0.86, width: 2 },
            ...(hover && !sameRef(hover, active)
              ? [{ ref: hover, inset: 0.04, size: 0.84, width: 1 }]
              : []),
          ].map(({ ref, inset, size, width }) => (
            <rect
              key={width}
              x={ref.pentadIndex + inset}
              y={ref.yearIndex + inset}
              width={size}
              height={size}
              fill="none"
              stroke="var(--focus)"
              strokeWidth={width}
              vectorEffect="non-scaling-stroke"
            />
          ))}
        </svg>
      </div>
    </div>
  );
}
