import { describe, expect, test } from 'bun:test';
import en from './messages/en.json';
import vi from './messages/vi.json';

function keys(value: unknown, prefix = ''): string[] {
  if (!value || typeof value !== 'object') return [];
  return Object.entries(value).flatMap(([key, child]) => [
    `${prefix}${key}`,
    ...keys(child, `${prefix}${key}.`),
  ]);
}

describe('message catalogs', () => {
  test('EN and VI have the same key set', () => {
    expect(keys(vi).sort()).toEqual(keys(en).sort());
  });

  test('no empty values', () => {
    for (const [locale, catalog] of [
      ['en', en],
      ['vi', vi],
    ] as const) {
      const empty = keys(catalog).filter((key) => {
        const value = key.split('.').reduce<unknown>((node, part) => {
          if (!node || typeof node !== 'object') return undefined;
          return (node as Record<string, unknown>)[part];
        }, catalog);
        return typeof value === 'string' && value.trim() === '';
      });
      expect({ locale, empty }).toEqual({ locale, empty: [] });
    }
  });
});
