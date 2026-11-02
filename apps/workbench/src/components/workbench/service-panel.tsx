'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useService } from '@/components/service/service-provider';
import { Chip, type ChipTone } from '@/components/ui/chip';
import { Icon, ICON } from '@/components/ui/icon';

export function RailStatusChip({ tone, label }: { tone: ChipTone; label: string }) {
  return <Chip tone={tone}>{label}</Chip>;
}

export function ServiceDown() {
  const t = useTranslations('Briefing.down');

  return (
    <div
      role="alert"
      className="border-bad/45 bg-panel flex flex-col gap-3 rounded-lg border p-3.5"
    >
      <div className="flex items-center gap-2.5">
        <span className="border-bad text-bad inline-flex size-7 items-center justify-center rounded-md border-[1.5px]">
          <Icon icon={ICON.xCircle} size="sm" />
        </span>
        <span className="text-subhead font-semibold">{t('title')}</span>
      </div>
      <p className="text-body text-ink-muted leading-relaxed">{t('body')}</p>
    </div>
  );
}

export function ConnectPanel() {
  const t = useTranslations('Briefing.connect');
  const service = useService();
  const [token, setToken] = useState('');
  const [empty, setEmpty] = useState(false);
  const checking = service.connection === 'checking';

  function submit() {
    if (!token.trim()) {
      setEmpty(true);
      return;
    }
    setEmpty(false);
    void service.connect(token);
  }

  return (
    <div className="border-line bg-panel flex flex-col gap-2.5 rounded-lg border p-3.5">
      <h3 className="text-subhead font-semibold">{t('title')}</h3>
      <p className="text-body text-ink-muted leading-relaxed">{t('body')}</p>

      <label htmlFor="briefing-token" className="text-meta text-ink-muted flex flex-col gap-1">
        {t('token')}
        <textarea
          id="briefing-token"
          name="token"
          autoComplete="off"
          value={token}
          onChange={(event) => {
            setToken(event.target.value);
            if (empty) setEmpty(false);
          }}
          rows={3}
          spellCheck={false}
          className="border-line-strong bg-raised text-meta text-ink placeholder:text-ink-subtle resize-none rounded-md border px-2.5 py-2 font-mono"
        />
      </label>

      {(empty || service.connection === 'rejected' || service.connection === 'unavailable') && (
        <p role="alert" className="text-meta text-bad">
          {empty
            ? t('empty')
            : service.connection === 'rejected'
              ? t('rejected')
              : t('unreachable')}
        </p>
      )}

      {checking ? (
        <span className="text-body text-ink-muted inline-flex items-center gap-2">
          <span className="fc-spin" aria-hidden="true" />
          {t('checking')}
        </span>
      ) : (
        <button
          type="button"
          onClick={submit}
          className="bg-ink text-canvas text-meta h-8 self-start rounded-md px-3.5 font-semibold"
        >
          {t('connect')}
        </button>
      )}
    </div>
  );
}

export function PrincipalRow() {
  const t = useTranslations('Briefing.run');
  const review = useTranslations('Review');
  const service = useService();
  const claims = service.claims;
  const name = claims?.name ?? claims?.sub ?? '';

  return (
    <div className="border-line flex items-center gap-2.5 rounded-md border px-2.5 py-2">
      <span className="bg-seg text-meta inline-flex size-7 shrink-0 items-center justify-center rounded-full font-semibold">
        {name.slice(0, 2).toUpperCase()}
      </span>
      <div className="flex min-w-0 flex-col">
        <span className="text-meta font-semibold">{name}</span>
        <span className="text-micro text-ink-subtle truncate font-mono">
          {service.isApprover ? review('approver') : review('reviewer')}
        </span>
      </div>
      <button
        type="button"
        onClick={service.disconnect}
        className="text-ink-subtle hover:text-ink text-label ml-auto underline underline-offset-2"
      >
        {t('disconnect')}
      </button>
    </div>
  );
}
