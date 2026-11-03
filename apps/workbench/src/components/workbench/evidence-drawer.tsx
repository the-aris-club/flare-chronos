'use client';

import { useEffect } from 'react';
import Image from 'next/image';
import { useLocale, useTranslations } from 'next-intl';
import { AmIcon, ICON } from '@/components/ui/icon';
import type { CalendarRegionData } from '@/lib/calendar/types';
import { buildEvidenceTables } from '@/lib/workbench/evidence-tables';
import type { AnnualSeries, Calibration, Epoch, MapPhysics } from '@/lib/workbench/types';
import { EvidenceIntro } from './evidence-intro';
import { EvidenceTable } from './evidence-table';

const FIGURES = [
  { id: 1, src: '/figures/fig-1.png' },
  { id: 2, src: '/figures/fig-2.png' },
  { id: 3, src: '/figures/fig-3.png' },
  { id: 4, src: '/figures/fig-4.png' },
  { id: 5, src: '/figures/fig-5.png' },
] as const;

type EvidenceDrawerProps = {
  open: boolean;
  onClose: () => void;
  series: AnnualSeries;
  epochs: Epoch[];
  physics: MapPhysics;
  calibration: Calibration;
  calendar: CalendarRegionData;
};

export function EvidenceDrawer({
  open,
  onClose,
  series,
  epochs,
  physics,
  calibration,
  calendar,
}: EvidenceDrawerProps) {
  const t = useTranslations('Evidence');
  const locale = useLocale();
  const tables = buildEvidenceTables({
    series,
    epochs,
    physics,
    calibration,
    calendar,
    locale,
    t,
  });

  useEffect(() => {
    if (!open) return;

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose();
    };

    const previous = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    document.addEventListener('keydown', onKeyDown);

    return () => {
      document.body.style.overflow = previous;
      document.removeEventListener('keydown', onKeyDown);
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="evidence-title"
      className="bg-scrim fixed inset-0 z-50 flex justify-end"
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <div className="border-line bg-panel flex h-dvh max-h-dvh w-full max-w-[580px] flex-col overflow-hidden border-y-0 border-r-0">
        <header className="border-line flex items-center gap-2 border-b px-3 py-2.5">
          <h2 id="evidence-title" className="text-subhead font-semibold">
            {t('title')}
          </h2>
          <span className="text-micro text-ink-subtle font-mono">{t('subtitle')}</span>
          <button
            type="button"
            onClick={onClose}
            aria-label={t('close')}
            autoFocus
            className="border-line text-ink-muted hover:bg-chip hover:text-ink ml-auto inline-flex size-7 items-center justify-center rounded-md border"
          >
            <AmIcon icon={ICON.close} size="sm" />
          </button>
        </header>

        <div className="tablet:grid-cols-2 grid gap-3 overflow-y-auto p-3">
          <EvidenceIntro physics={physics} calibration={calibration} />
          {FIGURES.map((figure) => {
            const table = tables[figure.id];

            return (
              <figure
                key={figure.id}
                className="border-line bg-raised flex flex-col gap-1.5 rounded-md border p-2"
              >
                <Image
                  src={figure.src}
                  width={1800}
                  height={1080}
                  alt={t(`caption${figure.id}`)}
                  className="border-line h-auto w-full rounded-sm border"
                />
                <figcaption className="flex flex-col gap-0.5">
                  <span className="text-body font-semibold">{t(`figure${figure.id}`)}</span>
                  <span className="text-meta text-ink-muted leading-relaxed">
                    {t(`caption${figure.id}`)}
                  </span>
                  <span className="text-micro text-ink-subtle font-mono">
                    {t(`source${figure.id}`)}
                  </span>
                </figcaption>
                {table && (
                  <EvidenceTable
                    caption={table.caption}
                    columns={table.columns}
                    rows={table.rows}
                  />
                )}
              </figure>
            );
          })}
        </div>
      </div>
    </div>
  );
}
