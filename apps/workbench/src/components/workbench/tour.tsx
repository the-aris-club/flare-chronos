'use client';

import { useEffect, useRef, useState } from 'react';
import { useLocale, useTranslations } from 'next-intl';
import { Icon, ICON } from '@/components/ui/icon';
import { formatSigma } from '@/lib/calendar/format';
import type { TourFigures } from '@/lib/workbench/tour-figures';

const STEPS = 6;
const TARGETS = ['map', 'kpi', 'cmp', 'clock', 'cal', 'brief'] as const;
const PROGRESS = [1, 2, 3, 4, 5, 6];

export function TourOverlay({ onClose, figures }: { onClose: () => void; figures: TourFigures }) {
  const t = useTranslations('Tour');
  const locale = useLocale();
  const values = { ...figures, peak: formatSigma(figures.peakSfai, locale) };
  const [step, setStep] = useState(0);
  const spot = useRef<HTMLDivElement>(null);
  const last = step === STEPS - 1;

  useEffect(() => {
    const target = document.querySelector(`[data-tour="${TARGETS[step]}"]`);
    const element = spot.current;
    if (!target || !element) {
      if (element) element.style.opacity = '0';
      return;
    }

    const root = document.documentElement;
    const previous = root.style.overflow;
    root.style.overflow = 'hidden';
    target.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'smooth' });

    const update = () => {
      const rect = target.getBoundingClientRect();
      element.style.left = `${Math.max(4, rect.left - 6)}px`;
      element.style.top = `${Math.max(4, rect.top - 6)}px`;
      element.style.width = `${Math.min(window.innerWidth - 8, rect.width + 12)}px`;
      element.style.height = `${Math.min(window.innerHeight - 8, rect.height + 12)}px`;
      element.style.opacity = '1';
    };

    update();
    const observer = new ResizeObserver(update);
    observer.observe(target);
    window.addEventListener('scroll', update, true);
    window.addEventListener('resize', update);
    const timer = window.setTimeout(update, 320);

    return () => {
      observer.disconnect();
      window.removeEventListener('scroll', update, true);
      window.removeEventListener('resize', update);
      window.clearTimeout(timer);
      root.style.overflow = previous;
      window.scrollTo(0, 0);
    };
  }, [step]);

  return (
    <>
      <div
        ref={spot}
        aria-hidden="true"
        className="fc-tour-spot border-cyan pointer-events-none fixed z-40 rounded-md border-2 opacity-0 transition-opacity duration-200"
      />
      <div
        role="region"
        aria-label={t('title')}
        className="border-line bg-panel max-tablet:bottom-18 fixed bottom-3 left-3 z-50 flex w-full max-w-sm flex-col gap-2 rounded-lg border p-3 shadow-lg"
      >
        <div className="flex items-center gap-2">
          <span className="text-micro text-ink-subtle font-mono tracking-widest uppercase">
            {t('step', { current: step + 1, total: STEPS })}
          </span>
          <span className="ml-1 flex flex-1 gap-0.5">
            {PROGRESS.map((value) => (
              <span
                key={value}
                className={`h-0.5 flex-1 rounded-full ${value <= step + 1 ? 'bg-cyan' : 'bg-line'}`}
              />
            ))}
          </span>
          <button
            type="button"
            onClick={onClose}
            className="text-meta text-ink-subtle hover:text-ink"
          >
            {t('exit')}
          </button>
          <button
            type="button"
            onClick={onClose}
            aria-label={t('close')}
            className="text-ink-muted hover:bg-chip hover:text-ink inline-flex size-6 items-center justify-center rounded-sm"
          >
            <Icon icon={ICON.close} size="sm" />
          </button>
        </div>

        <h2 className="text-subhead font-semibold">{t(`step${step + 1}.title`)}</h2>
        <div className="flex items-baseline gap-2">
          <span className="text-metric font-mono font-semibold">
            {t(`step${step + 1}.figure`, values)}
          </span>
          <span className="text-meta text-ink-subtle">
            {t(`step${step + 1}.figureLabel`, values)}
          </span>
        </div>
        <p className="text-body text-ink-muted leading-relaxed">
          {t(`step${step + 1}.body`, values)}
        </p>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setStep((value) => Math.max(0, value - 1))}
            disabled={step === 0}
            className="border-line-strong text-meta text-ink h-7 rounded-md border px-2.5 disabled:opacity-40"
          >
            {t('back')}
          </button>
          <button
            type="button"
            onClick={() => {
              if (last) onClose();
              else setStep((value) => value + 1);
            }}
            className="border-line-strong bg-seg text-meta text-ink h-7 rounded-md border px-2.5 font-medium"
          >
            {last ? t('done') : t('next')}
          </button>
        </div>
      </div>
    </>
  );
}
