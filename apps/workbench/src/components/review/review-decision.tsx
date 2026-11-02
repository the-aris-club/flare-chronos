'use client';

import { useState } from 'react';
import { useLocale, useTranslations } from 'next-intl';
import { useService } from '@/components/service/service-provider';
import { REASONS, reasonLabel } from '@/lib/review/reasons';
import type { AuditRow } from '@/lib/review/api';
import { DecisionChip, utcTime } from './review-bits';

type ReviewDecisionProps = {
  decided: AuditRow | undefined;
  approveAvailable: boolean;
  onRequest: (approved: boolean, reasonCode: string, note: string) => void;
};

export function ReviewDecision({ decided, approveAvailable, onRequest }: ReviewDecisionProps) {
  const t = useTranslations('Review');
  const locale = useLocale();
  const service = useService();
  const [reason, setReason] = useState('');
  const [note, setNote] = useState('');
  const [error, setError] = useState<string | null>(null);

  function request(approved: boolean) {
    if (!reason) {
      setError(t('errReason'));
      return;
    }
    if (reason === 'other' && !note.trim()) {
      setError(t('errNote'));
      return;
    }
    setError(null);
    onRequest(approved, reason, note.trim());
  }

  if (decided) {
    return (
      <section className="border-line bg-panel flex flex-col gap-2 rounded-lg border p-3">
        <span className="text-label text-ink-subtle font-mono tracking-widest uppercase">
          {t('decisionRec')}
        </span>
        <DecisionChip approved={decided.approved} />
        <p className="text-meta text-ink-muted">
          {decided.principal}
          <br />
          <span className="text-ink-subtle font-mono">
            {utcTime(decided.decidedAt)} · {decided.id}
          </span>
        </p>
        <p className="text-body">
          <span className="text-ink-subtle">{t('reason')}: </span>
          {reasonLabel(decided.reasonCode, locale)}
        </p>
        {decided.reason && (
          <p className="text-meta text-ink-muted">
            <span className="text-ink-subtle">{t('note')}: </span>
            {decided.reason}
          </p>
        )}
        <p className="text-meta text-ink-subtle border-line border-t pt-2">
          {decided.approved ? t('msgApprove') : t('withheldBody')}
        </p>
      </section>
    );
  }

  if (!service.isApprover) {
    return (
      <section className="border-line bg-panel flex flex-col gap-2 rounded-lg border p-3">
        <span className="text-label text-ink-subtle font-mono tracking-widest uppercase">
          {t('decision')}
        </span>
        <p className="text-meta text-ink-muted">{t('needApprover')}</p>
      </section>
    );
  }

  return (
    <section className="border-line bg-panel flex flex-col gap-2 rounded-lg border p-3">
      <span className="text-label text-ink-subtle font-mono tracking-widest uppercase">
        {t('decision')}
      </span>
      <label className="flex flex-col gap-1">
        <span className="text-meta text-ink-muted">
          {t('reason')} <span className="text-bad">*</span>
        </span>
        <select
          id="decision-reason"
          name="decision-reason"
          value={reason}
          onChange={(event) => {
            setReason(event.target.value);
            if (error) setError(null);
          }}
          className="border-line-strong bg-raised text-meta text-ink h-8 rounded-md border px-2"
        >
          <option value="">{t('chooseReason')}</option>
          {REASONS.map((item) => (
            <option key={item.value} value={item.value}>
              {locale === 'vi' ? item.vi : item.en}
            </option>
          ))}
        </select>
      </label>
      <label className="flex flex-col gap-1">
        <span className="text-meta text-ink-muted">{t('note')}</span>
        <textarea
          id="decision-note"
          name="decision-note"
          value={note}
          onChange={(event) => setNote(event.target.value)}
          rows={2}
          className="border-line-strong bg-raised text-meta text-ink resize-none rounded-md border px-2 py-1.5"
        />
      </label>
      {error && (
        <p role="alert" className="text-meta text-bad">
          {error}
        </p>
      )}
      <div className="grid grid-cols-2 gap-2">
        <button
          type="button"
          onClick={() => request(true)}
          disabled={!approveAvailable}
          className="border-ok text-ok hover:bg-chip text-meta inline-flex h-8 items-center justify-center gap-1 rounded-md border font-semibold disabled:opacity-40"
        >
          {t('approve')}
        </button>
        <button
          type="button"
          onClick={() => request(false)}
          className="border-bad text-bad hover:bg-chip text-meta inline-flex h-8 items-center justify-center gap-1 rounded-md border font-semibold"
        >
          {t('reject')}
        </button>
      </div>
      {!approveAvailable && (
        <p className="text-meta text-warn">
          {t('approveUnavail')}. {t('rejectStill')}
        </p>
      )}
      <p className="text-meta text-ink-subtle border-line border-t pt-2">{t('finalNote')}</p>
    </section>
  );
}
