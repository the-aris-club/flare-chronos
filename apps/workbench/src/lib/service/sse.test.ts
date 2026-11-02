import { describe, expect, test } from 'bun:test';
import { createSseParser } from './sse';

describe('createSseParser', () => {
  test('yields one event per blank-line-terminated frame, from the data JSON', () => {
    const parse = createSseParser();

    const events = parse(
      'id: 1\nevent: run_started\ndata: {"type":"run_started","thread_id":"t1"}\n\n' +
        'id: 2\nevent: tool_result\ndata: {"type":"tool_result","tools":["a"]}\n\n',
    );

    expect(events).toEqual([
      { type: 'run_started', thread_id: 't1' },
      { type: 'tool_result', tools: ['a'] },
    ]);
  });

  test('a frame split across chunks is held until it is complete', () => {
    const parse = createSseParser();

    expect(parse('id: 1\nevent: message\ndata: {"type":"mess')).toEqual([]);
    expect(parse('age","content":"hi"}\n')).toEqual([]);
    expect(parse('\n')).toEqual([{ type: 'message', content: 'hi' }]);
  });

  test('a frame whose data is not JSON is skipped, not thrown', () => {
    const parse = createSseParser();

    expect(parse('data: oops\n\ndata: {"type":"run_completed"}\n\n')).toEqual([
      { type: 'run_completed' },
    ]);
  });
});
