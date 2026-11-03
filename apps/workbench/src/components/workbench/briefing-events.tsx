'use client';

import Link from 'next/link';
import { useLocale, useTranslations } from 'next-intl';
import { localized } from '@/lib/workbench/format';
import { DecisionChip, reasonLabel, utcTime } from '@/components/review/review-bits';
import { AmIcon, ICON } from '@/components/ui/icon';
import { factText, type Decision, type Fact, type ReviewRun } from '@/data/fixtures/review';
import {
  factStatus,
  formatSeconds,
  phaseAt,
  PRINCIPAL,
  type RunSchedule,
  type RunStatus,
} from '@/lib/workbench/service';
import { EventRow, type EventState } from './briefing-event-row';

export function BriefingEvents({
  run,
  status,
  elapsed,
  schedule,
  degraded,
  decision,
}: {
  run: ReviewRun;
  status: RunStatus;
  elapsed: number;
  schedule: RunSchedule;
  degraded: boolean;
  decision: Decision | undefined;
}) {
  const t = useTranslations('Briefing.run');
  const review = useTranslations('Review');
  const locale = useLocale();
  const lang: 'en' | 'vi' = localized(locale, 'en', 'vi');
  const phase = decision ? 5 : phaseAt(status, elapsed, schedule);
  const settled = status === 'paused' || status === 'done' || Boolean(decision);
  const facts = Object.values(run.facts);
  const rewriteIndex = facts.findIndex((fact) => fact.verdict === 'rewritten');
  const factStates = facts.map((fact, index) =>
    factStatus(index, rewriteIndex, elapsed, schedule, settled),
  );
  const verified = factStates.filter((state) => state === 'verified').length;
  const rewriting = factStates.filter(
    (state) => state === 'rewriting' || state === 'nosource',
  ).length;
  const allVerified = verified === facts.length;
  const urgencyKey =
    run.urgency === 'crisis'
      ? 'crisisUrgency'
      : run.urgency === 'elevated'
        ? 'elevatedUrgency'
        : 'routineUrgency';

  function stateOf(index: number): EventState {
    if (phase < 0) return 'pending';
    if (phase > index) return 'done';
    if (phase === index) return index === 4 && status === 'paused' ? 'paused' : 'running';
    return 'pending';
  }

  const tools = run.tools;
  const toolDuration = (schedule.toolsEnd - schedule.classifyEnd) / Math.max(1, tools.length);
  function toolState(index: number): 'pending' | 'running' | 'done' {
    if (phase > 1) return 'done';
    if (phase < 1) return 'pending';
    const start = schedule.classifyEnd + index * toolDuration;
    if (elapsed < start) return 'pending';
    if (elapsed < start + toolDuration) return 'running';
    return 'done';
  }

  function toolResult(fact: Fact | undefined): string {
    if (!fact) return '';
    return fact.text;
  }

  const resultFor = (name: string) => {
    if (name.startsWith('footprint.modis_pixel')) {
      return `${toolResult(run.facts.modis_edge)} · ${toolResult(run.facts.scan)} × ${toolResult(run.facts.track)}`;
    }
    if (name.startsWith('footprint.viirs_pixel')) return toolResult(run.facts.viirs);
    if (name.startsWith('footprint.compare')) return toolResult(run.facts.reduction);
    if (name.startsWith('h3.polyfill')) return toolResult(run.facts.cells);
    if (name.startsWith('orbit.revisit')) return toolResult(run.facts.revisit);
    if (name.startsWith('episodes.cluster')) return toolResult(run.facts.cluster);
    return '';
  };

  const reasoning = run.brief.scientists
    .slice(1)
    .map((line) => factText(line, run.facts))
    .join(' ');
  const reasoningProgress =
    phase > 2
      ? 1
      : phase === 2
        ? Math.min(
            1,
            Math.max(
              0,
              (elapsed - schedule.toolsEnd) / Math.max(1, schedule.reasonEnd - schedule.toolsEnd),
            ),
          )
        : 0;
  const reasonProgress = Math.floor(reasoningProgress * reasoning.length);
  const decisionAt = decision ? utcTime(decision.at) : '';
  const published = decision?.kind === 'approve';

  return (
    <ol className="flex list-none flex-col p-0">
      <EventRow
        title={t('classify')}
        state={stateOf(0)}
        time={
          phase > 0
            ? formatSeconds(schedule.classifyEnd)
            : phase === 0
              ? `${formatSeconds(elapsed)}…`
              : ''
        }
      >
        {phase >= 0 && (
          <div className="text-meta text-ink-muted flex flex-col gap-1">
            <span>{t('classifyRegion', { region: run.region[lang] })}</span>
            <span>{t('classifyUrgency', { urgency: review(urgencyKey) })}</span>
            <span>{degraded ? t('classifyFallback') : t('classifyPrimary')}</span>
          </div>
        )}
      </EventRow>

      <EventRow
        title={t('tools')}
        state={stateOf(1)}
        time={
          phase > 1
            ? formatSeconds(schedule.toolsEnd - schedule.classifyEnd)
            : phase === 1
              ? `${formatSeconds(elapsed - schedule.classifyEnd)}…`
              : ''
        }
      >
        {phase >= 1 && (
          <div className="border-line bg-panel flex flex-col gap-1.5 rounded-md border p-2">
            {tools.map((tool, index) => {
              const state = toolState(index);
              return (
                <div key={tool.id} className="grid grid-cols-[12px_minmax(0,1fr)] gap-1.5">
                  <span className="mt-0.5 inline-flex">
                    {state === 'running' ? (
                      <span className="fc-spin" aria-hidden="true" />
                    ) : (
                      <AmIcon
                        icon={state === 'done' ? ICON.check : ICON.clock}
                        size="xs"
                        className={state === 'done' ? 'text-ok' : 'text-ink-subtle'}
                      />
                    )}
                  </span>
                  <div className="flex min-w-0 flex-col">
                    <code className="text-micro text-ink font-mono break-words">
                      {tool.name}({tool.fields})
                    </code>
                    <span className="text-micro text-ink-subtle font-mono">
                      {state === 'done'
                        ? `→ ${resultFor(tool.name)}`
                        : state === 'running'
                          ? t('calling')
                          : t('queued')}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </EventRow>

      <EventRow
        title={t('reasoning')}
        state={stateOf(2)}
        time={
          phase > 2
            ? formatSeconds(schedule.reasonEnd - schedule.toolsEnd)
            : phase === 2
              ? `${formatSeconds(elapsed - schedule.toolsEnd)}…`
              : ''
        }
      >
        {phase >= 2 && (
          <p className="border-line text-meta text-ink-muted border-l-2 py-1 pl-2.5 leading-relaxed">
            {reasoning.slice(0, reasonProgress)}
            {phase === 2 && <span className="fc-caret" aria-hidden="true" />}
          </p>
        )}
      </EventRow>

      <EventRow
        title={t('verification')}
        state={stateOf(3)}
        time={
          phase > 3
            ? formatSeconds(schedule.approvalAt - schedule.verifyStart)
            : phase === 3
              ? `${formatSeconds(elapsed - schedule.verifyStart)}…`
              : ''
        }
      >
        {phase >= 3 && (
          <div className="text-meta text-ink-muted flex flex-col gap-1">
            <span>{t('verifyLine', { verified, total: facts.length })}</span>
            {rewriting > 0 && <span className="text-warn">{t('rewritingLine')}</span>}
            {phase > 3 && rewriteIndex >= 0 && (
              <span className="text-ink-subtle">{t('rewrittenLine')}</span>
            )}
            <span className="text-micro text-ink-subtle font-mono">
              {facts.map((fact, index) => (
                <span key={fact.key} className={factStates[index] === 'verified' ? 'text-ok' : ''}>
                  {index > 0 ? ' · ' : ''}
                  {fact.call}
                </span>
              ))}
            </span>
          </div>
        )}
      </EventRow>

      <EventRow
        title={t('approval')}
        state={decision ? 'done' : stateOf(4) === 'paused' ? 'paused' : stateOf(4)}
        time={decisionAt}
      >
        {status === 'paused' && !decision && (
          <div className="border-warn bg-panel flex flex-col gap-2 rounded-md border-[1.5px] p-2.5">
            <span className="text-meta flex items-center gap-1.5 font-semibold">
              <AmIcon icon={ICON.pause} size="sm" className="text-warn" />
              {t('pausedTitle')}
            </span>
            <span className="text-micro text-ink-muted">
              {allVerified ? t('awaiting') : t('blocked', { count: facts.length - verified })}
            </span>
            <span className="text-micro text-ink-muted">
              {t('signingAs', { name: run.assignee, role: PRINCIPAL.role })}
            </span>
            <Link
              href={`/review/runs/${run.id}`}
              className="bg-ink text-canvas text-meta inline-flex h-7 items-center justify-center rounded-md px-2.5 font-semibold"
            >
              {t('openReview')}
            </Link>
            <span className="text-micro text-ink-subtle">{t('reviewOwns')}</span>
          </div>
        )}
        {decision && (
          <div className="border-line flex flex-col gap-1 rounded-md border p-2.5">
            <DecisionChip kind={decision.kind} />
            <span className="text-micro text-ink-subtle font-mono">
              {decision.reviewer} · {decisionAt} · {decision.audit}
            </span>
            <span className="text-micro text-ink-muted">
              {reasonLabel(decision.reason, locale)}
            </span>
          </div>
        )}
      </EventRow>

      <EventRow
        title={t('publish')}
        state={decision ? (published ? 'done' : 'rejected') : 'pending'}
        time={decisionAt}
      >
        {decision && (
          <p className="text-meta text-ink-muted">
            {published
              ? t('publishedLine', { name: decision.reviewer })
              : t('rejectedLine', { id: decision.audit })}
          </p>
        )}
      </EventRow>
    </ol>
  );
}
