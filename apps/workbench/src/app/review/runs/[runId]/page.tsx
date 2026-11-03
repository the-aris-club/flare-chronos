// TODO(api): review run detail — replace runById with GET /api/v1/review/runs/:id.
import { notFound } from 'next/navigation';
import { ReviewRun } from '@/components/review/review-run';
import { runById } from '@/data/fixtures/review-runs';

export default async function ReviewRunPage({ params }: { params: Promise<{ runId: string }> }) {
  const { runId } = await params;
  const run = runById(runId);
  if (!run) notFound();

  return <ReviewRun run={run} />;
}
