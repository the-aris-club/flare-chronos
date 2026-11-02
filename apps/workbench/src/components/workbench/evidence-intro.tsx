'use client';

import { useLocale, useTranslations } from 'next-intl';
import { formatCount, formatDecimal } from '@/lib/workbench/format';
import type { Calibration, MapPhysics } from '@/lib/workbench/types';

export function EvidenceIntro({
  physics,
  calibration,
}: {
  physics: MapPhysics;
  calibration: Calibration;
}) {
  const t = useTranslations('Evidence');
  const locale = useLocale();
  const viirsRadius = Math.sqrt(physics.viirsNadir / physics.modisEdge) * 54;
  const ksBefore = Math.max(0.01, calibration.ksBefore);
  const ksAfter = Math.max(0.01, calibration.ksAfter);

  return (
    <div className="tablet:col-span-2 grid grid-cols-1 gap-3 lg:grid-cols-2">
      <section className="border-line bg-raised flex flex-col gap-2 rounded-md border p-3">
        <div className="flex flex-wrap items-baseline gap-2">
          <span className="text-body font-semibold">1 · {t('scanTitle')}</span>
          <span className="text-metric ml-auto font-mono font-semibold">
            {formatDecimal(physics.ratio, locale)}×
          </span>
        </div>
        <p className="text-meta text-ink-muted leading-relaxed">{t('scanBody')}</p>
        <div className="border-line relative rounded-md border border-dashed p-2">
          <span className="text-micro text-ink-subtle absolute top-1 right-2 font-mono uppercase">
            {t('schematic')}
          </span>
          <svg
            viewBox="0 0 260 100"
            role="img"
            aria-label={t('scanTitle')}
            className="h-auto w-full"
          >
            <ellipse
              cx={82}
              cy={50}
              rx={72}
              ry={29}
              transform="rotate(-8 82 50)"
              fill="var(--amber)"
              fillOpacity={0.14}
              stroke="var(--amber)"
              strokeWidth={1.2}
            />
            <circle
              cx={184}
              cy={50}
              r={18}
              fill="var(--amber)"
              fillOpacity={0.14}
              stroke="var(--amber)"
              strokeWidth={1.2}
            />
            <circle cx={232} cy={50} r={viirsRadius} fill="var(--raw)" fillOpacity={0.85} />
            <text
              x={82}
              y={92}
              fontSize={8}
              textAnchor="middle"
              fill="var(--text-subtle)"
              fontFamily="var(--font-plex-mono)"
            >
              {t('modisEdge')} {formatDecimal(physics.modisEdge, locale)} km²
            </text>
            <text
              x={184}
              y={78}
              fontSize={8}
              textAnchor="middle"
              fill="var(--text-subtle)"
              fontFamily="var(--font-plex-mono)"
              className="max-tablet:hidden"
            >
              {t('modisNadir')}
            </text>
            <text
              x={258}
              y={94}
              fontSize={8}
              textAnchor="end"
              fill="var(--text-subtle)"
              fontFamily="var(--font-plex-mono)"
              className="max-tablet:hidden"
            >
              {t('viirsNadir')}
            </text>
          </svg>
        </div>
      </section>

      <section className="border-line bg-raised flex flex-col gap-2 rounded-md border p-3">
        <div className="flex flex-wrap items-baseline gap-2">
          <span className="text-body font-semibold">2 · {t('calTitle')}</span>
          <span className="text-metric ml-auto font-mono font-semibold">
            {formatDecimal(calibration.ksBefore, locale, 4)} →{' '}
            {formatDecimal(calibration.ksAfter, locale, 4)}
          </span>
        </div>
        <p className="text-meta text-ink-muted leading-relaxed">{t('calBody')}</p>
        <div className="flex flex-col gap-1.5">
          {[
            [t('ksBefore'), ksBefore, 'var(--bad)'],
            [t('ksAfter'), ksAfter, 'var(--ok)'],
          ].map(([label, value, color]) => (
            <div key={String(label)} className="flex items-center gap-2">
              <span className="text-micro text-ink-subtle w-12 font-mono">{label}</span>
              <svg width={180} height={8} aria-hidden="true">
                <rect
                  width={(Number(value) / ksBefore) * 180}
                  height={8}
                  rx={2}
                  fill={String(color)}
                />
              </svg>
              <span className="text-micro font-mono">
                {formatDecimal(Number(value), locale, 4)}
              </span>
            </div>
          ))}
        </div>
        <span className="text-micro text-ink-subtle font-mono">
          {t('pairs', { count: formatCount(calibration.pairs, locale) })}
        </span>
      </section>

      <section className="border-line bg-raised flex flex-col gap-2 rounded-md border p-3 lg:col-span-2">
        <span className="text-body font-semibold">3 · {t('limitsTitle')}</span>
        <ul className="text-meta text-ink-muted flex list-disc flex-col gap-1 pl-4 leading-relaxed">
          <li>{t('limitWindow')}</li>
          <li>
            {t('limitHoldout', {
              year: calibration.holdout.trainLastYear,
              gain: formatDecimal(calibration.holdout.gainMw, locale, 1),
              low: formatDecimal(calibration.holdout.ciLowMw, locale, 1),
              high: formatDecimal(calibration.holdout.ciHighMw, locale, 1),
              significant:
                calibration.holdout.ciLowMw > 0 || calibration.holdout.ciHighMw < 0 ? 'yes' : 'no',
            })}
          </li>
          <li>{t('limitInSample')}</li>
          <li>{t('limitReproduce')}</li>
        </ul>
      </section>
    </div>
  );
}
