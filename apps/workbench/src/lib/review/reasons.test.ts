import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'node:fs';
import { REASON_CODES } from './reasons';

describe('REASON_CODES', () => {
  test('are exactly the reason codes the service publishes in its OpenAPI contract', () => {
    const contract = JSON.parse(
      readFileSync(new URL('../../../../../docs/openapi/ai-service.json', import.meta.url), 'utf8'),
    );
    const published = contract.components.schemas.ResumeRequest.properties.reason_code;
    const codes = (published.anyOf ?? [published]).flatMap((node: { enum?: string[] }) => node.enum ?? []);

    expect([...REASON_CODES].sort()).toEqual(codes.sort());
  });
});
