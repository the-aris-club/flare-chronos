export type Claims = { sub: string; name: string | undefined; roles: string[]; exp: number };

/** `Buffer` is Node-only; a browser has `atob` and `TextDecoder`. */
function base64UrlToText(value: string): string {
  const binary = atob(value.replaceAll('-', '+').replaceAll('_', '/'));
  return new TextDecoder().decode(Uint8Array.from(binary, (char) => char.charCodeAt(0)));
}

/**
 * Reads a bearer token's claims for display only. The signature is never checked here:
 * `ai-service` is the only place a token is validated, so nothing in the Workbench may
 * treat these claims as authorization.
 */
export function decodeClaims(token: string): Claims | null {
  // `fc-dev-<jwt>` / `fc-examiner-<jwt>`: the prefix is a label, the JWT is the credential.
  const payload = token.replace(/^fc-(?:dev|examiner)-/, '').split('.')[1];
  if (!payload) return null;

  try {
    const claims = JSON.parse(base64UrlToText(payload)) as Record<string, unknown>;
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
