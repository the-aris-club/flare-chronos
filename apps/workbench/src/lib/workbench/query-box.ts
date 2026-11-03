import type { BBox } from './regions';

/** The box FIRMS was queried with, as a short caption: latitude range, then longitude range. */
export function formatQueryBox(box: BBox, locale: string): string {
  const [west, south, east, north] = box;
  const number = new Intl.NumberFormat(locale, { maximumFractionDigits: 1 });
  const vi = locale.startsWith('vi');
  const eastLetter = vi ? 'Đ' : 'E';
  const westLetter = vi ? 'T' : 'W';
  const lat = (value: number) => `${number.format(Math.abs(value))}°${value < 0 ? 'S' : 'N'}`;
  const lonLetter = (value: number) => (value < 0 ? westLetter : eastLetter);

  const lonStart = number.format(Math.abs(west));
  const lonEnd = number.format(Math.abs(east));
  const letter = lonLetter(east);

  return `${lat(south)}–${lat(north)} · ${lonStart}–${lonEnd}°${letter}`;
}
