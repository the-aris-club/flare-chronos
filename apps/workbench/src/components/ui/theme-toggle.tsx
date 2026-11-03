'use client';

import { useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { Icon, ICON } from '@/components/ui/icon';
import { useTheme } from '@/components/ui/theme-provider';
import { writeCookie } from '@/lib/browser';
import { THEME_COOKIE } from '@/lib/theme';

export function ThemeToggle() {
  const t = useTranslations('Header');
  const { theme, setTheme } = useTheme();
  const next = theme === 'dark' ? 'light' : 'dark';
  const label = t(next === 'dark' ? 'themeToDark' : 'themeToLight');

  const handleClick = useCallback(() => {
    setTheme(next);
    writeCookie(THEME_COOKIE, next);
  }, [setTheme, next]);

  return (
    <button
      type="button"
      onClick={handleClick}
      aria-label={label}
      title={label}
      className="border-line-strong text-ink-muted hover:bg-chip hover:text-ink inline-flex size-8 items-center justify-center rounded-md border transition-colors"
    >
      <Icon icon={ICON.theme} size="sm" />
    </button>
  );
}
