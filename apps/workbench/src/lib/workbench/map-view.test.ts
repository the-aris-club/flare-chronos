import { describe, expect, test } from 'bun:test';
import { markerScale } from './map-view';

describe('markerScale', () => {
  test('is 1 zoomed out, grows with zoom, and stops at 2.4 from 8x', () => {
    expect(markerScale(1)).toBe(1);
    expect(markerScale(2)).toBeGreaterThan(1);
    expect(markerScale(4)).toBeGreaterThan(markerScale(2));
    expect(markerScale(8)).toBeCloseTo(2.4, 5);
    expect(markerScale(64)).toBeCloseTo(2.4, 5);
  });
});
