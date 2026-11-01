'use client';

import type { ReactNode } from 'react';
import { useTranslations } from 'next-intl';
import { AmIcon, ICON } from '@/components/ui/icon';

export type EventState = 'pending' | 'running' | 'done' | 'paused' | 'rejected';

const STATE_STYLE: Record<EventState, string> = {
  pending: 'border-line-strong text-ink-subtle',
  running: 'border-line-strong text-ink-muted',
  done: 'border-ok text-ok',
  paused: 'border-warn text-warn',
  rejected: 'border-bad text-bad',
};

export function EventRow({
  title,
  state,
  time,
  children,
}: {
  title: string;
  state: EventState;
  time: string;
  children?: ReactNode;
}) {
  const t = useTranslations('Briefing.run');
  const label = {
    pending: t('eventPending'),
    running: t('eventRunning'),
    done: t('eventDone'),
    paused: t('eventPaused'),
    rejected: t('eventRejected'),
  }[state];
  const glyph = {
    pending: ICON.clock,
    running: ICON.service,
    done: ICON.checkCircle,
    paused: ICON.pause,
    rejected: ICON.xCircle,
  }[state];

  return (
    <li className="grid grid-cols-[20px_minmax(0,1fr)] gap-2.5">
      <div className="flex flex-col items-center">
        <span
          className={`inline-flex size-5 shrink-0 items-center justify-center rounded-full border-[1.5px] ${STATE_STYLE[state]}`}
        >
          {state === 'running' ? (
            <span className="fc-spin" aria-hidden="true" />
          ) : (
            <AmIcon icon={glyph} size="xs" />
          )}
        </span>
        <i aria-hidden="true" className="bg-line-strong w-px flex-1" />
      </div>
      <div className="flex min-w-0 flex-col gap-1 pb-3.5">
        <div className="flex items-baseline gap-2">
          <span className="text-body font-semibold">{title}</span>
          <span className={`text-micro font-mono ${STATE_STYLE[state].split(' ')[1]}`}>
            {label}
          </span>
          <span className="text-micro text-ink-subtle ml-auto font-mono">{time}</span>
        </div>
        {children}
      </div>
    </li>
  );
}
