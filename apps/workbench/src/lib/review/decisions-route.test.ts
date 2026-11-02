import { afterAll, beforeEach, describe, expect, test } from 'bun:test';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const dir = await mkdtemp(path.join(tmpdir(), 'review-decisions-'));
const store = path.join(dir, 'decisions.json');
process.env.REVIEW_DECISIONS_PATH = store;

const { GET, POST } = await import('@/app/api/review/decisions/route');

function post(body: unknown) {
  return POST(
    new Request('http://test/api/review/decisions', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  );
}

beforeEach(async () => {
  await rm(store, { force: true });
});

afterAll(async () => {
  await rm(dir, { recursive: true, force: true });
});

describe('decisions route', () => {
  test('a corrupt store is reported, never replaced by the seed on the next write', async () => {
    await writeFile(store, '{"RUN-0411": {', 'utf8');

    const response = await post({ runId: 'RUN-0412', kind: 'approve', reason: 'evidence' });

    expect(response.status).toBe(503);
    expect(await readFile(store, 'utf8')).toBe('{"RUN-0411": {');
  });

  test('concurrent decisions on different runs are all kept, with distinct audit ids', async () => {
    await writeFile(store, '{}\n', 'utf8');

    const responses = await Promise.all([
      post({ runId: 'RUN-0411', kind: 'approve', reason: 'evidence' }),
      post({ runId: 'RUN-0412', kind: 'approve', reason: 'evidence' }),
      post({ runId: 'RUN-0413', kind: 'reject', reason: 'evidence' }),
    ]);

    expect(responses.map((response) => response.status)).toEqual([201, 201, 201]);
    const saved = JSON.parse(await readFile(store, 'utf8')) as Record<string, { audit: string }>;
    expect(Object.keys(saved).sort()).toEqual(['RUN-0411', 'RUN-0412', 'RUN-0413']);
    expect(new Set(Object.values(saved).map((decision) => decision.audit)).size).toBe(3);
  });

  test('a body with the wrong types is a 400 and writes nothing', async () => {
    await writeFile(store, '{}\n', 'utf8');

    const badNote = await post({ runId: 'RUN-0412', kind: 'approve', reason: 'evidence', note: 5 });
    const badReason = await post({ runId: 'RUN-0412', kind: 'approve', reason: { a: 1 } });
    const noBody = await post(null);

    expect([badNote.status, badReason.status, noBody.status]).toEqual([400, 400, 400]);
    expect(await readFile(store, 'utf8')).toBe('{}\n');
  });

  test('a repeated decision on the same run is a 409 and keeps the first', async () => {
    await writeFile(store, '{}\n', 'utf8');
    const first = await post({ runId: 'RUN-0412', kind: 'approve', reason: 'evidence' });
    const again = await post({ runId: 'RUN-0412', kind: 'reject', reason: 'evidence' });

    expect([first.status, again.status]).toEqual([201, 409]);
    const saved = JSON.parse(await readFile(store, 'utf8')) as Record<string, { kind: string }>;
    expect(saved['RUN-0412']?.kind).toBe('approve');
  });

  test('GET serves the seed when no store exists yet and a 503 when the store is corrupt', async () => {
    const fresh = await GET();
    const seeded = (await fresh.json()) as { decisions: Record<string, unknown> };
    expect(fresh.status).toBe(200);
    expect(Object.keys(seeded.decisions)).toContain('RUN-0411');

    await writeFile(store, 'not json', 'utf8');
    expect((await GET()).status).toBe(503);
  });
});
