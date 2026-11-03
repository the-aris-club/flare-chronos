export const THEME_COOKIE = 'fc-theme';
export const COOKIE_MAX_AGE = 60 * 60 * 24 * 365;

export type Theme = 'dark' | 'light';

export const DEFAULT_THEME: Theme = 'dark';

export function isTheme(value: string | undefined): value is Theme {
  return value === 'dark' || value === 'light';
}
