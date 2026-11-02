'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useService } from '@/components/service/service-provider';
import { Icon, ICON } from '@/components/ui/icon';
import { IDLE_RUN, reduceRun, type RunView } from '@/lib/service/run';
import { BriefingRun, type Preset } from './briefing-run';
import { ConnectPanel, RailStatusChip, ServiceDown } from './service-panel';

export type RailState = 'auto' | 'open' | 'closed';

type BriefingRailProps = {
  region: 'mekong' | 'amazon';
  state: RailState;
  onToggle: () => void;
};

const QUERIES: Record<Preset['useCase'], (region: string) => string> = {
  'UC-2.2': (region) =>
    `UC-2.2 Compute uncertainty-aware tactical dispatch for rangers in ${region} in 2024.`,
  'UC-S1.4': (region) => `UC-S1.4 Generate flash NRT tactical ranger alert for ${region} in 2026.`,
};

export function BriefingRail({ region, state, onToggle }: BriefingRailProps) {
  const t = useTranslations('Briefing');
  const review = useTranslations('Review');
  const service = useService();
  const [run, setRun] = useState<RunView>(IDLE_RUN);
  const connected = service.connection === 'connected';

  async function start(preset: Preset) {
    const params = new URLSearchParams({
      use_case_id: preset.useCase,
      query: QUERIES[preset.useCase](region),
    });
    setRun({ ...IDLE_RUN, phase: 'running' });

    const events = service.stream(`/api/v1/analysis/stream?${params}`);
    let next = await events.next();
    while (!next.done) {
      const event = next.value;
      setRun((current) => reduceRun(current, event));
      next = await events.next();
    }
    if (next.value) {
      setRun((current) => ({ ...current, phase: 'failed', error: next.value ?? 'unavailable' }));
    }
    await service.refresh();
  }

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
          {service.connection === 'unavailable' ? (
            <RailStatusChip tone="bad" label={t('service.down')} />
          ) : !connected ? (
            <RailStatusChip tone="neutral" label={t('service.notConnected')} />
          ) : run.phase === 'paused' ? (
            <RailStatusChip tone="cyan" label={review('needs')} />
          ) : run.phase === 'running' ? (
            <RailStatusChip tone="warn" label={t('run.running')} />
          ) : run.phase === 'failed' ? (
            <RailStatusChip tone="bad" label={review('failed')} />
          ) : (
            <RailStatusChip tone="neutral" label={t('run.ready')} />
          )}
          <button
            type="button"
            onClick={onToggle}
            aria-label={t('close')}
            className="border-line text-ink-muted hover:bg-chip hover:text-ink ml-auto inline-flex size-7 items-center justify-center rounded-md border"
          >
            <Icon icon={ICON.chevron} size="sm" className="rotate-90" />
          </button>
        </header>

        <div className="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto p-3">
          {service.connection === 'unavailable' && <ServiceDown />}
          {connected ? (
            <BriefingRun run={run} region={region} onStart={(preset) => void start(preset)} />
          ) : (
            <ConnectPanel />
          )}
        </div>
      </div>

      <button
        type="button"
        onClick={onToggle}
        aria-label={t('open')}
        className="fc-rail-collapsed text-ink-muted hover:bg-chip hover:text-ink hidden h-full flex-col items-center gap-2 py-3 group-data-[state=closed]:flex"
      >
        <Icon icon={ICON.chevron} size="sm" className="-rotate-90" />
        <span className="fc-vertical text-meta">{t('title')}</span>
        <span
          aria-hidden="true"
          className={`size-2 rounded-full ${
            service.connection === 'unavailable'
              ? 'bg-bad'
              : connected
                ? 'bg-ok'
                : 'bg-line-strong'
          }`}
        />
      </button>
    </aside>
  );
}
