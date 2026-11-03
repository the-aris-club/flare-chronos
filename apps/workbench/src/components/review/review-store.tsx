'use client';

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import {
  INITIAL_DECISIONS,
  type Decision,
  type DecisionKind,
  type ReviewRun,
} from '@/data/fixtures/review';
import { REVIEW_RUNS } from '@/data/fixtures/review-runs';
import { makeDecision } from '@/lib/review/decision';

type AuditRow = {
  at: string;
  runId: string;
  reviewer: string;
  role: string;
  audit: string;
  kind: DecisionKind;
  reason: string;
  note: string;
  useCase: string;
};

type ReviewStoreValue = {
  runs: ReviewRun[];
  decisions: Record<string, Decision>;
  decisionsFor: (id: string) => Decision | undefined;
  record: (id: string, kind: DecisionKind, reason: string, note: string) => void;
  needsDecision: number;
  audit: AuditRow[];
};

const ReviewStoreContext = createContext<ReviewStoreValue | null>(null);

export function ReviewStoreProvider({ children }: { children: React.ReactNode }) {
  const [decisions, setDecisions] = useState<Record<string, Decision>>(INITIAL_DECISIONS);

  useEffect(() => {
    let live = true;
    fetch('/api/review/decisions', { cache: 'no-store' })
      .then((response) => (response.ok ? response.json() : null))
      .then((data: { decisions?: Record<string, Decision> } | null) => {
        if (live && data?.decisions) {
          setDecisions((current) => ({ ...current, ...data.decisions }));
        }
      })
      .catch(() => {});
    return () => {
      live = false;
    };
  }, []);

  const record = useCallback((id: string, kind: DecisionKind, reason: string, note: string) => {
    setDecisions((current) => {
      if (current[id]) return current;
      const next = makeDecision(kind, reason, note, Object.values(current));
      void fetch('/api/review/decisions', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ runId: id, kind, reason, note }),
      })
        .then((response) => (response.ok ? response.json() : null))
        .then((data: { decision?: Decision } | null) => {
          if (data?.decision)
            setDecisions((latest) => ({ ...latest, [id]: data.decision as Decision }));
        })
        .catch(() => {});
      return { ...current, [id]: next };
    });
  }, []);

  const value = useMemo<ReviewStoreValue>(() => {
    const audit = Object.entries(decisions)
      .map(([runId, decision]) => {
        const run = REVIEW_RUNS.find((item) => item.id === runId);
        return {
          at: decision.at,
          runId,
          reviewer: decision.reviewer,
          role: decision.role,
          audit: decision.audit,
          kind: decision.kind,
          reason: decision.reason,
          note: decision.note,
          useCase: run?.useCase ?? '—',
        };
      })
      .sort((a, b) => b.at.localeCompare(a.at));

    return {
      runs: REVIEW_RUNS,
      decisions,
      decisionsFor: (id) => decisions[id],
      record,
      needsDecision: REVIEW_RUNS.filter((run) => !decisions[run.id]).length,
      audit,
    };
  }, [decisions, record]);

  return <ReviewStoreContext.Provider value={value}>{children}</ReviewStoreContext.Provider>;
}

export function useReviewStore(): ReviewStoreValue {
  const value = useContext(ReviewStoreContext);
  if (!value) throw new Error('useReviewStore must be used inside ReviewStoreProvider');
  return value;
}
