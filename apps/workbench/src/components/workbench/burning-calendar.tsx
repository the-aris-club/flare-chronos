'use client';

import { useCallback, useMemo, useRef, useState } from 'react';
import { useLocale, useTranslations } from 'next-intl';
import { SegmentedControl } from '@/components/ui/segmented-control';
import { buildCells, findInitialCell, PENTADS_PER_YEAR } from '@/lib/calendar/model';
import { formatHfd, formatSigma } from '@/lib/calendar/format';
import { pentadDates } from '@/lib/calendar/pentad';
import type { CalendarRegionData, CellRef, HfdUnit, Metric } from '@/lib/calendar/types';
import { CalendarGrid } from './calendar-grid';
import { CalendarLegend } from './calendar-legend';
import { CalendarSummary } from './calendar-summary';

type BurningCalendarProps = {
  region: CalendarRegionData;
  regionLabel: string;
  unit: HfdUnit;
  onMeasuredYear: (year: number) => void;
};

export function BurningCalendar({
  region,
  regionLabel,
  unit,
  onMeasuredYear,
}: BurningCalendarProps) {
  const t = useTranslations('Calendar');
  const locale = useLocale();
  const initial = useMemo(() => findInitialCell(region), [region]);
  const [metric, setMetric] = useState<Metric>('hfd');
  const [active, setActive] = useState<CellRef>(initial);
  const [hover, setHover] = useState<CellRef | null>(null);
  const tipRef = useRef<HTMLDivElement>(null);

  const cells = useMemo(() => buildCells(region), [region]);
  const focused = hover ?? active;
  const observedCells = cells.filter((cell) => cell.observed).length;
  const focusedCell = cells[focused.yearIndex * PENTADS_PER_YEAR + focused.pentadIndex];

  const start = region.years[0];
  const end = region.years[region.years.length - 1];
  const lastYear = region.years.length - 1;

  const moveTip = useCallback((x: number, y: number) => {
    const node = tipRef.current;
    if (!node) return;
    node.style.setProperty('--cal-tip-x', `${Math.min(x + 14, window.innerWidth - 190)}px`);
    node.style.setProperty('--cal-tip-y', `${Math.min(y + 18, window.innerHeight - 92)}px`);
  }, []);

  const activate = useCallback(
    (next: CellRef) => {
      setActive(next);
      const year = region.years[next.yearIndex];
      if (region.observedYears.includes(year)) onMeasuredYear(year);
    },
    [region, onMeasuredYear],
  );

  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent<HTMLDivElement>) => {
      const { yearIndex, pentadIndex } = active;
      let next: CellRef;

      switch (event.key) {
        case 'ArrowRight':
          next = { yearIndex, pentadIndex: Math.min(PENTADS_PER_YEAR - 1, pentadIndex + 1) };
          break;
        case 'ArrowLeft':
          next = { yearIndex, pentadIndex: Math.max(0, pentadIndex - 1) };
          break;
        case 'ArrowDown':
          next = { yearIndex: Math.min(lastYear, yearIndex + 1), pentadIndex };
          break;
        case 'ArrowUp':
          next = { yearIndex: Math.max(0, yearIndex - 1), pentadIndex };
          break;
        case 'Home':
          next = { yearIndex, pentadIndex: 0 };
          break;
        case 'End':
          next = { yearIndex, pentadIndex: PENTADS_PER_YEAR - 1 };
          break;
        case 'PageUp':
          next = { yearIndex: Math.max(0, yearIndex - 5), pentadIndex };
          break;
        case 'PageDown':
          next = { yearIndex: Math.min(lastYear, yearIndex + 5), pentadIndex };
          break;
        case 'Enter':
        case ' ':
          setHover(null);
          event.preventDefault();
          return;
        default:
          return;
      }

      event.preventDefault();
      activate(next);
      setHover(null);
    },
    [active, lastYear, activate, setHover],
  );

  const metricOptions = useMemo<ReadonlyArray<{ value: Metric; label: string }>>(
    () => [
      { value: 'hfd', label: t('metrics.hfd') },
      { value: 'sfai', label: t('metrics.sfai') },
    ],
    [t],
  );

  return (
    <section
      aria-labelledby="calendar-title"
      data-tour="cal"
      className="border-line bg-panel relative flex flex-col overflow-hidden rounded-lg border"
    >
      <svg aria-hidden="true" className="absolute size-0 overflow-hidden">
        <defs>
          <pattern
            id="fc-hatch"
            width={0.35}
            height={0.35}
            patternUnits="userSpaceOnUse"
            patternTransform="rotate(45)"
          >
            <line x1={0} y1={0} x2={0} y2={0.35} stroke="var(--hatch)" strokeWidth={0.07} />
          </pattern>
        </defs>
      </svg>

      <header className="border-line flex flex-wrap items-center gap-x-3 gap-y-1.5 border-b px-2.5 py-2">
        <h1 id="calendar-title" className="text-body font-semibold">
          {t('title')}
        </h1>
        <span className="text-label text-ink-subtle font-mono">{t('period', { start, end })}</span>
        <SegmentedControl
          label={t('metric')}
          value={metric}
          options={metricOptions}
          onChange={setMetric}
        />
        <span aria-hidden="true" className="flex-1" />
        <CalendarLegend metric={metric} scoredCells={region.scoredCells} />
      </header>

      <p className="text-meta text-ink-muted px-1" data-testid="calendar-provenance">
        {t('provenance', {
          observed: observedCells,
          total: cells.length,
          pct: new Intl.NumberFormat(locale, { maximumFractionDigits: 1 }).format(
            (observedCells / cells.length) * 100,
          ),
        })}
      </p>

      <p id="calendar-instructions" className="sr-only">
        {t('aria.instructions')}
      </p>

      <div
        role="application"
        tabIndex={0}
        aria-label={t('aria.grid', { region: regionLabel, start, end })}
        aria-describedby="calendar-instructions"
        onKeyDown={handleKeyDown}
        className="min-h-0 overflow-auto"
      >
        <div className="max-tablet:min-w-calendar px-2.5 pt-1.5 pb-1">
          <CalendarGrid
            region={region}
            cells={cells}
            metric={metric}
            active={active}
            hover={hover}
            onActive={activate}
            onHover={setHover}
            onTip={moveTip}
          />
        </div>
      </div>

      <p className="sr-only">
        {t('aria.summary', {
          over: region.alertCells,
          crisis: region.crisisCells,
        })}
      </p>

      <CalendarSummary
        cell={focusedCell}
        hovering={hover !== null}
        metric={metric}
        unit={unit}
        maxHfd={region.maxHfd}
        locale={locale}
      />

      <div
        ref={tipRef}
        aria-hidden="true"
        data-open={hover !== null}
        className="fc-cal-tip border-line bg-panel text-meta max-tablet:hidden pointer-events-none fixed z-20 flex flex-col gap-0.5 rounded-md border p-2 shadow-lg"
      >
        <span className="font-mono font-semibold whitespace-nowrap">
          {t('readout.when', {
            year: focusedCell.year,
            pentad: focusedCell.pentad,
            dates: pentadDates(focusedCell.pentad, locale),
          })}
        </span>
        <span className="text-ink-muted text-micro whitespace-nowrap">
          {focusedCell.observed ? t('status.observed') : t('status.modelled')} ·{' '}
          {metric === 'hfd'
            ? t(unit === 'density' ? 'readout.hfd' : 'readout.hfdDetections', {
                value: formatHfd(focusedCell.hfd, locale),
              })
            : focusedCell.sfai === null
              ? t('readout.notScored')
              : t('readout.sfai', { value: formatSigma(focusedCell.sfai, locale) })}
        </span>
        {focusedCell.crisis || focusedCell.alert ? (
          <span className="text-cyan text-micro font-mono whitespace-nowrap">
            {focusedCell.crisis ? t('readout.crisis') : t('readout.alert')}
          </span>
        ) : null}
      </div>
    </section>
  );
}
