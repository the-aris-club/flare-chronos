import { Suspense } from 'react';
import { notFound } from 'next/navigation';
import { WorkbenchShell } from '@/components/workbench/workbench-shell';
import { loadCalendar } from '@/lib/calendar/load';
import { loadWorkbench } from '@/lib/workbench/series';

type WorkbenchParams = Promise<{ zone: string }>;
type WorkbenchSearchParams = Promise<{ epoch?: string; tour?: string }>;

const loadingFallback = (
  <div className="bg-canvas text-ink flex h-dvh items-center justify-center">
    Loading workbench…
  </div>
);

export default async function WorkbenchZonePage({
  params,
  searchParams,
}: {
  params: WorkbenchParams;
  searchParams: WorkbenchSearchParams;
}) {
  const [{ zone }, query, dataset] = await Promise.all([params, searchParams, loadCalendar()]);
  if (zone !== 'mekong' && zone !== 'amazon') notFound();

  const workbench = await loadWorkbench(dataset);
  const epochs = workbench.epochs[zone];
  const requested = Number(query.epoch);
  const valid = Number.isInteger(requested) && epochs.some((epoch) => epoch.year === requested);
  const fallback = epochs.find((epoch) => epoch.year === 2024)?.year ?? epochs[0]?.year ?? 2001;

  return (
    <Suspense fallback={loadingFallback}>
      <WorkbenchShell
        key={zone}
        dataset={dataset}
        workbench={workbench}
        initialRegion={zone}
        initialYear={valid ? requested : fallback}
        initialTour={query.tour === '1'}
      />
    </Suspense>
  );
}
