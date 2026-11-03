'use client';

import { createContext, useContext, useEffect, useMemo, useRef, useState, useCallback } from 'react';
import { usePathname } from 'next/navigation';
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

export function LoadingProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [visible, setVisible] = useState(true);
  const [steps, setSteps] = useState<BootStep[]>(DEFAULT_STEPS);
  const [done, setDone] = useState<BootStep[]>([]);
  const startedAt = useRef<number>(0);
  const fallbackTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearFallback = useCallback(() => {
    if (fallbackTimer.current) {
      clearTimeout(fallbackTimer.current);
      fallbackTimer.current = null;
    }
  }, []);

  const start = useCallback(
    (nextSteps?: BootStep[]) => {
      clearFallback();
      if (nextSteps) setSteps(nextSteps);
      setDone([]);
      startedAt.current = performance.now();
      setVisible(true);
      fallbackTimer.current = setTimeout(() => {
        setSteps((current) => {
          setDone(current);
          return current;
        });
      }, 15000);
    },
    [clearFallback],
  );

  const register = useCallback(
    (nextSteps: BootStep[]) => {
      clearFallback();
      setSteps(nextSteps);
      setDone([]);
      setVisible(true);
      startedAt.current = performance.now();
      fallbackTimer.current = setTimeout(() => {
        setSteps((current) => {
          setDone(current);
          return current;
        });
      }, 15000);
    },
    [clearFallback],
  );

  const mark = useCallback((step: BootStep) => {
    setDone((prev) => (prev.includes(step) ? prev : [...prev, step]));
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react/set-state-in-effect
    start();
    // eslint-disable-next-line react/exhaustive-effect-dependencies
  }, [pathname, start]);

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
