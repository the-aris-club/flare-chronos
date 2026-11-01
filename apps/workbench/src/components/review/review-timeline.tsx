'use client';

import { useState } from 'react';
import { useLocale, useTranslations } from 'next-intl';
import { localized } from '@/lib/workbench/format';
import { AmIcon, ICON } from '@/components/ui/icon';
import type { Decision, ReviewRun } from '@/data/fixtures/review';
import { reasonLabel } from './review-bits';

type StepKey = 'classify' | 'tools' | 'reasoning' | 'verification' | 'approval' | 'briefing';

const STEPS: StepKey[] = ['classify', 'tools', 'reasoning', 'verification', 'approval', 'briefing'];

export function ReviewTimeline({
  run,
  decision,
  compact = false,
}: {
  run: ReviewRun;
  decision: Decision | undefined;
  compact?: boolean;
}) {
  const t = useTranslations('Briefing.run');
  const review = useTranslations('Review');
  const locale = useLocale();
  const [active, setActive] = useState<StepKey | null>(null);
  const lang: 'en' | 'vi' = localized(locale, 'en', 'vi');

  const detail = (step: StepKey) => {
    switch (step) {
      case 'classify':
        return (
          <div className="text-meta text-ink-muted flex flex-col gap-1">
            <span>{`${run.region[lang]} · ${run.period[lang]}`}</span>
            <span className="font-mono">{run.classifier}</span>
            <span>{`${run.useCase} · ${run.useCaseName[lang]}`}</span>
          </div>
        );
      case 'tools':
        return (
          <ul className="flex flex-col gap-1.5">
            {run.tools.map((tool) => (
              <li key={tool.id} className="text-meta flex flex-wrap items-baseline gap-x-2">
                <span className="text-ink-subtle font-mono">{tool.id}</span>
                <span className="font-mono">{tool.name}</span>
                <span className="text-ink-subtle">{tool.fields}</span>
                <span className="text-ink-subtle ml-auto font-mono">{tool.time}</span>
              </li>
            ))}
          </ul>
        );
      case 'reasoning':
        return (
          <p className="text-meta text-ink-muted">
            {review('reasonOnly')} {run.useCaseName[lang]}.
          </p>
        );
      case 'verification':
        return <p className="text-meta text-ink-muted">{run.verification}</p>;
      case 'approval':
        return (
          <p className="text-meta text-ink-muted">
            {decision
              ? `${decision.reviewer} · ${reasonLabel(decision.reason, locale)} · ${decision.audit}`
              : review('noRec')}
          </p>
        );
      case 'briefing':
        return (
          <p className="text-meta text-ink-muted">
            {decision
              ? decision.kind === 'approve'
                ? review('msgApprove')
                : review('withheldBody')
              : review('noRec')}
          </p>
        );
    }
  };

  if (compact) {
    return (
      <section aria-label={t('timeline')} className="border-line bg-panel rounded-lg border">
        <div className="flex flex-col px-3 py-2">
          <span className="text-label text-ink-subtle mb-1 font-mono uppercase">
            {t('timeline')}
          </span>
          {STEPS.map((step, index) => {
            const done =
              index < 4 ||
              (step === 'approval' && !!decision) ||
              (step === 'briefing' && !!decision);
            const current = !done && (step === 'approval' || (step === 'briefing' && !!decision));
            const icon = done ? ICON.check : current ? ICON.dot : ICON.clock;
            const tone = done ? 'text-ok' : current ? 'text-cyan' : 'text-ink-subtle';

            return (
              <div key={step}>
                <button
                  type="button"
                  onClick={() => setActive(active === step ? null : step)}
                  aria-expanded={active === step}
                  className={`text-meta flex min-h-6 w-full items-center gap-2 rounded-sm px-1 py-1 text-left ${
                    active === step ? 'bg-seg text-ink' : 'text-ink-muted hover:text-ink'
                  }`}
                >
                  <AmIcon icon={icon} size="xs" className={tone} />
                  {t(step)}
                </button>
                {active === step && <div className="px-6 pb-2">{detail(step)}</div>}
              </div>
            );
          })}
        </div>
      </section>
    );
  }

  return (
    <section aria-label={t('timeline')} className="border-line bg-panel rounded-lg border">
      <div className="flex items-center gap-1 overflow-x-auto px-3 py-2">
        <span className="text-label text-ink-subtle mr-2 shrink-0 font-mono uppercase">
          {t('timeline')}
        </span>
        {STEPS.map((step, index) => {
          const done =
            index < 4 || (step === 'approval' && !!decision) || (step === 'briefing' && !!decision);
          const current = !done && (step === 'approval' || (step === 'briefing' && !!decision));
          const icon = done ? ICON.check : current ? ICON.dot : ICON.clock;
          const tone = done ? 'text-ok' : current ? 'text-cyan' : 'text-ink-subtle';

          return (
            <button
              key={step}
              type="button"
              onClick={() => setActive(active === step ? null : step)}
              aria-expanded={active === step}
              className={`text-meta inline-flex min-h-6 shrink-0 items-center gap-1.5 rounded-sm px-1.5 py-1 ${
                active === step ? 'bg-seg text-ink' : 'text-ink-muted hover:text-ink'
              }`}
            >
              <AmIcon icon={icon} size="xs" className={tone} />
              {t(step)}
              {index < STEPS.length - 1 && (
                <span aria-hidden="true" className="text-ink-subtle pl-1">
                  /
                </span>
              )}
            </button>
          );
        })}
        <span className="text-meta text-ink-subtle ml-auto shrink-0 font-mono">{run.duration}</span>
      </div>
      {active && (
        <div className="border-line border-t px-3 py-2">
          <h3 className="text-body mb-1.5 font-semibold">{t(active)}</h3>
          {detail(active)}
        </div>
      )}
    </section>
  );
}
