'use client';

import Link from 'next/link';
import { useMemo, useState } from 'react';
import { useLocale, useTranslations } from 'next-intl';
import { localized } from '@/lib/workbench/format';
import { BriefingEvents } from './briefing-events';
import { BriefText } from '@/components/review/brief-text';
import { DecisionChip, reasonLabel, utcTime } from '@/components/review/review-bits';
import { useReviewStore } from '@/components/review/review-store';
import { AmIcon, ICON } from '@/components/ui/icon';
import { SegmentedControl } from '@/components/ui/segmented-control';
import { AUDIENCES, type Audience, type ReviewRun } from '@/data/fixtures/review';
import {
  factStatus,
  formatSeconds,
  phaseAt,
  type FactStatus,
  type RunSchedule,
  type RunState,
  type ServiceState,
} from '@/lib/workbench/service';
import { PrincipalRow, RailStatusChip } from './service-panel';

export function BriefingRun({
  run,
  service,
  runState,
  schedule,
  onStart,
  onDisconnect,
}: {
  run: ReviewRun;
  service: ServiceState;
  runState: RunState;
  schedule: RunSchedule;
  onStart: () => void;
  onDisconnect: () => void;
}) {
  const t = useTranslations('Briefing.run');
  const review = useTranslations('Review');
  const locale = useLocale();
  const lang: 'en' | 'vi' = localized(locale, 'en', 'vi');
  const store = useReviewStore();
  const decision = store.decisionsFor(run.id);
  const facts = useMemo(() => Object.values(run.facts), [run.facts]);
  const [audience, setAudience] = useState<Audience>('rangers');
  const [factKey, setFactKey] = useState<string | null>(null);
  const fact = factKey ? run.facts[factKey] : null;

  const settled = runState.status === 'paused' || runState.status === 'done' || Boolean(decision);
  const phase = phaseAt(runState.status, runState.elapsed, schedule);
  const rewriteIndex = facts.findIndex((item) => item.verdict === 'rewritten');
  const states = useMemo(
    () =>
      facts.map((_, index) => factStatus(index, rewriteIndex, runState.elapsed, schedule, settled)),
    [facts, rewriteIndex, runState.elapsed, schedule, settled],
  );
  const verified = states.filter((state) => state === 'verified').length;
  const allVerified = verified === facts.length;
  const showBrief = Boolean(decision) || phase >= 2;
  const running = runState.status === 'running';
  const statusLabel = decision
    ? decision.kind === 'approve'
      ? t('published')
      : t('rejected')
    : running
      ? t('running')
      : runState.status === 'paused'
        ? review('needs')
        : t('ready');
  const statusTone = decision
    ? decision.kind === 'approve'
      ? 'ok'
      : 'bad'
    : running
      ? 'warn'
      : runState.status === 'paused'
        ? 'cyan'
        : 'neutral';
  const elapsed = settled ? schedule.approvalAt : runState.elapsed;
  const duration = phase >= 0 ? formatSeconds(elapsed) : run.duration;

  const statusFor = (key: string): FactStatus => {
    const index = facts.findIndex((item) => item.key === key);
    if (index < 0) return 'verified';
    return states[index];
  };

  const gate = decision
    ? decision.kind === 'approve'
      ? t('signed', { name: decision.reviewer, id: decision.audit })
      : t('rejectedGate', { name: decision.reviewer, id: decision.audit })
    : allVerified
      ? t('awaiting')
      : t('blocked', { count: facts.length - verified });

  return (
    <div className="flex flex-col gap-3">
      <div className="border-line bg-panel flex flex-col gap-2 rounded-lg border p-3">
        <div className="flex flex-wrap items-center gap-1.5">
          <RailStatusChip tone={statusTone} label={statusLabel} />
          <Link
            href={`/review/runs/${run.id}`}
            className="text-meta text-ink-muted hover:text-ink ml-auto inline-flex items-center gap-1"
          >
            {t('openReview')}
            <AmIcon icon={ICON.external} size="sm" />
          </Link>
        </div>
        <span className="text-meta text-ink-muted">
          {t('target', { region: run.region[lang], period: run.period[lang] })}
        </span>
        <span className="text-micro text-ink-subtle font-mono">{run.useCaseName[lang]}</span>
        <div className="border-line flex items-center justify-between gap-2 border-t pt-2">
          <span className="text-meta text-ink-muted">
            {t('numbers', { verified, total: facts.length })}
          </span>
          <span className="text-micro text-ink-subtle font-mono">{duration}</span>
        </div>
      </div>

      <PrincipalRow onDisconnect={onDisconnect} />

      {service === 'degraded' && (
        <div
          role="status"
          className="border-warn/50 text-meta text-ink-muted flex gap-2.5 rounded-md border px-2.5 py-2 leading-relaxed"
        >
          <AmIcon icon={ICON.alert} size="sm" className="text-warn mt-0.5 shrink-0" />
          <span>
            <b className="text-ink font-semibold">{t('degradedTitle')}</b> {t('degradedBody')}
          </span>
        </div>
      )}

      <div className="flex items-center gap-2">
        <div className="flex min-w-0 flex-col">
          <span className="text-micro text-ink-subtle font-mono tracking-widest uppercase">
            {t('runId', { id: run.id })} · {t('sample')}
          </span>
          <span className="text-meta truncate font-semibold">
            {run.region[lang]} · {run.period[lang]}
          </span>
        </div>
        {!decision && (
          <button
            type="button"
            onClick={onStart}
            disabled={running || runState.status === 'paused'}
            className="bg-ink text-canvas text-meta ml-auto h-7 shrink-0 rounded-md px-2.5 font-semibold disabled:cursor-not-allowed disabled:opacity-50"
          >
            {running || runState.status === 'paused' ? t('inProgress') : t('start')}
          </button>
        )}
      </div>

      <div className="flex flex-wrap gap-1.5">
        <span className="border-line-strong text-micro text-ink-muted inline-flex h-5 items-center rounded-sm border px-1.5 font-mono">
          {service === 'degraded' ? t('classifierFallback') : t('classifierPrimary')}
        </span>
        <span
          className={`text-micro inline-flex h-5 items-center rounded-sm border px-1.5 font-mono ${
            service === 'degraded' ? 'border-warn text-warn' : 'border-ok text-ok'
          }`}
        >
          {service === 'degraded' ? t('tierFallback') : t('tierFull')}
        </span>
      </div>

      <BriefingEvents
        run={run}
        status={runState.status}
        elapsed={runState.elapsed}
        schedule={schedule}
        degraded={service === 'degraded'}
        decision={decision}
      />

      {showBrief && (
        <div className="border-line bg-panel flex flex-col overflow-hidden rounded-lg border">
          <div className="border-line flex flex-wrap items-center gap-2 border-b px-3 py-2">
            <span className="text-body font-semibold">{t('briefing')}</span>
            <span
              className={`text-label inline-flex h-5 items-center rounded-sm border px-1.5 font-mono ${
                decision
                  ? decision.kind === 'approve'
                    ? 'border-ok text-ok'
                    : 'border-bad text-bad'
                  : 'border-line text-ink-subtle border-dashed'
              }`}
            >
              {decision
                ? decision.kind === 'approve'
                  ? t('published')
                  : t('rejected')
                : t('draft')}
            </span>
          </div>
          <div className="px-3 pt-2">
            <SegmentedControl
              label={t('audience')}
              value={audience}
              options={AUDIENCES.map((item) => ({
                value: item.value,
                label: localized(locale, item.en, item.vi),
              }))}
              onChange={setAudience}
            />
          </div>
          <div className="px-3 py-2.5">
            {lang === 'vi' && (
              <p className="text-meta text-ink-subtle border-line mb-2 border-l-2 px-2 py-1">
                {review('viBriefNote')}
              </p>
            )}
            {decision?.kind === 'reject' ? (
              <div className="border-purple/50 rounded-md border p-3">
                <h3 className="text-body font-semibold">{review('withheldTitle')}</h3>
                <p className="text-meta text-ink-muted mt-1">{review('withheldBody')}</p>
              </div>
            ) : (
              <BriefText
                lines={run.brief[audience]}
                facts={run.facts}
                showKeys={true}
                onFact={setFactKey}
                statusFor={decision ? undefined : statusFor}
              />
            )}
          </div>
          <div
            className={`border-line text-micro flex items-center gap-2 border-t px-3 py-2 ${
              decision
                ? decision.kind === 'approve'
                  ? 'text-ok'
                  : 'text-bad'
                : allVerified
                  ? 'text-ink-muted'
                  : 'text-warn'
            }`}
          >
            <span className="text-ink-subtle font-mono">
              {verified}/{facts.length}
            </span>
            {gate}
          </div>
        </div>
      )}

      {fact && (
        <div className="border-line bg-panel rounded-md border p-2.5">
          <span className="text-label text-ink-subtle font-mono uppercase">
            {t('verification')}
          </span>
          <p className="text-meta mt-1 font-mono">{fact.text}</p>
          <p className="text-micro text-ink-subtle mt-1">
            {t('source', { source: `${fact.tool} · ${fact.field}` })}
          </p>
          <p className="text-micro text-ink-subtle">
            {fact.provenance} · {fact.raw}
          </p>
          {fact.note && <p className="text-micro text-warn mt-1">{fact.note}</p>}
        </div>
      )}

      <div className="border-line bg-panel flex flex-col gap-1.5 rounded-lg border p-3">
        <span className="text-label text-ink-subtle font-mono uppercase">
          {decision ? review('decisionRec') : review('decision')}
        </span>
        {decision ? (
          <>
            <DecisionChip kind={decision.kind} />
            <span className="text-meta text-ink-muted">
              {decision.reviewer} · {reasonLabel(decision.reason, locale)}
            </span>
            <span className="text-micro text-ink-subtle font-mono">
              {utcTime(decision.at)} · {decision.audit}
            </span>
            {decision.note && <span className="text-meta text-ink-subtle">{decision.note}</span>}
          </>
        ) : (
          <>
            <span className="text-meta text-ink-muted">
              {runState.status === 'paused' ? t('awaiting') : t('reviewOwns')}
            </span>
            <Link
              href={`/review/runs/${run.id}`}
              className="bg-ink text-canvas text-meta mt-1 inline-flex h-7 items-center justify-center rounded-md px-2.5 font-semibold"
            >
              {t('openReview')}
            </Link>
          </>
        )}
      </div>
    </div>
  );
}
