'use client';

import { useTranslations } from 'next-intl';
import type { Fact, ReviewRun } from '@/data/fixtures/review';
import { FactChip } from './review-bits';
import { ReviewDialog } from './review-dialog';

type CitationDialogProps = {
  run: ReviewRun;
  fact: Fact;
  onClose: () => void;
};

export function CitationDialog({ run, fact, onClose }: CitationDialogProps) {
  const t = useTranslations('Review');

  return (
    <ReviewDialog
      title={t('citation')}
      subtitle={`${run.id} · ${fact.key}`}
      onClose={onClose}
      footer={
        <>
          <span className="text-meta text-ink-subtle font-mono">
            {fact.call} · {fact.tool}
          </span>
          <button
            type="button"
            onClick={onClose}
            className="border-line-strong text-meta ml-auto inline-flex h-8 items-center rounded-md border px-3 font-medium"
          >
            {t('close')}
          </button>
        </>
      }
    >
      <div className="flex flex-col gap-3">
        <div className="border-line bg-raised rounded-md border p-3">
          <p className="text-body-lg leading-relaxed">
            {fact.text} <span className="text-ink-subtle">· {fact.tool}</span>
          </p>
        </div>

        <dl className="grid grid-cols-[auto_minmax(0,1fr)] gap-x-4 gap-y-2">
          {[
            [t('rendered'), fact.text],
            [t('factKey'), `${fact.key} · ${fact.field}`],
            [t('srcTool'), fact.tool],
            [t('rawVal'), fact.raw],
            [t('provTag'), fact.provenance],
            [t('lastCheck'), fact.call],
          ].map(([label, value]) => (
            <div key={label} className="contents">
              <dt className="text-meta text-ink-subtle">{label}</dt>
              <dd className="text-meta font-mono">{value}</dd>
            </div>
          ))}
          <dt className="text-meta text-ink-subtle">{t('verdict')}</dt>
          <dd>
            <FactChip verdict={fact.verdict} />
          </dd>
        </dl>

        {fact.verdict === 'rewritten' && fact.rejected && (
          <div className="border-amber/50 rounded-md border p-3">
            <p className="text-meta">
              <span className="text-ink-subtle">{t('rejectedV')} </span>
              <span className="font-mono line-through">{fact.rejected}</span>
              <span className="text-ink-subtle"> → {t('acceptedV')} </span>
              <span className="font-mono">{fact.value}</span>
            </p>
            <p className="text-meta text-ink-muted mt-1">
              <span className="text-ink-subtle">{t('verNote')}: </span>
              {fact.note}
            </p>
          </div>
        )}
      </div>
    </ReviewDialog>
  );
}
