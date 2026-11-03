'use client';

import { useTranslations } from 'next-intl';
import { Chip, type ChipTone } from '@/components/ui/chip';
import { AmIcon, ICON } from '@/components/ui/icon';
import { PRINCIPAL, type ConnState, type ServiceState } from '@/lib/workbench/service';
import { RoleText } from '@/components/review/review-bits';

export function RailStatusChip({ tone, label }: { tone: ChipTone; label: string }) {
  return <Chip tone={tone}>{label}</Chip>;
}

export function ServiceDown({
  lastHealthy,
  onRetry,
}: {
  lastHealthy: string;
  onRetry: () => void;
}) {
  const t = useTranslations('Briefing.down');

  return (
    <div
      role="alert"
      className="border-bad/45 bg-panel flex flex-col gap-3 rounded-lg border p-3.5"
    >
      <div className="flex items-center gap-2.5">
        <span className="border-bad text-bad inline-flex size-7 items-center justify-center rounded-md border-[1.5px]">
          <AmIcon icon={ICON.xCircle} size="sm" />
        </span>
        <span className="text-subhead font-semibold">{t('title')}</span>
      </div>
      <dl className="text-body grid grid-cols-[5.5rem_minmax(0,1fr)] gap-x-2.5 gap-y-1.5">
        <dt className="text-ink-subtle">{t('reason')}</dt>
        <dd>{t('reasonValue')}</dd>
        <dt className="text-ink-subtle">{t('tier')}</dt>
        <dd>{t('tierValue')}</dd>
        <dt className="text-ink-subtle">{t('lastHealthy')}</dt>
        <dd className="text-meta font-mono">{lastHealthy}</dd>
        <dt className="text-ink-subtle">{t('nextRetry')}</dt>
        <dd className="text-meta font-mono">{t('nextRetryValue')}</dd>
      </dl>
      <p className="text-body text-ink-muted leading-relaxed">{t('body')}</p>
      <button
        type="button"
        onClick={onRetry}
        className="border-line-strong text-meta text-ink hover:bg-chip h-8 self-start rounded-md border px-3 font-medium"
      >
        {t('retry')}
      </button>
    </div>
  );
}

export function ConnectPanel({
  conn,
  token,
  error,
  onToken,
  onVerify,
  onConnect,
}: {
  conn: ConnState;
  token: string;
  error: 'empty' | 'rejected' | null;
  onToken: (value: string) => void;
  onVerify: () => void;
  onConnect: () => void;
}) {
  const t = useTranslations('Briefing.connect');
  const tb = useTranslations('Briefing');

  return (
    <div className="border-line bg-panel flex flex-col gap-2.5 rounded-lg border p-3.5">
      <span className="text-micro text-ink-subtle font-mono tracking-widest uppercase">
        {t('step')}
      </span>
      <h3 className="text-subhead font-semibold">{t('title')}</h3>
      <p className="text-body text-ink-muted leading-relaxed">{t('body')}</p>

      <label htmlFor="briefing-token" className="text-meta text-ink-muted flex flex-col gap-1">
        {t('token')}
        <textarea
          id="briefing-token"
          name="token"
          autoComplete="off"
          value={token}
          onChange={(event) => onToken(event.target.value)}
          rows={3}
          spellCheck={false}
          placeholder="fc_live_..."
          className="border-line-strong bg-raised text-meta text-ink placeholder:text-ink-subtle resize-none rounded-md border px-2.5 py-2 font-mono"
        />
      </label>

      {error && (
        <p role="alert" className="text-meta text-bad">
          {error === 'empty' ? t('empty') : t('rejected')}
        </p>
      )}

      {conn === 'none' || conn === 'error' ? (
        <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={onVerify}
            className="bg-ink text-canvas text-meta h-8 rounded-md px-3.5 font-semibold"
          >
            {t('verify')}
          </button>
        </div>
      ) : conn === 'resolving' ? (
        <span className="text-body text-ink-muted inline-flex items-center gap-2">
          <span className="fc-spin" aria-hidden="true" />
          {t('resolving')}
        </span>
      ) : (
        <div className="border-line-strong bg-raised flex flex-col gap-2.5 rounded-md border p-2.5">
          <span className="text-micro text-ink-subtle font-mono tracking-widest uppercase">
            {t('resolvedStep')}
          </span>
          <div className="flex items-center gap-2.5">
            <span className="bg-seg text-meta inline-flex size-8 items-center justify-center rounded-full font-semibold">
              {PRINCIPAL.initials}
            </span>
            <div className="flex min-w-0 flex-col">
              <span className="text-body font-semibold">{PRINCIPAL.name}</span>
              <span className="text-micro text-ink-subtle font-mono">{PRINCIPAL.email}</span>
            </div>
          </div>
          <dl className="text-meta grid grid-cols-[4rem_minmax(0,1fr)] gap-x-2.5 gap-y-1">
            <dt className="text-ink-subtle">{t('role')}</dt>
            <dd>{t('roleValue')}</dd>
            <dt className="text-ink-subtle">{t('scopes')}</dt>
            <dd className="text-micro font-mono">{tb('scopesValue')}</dd>
            <dt className="text-ink-subtle">{t('expires')}</dt>
            <dd className="text-micro font-mono">{PRINCIPAL.expires}</dd>
          </dl>
          <button
            type="button"
            onClick={onConnect}
            className="bg-ink text-canvas text-meta h-8 self-start rounded-md px-3.5 font-semibold"
          >
            {t('connectAs', { name: PRINCIPAL.name })}
          </button>
        </div>
      )}
    </div>
  );
}

