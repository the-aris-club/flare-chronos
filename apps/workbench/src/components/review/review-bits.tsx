'use client';

import { useLocale, useTranslations } from 'next-intl';
import { localized } from '@/lib/workbench/format';
import { Chip } from '@/components/ui/chip';
import { AmIcon, ICON } from '@/components/ui/icon';
import {
  REASONS,
  type DecisionKind,
  type FactVerdict,
  type RunStatus,
} from '@/data/fixtures/review';

export function initials(name: string): string {
  const parts = name.split(/\s+/).filter(Boolean);
  if (parts.length === 0) return '';
  return `${parts[0][0]}${parts.at(-1)?.[0] ?? ''}`.toUpperCase();
}

const UTC_CLOCK = new Intl.DateTimeFormat('en-GB', {
  hour: '2-digit',
  minute: '2-digit',
  second: '2-digit',
  hour12: false,
  timeZone: 'UTC',
});

export function utcNow(): string {
  return `${UTC_CLOCK.format(new Date())} UTC`;
}

export function utcTime(value: string): string {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : `${UTC_CLOCK.format(date)} UTC`;
}

export function RoleText({ role }: { role: string }) {
  const t = useTranslations('Review');
  if (role === 'Approver') return <>{t('approver')}</>;
  if (role === 'Reviewer') return <>{t('reviewer')}</>;
  return <>{role}</>;
}

export function StatusChip({ status }: { status: RunStatus }) {
  const t = useTranslations('Review');
  const labels: Record<RunStatus, string> = {
    needs: t('needs'),
    published: t('published'),
    withheld: t('withheld'),
  };
  const icons = { needs: ICON.dot, published: ICON.check, withheld: ICON.close };
  const tones = { needs: 'cyan', published: 'ok', withheld: 'purple' } as const;
  return (
    <Chip tone={tones[status]} icon={icons[status]}>
      {labels[status]}
    </Chip>
  );
}

export function UrgencyChip({ urgency }: { urgency: 'crisis' | 'elevated' }) {
  const t = useTranslations('Review');
  const crisis = urgency === 'crisis';
  return (
    <Chip tone={crisis ? 'raw' : 'warn'} icon={crisis ? ICON.alert : ICON.dot}>
      {crisis ? t('crisisUrgency') : t('elevatedUrgency')}
    </Chip>
  );
}

export function DecisionChip({ kind }: { kind: DecisionKind }) {
  const t = useTranslations('Review');
  const approve = kind === 'approve';
  return (
    <Chip tone={approve ? 'ok' : 'bad'} icon={approve ? ICON.check : ICON.close}>
      {approve ? t('approved') : t('rejected')}
    </Chip>
  );
}

export function FactChip({ verdict }: { verdict: FactVerdict }) {
  const t = useTranslations('Review');
  const label =
    verdict === 'verified'
      ? t('verified')
      : verdict === 'rewritten'
        ? t('rewritten')
        : t('nosource');
  const tone =
    verdict === 'verified' ? 'text-teal' : verdict === 'rewritten' ? 'text-amber' : 'text-bad';
  const glyph =
    verdict === 'verified' ? ICON.check : verdict === 'rewritten' ? ICON.rewrite : ICON.alert;

  return (
    <span
      className={`text-label inline-flex items-center gap-1 font-mono whitespace-nowrap ${tone}`}
    >
      <AmIcon icon={glyph} size="xs" />
      {label}
    </span>
  );
}

export function CheckRow({ ok, label, detail }: { ok: boolean; label: string; detail: string }) {
  const t = useTranslations('Review');

  return (
    <div className="border-line flex items-start gap-2 border-b py-2 last:border-0">
      <AmIcon
        icon={ok ? ICON.check : ICON.alert}
        size="sm"
        className={`mt-0.5 shrink-0 ${ok ? 'text-ok' : 'text-warn'}`}
      />
      <span className="min-w-0 flex-1">
        <span className="text-body block font-medium">{label}</span>
        <span className="text-meta text-ink-subtle block">{detail}</span>
      </span>
      <span className={`text-label font-mono ${ok ? 'text-ok' : 'text-warn'}`}>
        {ok ? t('pass') : t('fail')}
      </span>
    </div>
  );
}

export function reasonLabel(value: string, locale: string): string {
  const reason = REASONS.find((item) => item.value === value);
  if (!reason) return value;
  return localized(locale, reason.en, reason.vi);
}

export function ReasonText({ value }: { value: string }) {
  const locale = useLocale();
  return <>{reasonLabel(value, locale)}</>;
}
