export type ServiceEvent = { type: string; [key: string]: unknown };

/**
 * Incremental Server-Sent Events parser. `EventSource` cannot send the bearer header, so
 * the stream is read with `fetch` and fed here chunk by chunk. Every frame's `data` line
 * carries the whole event as JSON (see `ai_service.events`).
 */
export function createSseParser(): (chunk: string) => ServiceEvent[] {
  let buffer = '';

  return (chunk) => {
    buffer += chunk.replaceAll('\r\n', '\n');
    const frames = buffer.split('\n\n');
    buffer = frames.pop() ?? '';

    const events: ServiceEvent[] = [];
    for (const frame of frames) {
      const data = frame
        .split('\n')
        .filter((line) => line.startsWith('data:'))
        .map((line) => line.slice(5).trimStart())
        .join('\n');
      try {
        const event = JSON.parse(data) as ServiceEvent;
        if (typeof event.type === 'string') events.push(event);
      } catch {
        // A frame that is not an event (a keep-alive, a proxy error page) is skipped.
      }
    }
    return events;
  };
}
