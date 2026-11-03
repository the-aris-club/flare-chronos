'use client';

import { ThemeProvider as NextThemesProvider, useTheme as useNextTheme } from 'next-themes';
import type { Theme } from '@/lib/theme';

const THEMES = ['dark', 'light'];

export function ThemeProvider({
  initialTheme,
  children,
}: {
  initialTheme: Theme;
  children: React.ReactNode;
}) {
  return (
    <NextThemesProvider
      attribute="data-theme"
      defaultTheme={initialTheme}
      enableSystem={false}
      disableTransitionOnChange
      themes={THEMES}
      storageKey="fc-theme"
    >
      {children}
    </NextThemesProvider>
  );
}

export function useTheme(): { theme: Theme; setTheme: (theme: Theme) => void } {
  const { theme: rawTheme, resolvedTheme, setTheme: setNextTheme } = useNextTheme();

  const theme: Theme =
    rawTheme === 'light' || rawTheme === 'dark'
      ? rawTheme
      : resolvedTheme === 'light'
        ? 'light'
        : 'dark';

  return {
    theme,
    setTheme: (next: Theme) => setNextTheme(next),
  };
}
