import { describe, expect, test } from 'bun:test';
import { formatQueryBox } from './query-box';

describe('formatQueryBox', () => {
  test('writes latitude then longitude with hemisphere letters, in English', () => {
    expect(formatQueryBox([-62, -14, -50, -4], 'en')).toBe('14°S–4°S · 62–50°W');
  });

  test('uses the Vietnamese decimal comma and west letter', () => {
    expect(formatQueryBox([100, 8.5, 109.5, 23.5], 'vi')).toBe('8,5°N–23,5°N · 100–109,5°Đ');
  });
});
