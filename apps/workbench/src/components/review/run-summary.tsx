'use client';

import { useLocale, useTranslations } from 'next-intl';
import { localized } from '@/lib/workbench/format';
import { CheckRow } from '@/components/review/review-bits';
import { MiniMap } from '@/components/review/mini-map';
import { PRINCIPAL, type ReviewRun } from '@/data/fixtures/review';

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
  const locale = useLocale();
  const lang: 'en' | 'vi' = localized(locale, 'en', 'vi');
  const regionKey = run.region.en === 'Amazon' ? 'amazon' : 'mekong';

  return (
    <div className="flex flex-col gap-4">
      <Section label={t('authorizing')}>
        <div className="border-line bg-panel rounded-lg border p-3">
          <span className="text-label text-ink-subtle font-mono uppercase">{t('proposed')}</span>
          <p className="text-body-lg mt-1.5 font-semibold">{run.action[lang]}</p>
          <p className="text-meta text-ink-subtle mt-1">{run.scope[lang]}</p>
        </div>
      </Section>

      <Section label={t('regionPeriod')}>
        <div className="border-line bg-panel flex flex-col gap-2 rounded-lg border p-3">
          <dl className="grid grid-cols-[auto_minmax(0,1fr)] gap-x-3 gap-y-1">
            <dt className="text-meta text-ink-subtle">{t('region')}</dt>
            <dd className="text-meta text-right">{run.region[lang]}</dd>
            <dt className="text-meta text-ink-subtle">{t('period')}</dt>
            <dd className="text-meta text-right">{run.period[lang]}</dd>
          </dl>
          <MiniMap region={regionKey} caption={`${run.region[lang]} · ${run.period[lang]}`} />
        </div>
      </Section>

      <Section label={t('thresholds')}>
        <div className="border-line bg-panel flex flex-col gap-2 rounded-lg border p-3">
          <div className="flex items-baseline justify-between gap-2">
            <span className="text-meta text-ink-subtle">{t('sfaiVal')}</span>
            <span className="text-metric font-mono font-semibold">
              {run.sfai === 'Not evaluated' ? t('notEvaluated') : run.sfai}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div className="border-cyan/60 rounded-md border border-dashed p-2">
              <span className="text-micro text-ink-subtle block font-mono uppercase">
                {t('display')}
              </span>
              <span className="text-title font-mono">+2.2σ</span>
            </div>
            <div className="border-raw/60 rounded-md border p-2">
              <span className="text-micro text-ink-subtle block font-mono uppercase">
                {t('crisis')}
              </span>
              <span className="text-title font-mono">+2.5σ</span>
            </div>
          </div>
          <p className="text-meta text-ink-subtle">{run.thresholdNote[lang]}</p>
        </div>
      </Section>

      <Section label={t('evStatus')}>
        <div className="border-line bg-panel flex flex-col gap-1 rounded-lg border p-3">
          <span className="text-meta flex items-center gap-1.5">
            <span className="bg-teal inline-block size-2 rounded-xs" />
            {run.epoch[lang]}
          </span>
          <span className="text-meta text-ink-muted flex items-center gap-1.5">
            <span className="border-line-strong inline-block size-2 rounded-xs border" />
            {run.cellLabel[lang]}
          </span>
        </div>
      </Section>
    </div>
  );
}

export function EvidenceSummary({ run }: { run: ReviewRun }) {
  const t = useTranslations('Review');
  const locale = useLocale();
  const lang: 'en' | 'vi' = localized(locale, 'en', 'vi');
  const facts = Object.values(run.facts);
  const noSource = facts.filter((fact) => fact.verdict === 'nosource').length;
  const verified = facts.length - noSource;
  const rewrites = facts.filter((fact) => fact.rejected).length;
  const approveAvailable = noSource === 0;

  return (
    <div className="flex flex-col gap-3">
      <Section label={t('evidence')}>
        <div className="border-line bg-panel flex flex-col gap-1.5 rounded-lg border p-3">
          {[
            [t('verified'), `${verified}/${facts.length}`, verified === facts.length],
            [t('nosource'), String(noSource), noSource === 0],
            [t('citationIssues'), '0', true],
            [t('selfCorrections'), String(rewrites), true],
            [t('synthesisSource'), 'LLM synthesis', true],
          ].map(([label, value, ok]) => (
            <div key={String(label)} className="text-meta flex items-center justify-between gap-2">
              <span className="text-ink-muted">{label}</span>
              <span className={`font-mono ${ok ? 'text-ok' : 'text-bad'}`}>{value}</span>
            </div>
          ))}
          <span className="text-micro text-ink-subtle border-line mt-1 border-t pt-1">
            {run.verification}
          </span>
        </div>
      </Section>

      <Section label={t('basis')}>
        <div className="border-line bg-panel rounded-lg border px-3 py-1">
          <CheckRow ok label={t('actionStated')} detail={run.action[lang]} />
          <CheckRow
            ok={approveAvailable}
            label={t('everyNumber')}
            detail={`${verified}/${facts.length} · ${rewrites} ${t('selfCorrections').toLowerCase()}`}
          />
          <CheckRow ok label={t('noCitationIssues')} detail={t('noMissingSources')} />
          <CheckRow ok label={t('thresholdEpoch')} detail={run.epoch[lang]} />
          <CheckRow ok label={t('serviceHealthy')} detail={t('fullService')} />
          <CheckRow ok label={t('reviewerCheck')} detail={`${PRINCIPAL.name} · ${t('approver')}`} />
        </div>
      </Section>

      <Section label={t('approver')}>
        <div className="border-line bg-panel flex items-center gap-2 rounded-lg border p-3">
          <span className="bg-seg text-ink text-meta inline-flex size-8 items-center justify-center rounded-full font-mono font-semibold">
            {PRINCIPAL.initials}
          </span>
          <span className="flex min-w-0 flex-col leading-tight">
            <span className="text-body font-semibold">{PRINCIPAL.name}</span>
            <span className="text-meta text-ink-subtle">
              {t('approver')} · {t('owner')}
            </span>
          </span>
        </div>
      </Section>
    </div>
  );
}
