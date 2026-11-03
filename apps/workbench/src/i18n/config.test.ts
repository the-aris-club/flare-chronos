import { describe, expect, test } from 'bun:test';
import { defaultLocale, isLocale, locales, LOCALE_COOKIE } from './config';

describe('i18n config', () => {
  test('locales contains en and vi', () => {
    expect(locales).toEqual(['en', 'vi']);
  });

  test('defaultLocale is en', () => {
    expect(defaultLocale).toBe('en');
  });

  test('LOCALE_COOKIE is set', () => {
    expect(LOCALE_COOKIE).toBe('fc-locale');
  });

  test('isLocale accepts valid locales', () => {
    expect(isLocale('en')).toBe(true);
    expect(isLocale('vi')).toBe(true);
  });

  test('isLocale rejects invalid values', () => {
    expect(isLocale(undefined)).toBe(false);
    expect(isLocale('fr')).toBe(false);
    expect(isLocale('')).toBe(false);
  });
});
