import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { NextResponse } from 'next/server';
import { INITIAL_DECISIONS, type Decision, type DecisionKind } from '@/data/fixtures/review';
import { REVIEW_RUNS } from '@/data/fixtures/review-runs';
import { makeDecision } from '@/lib/review/decision';

export const dynamic = 'force-dynamic';

const STORE = path.resolve(
  process.env.REVIEW_DECISIONS_PATH ??
    path.join(process.cwd(), '../../data/runtime/review-decisions.json'),
);

class StoreUnavailable extends Error {}

/**
 * Serialises the read-modify-write of the store within this process so two POSTs cannot
 * read the same snapshot. Across processes the single-file store still needs a lock or a
 * database; this is replaced when the real API is wired.
 */
let queue: Promise<unknown> = Promise.resolve();
function serialised<T>(task: () => Promise<T>): Promise<T> {
  const run = queue.then(task, task);
  queue = run.catch(() => undefined);
  return run;
}

/** Only a missing file falls back to the seed; an unreadable or corrupt store is an error. */
async function readDecisions(): Promise<Record<string, Decision>> {
  let text: string;
  try {
    text = await readFile(STORE, 'utf8');
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') return { ...INITIAL_DECISIONS };
    throw new StoreUnavailable('decision store unreadable');
  }
  try {
    return JSON.parse(text) as Record<string, Decision>;
  } catch {
    throw new StoreUnavailable('decision store corrupt');
  }
}

function storeUnavailable() {
  return NextResponse.json({ error: 'store_unavailable' }, { status: 503 });
}

async function writeDecisions(decisions: Record<string, Decision>) {
  await mkdir(path.dirname(STORE), { recursive: true });
  await writeFile(STORE, `${JSON.stringify(decisions, null, 2)}\n`, 'utf8');
}

export async function GET() {
  try {
    return NextResponse.json(
      { decisions: await readDecisions() },
      { headers: { 'cache-control': 'no-store' } },
    );
  } catch {
    return storeUnavailable();
  }
}

export function POST(request: Request) {
  return serialised(() => handlePost(request));
}

async function handlePost(request: Request) {
  let body: { runId?: unknown; kind?: unknown; reason?: unknown; note?: unknown };
  try {
    const parsed: unknown = await request.json();
    if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
      return NextResponse.json({ error: 'invalid_json' }, { status: 400 });
    }
    body = parsed as typeof body;
  } catch {
    return NextResponse.json({ error: 'invalid_json' }, { status: 400 });
  }

  const run = REVIEW_RUNS.find((item) => item.id === body.runId);
  if (!run) return NextResponse.json({ error: 'unknown_run' }, { status: 404 });
  const kind: DecisionKind | null =
    body.kind === 'approve' || body.kind === 'reject' ? body.kind : null;
  if (!kind) return NextResponse.json({ error: 'invalid_kind' }, { status: 400 });
  if (typeof body.reason !== 'string' || !body.reason) {
    return NextResponse.json({ error: 'reason_required' }, { status: 400 });
  }
  if (body.note !== undefined && typeof body.note !== 'string') {
    return NextResponse.json({ error: 'invalid_note' }, { status: 400 });
  }

  let decisions: Record<string, Decision>;
  try {
    decisions = await readDecisions();
  } catch {
    return storeUnavailable();
  }
  if (decisions[run.id]) {
    return NextResponse.json(
      { error: 'already_decided', decision: decisions[run.id] },
      { status: 409 },
    );
  }

  const decision = makeDecision(
    kind,
    body.reason,
    (body.note ?? '').trim(),
    Object.values(decisions),
  );
  decisions[run.id] = decision;

  try {
    await writeDecisions(decisions);
  } catch {
    return storeUnavailable();
  }

  return NextResponse.json({ decision }, { status: 201 });
}
