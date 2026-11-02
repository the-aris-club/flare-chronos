/** Reason Codes the service accepts on a Sign-off Decision (see `ReasonCode` in ai-service). */
export const REASONS = [
  { value: 'evidence', en: 'Evidence confirmed', vi: 'Dữ liệu kiểm chứng đã xác nhận' },
  { value: 'stale', en: 'Stale data', vi: 'Dữ liệu lỗi thời' },
  { value: 'duplicate', en: 'Duplicate alert', vi: 'Cảnh báo trùng lặp' },
  { value: 'conflict', en: 'Evidence conflict', vi: 'Dữ liệu kiểm chứng mâu thuẫn' },
  { value: 'authority', en: 'Outside authority', vi: 'Ngoài thẩm quyền' },
  { value: 'degraded', en: 'Service degraded', vi: 'Dịch vụ suy giảm' },
  { value: 'other', en: 'Other', vi: 'Khác' },
] as const;

export function reasonLabel(code: string, locale: string): string {
  const reason = REASONS.find((item) => item.value === code);
  if (!reason) return code || '—';
  return locale === 'vi' ? reason.vi : reason.en;
}
