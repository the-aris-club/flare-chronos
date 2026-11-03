'use client';

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
} from 'react';
import { BootOverlay } from '@/components/globe/boot-overlay';
import type { BootStep } from '@/lib/globe/types';

type LoadingApi = {
  steps: BootStep[];
  done: BootStep[];
  visible: boolean;
  register: (steps: BootStep[]) => void;
  mark: (step: BootStep) => void;
  start: (steps?: BootStep[]) => void;
};

const Ctx = createContext<LoadingApi | null>(null);

export function useLoading(): LoadingApi {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error('useLoading must be used within LoadingProvider');
  return ctx;
}

const DEFAULT_STEPS: BootStep[] = ['fonts', 'page'];
const HARD_CAP_MS = 15000;

export function LoadingProvider({ children }: { children: React.ReactNode }) {
  const [visible, setVisible] = useState(false);
  const [steps, setSteps] = useState<BootStep[]>(DEFAULT_STEPS);
  const [done, setDone] = useState<BootStep[]>([]);
  const fallbackTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const stepsRef = useRef<BootStep[]>(DEFAULT_STEPS);

  const clearFallback = useCallback(() => {
    if (fallbackTimer.current) {
      clearTimeout(fallbackTimer.current);
      fallbackTimer.current = null;
    }
  }, []);

  const begin = useCallback(
    (nextSteps: BootStep[]) => {
      clearFallback();
      stepsRef.current = nextSteps;
      setSteps(nextSteps);
      setDone([]);
      setVisible(true);
      fallbackTimer.current = setTimeout(() => setDone(nextSteps), HARD_CAP_MS);
    },
    [clearFallback],
  );

  const register = useCallback((nextSteps: BootStep[]) => begin(nextSteps), [begin]);

  const start = useCallback(
    (nextSteps?: BootStep[]) => begin(nextSteps ?? stepsRef.current),
    [begin],
  );

  const mark = useCallback((step: BootStep) => {
    setDone((prev) => (prev.includes(step) ? prev : [...prev, step]));
  }, []);

  const handleDone = useCallback(() => {
    clearFallback();
    setVisible(false);
  }, [clearFallback]);

  const value = useMemo<LoadingApi>(
    () => ({ steps, done, visible, register, mark, start }),
    [steps, done, visible, register, mark, start],
  );

  return (
    <Ctx.Provider value={value}>
      {children}
      {visible && <BootOverlay steps={steps} done={done} onDone={handleDone} />}
    </Ctx.Provider>
  );
}
