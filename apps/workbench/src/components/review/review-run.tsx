'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { useLocale, useTranslations } from 'next-intl';
import { useService } from '@/components/service/service-provider';
import { Icon, ICON } from '@/components/ui/icon';
import { Markdown } from '@/components/ui/markdown';
import type { FailureReason } from '@/lib/service/client';
import { parseAudit, parseRun, type AuditRow, type ReviewRun } from '@/lib/review/api';
import { DecisionChip, StatusChip, utcTime } from './review-bits';
import { ConfirmDialog } from './confirm-dialog';
import { ReviewDecision } from './review-decision';
import { useLabels } from './use-labels';
import { EvidenceSummary, RunSummary } from './run-summary';
import { VerificationTable } from './verification-table';

type Pending = { approved: boolean; reason: string; note: string } | null;
type Load = 'loading' | 'ready' | 'not_found' | 'forbidden' | 'failed';

const FAILURE_LOAD: Record<FailureReason, Load> = {
  not_found: 'not_found',
  forbidden: 'forbidden',
  unauthorized: 'failed',
  unavailable: 'failed',
};

const LOAD_MESSAGE: Record<Exclude<Load, 'ready'>, string> = {
  loading: 'loadingQ',
  not_found: 'runNotFound',
  forbidden: 'runForbidden',
  failed: 'queueFailed',
};

export function ReviewRunView({ runId }: { runId: string }) {
  const t = useTranslations('Review');
  const locale = useLocale();
  const labels = useLabels();
  const service = useService();
  const [run, setRun] = useState<ReviewRun | null>(null);
  const [audit, setAudit] = useState<AuditRow[]>([]);
  const [load, setLoad] = useState<Load>('loading');
  const [pending, setPending] = useState<Pending>(null);
  const [saveFailed, setSaveFailed] = useState(false);
  const { get } = service;

  const refetch = useCallback(async () => {
    const [detail, trail] = await Promise.all([
      get(`/api/v1/review/runs/${runId}`),
      get(`/api/v1/review/runs/${runId}/audit`),
    ]);
    if (!detail.ok) {
      setLoad(FAILURE_LOAD[detail.reason]);
      return;
    }
    try {
      setRun(parseRun(detail.data));
      setAudit(trail.ok ? parseAudit(trail.data) : []);
      setLoad('ready');
    } catch {
      setLoad('failed');
    }
  }, [get, runId]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void refetch();
  }, [refetch]);

  if (load !== 'ready' || !run) {
    return (
      <p
        role={load === 'loading' ? 'status' : 'alert'}
        className="text-meta text-ink-muted px-4 py-10 text-center"
      >
        {t(LOAD_MESSAGE[load === 'ready' ? 'failed' : load])}
      </p>
    );
  }

  const decided = audit.at(-1);
  const approveAvailable = run.verification.passed && run.verification.unverified.length === 0;

  const confirm = useCallback(async () => {
    if (!pending || !run) return;
    const failure = await service.decide(run.id, {
      approved: pending.approved,
      reasonCode: pending.reason,
      reason: pending.note,
    });
    setPending(null);
    setSaveFailed(failure !== null);
    await refetch();
  }, [pending, run, service, refetch]);

  const handleRequest = useCallback(
    (approved: boolean, reason: string, note: string) => setPending({ approved, reason, note }),
    [],
  );

  const handlePendingClose = useCallback(() => setPending(null), []);

  const handleConfirm = useCallback(() => {
    void confirm();
  }, [confirm]);

  return (
    <div className="tablet:px-5 tablet:py-6 mx-auto flex w-full max-w-400 flex-col gap-3 px-3 py-4 xl:h-[calc(100dvh-3.25rem)] xl:py-4">
      <div className="flex shrink-0 flex-wrap items-center gap-2">
        <Link
          href="/review"
          className="text-meta text-ink-muted hover:text-ink border-line-strong inline-flex h-8 items-center gap-1 rounded-md border px-2"
        >
          <Icon icon={ICON.back} size="sm" />
          {t('back')}
        </Link>
        <h1 className="text-title min-w-0 font-mono font-semibold break-all">{run.id}</h1>
        <span className="text-meta text-ink-muted">
          {run.useCase} · {labels.caseLabel(run.useCase)}
        </span>
        <StatusChip status={run.status} />
        {decided && <DecisionChip approved={decided.approved} />}
      </div>

      {saveFailed && (
        <p role="alert" className="text-meta text-bad">
          {t('saveFailed')}
        </p>
      )}

      <div className="grid grid-cols-1 gap-3 xl:min-h-0 xl:flex-1 xl:grid-cols-[18rem_minmax(0,1fr)_20rem] xl:grid-rows-[minmax(0,1fr)]">
        <div className="xl:min-h-0 xl:overflow-y-auto">
          <RunSummary run={run} />
        </div>

        <section className="border-line bg-panel flex max-h-[70dvh] min-w-0 flex-col gap-3 overflow-y-auto rounded-lg border p-3 *:shrink-0 xl:max-h-none xl:min-h-0">
          <h2 className="text-subhead font-semibold">{t('fullBrief')}</h2>
          {run.status === 'withheld' ? (
            <div className="border-purple/50 rounded-md border p-4">
              <h3 className="text-body font-semibold">{t('withheldTitle')}</h3>
              <p className="text-meta text-ink-muted mt-1">{t('withheldBody')}</p>
              {decided && (
                <p className="text-meta text-ink-subtle mt-2 font-mono">
                  {decided.id} · {utcTime(decided.decidedAt)}
                </p>
              )}
            </div>
          ) : (
            <>
              <Markdown>{run.briefing}</Markdown>
              {locale === 'vi' && (
                <p className="text-meta text-ink-subtle border-line border-l-2 px-2 py-1">
                  {t('viBriefNote')}
                </p>
              )}
            </>
          )}
          <h3 className="text-body font-semibold">{t('verTable')}</h3>
          <VerificationTable facts={run.facts} />
          <h3 className="text-body font-semibold">{t('timeline')}</h3>
          <p className="text-meta text-ink-muted font-mono break-words">
            {run.tools.join(' · ') || '—'}
          </p>
        </section>

        <div className="flex flex-col gap-3 xl:min-h-0 xl:overflow-y-auto">
          <EvidenceSummary run={run} />
          <ReviewDecision
            decided={decided}
            approveAvailable={approveAvailable}
            onRequest={handleRequest}
          />
        </div>
      </div>

      {pending && (
        <ConfirmDialog
          run={run}
          approved={pending.approved}
          reason={pending.reason}
          note={pending.note}
          onClose={handlePendingClose}
          onConfirm={handleConfirm}
        />
      )}
    </div>
  );
}
