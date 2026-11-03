import { access, readFile } from 'node:fs/promises';
import path from 'node:path';
import { cache } from 'react';
import { buildDesignFixture } from './fixture';
import { buildArtifact, fail, record, type Json } from './parse';
import type { CalendarDataset } from './types';

async function firstExisting(candidates: (string | undefined)[]): Promise<string> {
  const found = await Promise.all(
    candidates.map(async (candidate) => {
      if (!candidate) return null;

      try {
        await access(candidate);
        return candidate;
      } catch {
        return null;
      }
    }),
  );

  const file = found.find((candidate) => candidate !== null);
  if (!file) fail('no data file found');

  return file;
}

async function readJson(file: string): Promise<Json> {
  return record(JSON.parse(await readFile(file, 'utf8')), path.basename(file));
}

export const loadCalendar = cache(async (): Promise<CalendarDataset> => {
  if (process.env.CALENDAR_FIXTURE === 'design') {
    const file = await firstExisting([
      process.env.CALENDAR_FIXTURE_PATH,
      path.resolve(process.cwd(), '../../docs/design/fixtures/design-calendar.json'),
      path.resolve(process.cwd(), 'docs/design/fixtures/design-calendar.json'),
    ]);

    return buildDesignFixture(await readJson(file));
  }

  const file = await firstExisting([
    process.env.CALENDAR_DATA_PATH,
    path.resolve(process.cwd(), '../../data/processed/burning_calendar.json'),
    path.resolve(process.cwd(), 'data/processed/burning_calendar.json'),
  ]);

  return buildArtifact(await readJson(file));
});
