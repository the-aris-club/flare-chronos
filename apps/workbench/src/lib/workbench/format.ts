export function formatEpochDate(date: string | null, locale: string): string {
  if (!date) return '—';

  const [year, month, day] = date.split('-').map(Number);
  if (locale === 'vi') return `${pad2(day)}/${pad2(month)}`;
  return new Intl.DateTimeFormat(locale, {
    day: 'numeric',
    month: 'short',
    timeZone: 'UTC',
  }).format(new Date(Date.UTC(year, month - 1, day)));
}

export function formatEpochRange(date: string | null, locale: string, days = 5): string {
  if (!date) return '—';
  const [year, month, day] = date.split('-').map(Number);
  const start = new Date(Date.UTC(year, month - 1, day));
  const end = new Date(start.getTime() + (days - 1) * 86_400_000);
  if (locale === 'vi') {
    return `${pad2(start.getUTCDate())}/${pad2(start.getUTCMonth() + 1)} – ${pad2(end.getUTCDate())}/${pad2(end.getUTCMonth() + 1)}`;
  }
  const dayFmt = new Intl.DateTimeFormat(locale, { day: 'numeric', timeZone: 'UTC' });
  const monthFmt = new Intl.DateTimeFormat(locale, { month: 'short', timeZone: 'UTC' });
  const startMonth = monthFmt.format(start);
  const endMonth = monthFmt.format(end);
  return startMonth === endMonth
    ? `${startMonth} ${dayFmt.format(start)}–${dayFmt.format(end)}`
    : `${startMonth} ${dayFmt.format(start)}–${endMonth} ${dayFmt.format(end)}`;
}

export function formatEpochDays(date: string | null, locale: string, days = 5): string {
  if (!date) return '—';
  const [year, month, day] = date.split('-').map(Number);
  const start = new Date(Date.UTC(year, month - 1, day));
  const end = new Date(start.getTime() + (days - 1) * 86_400_000);
  if (locale === 'vi') {
    const startMonth = pad2(start.getUTCMonth() + 1);
    const endMonth = pad2(end.getUTCMonth() + 1);
    return startMonth === endMonth
      ? `${pad2(start.getUTCDate())}–${pad2(end.getUTCDate())}/${startMonth}`
      : `${pad2(start.getUTCDate())}/${startMonth}–${pad2(end.getUTCDate())}/${endMonth}`;
  }
  const fmt = new Intl.DateTimeFormat(locale, { day: 'numeric', timeZone: 'UTC' });
  return `${fmt.format(start)}–${fmt.format(end)}`;
}

function pad2(value: number): string {
  return String(value).padStart(2, '0');
}

export function formatCount(value: number, locale: string): string {
  return new Intl.NumberFormat(locale, { maximumFractionDigits: 0 }).format(value);
}

export function formatPercent(value: number, locale: string, digits = 0): string {
  return new Intl.NumberFormat(locale, {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
    signDisplay: 'exceptZero',
  }).format(value);
}

export function formatCompact(value: number, locale: string): string {
  if (locale === 'vi' && Math.abs(value) >= 1000) {
    const scaled = Math.abs(value) >= 1_000_000 ? value / 1_000_000 : value / 1000;
    const suffix = Math.abs(value) >= 1_000_000 ? 'tr' : 'k';
    return `${new Intl.NumberFormat('vi', { maximumFractionDigits: 1 }).format(scaled)}${suffix}`;
  }
  return new Intl.NumberFormat(locale, {
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(value);
}

export function formatDecimal(value: number, locale: string, digits = 2): string {
  return new Intl.NumberFormat(locale, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value);
}

export function localized<T>(locale: string, en: T, vi: T): T {
  return locale === 'vi' ? vi : en;
}

export function isVi(locale: string): boolean {
  return locale === 'vi';
}
