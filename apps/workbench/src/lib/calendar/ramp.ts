import type { Theme } from '@/lib/theme';

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

export function seqColor(t: number, theme: Theme): string {
  const value = clamp(t, 0, 1);

  if (theme === 'light') {
    const l = (0.95 - 0.62 * value).toFixed(3);
    const c = (0.04 + 0.14 * value).toFixed(3);
    const h = (90 - 62 * value).toFixed(1);
    return `oklch(${l} ${c} ${h})`;
  }

  const l = (0.25 + 0.68 * value).toFixed(3);
  const c = (0.05 + 0.13 * value).toFixed(3);
  const h = (25 + 65 * value).toFixed(1);
  return `oklch(${l} ${c} ${h})`;
}

export function divColor(z: number, theme: Theme): string {
  const alpha = Math.min(3, Math.abs(z)) / 3;
  const hue = z < 0 ? 255 : 35;

  if (theme === 'light') {
    const l = (0.96 - 0.44 * alpha).toFixed(3);
    const c = (0.005 + 0.15 * alpha).toFixed(3);
    return `oklch(${l} ${c} ${hue})`;
  }

  const l = (0.3 + 0.45 * alpha).toFixed(3);
  const c = (0.01 + 0.14 * alpha).toFixed(3);
  return `oklch(${l} ${c} ${hue})`;
}
