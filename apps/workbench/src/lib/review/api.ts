export type ReviewStatus = 'needs' | 'published' | 'withheld' | 'failed';
export const REVIEW_STATUSES: readonly ReviewStatus[] = ['needs', 'published', 'withheld', 'failed'];

export type ReviewRow = {
  id: string;
  owner: string;
  useCase: string;
  status: ReviewStatus;
  startedAt: string;
  updatedAt: string;
};

export type ReviewFact = {
  key: string;
  value: number;
  unit: string;
  tool: string;
  provenance: string;
};

export type ReviewRun = ReviewRow & {
  mode: string;
  question: string;
  briefing: string;
  verification: {
    passed: boolean;
    checked: number;
    unverified: number[];
    unresolved: string[];
  };
  selfCorrections: number;
  entity: { region: string | undefined; epochYears: number[] };
  facts: ReviewFact[];
  tools: string[];
};

export type AuditRow = {
  id: string;
  runId: string;
  principal: string;
  approved: boolean;
  reason: string;
  reasonCode: string;
  decidedAt: string;
};

type Json = Record<string, unknown>;

class ShapeError extends Error {}

function object(value: unknown, name: string): Json {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new ShapeError(`${name} must be an object`);
  }
  return value as Json;
}

function string(node: Json, key: string): string {
  const value = node[key];
  if (typeof value !== 'string') throw new ShapeError(`${key} must be a string`);
  return value;
}

function optionalString(node: Json, key: string): string {
  const value = node[key];
  return typeof value === 'string' ? value : '';
}

function array(node: Json, key: string): unknown[] {
  const value = node[key];
  if (!Array.isArray(value)) throw new ShapeError(`${key} must be a list`);
  return value;
}

function row(raw: unknown): ReviewRow {
  const node = object(raw, 'run');
  const status = string(node, 'status') as ReviewStatus;
  if (!REVIEW_STATUSES.includes(status)) throw new ShapeError(`unknown status ${status}`);

  return {
    id: string(node, 'id'),
    owner: string(node, 'owner'),
    useCase: optionalString(node, 'use_case_id'),
    status,
    startedAt: string(node, 'started_at'),
    updatedAt: string(node, 'updated_at'),
  };
}

/** Parse the queue. Anything off-contract throws: Review never shows a guessed row. */
export function parseRunList(body: unknown): ReviewRow[] {
  return array(object(body, 'body'), 'runs').map(row);
}

export function parseRun(body: unknown): ReviewRun {
  const node = object(body, 'run');
  const verification = object(node.verification ?? {}, 'verification');
  const entity = object(node.entity ?? {}, 'entity');

  return {
    ...row(node),
    mode: optionalString(node, 'mode'),
    question: optionalString(node, 'question'),
    briefing: optionalString(node, 'briefing'),
    verification: {
      passed: verification.passed === true,
      checked: Number(verification.checked_numbers_count ?? 0),
      unverified: Array.isArray(verification.unverified_numbers)
        ? (verification.unverified_numbers as number[])
        : [],
      unresolved: Array.isArray(verification.unresolved_citations)
        ? (verification.unresolved_citations as string[])
        : [],
    },
    selfCorrections: Number(node.self_corrections ?? 0),
    entity: {
      region: typeof entity.region === 'string' ? entity.region : undefined,
      epochYears: Array.isArray(entity.epoch_years) ? (entity.epoch_years as number[]) : [],
    },
    facts: array(node, 'facts').map((raw) => {
      const fact = object(raw, 'fact');
      if (typeof fact.value !== 'number') throw new ShapeError('fact value must be a number');
      return {
        key: string(fact, 'fact_key'),
        value: fact.value,
        unit: optionalString(fact, 'unit'),
        tool: string(fact, 'source_tool'),
        provenance: optionalString(fact, 'provenance'),
      };
    }),
    tools: array(node, 'tools').map(String),
  };
}

export function parseAudit(body: unknown): AuditRow[] {
  return array(object(body, 'body'), 'audit').map((raw) => {
    const node = object(raw, 'audit row');
    return {
      id: string(node, 'id'),
      runId: string(node, 'thread_id'),
      principal: string(node, 'principal'),
      approved: node.approved === true,
      reason: optionalString(node, 'reason'),
      reasonCode: optionalString(node, 'reason_code'),
      decidedAt: string(node, 'decided_at'),
    };
  });
}
