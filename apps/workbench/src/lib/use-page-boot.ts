import { useEffect } from 'react';
import { useLoading } from '@/components/ui/loading-provider';
import type { BootStep } from '@/lib/globe/types';

export function usePageBoot(steps: BootStep[]) {
  const loading = useLoading();

  useEffect(() => {
    loading.register(steps);

    let cancelled = false;
    const mark = loading.mark;

    document.fonts.ready.then(() => {
      if (!cancelled) mark('fonts');
    });

    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        if (!cancelled) mark('page');
      });
    });

    const remaining = steps.filter((step) => step !== 'fonts' && step !== 'page');
    const timer = window.setTimeout(() => {
      if (cancelled) return;
      remaining.forEach((step) => mark(step));
    }, 800);

    const fallback = window.setTimeout(() => {
      if (cancelled) return;
      steps.forEach((step) => mark(step));
    }, 15000);

    return () => {
      cancelled = true;
      window.clearTimeout(timer);
      window.clearTimeout(fallback);
    };
  }, [steps, loading]);
}
