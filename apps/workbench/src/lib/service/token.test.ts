import { describe, expect, test } from 'bun:test';
import { decodeClaims } from './token';

function jwt(payload: object): string {
  const part = (value: object) => Buffer.from(JSON.stringify(value)).toString('base64url');
  return `${part({ alg: 'HS256', typ: 'JWT' })}.${part(payload)}.signature`;
}

describe('decodeClaims', () => {
  test('reads the subject, name, roles and expiry for display', () => {
    const claims = decodeClaims(
      jwt({ sub: 'ana', name: 'Ana Nguyen', roles: ['approver'], exp: 1893456000 }),
    );

    expect(claims).toEqual({
      sub: 'ana',
      name: 'Ana Nguyen',
      roles: ['approver'],
      exp: 1893456000,
    });
  });

  test('a token without a name or roles still has a subject and no roles', () => {
    expect(decodeClaims(jwt({ sub: 'bob', exp: 1 }))).toEqual({
      sub: 'bob',
      name: undefined,
      roles: [],
      exp: 1,
    });
  });

  test('decodes in a browser, where Node\'s Buffer does not exist, including non-ASCII names', () => {
    const token = jwt({ sub: 'mai', name: 'Nguyễn Thị Mai', roles: ['approver'], exp: 2 });
    const original = globalThis.Buffer;
    // @ts-expect-error simulate a browser global scope
    globalThis.Buffer = undefined;
    try {
      expect(decodeClaims(token)?.name).toBe('Nguyễn Thị Mai');
    } finally {
      globalThis.Buffer = original;
    }
  });

  test('text that is not a token, or has no subject, is not claims', () => {
    expect(decodeClaims('not-a-token')).toBeNull();
    expect(decodeClaims(jwt({ exp: 1 }))).toBeNull();
    expect(decodeClaims('a.%%%.c')).toBeNull();
  });
});
