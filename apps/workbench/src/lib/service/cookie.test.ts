import { describe, expect, test } from 'bun:test';
import { CLEAR_TOKEN_COOKIE, readTokenCookie, saveTokenCookie } from './cookie';

const NOW = 1_800_000_000_000;

describe('token cookie', () => {
  test('what is saved is what is read back, among other cookies', () => {
    const token = 'fc-dev-aaa.bbb.ccc';
    const saved = saveTokenCookie(token, NOW / 1000 + 3600, NOW, false).split(';')[0];

    expect(readTokenCookie(`theme=dark; ${saved}; locale=vi`)).toBe(token);
  });

  test('lives until the token expires, never longer than 30 days', () => {
    expect(saveTokenCookie('t', NOW / 1000 + 3600, NOW, false)).toContain('Max-Age=3600');
    expect(saveTokenCookie('t', NOW / 1000 + 90 * 86400, NOW, false)).toContain(
      `Max-Age=${30 * 86400}`,
    );
    expect(saveTokenCookie('t', NOW / 1000 - 5, NOW, false)).toContain('Max-Age=0');
  });

  test('is same-site strict, and secure only over https', () => {
    expect(saveTokenCookie('t', NOW / 1000 + 60, NOW, false)).not.toContain('Secure');
    const secure = saveTokenCookie('t', NOW / 1000 + 60, NOW, true);
    expect(secure).toContain('SameSite=Strict');
    expect(secure).toContain('; Secure');
  });

  test('no cookie reads as no token, and the clearing cookie expires at once', () => {
    expect(readTokenCookie('theme=dark')).toBe('');
    expect(CLEAR_TOKEN_COOKIE).toContain('Max-Age=0');
  });
});
