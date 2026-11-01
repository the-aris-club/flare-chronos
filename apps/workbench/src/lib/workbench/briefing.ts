export type VerifyResult = { ok: true } | { ok: false; reason: 'empty' | 'rejected' };

// TODO(api): briefing connect — replace this local check with the
// POST /api/v1/analysis/stream handshake and the run stream; the run state in
// components/workbench/briefing-run.tsx must be replaced by that response.
export function verifyToken(token: string): VerifyResult {
  const value = token.trim();
  if (value.length === 0) {
    return { ok: false, reason: 'empty' };
  }
  if (value.length < 16) {
    return { ok: false, reason: 'rejected' };
  }

  return { ok: true };
}
