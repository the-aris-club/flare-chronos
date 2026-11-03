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
import {
  INITIAL_DECISIONS,
  type Decision,
  type DecisionKind,
  type ReviewRun,
} from '@/data/fixtures/review';
import { REVIEW_RUNS } from '@/data/fixtures/review-runs';
import { makeDecision } from '@/lib/review/decision';
import { submitDecision } from '@/lib/review/submit-decision';

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
  /** Set when the last decision could not be persisted and was rolled back. */
  saveFailed: boolean;
  dismissSaveFailed: () => void;
};

const ReviewStoreContext = createContext<ReviewStoreValue | null>(null);

export function ReviewStoreProvider({ children }: { children: React.ReactNode }) {
  const [decisions, setDecisions] = useState<Record<string, Decision>>(INITIAL_DECISIONS);
  const [saveFailed, setSaveFailed] = useState(false);
  const decisionsRef = useRef(decisions);
  useEffect(() => {
    decisionsRef.current = decisions;
  }, [decisions]);

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
    const current = decisionsRef.current;
    if (current[id]) return;
    const optimistic = makeDecision(kind, reason, note, Object.values(current));
    decisionsRef.current = { ...current, [id]: optimistic };
    setDecisions((latest) => (latest[id] ? latest : { ...latest, [id]: optimistic }));
    setSaveFailed(false);

    void submitDecision(fetch, id, kind, reason, note).then((result) => {
      if (result.ok) {
        setDecisions((latest) => ({ ...latest, [id]: result.decision }));
        return;
      }
      setDecisions((latest) => {
        const { [id]: _rolledBack, ...rest } = latest;
        return rest;
      });
      setSaveFailed(true);
    });
  }, []);

  const dismissSaveFailed = useCallback(() => setSaveFailed(false), []);

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
      saveFailed,
      dismissSaveFailed,
    };
  }, [decisions, record, saveFailed, dismissSaveFailed]);

  return <ReviewStoreContext.Provider value={value}>{children}</ReviewStoreContext.Provider>;
}

export function useReviewStore(): ReviewStoreValue {
  const value = useContext(ReviewStoreContext);
  if (!value) throw new Error('useReviewStore must be used inside ReviewStoreProvider');
  return value;
}
