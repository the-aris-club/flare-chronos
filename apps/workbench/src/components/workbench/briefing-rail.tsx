'use client';

import { useEffect, useMemo, useState } from 'react';
import { useLocale, useTranslations } from 'next-intl';
import { StatusChip, utcNow } from '@/components/review/review-bits';
import { useReviewStore } from '@/components/review/review-store';
import { AmIcon, ICON } from '@/components/ui/icon';
import { runById } from '@/data/fixtures/review-runs';
import { verifyToken } from '@/lib/workbench/briefing';
import {
  IDLE_RUN,
  scheduleFor,
  type ConnState,
  type RunState,
  type ServiceState,
} from '@/lib/workbench/service';
import { BriefingRun } from './briefing-run';
import { ConnectPanel, RailStatusChip, ServiceDown, ServiceSimulator } from './service-panel';

export type RailState = 'auto' | 'open' | 'closed';

type BriefingRailProps = {
  region: 'mekong' | 'amazon';
  state: RailState;
  service: ServiceState;
  conn: ConnState;
  onToggle: () => void;
  onService: (service: ServiceState) => void;
  onConn: (conn: ConnState) => void;
};

// TODO(api): briefing run — replace this fixture with the live run stream.
const RUN_ID = 'RUN-0412';

export function BriefingRail({
  region,
  state,
  service,
  conn,
  onToggle,
  onService,
  onConn,
}: BriefingRailProps) {
  const t = useTranslations('Briefing');
  const review = useTranslations('Review');
  const regionNames = useTranslations('Header.regions');
  const lang = useLocale() === 'vi' ? 'vi' : 'en';
  const store = useReviewStore();
  const run = runById(RUN_ID);
  const decision = run ? store.decisionsFor(run.id) : undefined;
  const [token, setToken] = useState('');
  const [error, setError] = useState<'empty' | 'rejected' | null>(null);
  const [lastHealthy, setLastHealthy] = useState('—');
  const [runState, setRunState] = useState<RunState>(IDLE_RUN);
  const schedule = useMemo(() => scheduleFor(service === 'degraded'), [service]);
  const connected = conn === 'connected';

  useEffect(() => {
    if (conn !== 'resolving') return;
    const timer = window.setTimeout(() => onConn('resolved'), 900);
    return () => window.clearTimeout(timer);
  }, [conn, onConn]);

  useEffect(() => {
    if (runState.status !== 'running') return;
    const timer = window.setInterval(() => {
      setRunState((current) => {
        if (current.status !== 'running') return current;
        const elapsed = Date.now() - current.startedAt;
        if (elapsed >= schedule.approvalAt) {
          return { ...current, status: 'paused', elapsed: schedule.approvalAt };
        }
        return { ...current, elapsed };
      });
    }, 80);
    return () => window.clearInterval(timer);
  }, [runState.status, schedule.approvalAt]);

  function selectService(next: ServiceState) {
    if (next === 'down') setLastHealthy(utcNow());
    onService(next);
    if (next === 'down') setRunState(IDLE_RUN);
  }

  function verify() {
    const result = verifyToken(token);
    if (!result.ok) {
      setError(result.reason);
      return;
    }
    setError(null);
    onConn('resolving');
  }

  function connect() {
    setError(null);
    setToken('');
    setRunState(IDLE_RUN);
    onConn('connected');
  }

  function disconnect() {
    setToken('');
    setError(null);
    setRunState(IDLE_RUN);
    onConn('none');
  }

  function start() {
    if (service === 'down' || !connected) return;
    setRunState({
      status: 'running',
      startedAt: Date.now(),
      elapsed: 0,
      reason: '',
      reasonError: false,
    });
  }

  const tone = decision ? (decision.kind === 'approve' ? 'ok' : 'bad') : null;

  return (
    <aside
      data-tour="brief"
      aria-label={t('title')}
      data-state={state}
      className="fc-rail border-line bg-surface group z-30 flex shrink-0 flex-col border-l transition-all duration-200"
    >
      <div className="fc-rail-content flex min-h-0 flex-1 flex-col group-data-[state=closed]:hidden">
        <header className="border-line flex items-center gap-2 border-b px-3 py-2.5">
          <h2 className="text-body font-semibold">{t('title')}</h2>
          {service === 'down' ? (
            <RailStatusChip tone="bad" label={t('service.down')} />
          ) : !connected ? (
            <RailStatusChip tone="neutral" label={t('service.notConnected')} />
          ) : decision && run ? (
            <StatusChip status={decision.kind === 'approve' ? 'published' : 'withheld'} />
          ) : runState.status === 'paused' ? (
            <RailStatusChip tone="cyan" label={review('needs')} />
          ) : runState.status === 'running' ? (
            <RailStatusChip tone="warn" label={t('run.running')} />
          ) : (
            <RailStatusChip tone="neutral" label={t('run.ready')} />
          )}
          <button
            type="button"
            onClick={onToggle}
            aria-label={t('close')}
            className="border-line text-ink-muted hover:bg-chip hover:text-ink ml-auto inline-flex size-7 items-center justify-center rounded-md border"
          >
            <AmIcon icon={ICON.chevron} size="sm" className="rotate-90" />
          </button>
        </header>

        <div className="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto p-3">
          {service === 'down' ? (
            <ServiceDown lastHealthy={lastHealthy} onRetry={() => onService('up')} />
          ) : !connected ? (
            <ConnectPanel
              conn={conn}
              token={token}
              error={error}
              onToken={(value) => {
                setToken(value);
                if (error) setError(null);
              }}
              onVerify={verify}
              onConnect={connect}
            />
          ) : run ? (
            <>
              {(run.region.en === 'Amazon' ? 'amazon' : 'mekong') !== region && (
                <p
                  role="note"
                  className="text-meta text-ink-muted border-line rounded-md border border-dashed p-2"
                >
                  {t('sampleOtherRegion', {
                    runRegion: run.region[lang],
                    region: regionNames(`${region}Long`),
                  })}
                </p>
              )}
              <BriefingRun
                run={run}
                service={service}
                runState={runState}
                schedule={schedule}
                onStart={start}
                onDisconnect={disconnect}
              />
            </>
          ) : null}
        </div>

        <ServiceSimulator
          service={service}
          onService={selectService}
          onReset={() => setRunState(IDLE_RUN)}
          canReset={!decision}
        />
      </div>

      <button
        type="button"
        onClick={onToggle}
        aria-label={t('open')}
        className="fc-rail-collapsed text-ink-muted hover:bg-chip hover:text-ink hidden h-full flex-col items-center gap-2 py-3 group-data-[state=closed]:flex"
      >
        <AmIcon icon={ICON.chevron} size="sm" className="-rotate-90" />
        <span className="fc-vertical text-meta">{t('title')}</span>
        <span
          aria-hidden="true"
          className={`size-2 rounded-full ${
            tone === 'ok'
              ? 'bg-ok'
              : tone === 'bad'
                ? 'bg-bad'
                : service === 'down'
                  ? 'bg-bad'
                  : 'bg-line-strong'
          }`}
        />
      </button>
    </aside>
  );
}
