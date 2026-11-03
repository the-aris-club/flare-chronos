import { describe, expect, test } from 'bun:test';
import { pentadDates } from '@/lib/calendar/pentad';
import { formatCompact, formatEpochDate, formatEpochDays, formatEpochRange } from './format';

describe('Vietnamese dates and counts', () => {
  test('epoch dates use dd/MM', () => {
    expect(formatEpochDate('2025-03-15', 'vi')).toBe('15/03');
    expect(formatEpochDays('2025-03-15', 'vi')).toBe('15–19/03');
    expect(formatEpochRange('2025-02-27', 'vi')).toBe('27/02 – 03/03');
  });

  test('pentad dates use dd/MM', () => {
    expect(pentadDates(1, 'vi')).toBe('01/01–05/01');
  });

  test('thousands keep k, not the latitude letter N', () => {
    expect(formatCompact(15_400, 'vi')).toBe('15,4k');
  });
});
