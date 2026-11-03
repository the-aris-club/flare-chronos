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

async function readDecisions(): Promise<Record<string, Decision>> {
  try {
    return JSON.parse(await readFile(STORE, 'utf8')) as Record<string, Decision>;
  } catch {
    return { ...INITIAL_DECISIONS };
  }
}

async function writeDecisions(decisions: Record<string, Decision>) {
  await mkdir(path.dirname(STORE), { recursive: true });
  await writeFile(STORE, `${JSON.stringify(decisions, null, 2)}\n`, 'utf8');
}

export async function GET() {
  return NextResponse.json(
    { decisions: await readDecisions() },
    { headers: { 'cache-control': 'no-store' } },
  );
}

export async function POST(request: Request) {
  let body: { runId?: string; kind?: DecisionKind; reason?: string; note?: string };
  try {
    body = (await request.json()) as typeof body;
  } catch {
    return NextResponse.json({ error: 'invalid_json' }, { status: 400 });
  }

  const run = REVIEW_RUNS.find((item) => item.id === body.runId);
  if (!run) return NextResponse.json({ error: 'unknown_run' }, { status: 404 });
  if (body.kind !== 'approve' && body.kind !== 'reject') {
    return NextResponse.json({ error: 'invalid_kind' }, { status: 400 });
  }
  if (!body.reason) return NextResponse.json({ error: 'reason_required' }, { status: 400 });
  if (body.kind === 'reject' && !body.reason) {
    return NextResponse.json({ error: 'reason_required' }, { status: 400 });
  }

  const decisions = await readDecisions();
  if (decisions[run.id]) {
    return NextResponse.json(
      { error: 'already_decided', decision: decisions[run.id] },
      { status: 409 },
    );
  }

  const decision = makeDecision(
    body.kind,
    body.reason,
    (body.note ?? '').trim(),
    Object.values(decisions),
  );
  decisions[run.id] = decision;

  try {
    await writeDecisions(decisions);
  } catch {
    return NextResponse.json({ error: 'store_unavailable' }, { status: 503 });
  }

  return NextResponse.json({ decision }, { status: 201 });
}
