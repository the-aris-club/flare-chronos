'use client';

import { useMemo } from 'react';
import { useLocale, useTranslations } from 'next-intl';
import { buildClock } from '@/lib/workbench/clock';
import { pentadDates, monthIndexAt } from '@/lib/calendar/pentad';
import { formatCompact } from '@/lib/workbench/format';
import type { CalendarRegionData } from '@/lib/calendar/types';

const CENTER = 160;
const INNER = 26;
const OUTER = 118;
const NINO_YEAR = 2016;

function point(pentad: number, radius: number) {
  const angle = -Math.PI / 2 + ((pentad - 1) / 73) * Math.PI * 2;
  // Round so server and client render the same attribute text (hydration-safe).
  return {
    x: Math.round((CENTER + radius * Math.cos(angle)) * 100) / 100,
    y: Math.round((CENTER + radius * Math.sin(angle)) * 100) / 100,
  };
}

function linePath(values: number[], max: number, close = true): string {
  const parts = values.map((value, index) => {
    const position = point(index + 1, INNER + (value / max) * (OUTER - INNER));
    return `${index === 0 ? 'M' : 'L'}${position.x.toFixed(1)} ${position.y.toFixed(1)}`;
  });

  return `${parts.join(' ')}${close ? ' Z' : ''}`;
}

export function ClockPane({
  region,
  year,
  regionLabel,
}: {
  region: CalendarRegionData;
  year: number;
  regionLabel: string;
}) {
  const t = useTranslations('Clock');
  const locale = useLocale();
  const months = t.raw('months') as string[];
  const clock = useMemo(() => buildClock(region, year), [region, year]);
  const ninoIndex = region.years.indexOf(NINO_YEAR);
  const nino = ninoIndex >= 0 ? region.hfd[ninoIndex] : clock.points.map(() => 0);
  const peakDates = pentadDates(clock.peak.pentad, locale);
  const peak = point(clock.peak.pentad, INNER + (clock.peak.hfd / clock.max) * (OUTER - INNER));

  const band =
    [
      ...clock.points.map((entry) => {
        const position = point(entry.pentad, INNER + (entry.q75 / clock.max) * (OUTER - INNER));
        return `${entry.pentad === 1 ? 'M' : 'L'}${position.x.toFixed(1)} ${position.y.toFixed(1)}`;
      }),
      ...[...clock.points].reverse().map((entry) => {
        const position = point(entry.pentad, INNER + (entry.q25 / clock.max) * (OUTER - INNER));
        return `L${position.x.toFixed(1)} ${position.y.toFixed(1)}`;
      }),
    ].join(' ') + ' Z';

  return (
    <section
      data-tour="clock"
      aria-labelledby="clock-title"
      className="border-line bg-panel flex h-105 flex-col overflow-hidden rounded-lg border"
    >
      <header className="border-line border-b px-3 py-2">
        <h2 id="clock-title" className="text-body font-semibold">
          {t('title')}
        </h2>
        <p className="text-micro text-ink-subtle font-mono">
          {t('subtitle', { region: regionLabel })}
        </p>
      </header>

      <div className="min-h-0 flex-1 px-2 pt-1">
        <svg
          viewBox="0 0 320 320"
          role="img"
          aria-label={t('aria', {
            year,
            region: regionLabel,
            pentad: clock.peak.pentad,
            dates: peakDates,
          })}
          className="size-full"
        >
          {[0.25, 0.5, 0.75, 1].map((fraction) => (
            <g key={fraction}>
              <circle
                cx={CENTER}
                cy={CENTER}
                r={INNER + fraction * (OUTER - INNER)}
                fill="none"
                stroke="var(--line)"
                strokeWidth={0.8}
              />
              <text
                x={CENTER + 4}
                y={CENTER - (INNER + fraction * (OUTER - INNER)) + 3}
                fill="var(--text-subtle)"
                fontFamily="var(--font-plex-mono)"
                fontSize={8}
              >
                {formatCompact(clock.max * fraction, locale)}
              </text>
            </g>
          ))}

          {clock.points.map((entry) => {
            const month = monthIndexAt(entry.pentad - 1);
            if (month === null) return null;
            const position = point(entry.pentad, OUTER + 18);

            return (
              <text
                key={entry.pentad}
                x={position.x}
                y={position.y + 3}
                textAnchor="middle"
                fill="var(--text-subtle)"
                fontFamily="var(--font-plex-mono)"
                fontSize={10}
              >
                {months[month]}
              </text>
            );
          })}

          <path d={band} fill="var(--raised)" stroke="var(--line)" strokeWidth={0.8} />
          <path
            d={linePath(nino, clock.max)}
            fill="none"
            stroke="var(--fire)"
            strokeWidth={1.2}
            strokeDasharray="3 2"
          />
          <path
            d={linePath(
              clock.points.map((entry) => entry.hfd),
              clock.max,
            )}
            fill="none"
            stroke="var(--teal)"
            strokeWidth={1.8}
          />

          <circle cx={peak.x} cy={peak.y} r={3.2} fill="var(--teal)" />
          <line
            x1={CENTER}
            y1={CENTER}
            x2={peak.x}
            y2={peak.y}
            stroke="var(--teal)"
            strokeWidth={0.8}
            strokeDasharray="2 2"
          />

          <text
            x={CENTER}
            y={CENTER - 2}
            textAnchor="middle"
            fill="var(--text)"
            fontFamily="var(--font-plex-mono)"
            fontSize={24}
            fontWeight={600}
          >
            {year}
          </text>
          <text
            x={CENTER}
            y={CENTER + 14}
            textAnchor="middle"
            fill="var(--text-subtle)"
            fontFamily="var(--font-plex-mono)"
            fontSize={9}
            letterSpacing="0.08em"
          >
            HFD
          </text>
        </svg>
      </div>

      <footer className="border-line text-micro text-ink-muted flex flex-wrap items-center gap-x-3 gap-y-1 border-t px-3 py-1.5">
        <span className="inline-flex items-center gap-1.5">
          <svg width={14} height={8} aria-hidden="true">
            <rect width={14} height={8} fill="var(--raised)" stroke="var(--line)" />
          </svg>
          {t('iqr')}
        </span>
        <span className="inline-flex items-center gap-1.5">
          <svg width={16} height={3} aria-hidden="true">
            <line
              x1={0}
              y1={1.5}
              x2={16}
              y2={1.5}
              stroke="var(--amber)"
              strokeWidth={1.5}
              strokeDasharray="3 2"
            />
          </svg>
          {t('elnino')}
        </span>
        <span className="inline-flex items-center gap-1.5">
          <svg width={16} height={3} aria-hidden="true">
            <line x1={0} y1={1.5} x2={16} y2={1.5} stroke="var(--teal)" strokeWidth={1.8} />
          </svg>
          {t('selected', { year })}
        </span>
        <span className="ml-auto font-mono">
          {t('peak', { pentad: clock.peak.pentad, dates: peakDates })}
        </span>
      </footer>
    </section>
  );
}
