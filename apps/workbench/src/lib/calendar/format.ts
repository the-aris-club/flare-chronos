export function formatHfd(value: number, locale: string): string {
  const options: Intl.NumberFormatOptions =
    value > 0 && value < 1
      ? { maximumSignificantDigits: 2 }
      : { maximumFractionDigits: value >= 10 ? 0 : 2 };

  return new Intl.NumberFormat(locale, options).format(value);
}

export function formatSigma(value: number, locale: string): string {
  const formatted = new Intl.NumberFormat(locale, {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
    signDisplay: 'exceptZero',
  }).format(value);

  return formatted.replace('-', '−');
}
