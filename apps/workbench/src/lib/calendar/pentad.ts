const MONTH_STARTS = [1, 7, 12, 19, 25, 31, 37, 43, 49, 55, 61, 67];

const REFERENCE_YEAR = 2023;
const DAYS_IN_YEAR = 365;

const dateFormat = new Map<string, Intl.DateTimeFormat>();

function formatter(locale: string): Intl.DateTimeFormat {
  const cached = dateFormat.get(locale);
  if (cached) return cached;

  const created = new Intl.DateTimeFormat(locale, {
    day: 'numeric',
    month: 'short',
    timeZone: 'UTC',
  });
  dateFormat.set(locale, created);
  return created;
}

function dayOfYearToLabel(dayOfYear: number, locale: string): string {
  if (locale === 'vi') {
    const date = new Date(Date.UTC(REFERENCE_YEAR, 0, dayOfYear));
    return `${String(date.getUTCDate()).padStart(2, '0')}/${String(date.getUTCMonth() + 1).padStart(2, '0')}`;
  }
  return formatter(locale).format(new Date(Date.UTC(REFERENCE_YEAR, 0, dayOfYear)));
}

export function monthIndexAt(pentadIndex: number): number | null {
  const index = MONTH_STARTS.indexOf(pentadIndex + 1);

  return index === -1 ? null : index;
}

export function pentadDates(pentad: number, locale: string): string {
  const first = (pentad - 1) * 5 + 1;
  const last = Math.min(pentad * 5, DAYS_IN_YEAR);

  return `${dayOfYearToLabel(first, locale)}–${dayOfYearToLabel(last, locale)}`;
}
