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

function asObject(value: unknown, name: string): Json {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new ShapeError(`${name} must be an object`);
  }
  return value as Json;
}

function requireString(node: Json, key: string): string {
  const value = node[key];
  if (typeof value !== 'string') throw new ShapeError(`${key} must be a string`);
  return value;
}

function optionalString(node: Json, key: string): string {
  const value = node[key];
  return typeof value === 'string' ? value : '';
}

function requireList(node: Json, key: string): unknown[] {
  const value = node[key];
  if (!Array.isArray(value)) throw new ShapeError(`${key} must be a list`);
  return value;
}

function row(raw: unknown): ReviewRow {
  const node = asObject(raw, 'run');
  const status = requireString(node, 'status') as ReviewStatus;
  if (!REVIEW_STATUSES.includes(status)) throw new ShapeError(`unknown status ${status}`);

  return {
    id: requireString(node, 'id'),
    owner: requireString(node, 'owner'),
    useCase: optionalString(node, 'use_case_id'),
    status,
    startedAt: requireString(node, 'started_at'),
    updatedAt: requireString(node, 'updated_at'),
  };
}

/** Parse the queue. Anything off-contract throws: Review never shows a guessed row. */
export function parseRunList(body: unknown): ReviewRow[] {
  return requireList(asObject(body, 'body'), 'runs').map(row);
}

export function parseRun(body: unknown): ReviewRun {
  const node = asObject(body, 'run');
  const verification = asObject(node.verification ?? {}, 'verification');
  const entity = asObject(node.entity ?? {}, 'entity');

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
    facts: requireList(node, 'facts').map((raw) => {
      const fact = asObject(raw, 'fact');
      if (typeof fact.value !== 'number') throw new ShapeError('fact value must be a number');
      return {
        key: requireString(fact, 'fact_key'),
        value: fact.value,
        unit: optionalString(fact, 'unit'),
        tool: requireString(fact, 'source_tool'),
        provenance: optionalString(fact, 'provenance'),
      };
    }),
    tools: requireList(node, 'tools').map(String),
  };
}

export function parseAudit(body: unknown): AuditRow[] {
  return requireList(asObject(body, 'body'), 'audit').map((raw) => {
    const node = asObject(raw, 'audit row');
    return {
      id: requireString(node, 'id'),
      runId: requireString(node, 'thread_id'),
      principal: requireString(node, 'principal'),
      approved: node.approved === true,
      reason: optionalString(node, 'reason'),
      reasonCode: optionalString(node, 'reason_code'),
      decidedAt: requireString(node, 'decided_at'),
    };
  });
}
