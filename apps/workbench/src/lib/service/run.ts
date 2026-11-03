import type { ServiceEvent } from './sse';

export type Verification = {
  passed: boolean;
  checked_numbers_count?: number;
  unverified_numbers?: number[];
  unresolved_citations?: string[];
};

export type Fact = { key: string; value: number; unit: string; tool: string };

export type SignOff = {
  question: string;
  briefing: string;
  verification: Verification;
  facts: Fact[];
  entity: { region?: string; epoch_years?: number[] };
  selfCorrections: number;
};

export type RunView = {
  phase: 'idle' | 'running' | 'paused' | 'done' | 'failed';
  threadId: string | undefined;
  useCaseId: string | undefined;
  mode: string | undefined;
  nodes: string[];
  tools: string[];
  reasoning: string;
  verification: Verification | undefined;
  briefing: string | undefined;
  signOff: SignOff | undefined;
  approved: boolean | undefined;
  error: string | undefined;
};

export const IDLE_RUN: RunView = {
  phase: 'idle',
  threadId: undefined,
  useCaseId: undefined,
  mode: undefined,
  nodes: [],
  tools: [],
  reasoning: '',
  verification: undefined,
  briefing: undefined,
  signOff: undefined,
  approved: undefined,
  error: undefined,
};

function asText(value: unknown): string {
  return typeof value === 'string' ? value : '';
}

function asList<T>(value: unknown): T[] {
  return Array.isArray(value) ? (value as T[]) : [];
}

function verificationFrom(report: unknown): Verification {
  const node = (report ?? {}) as Verification;
  return { ...node, passed: node.passed === true };
}

function signOffFrom(event: ServiceEvent): SignOff {
  const evidence = (event.evidence ?? {}) as Record<string, unknown>;

  return {
    question: asText(event.question),
    briefing: asText(evidence.final_briefing),
    verification: verificationFrom(evidence.verification_report),
    facts: asList<Record<string, unknown>>(evidence.verified_ledger_entries).map((entry) => ({
      key: asText(entry.fact_key),
      value: Number(entry.numeric_value),
      unit: asText(entry.unit),
      tool: asText(entry.source_tool),
    })),
    entity: (evidence.entity ?? {}) as SignOff['entity'],
    selfCorrections: Number(evidence.self_corrections ?? 0),
  };
}

/** Folds one stream event into the run the briefing rail renders. */
export function reduceRun(run: RunView, event: ServiceEvent): RunView {
  switch (event.type) {
    case 'run_started':
      return {
        ...run,
        phase: 'running',
        threadId: asText(event.thread_id) || run.threadId,
        useCaseId: asText(event.use_case_id) || run.useCaseId,
        mode: asText(event.mode) || run.mode,
        error: undefined,
      };
    case 'node_completed':
      return { ...run, nodes: [...run.nodes, asText(event.node)] };
    case 'tool_result':
      return {
        ...run,
        tools: [...run.tools, ...asList<string>(event.tools).filter((t) => !run.tools.includes(t))],
      };
    case 'reasoning':
      return { ...run, reasoning: run.reasoning + asText(event.text) };
    case 'sign_off_required':
      return { ...run, signOff: signOffFrom(event) };
    case 'run_paused':
      return { ...run, phase: 'paused' };
    case 'verification':
      return { ...run, verification: event as unknown as Verification };
    case 'briefing':
      return { ...run, briefing: asText(event.text) };
    case 'run_completed': {
      const decision = (event.sign_off_decision ?? {}) as { approved?: boolean };
      return { ...run, phase: 'done', approved: decision.approved };
    }
    case 'run_failed':
      return { ...run, phase: 'failed', error: asText(event.error) };
    default:
      return run;
  }
}
