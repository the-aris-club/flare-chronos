'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useLocale, useTranslations } from 'next-intl';
import { localized } from '@/lib/workbench/format';
import { useReviewStore } from '@/components/review/review-store';
import { AmIcon, ICON } from '@/components/ui/icon';
import {
  AUDIENCES,
  statusOf,
  type Audience,
  type DecisionKind,
  type ReviewRun,
} from '@/data/fixtures/review';
import { BriefText } from './brief-text';
import { BriefingDialog } from './briefing-dialog';
import { CitationDialog } from './citation-dialog';
import { ConfirmDialog } from './confirm-dialog';
import { DecisionChip, StatusChip, UrgencyChip, utcTime } from './review-bits';
import { ReviewDecision } from './review-decision';
import { EvidenceSummary, RunSummary } from './run-summary';
import { ReviewTimeline } from './review-timeline';

type Dialog =
  | { kind: 'briefing' }
  | { kind: 'citation'; key: string }
  | { kind: 'confirm'; decision: DecisionKind; reason: string; note: string }
  | null;

export function ReviewRun({ run }: { run: ReviewRun }) {
  const t = useTranslations('Review');
  const locale = useLocale();
  const lang: 'en' | 'vi' = localized(locale, 'en', 'vi');
  const store = useReviewStore();
  const decision = store.decisionsFor(run.id);
  const status = statusOf(run.id, store.decisions);
  const [audience, setAudience] = useState<Audience>('rangers');
  const [showKeys, setShowKeys] = useState(false);
  const [dialog, setDialog] = useState<Dialog>(null);
  const facts = Object.values(run.facts);
  const noSource = facts.filter((fact) => fact.verdict === 'nosource').length;
  const approveAvailable = noSource === 0;

  useEffect(() => {
    const query = new URLSearchParams(window.location.search);
    const overlay = query.get('overlay');
    const timer = window.setTimeout(() => {
      if (overlay === 'briefing') setDialog({ kind: 'briefing' });
      if (overlay === 'citation') {
        setDialog({ kind: 'citation', key: Object.keys(run.facts)[0] ?? '' });
      }
      if (overlay === 'confirm') {
        setDialog({ kind: 'confirm', decision: 'approve', reason: 'evidence', note: '' });
      }
    }, 0);

    return () => window.clearTimeout(timer);
  }, [run]);

  const fact = dialog?.kind === 'citation' ? run.facts[dialog.key] : null;

  return (
    <div className="tablet:px-5 tablet:py-6 mx-auto flex w-full max-w-400 flex-col gap-3 px-3 py-4">
      <div className="flex flex-wrap items-center gap-2">
        <Link
          href="/review"
          className="text-meta text-ink-muted hover:text-ink border-line-strong inline-flex h-8 items-center gap-1 rounded-md border px-2"
        >
          <AmIcon icon={ICON.back} size="sm" />
          {t('back')}
        </Link>
        <h1 className="text-title font-mono font-semibold">{run.id}</h1>
        <span className="text-meta text-ink-muted">
          {run.useCase} · {run.useCaseName[lang]}
        </span>
        <StatusChip status={status} />
        <UrgencyChip urgency={run.urgency} />
        {decision && <DecisionChip kind={decision.kind} />}
        <button
          type="button"
          onClick={() => setDialog({ kind: 'briefing' })}
          className="text-meta border-line-strong hover:bg-chip ml-auto inline-flex h-8 items-center rounded-md border px-3 font-medium"
        >
          {t('viewFull')}
        </button>
      </div>

      <div className="grid grid-cols-1 gap-3 xl:grid-cols-[18rem_minmax(0,1fr)_20rem]">
        <RunSummary run={run} />

        <section className="border-line bg-panel flex min-w-0 flex-col gap-3 rounded-lg border p-3">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-subhead font-semibold">{t('fullBrief')}</h2>
            <div
              role="group"
              aria-label={t('audience')}
              className="border-line-strong ml-auto inline-flex gap-0.5 rounded-md border p-0.5"
            >
              {AUDIENCES.map((item) => (
                <button
                  key={item.value}
                  type="button"
                  onClick={() => setAudience(item.value)}
                  aria-pressed={audience === item.value}
                  className={`text-meta h-7 rounded-sm px-2 font-medium ${
                    audience === item.value ? 'bg-seg text-ink' : 'text-ink-subtle hover:text-ink'
                  }`}
                >
                  {localized(locale, item.en, item.vi)}
                </button>
              ))}
            </div>
            <button
              type="button"
              onClick={() => setShowKeys((value) => !value)}
              aria-pressed={showKeys}
              className={`text-meta h-7 rounded-md border px-2 font-medium ${
                showKeys
                  ? 'border-line-strong bg-seg text-ink'
                  : 'border-line-strong text-ink-muted'
              }`}
            >
              {t('showKeys')}
            </button>
          </div>

          <div className="text-meta text-ink-subtle flex flex-wrap items-center gap-x-3 gap-y-1">
            <span className="inline-flex items-center gap-1">
              <AmIcon icon={ICON.check} size="xs" className="text-teal" />
              {t('verified')}
            </span>
            <span className="inline-flex items-center gap-1">
              <AmIcon icon={ICON.rewrite} size="xs" className="text-amber" />
              {t('rewritten')}
            </span>
            <span className="inline-flex items-center gap-1">
              <AmIcon icon={ICON.alert} size="xs" className="text-bad" />
              {t('nosource')}
            </span>
            <span className="text-ink-subtle">· {t('chipHint')}</span>
          </div>

          {status === 'withheld' ? (
            <div className="border-purple/50 rounded-md border p-4">
              <h3 className="text-body font-semibold">{t('withheldTitle')}</h3>
              <p className="text-meta text-ink-muted mt-1">{t('withheldBody')}</p>
              {decision && (
                <p className="text-meta text-ink-subtle mt-2 font-mono">
                  {decision.audit} · {utcTime(decision.at)}
                </p>
              )}
            </div>
          ) : (
            <>
              {lang === 'vi' && (
                <p className="text-meta text-ink-subtle border-line border-l-2 px-2 py-1">
                  {t('viBriefNote')}
                </p>
              )}
              <BriefText
                lines={run.brief[audience]}
                facts={run.facts}
                showKeys={showKeys}
                onFact={(key) => setDialog({ kind: 'citation', key })}
              />
            </>
          )}
        </section>

        <div className="flex flex-col gap-3">
          <EvidenceSummary run={run} />
          <div id="review-decision">
            <ReviewDecision
              decision={decision}
              approveAvailable={approveAvailable}
              onRequest={(kind, reason, note) =>
                setDialog({ kind: 'confirm', decision: kind, reason, note })
              }
            />
          </div>
        </div>
      </div>

      <ReviewTimeline run={run} decision={decision} />

      {dialog?.kind === 'briefing' && (
        <BriefingDialog
          run={run}
          decision={decision}
          audience={audience}
          showKeys={showKeys}
          onAudience={setAudience}
          onShowKeys={() => setShowKeys((value) => !value)}
          onFact={(key) => setDialog({ kind: 'citation', key })}
          onClose={() => setDialog(null)}
          onDecision={() => {
            setDialog(null);
            document.getElementById('review-decision')?.scrollIntoView({ block: 'center' });
          }}
        />
      )}

      {dialog?.kind === 'citation' && fact && (
        <CitationDialog run={run} fact={fact} onClose={() => setDialog(null)} />
      )}

      {dialog?.kind === 'confirm' && (
        <ConfirmDialog
          run={run}
          kind={dialog.decision}
          reason={dialog.reason}
          note={dialog.note}
          onClose={() => setDialog(null)}
          onConfirm={() => {
            store.record(run.id, dialog.decision, dialog.reason, dialog.note);
            setDialog(null);
          }}
        />
      )}
    </div>
  );
}
