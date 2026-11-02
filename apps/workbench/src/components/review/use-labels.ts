'use client';

import { useTranslations } from 'next-intl';

/** `UC-2.2` is not a valid message key (dots nest), so identifiers are normalised. */
const messageKey = (id: string) => id.replace(/[^A-Za-z0-9]/g, '_');

/**
 * Labels for the identifiers the service returns, read from the message catalogs so they
 * follow the EN/VI term table. Run content itself (briefing, fact text) is never translated.
 */
export function useLabels() {
  const review = useTranslations('Review');
  const regions = useTranslations('Header.regions');

  return {
    reason: (code: string) =>
      review.has(`reasons.${code}`) ? review(`reasons.${code}`) : code || '—',
    useCase: (id: string) =>
      review.has(`useCases.${messageKey(id)}`) ? review(`useCases.${messageKey(id)}`) : '',
    region: (region: string | undefined) =>
      region && regions.has(region) ? regions(region) : (region ?? '—'),
  };
}
