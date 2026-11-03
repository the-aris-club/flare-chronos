'use client';

import { useLocale, useTranslations } from 'next-intl';
import { isVi, localized } from '@/lib/workbench/format';
import { AUDIENCES, type Audience, type Decision, type ReviewRun } from '@/data/fixtures/review';
import { SegmentedControl } from '@/components/ui/segmented-control';
import { BriefText } from './brief-text';
import { DecisionChip, StatusChip, utcTime } from './review-bits';
import { ReviewDialog } from './review-dialog';
import { VerificationTable } from './verification-table';

type BriefingDialogProps = {
  run: ReviewRun;
  decision: Decision | undefined;
  audience: Audience;
  showKeys: boolean;
  onAudience: (audience: Audience) => void;
  onShowKeys: () => void;
  onFact: (key: string) => void;
  onClose: () => void;
  onDecision: () => void;
};

export function BriefingDialog({
  run,
  decision,
  audience,
  showKeys,
  onAudience,
  onShowKeys,
  onFact,
  onClose,
  onDecision,
}: BriefingDialogProps) {
  const t = useTranslations('Review');
  const locale = useLocale();
  const status = decision ? (decision.kind === 'approve' ? 'published' : 'withheld') : 'needs';
  const audienceMeta = AUDIENCES.find((item) => item.value === audience) ?? AUDIENCES[0];
  const audienceLabel = localized(locale, audienceMeta.en, audienceMeta.vi);
  const audienceRole = localized(locale, audienceMeta.roleEn, audienceMeta.roleVi);

  return (
    <ReviewDialog
      title={`${run.id} · ${run.useCaseName[locale as 'en' | 'vi']}`}
      subtitle={`${run.useCase} · ${run.region[locale as 'en' | 'vi']}`}
      onClose={onClose}
      wide
      footer={
        <>
          <StatusChip status={status} />
          {decision && <DecisionChip kind={decision.kind} />}
          <span className="text-meta text-ink-subtle">
            {decision ? `${utcTime(decision.at)} · ${decision.audit}` : t('notReleased')}
          </span>
          <button
            type="button"
            onClick={onDecision}
            className="bg-ink text-canvas text-meta ml-auto inline-flex h-8 items-center rounded-md px-3 font-semibold"
          >
            {t('goDecision')}
          </button>
        </>
      }
    >
      <div className="flex flex-col gap-4">
        <div className="flex flex-wrap items-center gap-2">
          <SegmentedControl
            label={t('audience')}
            value={audience}
            options={AUDIENCES.map((item) => ({
              value: item.value,
              label: localized(locale, item.en, item.vi),
            }))}
            onChange={onAudience}
          />
          <button
            type="button"
            onClick={onShowKeys}
            aria-pressed={showKeys}
            className={`text-meta h-7 rounded-md border px-2 font-medium ${
              showKeys ? 'border-line-strong bg-seg text-ink' : 'border-line-strong text-ink-muted'
            }`}
          >
            {t('showKeys')}
          </button>
        </div>

        <div className="grid grid-cols-2 gap-2 lg:grid-cols-5">
          {[
            [t('audience'), `${audienceLabel} · ${audienceRole}`],
            [t('cognitivePath'), t('cognitivePathValue')],
            [t('system1'), t('system1Value')],
            [t('system2'), t('system2Value')],
            [t('synthesis'), t('synthesisValue')],
          ].map(([label, value]) => (
            <div key={label} className="border-line bg-raised rounded-md border px-2.5 py-2">
              <span className="text-micro text-ink-subtle block font-mono uppercase">{label}</span>
              <span className="text-meta mt-1 block">{value}</span>
            </div>
          ))}
        </div>

        {decision?.kind === 'reject' ? (
          <div className="border-purple/50 rounded-md border p-3">
            <h3 className="text-body font-semibold">{t('withheldTitle')}</h3>
            <p className="text-meta text-ink-muted mt-1">{t('withheldBody')}</p>
          </div>
        ) : (
          <>
            {isVi(locale) && (
              <p className="text-meta text-ink-subtle border-line rounded-sm border-l-2 px-2 py-1">
                {t('viBriefNote')}
              </p>
            )}
            <BriefText
              lines={run.brief[audience]}
              facts={run.facts}
              showKeys={showKeys}
              onFact={onFact}
            />
            <section className="flex flex-col gap-2">
              <h3 className="text-body font-semibold">{t('verTable')}</h3>
              <VerificationTable facts={run.facts} onFact={onFact} />
            </section>
          </>
        )}
      </div>
    </ReviewDialog>
  );
}
