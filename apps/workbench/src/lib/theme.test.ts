import { describe, expect, test } from 'bun:test';
import { DEFAULT_THEME, isTheme, THEME_COOKIE, type Theme } from './theme';

describe('theme config', () => {
  test('THEME_COOKIE is set', () => {
    expect(THEME_COOKIE).toBe('fc-theme');
  });

  test('DEFAULT_THEME is dark', () => {
    expect(DEFAULT_THEME).toBe('dark');
  });

  test('isTheme accepts valid themes', () => {
    expect(isTheme('dark')).toBe(true);
    expect(isTheme('light')).toBe(true);
  });

  test('isTheme rejects invalid values', () => {
    expect(isTheme(undefined)).toBe(false);
    expect(isTheme('system')).toBe(false);
    expect(isTheme('')).toBe(false);
  });

  test('Theme type covers dark and light', () => {
    const values: Theme[] = ['dark', 'light'];
    expect(values).toHaveLength(2);
  });
});
