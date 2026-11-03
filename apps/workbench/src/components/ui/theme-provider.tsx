'use client';

import { createContext, useCallback, useContext, useMemo, useState } from 'react';
import { applyTheme, writeCookie } from '@/lib/browser';
import { THEME_COOKIE, type Theme } from '@/lib/theme';

type ThemeContextValue = {
  theme: Theme;
  setTheme: (theme: Theme) => void;
};

const ThemeContext = createContext<ThemeContextValue | null>(null);

export function ThemeProvider({
  initialTheme,
  children,
}: {
  initialTheme: Theme;
  children: React.ReactNode;
}) {
  const [theme, setThemeState] = useState<Theme>(initialTheme);

  const setTheme = useCallback((next: Theme) => {
    setThemeState(next);
    applyTheme(next);
    writeCookie(THEME_COOKIE, next);
  }, []);

  const value = useMemo(() => ({ theme, setTheme }), [theme, setTheme]);

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme(): ThemeContextValue {
  const value = useContext(ThemeContext);

  if (value === null) {
    throw new Error('useTheme must be used inside ThemeProvider');
  }

  return value;
}
