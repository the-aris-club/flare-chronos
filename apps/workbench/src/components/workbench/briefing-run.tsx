'use client';

import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { AmIcon, ICON } from '@/components/ui/icon';
import { Markdown } from '@/components/ui/markdown';
import { useLabels } from '@/components/review/use-labels';
import type { RunView } from '@/lib/service/run';
import { PrincipalRow } from './service-panel';

export const PRESETS = [
  { useCase: 'UC-2.2', key: 'presetDispatch' },
  { useCase: 'UC-S1.4', key: 'presetAlert' },
] as const;

export type Preset = (typeof PRESETS)[number];

export function BriefingRun({
  run,
  region,
  onStart,
}: {
  run: RunView;
  region: 'mekong' | 'amazon';
  onStart: (preset: Preset) => void;
}) {
  const t = useTranslations('Briefing.run');
  const labels = useLabels();
  const busy = run.phase === 'running';
  const verification = run.signOff?.verification ?? run.verification;
  const unverified = verification?.unverified_numbers?.length ?? 0;
  const checked = verification?.checked_numbers_count ?? 0;
  const briefing = run.signOff?.briefing ?? run.briefing;

  return (
    <div className="flex flex-col gap-3">
      <PrincipalRow />

      <div className="border-line bg-panel flex flex-col gap-2 rounded-lg border p-3">
        <span className="text-micro text-ink-subtle font-mono tracking-widest uppercase">
          {t('target', { region: labels.region(region), period: '2024' })}
        </span>
        <div className="flex flex-wrap gap-2">
          {PRESETS.map((preset) => (
            <button
              key={preset.useCase}
              type="button"
              disabled={busy}
              onClick={() => onStart(preset)}
              className="bg-ink text-canvas text-meta h-8 rounded-md px-3 font-semibold disabled:opacity-40"
            >
              {t(preset.key)}
            </button>
          ))}
        </div>
      </div>

      {run.phase !== 'idle' && (
        <section aria-live="polite" className="border-line bg-panel flex flex-col gap-2.5 rounded-lg border p-3">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-subhead font-semibold">{t('timeline')}</h3>
            {run.useCaseId && (
              <span className="text-label text-ink-subtle font-mono">
                {run.useCaseId} · {labels.useCase(run.useCaseId)}
              </span>
            )}
            {run.mode && (
              <span className="text-label text-ink-subtle ml-auto font-mono">
                {t('mode', { mode: run.mode })}
              </span>
            )}
          </div>

          <ul className="text-meta flex flex-col gap-1.5">
            <li className="flex items-center gap-2">
              <AmIcon icon={run.nodes.length > 0 ? ICON.check : ICON.dot} size="xs" />
              {t('stepsLine', { count: run.nodes.length })}
            </li>
            <li className="flex items-start gap-2">
              <AmIcon icon={run.tools.length > 0 ? ICON.check : ICON.dot} size="xs" />
              <span className="min-w-0">
                {t('toolsLine', { count: run.tools.length })}
                <span className="text-ink-subtle block font-mono break-words">
                  {run.tools.join(' · ')}
                </span>
              </span>
            </li>
            {verification && (
              <li className="flex items-center gap-2">
                <AmIcon
                  icon={verification.passed ? ICON.check : ICON.alert}
                  size="xs"
                  className={verification.passed ? 'text-ok' : 'text-bad'}
                />
                {unverified === 0
                  ? t('numbers', { verified: checked, total: checked })
                  : t('blocked', { count: unverified })}
              </li>
            )}
          </ul>

          {briefing && (
            <div className="border-line border-t pt-2">
              <Markdown>{briefing}</Markdown>
            </div>
          )}

          {run.phase === 'paused' && run.threadId && (
            <div className="border-cyan/50 flex flex-col gap-2 rounded-md border p-2.5">
              <span className="text-body font-semibold">{t('pausedTitle')}</span>
              <p className="text-meta text-ink-muted">{t('reviewOwns')}</p>
              <Link
                href={`/review/runs/${run.threadId}`}
                className="bg-ink text-canvas text-meta inline-flex h-8 items-center self-start rounded-md px-3 font-semibold"
              >
                {t('openReview')}
              </Link>
            </div>
          )}

          {run.phase === 'done' && run.threadId && (
            <p className="text-meta text-ink-muted">
              {run.approved === undefined
                ? t('doneLine')
                : run.approved
                  ? t('doneApproved', { id: run.threadId })
                  : t('doneRejected', { id: run.threadId })}
            </p>
          )}

          {run.phase === 'failed' && (
            <p role="alert" className="text-meta text-bad">
              {t('failed')}: {run.error}
            </p>
          )}
        </section>
      )}
    </div>
  );
}
