import { PRINCIPAL, type Decision, type DecisionKind } from '@/data/fixtures/review';

export function nextAuditId(existing: string[]): string {
  let next = 196;
  const used = new Set(existing);

  while (used.has(`A-0${next}`)) next += 1;
  return `A-0${next}`;
}

export function makeDecision(
  kind: DecisionKind,
  reason: string,
  note: string,
  existing: Decision[],
): Decision {
  return {
    kind,
    reviewer: PRINCIPAL.name,
    role: kind === 'approve' ? PRINCIPAL.role : 'Reviewer',
    at: new Date(Math.floor(Date.now() / 1000) * 1000).toISOString(),
    reason,
    note,
    audit: nextAuditId(existing.map((decision) => decision.audit)),
  };
}
