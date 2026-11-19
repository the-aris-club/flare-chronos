import { describe, expect, test } from 'bun:test';
import { callService, resolveServiceUrl } from './client';

const respond = (status: number, body: unknown = {}) =>
  (async () => new Response(JSON.stringify(body), { status })) as unknown as typeof fetch;

describe('resolveServiceUrl', () => {
  test('a configured URL wins in every environment', () => {
    const expected = 'https://example.test/api';
    expect(resolveServiceUrl('production', expected)).toBe(expected);
    expect(resolveServiceUrl('development', expected)).toBe(expected);
  });

  test('production falls back to the API host, not localhost', () => {
    expect(resolveServiceUrl('production', undefined)).toBe(
      'https://api.flare-chronos.resonance.io.vn',
    );
  });

  test('local development still uses the loopback service', () => {
    expect(resolveServiceUrl('development', undefined)).toBe('http://127.0.0.1:5901');
  });
});

describe('callService', () => {
  test('sends the bearer token and returns the parsed body', async () => {
    let seen: Request | undefined;
    const fetcher = (async (url: string, init: RequestInit) => {
      seen = new Request(url, init);
      return new Response(JSON.stringify({ runs: [] }), { status: 200 });
    }) as unknown as typeof fetch;

    const result = await callService(fetcher, 'tok', '/api/v1/review/runs');

    expect(result).toEqual({ ok: true, data: { runs: [] } });
    expect(seen?.headers.get('authorization')).toBe('Bearer tok');
    expect(seen?.url.endsWith('/api/v1/review/runs')).toBe(true);
  });

  test.each([
    [401, 'unauthorized'],
    [403, 'forbidden'],
    [404, 'not_found'],
    [500, 'unavailable'],
  ] as const)('status %i is %s', async (status, reason) => {
    expect(await callService(respond(status), 'tok', '/x')).toEqual({ ok: false, reason });
  });

  test('a network failure is unavailable', async () => {
    const down = (async () => {
      throw new TypeError('fetch failed');
    }) as unknown as typeof fetch;

    expect(await callService(down, 'tok', '/x')).toEqual({ ok: false, reason: 'unavailable' });
  });
});
