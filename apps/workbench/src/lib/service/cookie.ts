/** The bearer token is kept in a cookie so a reload does not ask for it again. */
export const TOKEN_COOKIE = 'fc_token';

const MAX_AGE_CAP_S = 30 * 24 * 3600;

/**
 * The `document.cookie` assignment that stores `token` until it expires. Strict, because
 * only this origin ever reads it; Secure whenever the page itself is served over https.
 * It is script-readable (the browser calls `ai-service` directly), so it is no safer than
 * the page's own scripts; the token expiry is the real bound.
 */
export function saveTokenCookie(token: string, exp: number, now: number, secure: boolean): string {
  const left = exp > 0 ? Math.floor(exp - now / 1000) : MAX_AGE_CAP_S;
  const maxAge = Math.max(0, Math.min(left, MAX_AGE_CAP_S));
  return `${TOKEN_COOKIE}=${encodeURIComponent(token)}; Path=/; Max-Age=${maxAge}; SameSite=Strict${secure ? '; Secure' : ''}`;
}

export const CLEAR_TOKEN_COOKIE = `${TOKEN_COOKIE}=; Path=/; Max-Age=0; SameSite=Strict`;

/** The stored token out of a `document.cookie` string, or '' when there is none. */
export function readTokenCookie(cookies: string): string {
  for (const part of cookies.split(';')) {
    const [name, ...value] = part.trim().split('=');
    if (name === TOKEN_COOKIE) return decodeURIComponent(value.join('='));
  }
  return '';
}
