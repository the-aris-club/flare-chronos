'use client';

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import { parseRunList, type ReviewRow } from '@/lib/review/api';
import {
  callService,
  streamService,
  type FailureReason,
  type ServiceResult,
} from '@/lib/service/client';
import type { ServiceEvent } from '@/lib/service/sse';
import { CLEAR_TOKEN_COOKIE, readTokenCookie, saveTokenCookie } from '@/lib/service/cookie';
import { decodeClaims, type Claims } from '@/lib/service/token';

export type Connection = 'none' | 'checking' | 'connected' | 'rejected' | 'unavailable';
export type Decision = { approved: boolean; reasonCode: string; reason: string };

type ServiceValue = {
  connection: Connection;
  claims: Claims | null;
  /** The service decides; this only hides a button the service would refuse. */
  isApprover: boolean;
  connect: (token: string) => Promise<void>;
  disconnect: () => void;
  rows: ReviewRow[];
  rowsFailure: FailureReason | 'malformed' | null;
  needsDecision: number;
  refresh: () => Promise<void>;
  get: (path: string) => Promise<ServiceResult<unknown>>;
  stream: (path: string, init?: RequestInit) => AsyncGenerator<ServiceEvent, FailureReason | null>;
  decide: (runId: string, decision: Decision) => Promise<FailureReason | null>;
};

const ServiceContext = createContext<ServiceValue | null>(null);

/** The pasted bearer token is kept in memory and in a `fc_token` cookie (ADR-0016). */
export function ServiceProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState('');
  const [connection, setConnection] = useState<Connection>('none');
  const [rows, setRows] = useState<ReviewRow[]>([]);
  const [rowsFailure, setRowsFailure] = useState<ServiceValue['rowsFailure']>(null);
  const tokenRef = useRef('');
  const retryCountRef = useRef(0);
  const retryTimerRef = useRef<number | null>(null);

  const get = useCallback((path: string) => callService(fetch, tokenRef.current, path), []);

  const refresh = useCallback(async () => {
    if (!tokenRef.current) return;
    const result = await get('/api/v1/review/runs');
    if (!result.ok) {
      setRowsFailure(result.reason);
      return;
    }
    try {
      setRows(parseRunList(result.data));
      setRowsFailure(null);
    } catch {
      setRowsFailure('malformed');
    }
  }, [get]);

  const connect = useCallback(
    async (candidate: string) => {
      const value = candidate.trim();
      setConnection('checking');
      const result = await callService(fetch, value, '/api/v1/analysis/use-cases');
      if (!result.ok) {
        if (result.reason === 'unauthorized') document.cookie = CLEAR_TOKEN_COOKIE;
        // An empty token against an auth-required service is not a "rejected
        // token" — it just means nothing was provided yet. Stay neutral.
        if (result.reason === 'unauthorized' && !value) {
          setConnection('none');
          return;
        }
        setConnection(result.reason === 'unauthorized' ? 'rejected' : 'unavailable');
        return;
      }
      retryCountRef.current = 0;
      tokenRef.current = value;
      document.cookie = saveTokenCookie(
        value,
        decodeClaims(value)?.exp ?? 0,
        Date.now(),
        window.location.protocol === 'https:',
      );
      setToken(value);
      setConnection('connected');
      await refresh();
    },
    [refresh],
  );

  const disconnect = useCallback(() => {
    document.cookie = CLEAR_TOKEN_COOKIE;
    tokenRef.current = '';
    setToken('');
    setRows([]);
    setRowsFailure(null);
    setConnection('none');
  }, []);

  const stream = useCallback(
    (path: string, init?: RequestInit) => streamService(fetch, tokenRef.current, path, init),
    [],
  );

  const decide = useCallback(
    async (runId: string, decision: Decision) => {
      const events = stream('/api/v1/analysis/resume', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          thread_id: runId,
          approved: decision.approved,
          reason: decision.reason,
          reason_code: decision.reasonCode,
        }),
      });
      let next = await events.next();
      // eslint-disable-next-line eslint/no-await-in-loop
      while (!next.done) next = await events.next();
      await refresh();
      return next.value;
    },
    [stream, refresh],
  );

  // A reload reconnects with the stored token instead of asking for it again.
  // In the loopback demo (auth disabled) no token is required, so an empty
  // token connects the demo principal when nothing is stored.
  useEffect(() => {
    const stored = readTokenCookie(document.cookie);
    const candidate = stored || '';
    const id = window.setTimeout(() => void connect(candidate), 0);
    return () => window.clearTimeout(id);
  }, [connect]);

  // Auto-retry when the service is unavailable (network blip / cold start).
  // Uses exponential backoff capped at 30s; stops once connected or rejected.
  useEffect(() => {
    if (connection !== 'unavailable') {
      if (retryTimerRef.current) {
        window.clearTimeout(retryTimerRef.current);
        retryTimerRef.current = null;
      }
      return;
    }
    const candidate = tokenRef.current || readTokenCookie(document.cookie) || '';
    const attempt = retryCountRef.current + 1;
    retryCountRef.current = attempt;
    const delay = Math.min(30000, 2000 * 2 ** (attempt - 1));
    retryTimerRef.current = window.setTimeout(() => {
      retryTimerRef.current = null;
      void connect(candidate);
    }, delay);
    return () => {
      if (retryTimerRef.current) {
        window.clearTimeout(retryTimerRef.current);
        retryTimerRef.current = null;
      }
    };
  }, [connection, connect]);

  // Rows go stale while a reviewer reads; keep the queue current without a manual reload.
  useEffect(() => {
    if (connection !== 'connected') return;
    const timer = window.setInterval(() => void refresh(), 15000);
    return () => window.clearInterval(timer);
  }, [connection, refresh]);

  const claims = useMemo(() => (token ? decodeClaims(token) : null), [token]);

  const value = useMemo<ServiceValue>(
    () => ({
      connection,
      claims,
      isApprover: claims?.roles.includes('approver') ?? false,
      connect,
      disconnect,
      rows,
      rowsFailure,
      needsDecision: rows.filter((row) => row.status === 'needs').length,
      refresh,
      get,
      stream,
      decide,
    }),
    [connection, claims, connect, disconnect, rows, rowsFailure, refresh, get, stream, decide],
  );

  return <ServiceContext.Provider value={value}>{children}</ServiceContext.Provider>;
}

export function useService(): ServiceValue {
  const value = useContext(ServiceContext);
  if (!value) throw new Error('useService must be used inside ServiceProvider');
  return value;
}
