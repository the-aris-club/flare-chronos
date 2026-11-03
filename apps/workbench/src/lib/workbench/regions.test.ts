import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { REGION_DEFS } from './regions';

const client = readFileSync(
  path.resolve(
    import.meta.dir,
    '../../../../../packages/firms-ingestion/src/firms_ingestion/firms_client.py',
  ),
  'utf8',
);

function ingestionBox(name: string): number[] {
  const match = client.match(new RegExp(`${name} = "([^"]+)"`));
  if (!match?.[1]) throw new Error(`${name} not found`);
  return match[1].split(',').map(Number);
}

describe('region query boxes', () => {
  test('mirror the boxes the FIRMS ingestion queries', () => {
    expect([...REGION_DEFS.mekong.queryBox]).toEqual(ingestionBox('BBOX_MEKONG'));
    expect([...REGION_DEFS.amazon.queryBox]).toEqual(ingestionBox('BBOX_AMAZON'));
  });

  test('lie inside the display box', () => {
    for (const region of Object.values(REGION_DEFS)) {
      const [w, s, e, n] = region.bbox;
      const [qw, qs, qe, qn] = region.queryBox;
      expect(qw >= w && qs >= s && qe <= e && qn <= n).toBe(true);
    }
  });
});
