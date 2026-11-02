'use client';

import { useTranslations } from 'next-intl';
import type { ReviewRun } from '@/lib/review/api';
import { CheckRow } from './review-bits';
import { useLabels } from './use-labels';

function Section({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <section className="flex flex-col gap-2">
      <span className="text-label text-ink-subtle font-mono tracking-widest uppercase">
        {label}
      </span>
      {children}
    </section>
  );
}

export function RunSummary({ run }: { run: ReviewRun }) {
  const t = useTranslations('Review');
  const labels = useLabels();

  return (
    <div className="flex flex-col gap-4">
      <Section label={t('authorizing')}>
        <div className="border-line bg-panel rounded-lg border p-3">
          <span className="text-label text-ink-subtle font-mono uppercase">{t('proposed')}</span>
          <p className="text-body-lg mt-1.5 font-semibold">
            {labels.useCase(run.useCase) || run.useCase}
          </p>
          <p className="text-meta text-ink-subtle mt-1">{run.question}</p>
        </div>
      </Section>

      <Section label={t('regionPeriod')}>
        <dl className="border-line bg-panel grid grid-cols-[auto_minmax(0,1fr)] gap-x-3 gap-y-1 rounded-lg border p-3">
          <dt className="text-meta text-ink-subtle">{t('region')}</dt>
          <dd className="text-meta text-right">{labels.region(run.entity.region)}</dd>
          <dt className="text-meta text-ink-subtle">{t('period')}</dt>
          <dd className="text-meta text-right">{run.entity.epochYears.join(', ') || '—'}</dd>
          <dt className="text-meta text-ink-subtle">{t('owner')}</dt>
          <dd className="text-meta text-right">{run.owner}</dd>
          <dt className="text-meta text-ink-subtle">{t('mode')}</dt>
          <dd className="text-meta text-right font-mono">{run.mode || '—'}</dd>
        </dl>
      </Section>
    </div>
  );
}

export function EvidenceSummary({ run }: { run: ReviewRun }) {
  const t = useTranslations('Review');
  const unverified = run.verification.unverified.length;
  const unresolved = run.verification.unresolved.length;

  return (
    <div className="flex flex-col gap-3">
      <Section label={t('evidence')}>
        <div className="border-line bg-panel flex flex-col gap-1.5 rounded-lg border p-3">
          {[
            [
              t('verified'),
              `${run.verification.checked - unverified}/${run.verification.checked}`,
              unverified === 0,
            ],
            [t('nosource'), String(unverified), unverified === 0],
            [t('citationIssues'), String(unresolved), unresolved === 0],
            [t('selfCorrections'), String(run.selfCorrections), true],
          ].map(([label, value, ok]) => (
            <div key={String(label)} className="text-meta flex items-center justify-between gap-2">
              <span className="text-ink-muted">{label}</span>
              <span className={`font-mono ${ok ? 'text-ok' : 'text-bad'}`}>{value}</span>
            </div>
          ))}
        </div>
      </Section>

      <Section label={t('basis')}>
        <div className="border-line bg-panel rounded-lg border px-3 py-1">
          <CheckRow
            ok={run.verification.passed && unverified === 0}
            label={t('everyNumber')}
            detail={`${run.facts.length} ${t('factsInLedger')}`}
          />
          <CheckRow
            ok={unresolved === 0}
            label={t('noCitationIssues')}
            detail={t('noMissingSources')}
          />
        </div>
      </Section>
    </div>
  );
}