export function ServiceSimulator({
  service,
  onService,
  onReset,
  canReset,
}: {
  service: ServiceState;
  onService: (service: ServiceState) => void;
  onReset: () => void;
  canReset: boolean;
}) {
  const t = useTranslations('Briefing.sim');
  const options: { value: ServiceState; label: string }[] = [
    { value: 'up', label: t('up') },
    { value: 'degraded', label: t('degraded') },
    { value: 'down', label: t('down') },
  ];

  return (
    <div className="border-line flex flex-col gap-1.5 border-t border-dashed px-3 py-2">
      <div className="flex items-center gap-2">
        <span className="text-micro text-ink-subtle font-mono tracking-widest uppercase">
          {t('title')}
        </span>
        {canReset && (
          <button
            type="button"
            onClick={onReset}
            className="text-ink-subtle hover:text-ink text-label ml-auto underline underline-offset-2"
          >
            {t('reset')}
          </button>
        )}
      </div>
      <div
        role="group"
        aria-label={t('label')}
        className="border-line-strong inline-flex gap-0.5 self-start rounded-md border p-0.5"
      >
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            aria-pressed={service === option.value}
            onClick={() => onService(option.value)}
            className={`text-label h-5 rounded-sm px-2 font-medium ${
              service === option.value
                ? option.value === 'down'
                  ? 'bg-bad/20 text-bad'
                  : option.value === 'degraded'
                    ? 'bg-warn/20 text-warn'
                    : 'bg-seg text-ink'
                : 'text-ink-subtle hover:text-ink'
            }`}
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  );
}

export function PrincipalRow({ onDisconnect }: { onDisconnect: () => void }) {
  const t = useTranslations('Briefing.run');
  const tb = useTranslations('Briefing');

  return (
    <div className="border-line flex items-center gap-2.5 rounded-md border px-2.5 py-2">
      <span className="bg-seg text-meta inline-flex size-7 shrink-0 items-center justify-center rounded-full font-semibold">
        {PRINCIPAL.initials}
      </span>
      <div className="flex min-w-0 flex-col">
        <span className="text-meta font-semibold">{PRINCIPAL.name}</span>
        <span className="text-micro text-ink-subtle truncate font-mono">
          <RoleText role={PRINCIPAL.role} /> · {tb('scopesValue')}
        </span>
      </div>
      <button
        type="button"
        onClick={onDisconnect}
        className="text-ink-subtle hover:text-ink text-label ml-auto underline underline-offset-2"
      >
        {t('disconnect')}
      </button>
    </div>
  );
}
