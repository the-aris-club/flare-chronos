/**
 * Static labels for the identifiers the service returns. Run content (briefing and fact
 * text) is shown as the model wrote it; only these identifiers are translated here.
 */
export const REGION_LABELS: Record<string, { en: string; vi: string }> = {
  mekong: { en: 'Mekong', vi: 'Mê Kông' },
  amazon: { en: 'Amazon', vi: 'Amazon' },
};

export function regionLabel(region: string | undefined, locale: string): string {
  if (!region) return '—';
  const label = REGION_LABELS[region];
  if (!label) return region;
  return locale === 'vi' ? label.vi : label.en;
}

export const USE_CASE_LABELS: Record<string, { en: string; vi: string }> = {
  'UC-S1.4': { en: 'NRT crisis alert', vi: 'Cảnh báo nguy cấp gần thời gian thực' },
  'UC-2.2': { en: 'Footprint to dispatch', vi: 'Từ vết quét đến điều phối' },
};

export function useCaseLabel(id: string, locale: string): string {
  const label = USE_CASE_LABELS[id];
  if (!label) return '';
  return locale === 'vi' ? label.vi : label.en;
}
