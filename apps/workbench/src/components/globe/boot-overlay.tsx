'use client';

import { useEffect, useRef, useState } from 'react';
import { useTranslations } from 'next-intl';
import { BrandGlyph } from '@/components/ui/brand-mark';
import { BOOT_STEPS, type BootStep } from '@/lib/globe/types';

type BootOverlayProps = {
  steps?: BootStep[];
  done: BootStep[];
  onDone: () => void;
};

export function BootOverlay({ steps = BOOT_STEPS, done, onDone }: BootOverlayProps) {
  const t = useTranslations('Globe');
  const [fading, setFading] = useState(false);
  const mounted = useRef(0);
  const complete = steps.length > 0 && steps.every((step) => done.includes(step));
  const count = steps.filter((step) => done.includes(step)).length;
  const next = steps.find((step) => !done.includes(step));

  useEffect(() => {
    mounted.current = performance.now();
  }, []);

  // A fresh boot sequence must show the overlay again, even if the previous one
  // had already started fading out.
  useEffect(() => {
    // eslint-disable-next-line react/set-state-in-effect
    if (!complete) setFading(false);
  }, [complete]);

  useEffect(() => {
    if (!complete || mounted.current === 0) return;

    const wait = Math.max(0, 900 - (performance.now() - mounted.current));
    const fade = window.setTimeout(() => setFading(true), wait);
    const finish = window.setTimeout(onDone, wait + 200);

    return () => {
      window.clearTimeout(fade);
      window.clearTimeout(finish);
    };
  }, [complete, onDone]);

  return (
    <div
      role="status"
      aria-live="polite"
      aria-busy={!complete}
      className={`bg-canvas fixed inset-0 z-50 flex items-center justify-center px-6 transition-opacity duration-150 ${
        fading ? 'pointer-events-none opacity-0' : 'opacity-100'
      }`}
    >
      <div className="flex w-75 max-w-full flex-col items-center gap-5">
        <div className="flex flex-col items-center gap-3.5">
          <span className="relative block size-18">
            <span className="fc-boot-ring border-line border-t-fire border-r-amber absolute inset-0 rounded-full border" />
            <span className="absolute inset-0 flex items-center justify-center">
              <BrandGlyph large />
            </span>
          </span>
          <span className="text-metric font-bold tracking-tight">
            <span className="text-fire">Flare</span>
            <span className="text-brand">Chronos</span>
          </span>
        </div>

        <div className="flex w-full flex-col gap-2.5">
          <div className="bg-line relative h-0.5 w-full overflow-hidden rounded-sm">
            <div
              className="fc-boot-bar from-fire to-amber absolute inset-y-0 left-0 rounded-sm bg-gradient-to-r"
              data-step={count}
            />
          </div>
          <div className="text-label text-ink-subtle flex items-center gap-2 font-mono tracking-widest uppercase">
            <span className="min-w-0 flex-1 truncate">
              {next ? t(`boot.${next}`) : t('boot.ready')}
            </span>
            <span className="text-ink-muted">
              {count}/{steps.length}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
