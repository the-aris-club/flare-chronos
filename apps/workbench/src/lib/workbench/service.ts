export type ServiceState = 'up' | 'degraded' | 'down';
export type ConnState = 'none' | 'error' | 'resolving' | 'resolved' | 'connected';
export type RunStatus = 'idle' | 'running' | 'paused' | 'done';
export type FactStatus = 'pending' | 'checking' | 'verified' | 'rewriting' | 'nosource';

export type RunState = {
  status: RunStatus;
  startedAt: number;
  elapsed: number;
  reason: string;
  reasonError: boolean;
};

export type RunSchedule = {
  classifyEnd: number;
  toolsEnd: number;
  reasonEnd: number;
  verifyStart: number;
  approvalAt: number;
  step: number;
  rewrite: number;
  factor: number;
};

export { PRINCIPAL } from '@/data/fixtures/review';

export const IDLE_RUN: RunState = {
  status: 'idle',
  startedAt: 0,
  elapsed: 0,
  reason: '',
  reasonError: false,
};

export function scheduleFor(degraded: boolean): RunSchedule {
  const factor = degraded ? 1.5 : 1;
  const classifyEnd = 1400 * factor;
  const toolsEnd = 3800 * factor;
  const reasonEnd = 6200 * factor;
  const verifyStart = reasonEnd;
  const step = 320 * factor;
  const rewrite = 900 * factor;
  const approvalAt = verifyStart + 8 * step + rewrite + 300 * factor;

  return {
    classifyEnd,
    toolsEnd,
    reasonEnd,
    verifyStart,
    approvalAt,
    step,
    rewrite,
    factor,
  };
}

export function phaseAt(status: RunStatus, elapsed: number, schedule: RunSchedule): number {
  if (status === 'idle') return -1;
  if (status === 'paused') return 4;
  if (status === 'done') return 5;
  if (elapsed < schedule.classifyEnd) return 0;
  if (elapsed < schedule.toolsEnd) return 1;
  if (elapsed < schedule.reasonEnd) return 2;
  if (elapsed < schedule.approvalAt) return 3;
  return 4;
}

export function factStatus(
  index: number,
  rewriteIndex: number,
  elapsed: number,
  schedule: RunSchedule,
  settled: boolean,
): FactStatus {
  if (settled) return 'verified';
  const start = schedule.verifyStart + index * schedule.step;
  if (elapsed < start) return 'pending';
  if (index === rewriteIndex) {
    if (elapsed < start + schedule.rewrite * 0.35) return 'nosource';
    if (elapsed < start + schedule.rewrite) return 'rewriting';
    return 'verified';
  }
  if (elapsed < start + schedule.step) return 'checking';
  return 'verified';
}

export function formatSeconds(ms: number): string {
  return `${(Math.max(0, ms) / 1000).toFixed(1)} s`;
}
