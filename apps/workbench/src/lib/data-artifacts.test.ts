import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { describe, expect, test } from 'bun:test';

const ARTIFACTS = ['burning_calendar.json', 'empirical_results.json'] as const;

describe('traced data artifacts', () => {
  test.each(ARTIFACTS)('%s matches the processed source', async (name) => {
    const appCopy = path.resolve(process.cwd(), 'data/processed', name);
    const source = path.resolve(process.cwd(), '../../data/processed', name);
    const [copyText, sourceText] = await Promise.all([
      readFile(appCopy, 'utf8'),
      readFile(source, 'utf8'),
    ]);

    expect(JSON.parse(copyText)).toEqual(JSON.parse(sourceText));
  });
});
