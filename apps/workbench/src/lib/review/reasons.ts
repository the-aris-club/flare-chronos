/**
 * Reason Codes the service accepts on a Sign-off Decision. The list must equal the
 * `reason_code` enum in `docs/openapi/ai-service.json` (checked by `reasons.test.ts`);
 * their labels live in the message catalogs under `Review.reasons`.
 */
export const REASON_CODES = [
  'evidence',
  'stale',
  'duplicate',
  'conflict',
  'authority',
  'degraded',
  'other',
] as const;
