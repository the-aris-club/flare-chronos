import { useEffect } from 'react';
import { useLoading } from '@/components/ui/loading-provider';
import type { BootStep } from '@/lib/globe/types';

/**
 * Register this page's boot steps with the shared overlay and mark the ones the
 * hook can observe. `steps` must be a stable array (module-level constant): the
 * effect keys on it, so an inline literal would re-register on every render and
 * reset the progress to zero.
 */
export function usePageBoot(steps: BootStep[]) {
  const { register, mark } = useLoading();

  useEffect(() => {
    register(steps);

    let cancelled = false;
    const frame = requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        if (!cancelled) mark('page');
      });
    });

    void document.fonts.ready.then(() => {
      if (!cancelled) mark('fonts');
    });

    // Steps this page does not observe directly settle shortly after paint.
    const timer = window.setTimeout(() => {
      if (cancelled) return;
      for (const step of steps) {
        if (step !== 'fonts' && step !== 'page') mark(step);
      }
    }, 800);

    // Hard cap: never leave the overlay up.
    const fallback = window.setTimeout(() => {
      if (!cancelled) for (const step of steps) mark(step);
    }, 15000);

    return () => {
      cancelled = true;
      cancelAnimationFrame(frame);
      window.clearTimeout(timer);
      window.clearTimeout(fallback);
    };
  }, [steps, register, mark]);
}
