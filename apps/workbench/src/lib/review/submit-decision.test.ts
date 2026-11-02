import { describe, expect, test } from 'bun:test';
import type { Decision } from '@/data/fixtures/review';
import { submitDecision } from './submit-decision';

const saved: Decision = {
  kind: 'approve',
  reviewer: 'Nguyễn Thị Mai',
  role: 'Người phê duyệt',
  at: '2026-11-02T00:00:00Z',
  reason: 'evidence',
  note: '',
  audit: 'A-0196',
};

function reply(status: number, body: unknown): typeof fetch {
  return (async () => new Response(JSON.stringify(body), { status })) as unknown as typeof fetch;
}

describe('submitDecision', () => {
  test('posts the decision once and returns what the server stored', async () => {
    const calls: { url: string; body: unknown }[] = [];
    const fetcher = (async (url: string, init: RequestInit) => {
      calls.push({ url, body: JSON.parse(String(init.body)) });
      return new Response(JSON.stringify({ decision: saved }), { status: 201 });
    }) as unknown as typeof fetch;

    const result = await submitDecision(fetcher, 'RUN-0412', 'approve', 'evidence', 'ok');

    expect(calls).toEqual([
      {
        url: '/api/review/decisions',
        body: { runId: 'RUN-0412', kind: 'approve', reason: 'evidence', note: 'ok' },
      },
    ]);
    expect(result).toEqual({ ok: true, decision: saved });
  });

  test('a decision the server already holds is adopted, not an error', async () => {
    const result = await submitDecision(
      reply(409, { error: 'already_decided', decision: saved }),
      'RUN-0412',
      'reject',
      'evidence',
      '',
    );
    expect(result).toEqual({ ok: true, decision: saved });
  });

  test('a server or network failure is reported so the caller can roll back', async () => {
    const unavailable = await submitDecision(
      reply(503, { error: 'store_unavailable' }),
      'RUN-0412',
      'approve',
      'evidence',
      '',
    );
    const offline = await submitDecision(
      (async () => {
        throw new TypeError('network down');
      }) as unknown as typeof fetch,
      'RUN-0412',
      'approve',
      'evidence',
      '',
    );

    expect(unavailable).toEqual({ ok: false, error: 'store_unavailable' });
    expect(offline).toEqual({ ok: false, error: 'network' });
  });
});
