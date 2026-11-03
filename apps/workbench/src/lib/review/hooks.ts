import { useQuery } from '@tanstack/react-query';
import { useService } from '@/components/service/service-provider';
import { parseAudit, parseRun, parseRunList, type ReviewRow } from './api';

export function useReviewRuns() {
  const service = useService();
  return useQuery({
    queryKey: ['review', 'runs'],
    queryFn: async () => {
      const result = await service.get('/api/v1/review/runs');
      if (!result.ok) throw new Error(result.reason);
      return parseRunList(result.data);
    },
    enabled: service.connection === 'connected',
    refetchInterval: 15000,
  });
}

export function useReviewRun(runId: string) {
  const service = useService();
  return useQuery({
    queryKey: ['review', 'run', runId],
    queryFn: async () => {
      const detail = await service.get(`/api/v1/review/runs/${runId}`);
      if (!detail.ok) throw new Error(detail.reason);
      const run = parseRun(detail.data);
      const trail = await service.get(`/api/v1/review/runs/${runId}/audit`);
      const audit = trail.ok ? parseAudit(trail.data) : [];
      return { run, audit };
    },
    enabled: service.connection === 'connected',
  });
}

export function useReviewAudit(runs: ReviewRow[]) {
  const service = useService();
  return useQuery({
    queryKey: ['review', 'audit', runs.map((row) => row.id).join(',')],
    queryFn: async () => {
      const decided = runs.filter((row) => row.status !== 'needs');
      const groups = await Promise.all(
        decided.map(async (run) => {
          const result = await service.get(`/api/v1/review/runs/${run.id}/audit`);
          if (!result.ok) throw new Error(result.reason);
          return parseAudit(result.data).map((row) => ({ ...row, useCase: run.useCase }));
        }),
      );
      return groups.flat().sort((a, b) => b.decidedAt.localeCompare(a.decidedAt));
    },
    enabled: service.connection === 'connected' && runs.length > 0,
  });
}
