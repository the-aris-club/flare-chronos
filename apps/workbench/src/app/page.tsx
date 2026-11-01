import { getTranslations } from 'next-intl/server';
import { GlobeLanding } from '@/components/globe/globe-landing';
import { loadCalendar } from '@/lib/calendar/load';
import type { RegionId } from '@/lib/calendar/types';
import { loadWorkbench } from '@/lib/workbench/series';

export async function generateMetadata() {
  const t = await getTranslations('Meta');

  return { title: t('homeTitle') };
}

export default async function Home() {
  const dataset = await loadCalendar();
  const workbench = await loadWorkbench(dataset);

  function growth(region: RegionId): number {
    const series = workbench.series[region];
    const start = series.years.indexOf(2005);
    const end = series.years.indexOf(2024);
    const first = start >= 0 ? series.raw[start] : 0;
    const last = end >= 0 ? series.raw[end] : 0;

    return first > 0 ? Math.round(last / first) : 0;
  }

  const regions = (['mekong', 'amazon'] as const).map((id) => {
    const epochs = workbench.epochs[id];

    return {
      id,
      measured: epochs.map((epoch) => epoch.year),
      lastEpoch: epochs.at(-1)?.year ?? 2024,
    };
  });

  return (
    <GlobeLanding
      period={dataset.period}
      yearStart={dataset.period.start}
      total={dataset.period.end - dataset.period.start + 1}
      growth={{ mekong: growth('mekong'), amazon: growth('amazon') }}
      regions={regions}
    />
  );
}
