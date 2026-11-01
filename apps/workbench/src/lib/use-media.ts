'use client';

import { useSyncExternalStore } from 'react';

const DESKTOP = '(min-width: 1280px)';
const TABLET = '(min-width: 720px)';

function useMedia(query: string): boolean {
  return useSyncExternalStore(
    (onChange) => {
      const media = window.matchMedia(query);
      media.addEventListener('change', onChange);
      return () => media.removeEventListener('change', onChange);
    },
    () => window.matchMedia(query).matches,
    () => false,
  );
}

export function useIsDesktop(): boolean {
  return useMedia(DESKTOP);
}

export function useIsTablet(): boolean {
  return useMedia(TABLET);
}
