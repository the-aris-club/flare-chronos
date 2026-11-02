'use client';

import { useTranslations } from 'next-intl';
import { useService } from '@/components/service/service-provider';
import type { ReviewRun } from '@/lib/review/api';
import { ReviewDialog } from './review-dialog';
import { useLabels } from './use-labels';

type ConfirmDialogProps = {
  run: ReviewRun;
  approved: boolean;
  reason: string;
  note: string;
  onConfirm: () => void;
  onClose: () => void;
};

export function ConfirmDialog({
  run,
  approved,
  reason,
  note,
  onConfirm,
  onClose,
}: ConfirmDialogProps) {
  const t = useTranslations('Review');
  const labels = useLabels();
  const approve = approved;
  const service = useService();

  return (
    <ReviewDialog
      title={approve ? t('confirmApprove') : t('confirmReject')}
      subtitle={t('lastCheck')}
      onClose={onClose}
      footer={
        <>
          <button
            type="button"
            onClick={onClose}
            className="border-line-strong text-meta inline-flex h-8 items-center rounded-md border px-3 font-medium"
          >
            {t('cancel')}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className={`text-meta ml-auto inline-flex h-8 items-center rounded-md px-3 font-semibold ${
              approve ? 'bg-ok text-canvas' : 'bg-bad text-canvas'
            }`}
          >
            {approve ? t('confirmApprove') : t('confirmReject')}
          </button>
        </>
      }
    >
      <div className="flex flex-col gap-3">
        <dl className="grid grid-cols-[auto_minmax(0,1fr)] gap-x-4 gap-y-2">
          {[
            [t('run'), `${run.id} · ${run.useCase}`],
            [t('proposed'), run.question],
            [t('decision'), approve ? t('approve') : t('reject')],
            [t('reason'), labels.reason(reason)],
            [t('note'), note || '—'],
            [t('reviewer'), service.claims?.name ?? service.claims?.sub ?? '—'],
          ].map(([label, value]) => (
            <div key={label} className="contents">
              <dt className="text-meta text-ink-subtle">{label}</dt>
              <dd className="text-meta">{value}</dd>
            </div>
          ))}
        </dl>
        <p
          className={`text-body rounded-md border px-3 py-2 ${
            approve ? 'border-ok/50 text-ink' : 'border-bad/50 text-ink'
          }`}
        >
          {approve ? t('msgApprove') : t('msgReject')}
        </p>
        <p className="text-meta text-ink-subtle">{t('finalNote')}</p>
      </div>
    </ReviewDialog>
  );
}
