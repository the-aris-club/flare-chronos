import { describe, expect, test } from 'bun:test';
import { parseAudit, parseRun, parseRunList } from './api';

const SUMMARY = {
  id: 'run-1',
  owner: 'ana',
  use_case_id: 'UC-2.2',
  status: 'needs',
  started_at: '2026-11-02T08:00:00.000Z',
  updated_at: '2026-11-02T08:00:09.000Z',
};

describe('parseRunList', () => {
  test('reads the queue rows', () => {
    expect(parseRunList({ runs: [SUMMARY] })).toEqual([
      {
        id: 'run-1',
        owner: 'ana',
        useCase: 'UC-2.2',
        status: 'needs',
        startedAt: '2026-11-02T08:00:00.000Z',
        updatedAt: '2026-11-02T08:00:09.000Z',
      },
    ]);
  });

  test('a row with an unknown status is rejected, not shown as something else', () => {
    expect(() => parseRunList({ runs: [{ ...SUMMARY, status: 'approved' }] })).toThrow();
    expect(() => parseRunList({ runs: [{ ...SUMMARY, id: 7 }] })).toThrow();
    expect(() => parseRunList({})).toThrow();
  });
});

describe('parseRun', () => {
  const detail = {
    ...SUMMARY,
    mode: 'live',
    question: 'Authorize the operational action proposed by UC-2.2?',
    briefing: 'Send two teams.',
    verification: { passed: true, checked_numbers_count: 2, unverified_numbers: [] },
    self_corrections: 1,
    entity: { region: 'mekong', epoch_years: [2024] },
    facts: [
      { fact_key: 'cells', value: 13, unit: 'cells', source_tool: 'tool_a', provenance: 'core' },
    ],
    tools: ['tool_a'],
  };

  test('reads the evidence the reviewer signs off on', () => {
    const run = parseRun(detail);

    expect(run.briefing).toBe('Send two teams.');
    expect(run.verification.passed).toBe(true);
    expect(run.selfCorrections).toBe(1);
    expect(run.entity).toEqual({ region: 'mekong', epochYears: [2024] });
    expect(run.facts).toEqual([
      { key: 'cells', value: 13, unit: 'cells', tool: 'tool_a', provenance: 'core' },
    ]);
    expect(run.tools).toEqual(['tool_a']);
  });

  test('a fact without a numeric value is rejected', () => {
    expect(() =>
      parseRun({ ...detail, facts: [{ fact_key: 'x', value: 'many', source_tool: 't' }] }),
    ).toThrow();
  });
});

describe('parseAudit', () => {
  test('reads decisions with their reason code', () => {
    expect(
      parseAudit({
        audit: [
          {
            id: 'A-0001',
            thread_id: 'run-1',
            principal: 'carol',
            approved: false,
            reason: 'seen already',
            reason_code: 'duplicate',
            decided_at: '2026-11-02T08:05:00.000Z',
          },
        ],
      }),
    ).toEqual([
      {
        id: 'A-0001',
        runId: 'run-1',
        principal: 'carol',
        approved: false,
        reason: 'seen already',
        reasonCode: 'duplicate',
        decidedAt: '2026-11-02T08:05:00.000Z',
      },
    ]);
  });
});
