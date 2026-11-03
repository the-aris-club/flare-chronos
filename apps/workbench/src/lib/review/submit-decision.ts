import type { Decision, DecisionKind } from '@/data/fixtures/review';

export type SubmitResult = { ok: true; decision: Decision } | { ok: false; error: string };

/**
 * Persist one decision. Pure of React state so the caller can roll back an optimistic
 * update when this reports a failure.
 */
export async function submitDecision(
  fetcher: typeof fetch,
  runId: string,
  kind: DecisionKind,
  reason: string,
  note: string,
): Promise<SubmitResult> {
  let response: Response;
  try {
    response = await fetcher('/api/review/decisions', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ runId, kind, reason, note }),
    });
  } catch {
    return { ok: false, error: 'network' };
  }

  const data = (await response.json().catch(() => null)) as {
    decision?: Decision;
    error?: string;
  } | null;
  if ((response.ok || response.status === 409) && data?.decision) {
    return { ok: true, decision: data.decision };
  }
  return { ok: false, error: data?.error ?? `http_${response.status}` };
}
