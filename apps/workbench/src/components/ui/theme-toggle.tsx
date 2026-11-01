'use client';

import { useTranslations } from 'next-intl';
import { AmIcon, ICON } from '@/components/ui/icon';
import { useTheme } from '@/components/ui/theme-provider';

export function ThemeToggle() {
  const t = useTranslations('Header');
  const { theme, setTheme } = useTheme();
  const next = theme === 'dark' ? 'light' : 'dark';
  const label = t(next === 'dark' ? 'themeToDark' : 'themeToLight');

  return (
    <button
      type="button"
      onClick={() => setTheme(next)}
      aria-label={label}
      title={label}
      className="border-line-strong text-ink-muted hover:bg-chip hover:text-ink inline-flex size-8 items-center justify-center rounded-md border transition-colors"
    >
      <AmIcon icon={ICON.theme} size="sm" />
    </button>
  );
}
