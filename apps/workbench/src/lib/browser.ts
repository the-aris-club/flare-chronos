'use client';

import { COOKIE_MAX_AGE } from './theme';

export function writeCookie(name: string, value: string): void {
  document.cookie = `${name}=${value};path=/;max-age=${COOKIE_MAX_AGE};samesite=lax`;
}

export function applyTheme(theme: string): void {
  document.documentElement.dataset.theme = theme;
}
