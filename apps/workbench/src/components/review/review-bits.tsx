'use client';

import { useTranslations } from 'next-intl';
import { Chip } from '@/components/ui/chip';
import { AmIcon, ICON } from '@/components/ui/icon';
import type { ReviewStatus } from '@/lib/review/api';

const UTC_CLOCK = new Intl.DateTimeFormat('en-GB', {
  hour: '2-digit',
  minute: '2-digit',
  second: '2-digit',
  hour12: false,
  timeZone: 'UTC',
});

export function utcTime(value: string): string {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : `${UTC_CLOCK.format(date)} UTC`;
}

export function StatusChip({ status }: { status: ReviewStatus }) {
  const t = useTranslations('Review');
  const labels: Record<ReviewStatus, string> = {
    needs: t('needs'),
    published: t('published'),
    withheld: t('withheld'),
    failed: t('failed'),
  };
  const icons = {
    needs: ICON.dot,
    published: ICON.check,
    withheld: ICON.close,
    failed: ICON.alert,
  } as const;
  const tones = { needs: 'cyan', published: 'ok', withheld: 'purple', failed: 'bad' } as const;

  return (
    <Chip tone={tones[status]} icon={icons[status]}>
      {labels[status]}
    </Chip>
  );
}

export function DecisionChip({ approved }: { approved: boolean }) {
  const t = useTranslations('Review');
  return (
    <Chip tone={approved ? 'ok' : 'bad'} icon={approved ? ICON.check : ICON.close}>
      {approved ? t('approved') : t('rejected')}
    </Chip>
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
