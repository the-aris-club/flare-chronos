import { ReviewRunView } from '@/components/review/review-run';

export default async function ReviewRunPage({ params }: { params: Promise<{ runId: string }> }) {
  const { runId } = await params;

  return <ReviewRunView runId={runId} />;
}
