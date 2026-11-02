import { describe, expect, test } from 'bun:test';
import { IDLE_RUN, reduceRun } from './run';
import type { ServiceEvent } from './sse';

const play = (events: ServiceEvent[]) => events.reduce(reduceRun, IDLE_RUN);

const STARTED: ServiceEvent = {
  type: 'run_started',
  thread_id: 'run-1',
  use_case_id: 'UC-2.2',
  mode: 'live',
};

describe('reduceRun', () => {
  test('a run that reaches the sign-off gate is paused with its evidence', () => {
    const run = play([
      STARTED,
      { type: 'node_completed', node: 'classify_node', keys: [] },
      { type: 'tool_result', tools: ['tool_a', 'tool_b'] },
      { type: 'tool_result', tools: ['tool_b', 'tool_c'] },
      {
        type: 'sign_off_required',
        kind: 'sign_off',
        use_case_id: 'UC-2.2',
        question: 'Authorize the operational action proposed by UC-2.2?',
        evidence: {
          final_briefing: 'Send two teams.',
          verification_report: { passed: true, checked_numbers_count: 3 },
          verified_ledger_entries: [
            { fact_key: 'cells', numeric_value: 13, unit: 'cells', source_tool: 'tool_a' },
          ],
          entity: { region: 'mekong' },
          self_corrections: 1,
        },
      },
      { type: 'run_paused', thread_id: 'run-1', next: ['sign_off_gate_node'] },
    ]);

    expect(run.phase).toBe('paused');
    expect(run.threadId).toBe('run-1');
    expect(run.tools).toEqual(['tool_a', 'tool_b', 'tool_c']);
    expect(run.signOff?.question).toContain('UC-2.2');
    expect(run.signOff?.briefing).toBe('Send two teams.');
    expect(run.signOff?.verification.passed).toBe(true);
    expect(run.signOff?.facts).toEqual([
      { key: 'cells', value: 13, unit: 'cells', tool: 'tool_a' },
    ]);
    expect(run.signOff?.selfCorrections).toBe(1);
  });

  test('a completed run keeps the briefing and verification it ended with', () => {
    const run = play([
      STARTED,
      { type: 'verification', passed: true, checked_numbers_count: 2, unverified_numbers: [] },
      { type: 'briefing', text: 'All clear.', synthesis_mode: 'llm' },
      { type: 'run_completed', thread_id: 'run-1', sign_off_decision: { approved: true } },
    ]);

    expect(run.phase).toBe('done');
    expect(run.briefing).toBe('All clear.');
    expect(run.verification?.passed).toBe(true);
    expect(run.approved).toBe(true);
  });

  test('a failed run reports why', () => {
    const run = play([STARTED, { type: 'run_failed', error: 'run exceeded its time budget' }]);

    expect(run.phase).toBe('failed');
    expect(run.error).toBe('run exceeded its time budget');
  });

  test('a resumed run starts a new stream without losing the earlier evidence', () => {
    const paused = play([
      STARTED,
      {
        type: 'sign_off_required',
        question: 'q',
        evidence: { final_briefing: 'b', verification_report: { passed: true } },
      },
      { type: 'run_paused', thread_id: 'run-1' },
    ]);

    const resumed = [
      { type: 'run_started', thread_id: 'run-1', resumed: true },
      { type: 'run_completed', thread_id: 'run-1', sign_off_decision: { approved: false } },
    ].reduce(reduceRun, paused);

    expect(resumed.phase).toBe('done');
    expect(resumed.approved).toBe(false);
    expect(resumed.signOff?.briefing).toBe('b');
  });
});
