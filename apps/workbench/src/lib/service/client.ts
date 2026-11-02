import { createSseParser, type ServiceEvent } from './sse';

export const SERVICE_URL = process.env.NEXT_PUBLIC_AI_SERVICE_URL ?? 'http://127.0.0.1:8765';

export type FailureReason = 'unauthorized' | 'forbidden' | 'not_found' | 'unavailable';
export type ServiceResult<T> = { ok: true; data: T } | { ok: false; reason: FailureReason };

const REASONS: Record<number, FailureReason> = {
  401: 'unauthorized',
  403: 'forbidden',
  404: 'not_found',
};

function failure(status: number): { ok: false; reason: FailureReason } {
  return { ok: false, reason: REASONS[status] ?? 'unavailable' };
}

/** The one place a bearer token meets a request. A network error is `unavailable`. */
async function authedFetch(
  fetcher: typeof fetch,
  token: string,
  path: string,
  init: RequestInit,
): Promise<Response | null> {
  try {
    return await fetcher(`${SERVICE_URL}${path}`, {
      ...init,
      headers: { ...init.headers, authorization: `Bearer ${token}` },
    });
  } catch {
    return null;
  }
}

/** One authenticated JSON call to `ai-service`. */
export async function callService(
  fetcher: typeof fetch,
  token: string,
  path: string,
  init: RequestInit = {},
): Promise<ServiceResult<unknown>> {
  const response = await authedFetch(fetcher, token, path, init);
  if (!response) return { ok: false, reason: 'unavailable' };
  if (!response.ok) return failure(response.status);

  try {
    return { ok: true, data: await response.json() };
  } catch {
    return { ok: false, reason: 'unavailable' };
  }
}

/**
 * One authenticated Server-Sent Events call, read with `fetch` because `EventSource`
 * cannot send the bearer header (ADR-0012). Yields events until the server closes.
 */
export async function* streamService(
  fetcher: typeof fetch,
  token: string,
  path: string,
  init: RequestInit = {},
): AsyncGenerator<ServiceEvent, FailureReason | null> {
  const response = await authedFetch(fetcher, token, path, init);
  if (!response) return 'unavailable';
  if (!response.ok || !response.body) return failure(response.status).reason;

  const parse = createSseParser();
  const decoder = new TextDecoder();
  const reader = response.body.getReader();
  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) return null;
      yield* parse(decoder.decode(value, { stream: true }));
    }
  } catch {
    return 'unavailable';
  }
}
