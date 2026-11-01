'use client';

import { useLocale, useTranslations } from 'next-intl';
import { localized } from '@/lib/workbench/format';
import { PRINCIPAL, type DecisionKind, type ReviewRun } from '@/data/fixtures/review';
import { reasonLabel } from './review-bits';
import { ReviewDialog } from './review-dialog';

type ConfirmDialogProps = {
  run: ReviewRun;
  kind: DecisionKind;
  reason: string;
  note: string;
  onConfirm: () => void;
  onClose: () => void;
};

export function ConfirmDialog({ run, kind, reason, note, onConfirm, onClose }: ConfirmDialogProps) {
  const t = useTranslations('Review');
  const locale = useLocale();
  const approve = kind === 'approve';

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
            [t('proposed'), run.action[localized<'en' | 'vi'>(locale, 'en', 'vi')]],
            [t('decision'), approve ? t('approve') : t('reject')],
            [t('reason'), reasonLabel(reason, locale)],
            [t('note'), note || '—'],
            [t('reviewer'), `${PRINCIPAL.name} · ${PRINCIPAL.role}`],
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
