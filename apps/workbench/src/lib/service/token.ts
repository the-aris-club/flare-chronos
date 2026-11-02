export type Claims = { sub: string; name: string | undefined; roles: string[]; exp: number };

/**
 * Reads a bearer token's claims for display only. The signature is never checked here:
 * `ai-service` is the only place a token is validated, so nothing in the Workbench may
 * treat these claims as authorization.
 */
export function decodeClaims(token: string): Claims | null {
  const payload = token.split('.')[1];
  if (!payload) return null;

  try {
    const claims = JSON.parse(Buffer.from(payload, 'base64url').toString('utf8')) as Record<
      string,
      unknown
    >;
    if (typeof claims.sub !== 'string' || claims.sub === '') return null;

    return {
      sub: claims.sub,
      name: typeof claims.name === 'string' ? claims.name : undefined,
      roles: Array.isArray(claims.roles)
        ? claims.roles.filter((role): role is string => typeof role === 'string')
        : [],
      exp: typeof claims.exp === 'number' ? claims.exp : 0,
    };
  } catch {
    return null;
  }
}
