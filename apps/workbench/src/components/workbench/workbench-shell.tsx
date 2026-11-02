'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { useIsDesktop, useIsTablet } from '@/lib/use-media';
import type { CalendarDataset, RegionId } from '@/lib/calendar/types';
import type { MapFilters, WorkbenchData } from '@/lib/workbench/types';
import { MAP_DATA } from '@/lib/workbench/map-data';
import { AppHeader } from './app-header';
import { BriefingRail, type RailState } from './briefing-rail';
import { BurningCalendar } from './burning-calendar';
import { ClockPane } from './clock-pane';
import dynamic from 'next/dynamic';
const ComparatorPane = dynamic(() => import('./comparator-pane').then((m) => m.ComparatorPane), {
  loading: () => <div className="bg-chip h-64 animate-pulse rounded-md" />,
});
import { EvidenceDrawer } from './evidence-drawer';
import { EvidenceQuickLook } from './evidence-quick-look';
import { KpiStrip } from './kpi-strip';
import { MapPane } from './map-pane';
import { tourFigures } from '@/lib/workbench/tour-figures';
import { ConclusionStrip } from './conclusion-strip';
import { TourOverlay } from './tour';

type Tab = 'map' | 'trend' | 'cal' | 'brief';

const TABS: Tab[] = ['map', 'trend', 'cal', 'brief'];

export function WorkbenchShell({
  dataset,
  workbench,
  initialRegion = 'mekong',
  initialYear = 2024,
  initialTour = false,
}: {
  dataset: CalendarDataset;
  workbench: WorkbenchData;
  initialRegion?: RegionId;
  initialYear?: number;
  initialTour?: boolean;
}) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const t = useTranslations('Header.regions');
  const tTabs = useTranslations('Tabs');
  const [region, setRegion] = useState<RegionId>(initialRegion);
  const [year, setYear] = useState(initialYear);
  const [tab, setTab] = useState<Tab>('map');
  const isDesktop = useIsDesktop();
  const isTablet = useIsTablet();
  const [briefState, setBriefState] = useState<RailState>('auto');
  const [filters, setFilters] = useState<MapFilters>({
    sza: true,
    saa: true,
    static: true,
    dedup: true,
  });
  const [evidenceOpen, setEvidenceOpen] = useState(false);
  const [tourOpen, setTourOpen] = useState(initialTour);

  const calendar = dataset.regions[region];
  const series = workbench.series[region];
  const epochs = workbench.epochs[region];
  const epoch = epochs.find((item) => item.year === year) ?? epochs[0];
  const peak = workbench.sfai[region][year] ?? { value: null, pentad: null };
  const regionLabel = t(region);
  const briefingPressed = briefState === 'open' || (briefState === 'auto' && isDesktop);

  function changeRegion(next: RegionId) {
    const nextEpochs = workbench.epochs[next];
    const nextYear =
      nextEpochs.find((item) => item.year === year)?.year ??
      nextEpochs.find((item) => item.year === 2024)?.year ??
      nextEpochs[0]?.year ??
      2001;
    setRegion(next);
    setYear(nextYear);

    const query = new URLSearchParams(searchParams.toString());
    query.delete('region');
    query.set('epoch', String(nextYear));
    if (!tourOpen) query.delete('tour');
    router.push(`/workbench/${next}?${query.toString()}`);
  }

  function toggleBrief() {
    if (briefState === 'open') {
      setBriefState('closed');
      if (tab === 'brief') setTab('map');
      return;
    }
    if (briefState === 'closed') {
      setBriefState('open');
      return;
    }
    setBriefState(isDesktop ? 'closed' : 'open');
  }

  function chooseTab(next: Tab) {
    setTab(next);
    if (next === 'brief') {
      setBriefState('open');
    } else if (briefState === 'open') {
      setBriefState('closed');
    }
  }

  return (
    <div className="bg-canvas relative flex h-dvh flex-col overflow-hidden">
      <AppHeader
        region={region}
        period={dataset.period}
        briefingOpen={briefingPressed}
        onRegion={changeRegion}
        onTour={() => setTourOpen(true)}
        onEvidence={() => setEvidenceOpen(true)}
        onBriefing={toggleBrief}
        onService={() => setBriefState('open')}
      />

      <div className="flex min-h-0 flex-1">
        <main className="tablet:p-3 tablet:pb-3 min-w-0 flex-1 overflow-y-auto p-2.5 pb-20">
          <ConclusionStrip
            series={series}
            calibration={workbench.calibration}
            measured={calendar.observedYears.length}
            total={calendar.years.length}
          />
          <div className="grid grid-cols-1 gap-2.5 xl:grid-cols-3">
            <div
              className={`${tab === 'map' ? 'block' : 'hidden'} tablet:block tablet:order-2 xl:order-1 xl:col-span-3`}
            >
              <MapPane
                region={region}
                regionLabel={regionLabel}
                epochs={epochs}
                physics={workbench.physics}
                year={year}
                filters={filters}
                onFilter={(key) => setFilters((current) => ({ ...current, [key]: !current[key] }))}
                onYear={setYear}
              />
            </div>

            <div
              className={`${tab === 'trend' ? 'block' : 'hidden'} tablet:block tablet:order-1 xl:order-2 xl:col-span-3`}
            >
              <KpiStrip
                series={series}
                epoch={epoch}
                year={year}
                peak={peak}
                filters={filters}
                counts={MAP_DATA.regions[region].counts[String(year)]}
              />
            </div>

            <div
              className={`tablet:order-3 flex-col gap-2.5 xl:order-3 xl:col-span-3 ${
                tab === 'trend' ? 'flex' : 'tablet:flex hidden'
              }`}
            >
              <div className="wide:grid-cols-3 grid grid-cols-1 gap-2.5">
                <div className="wide:col-span-2">
                  <ComparatorPane
                    series={series}
                    regionLabel={regionLabel}
                    visible={tab === 'trend' || isTablet}
                  />
                </div>
                <ClockPane region={calendar} year={year} regionLabel={regionLabel} />
              </div>
              <EvidenceQuickLook
                physics={workbench.physics}
                calibration={workbench.calibration}
                onOpen={() => setEvidenceOpen(true)}
              />
            </div>

            <div
              className={`${tab === 'cal' ? 'block' : 'hidden'} tablet:block tablet:order-4 xl:order-4 xl:col-span-3`}
            >
              <BurningCalendar
                key={region}
                region={calendar}
                regionLabel={regionLabel}
                unit={dataset.unit}
                onMeasuredYear={setYear}
              />
            </div>
          </div>
        </main>

        {briefState === 'open' && (
          <button
            type="button"
            aria-label={tTabs('closeBriefing')}
            onClick={toggleBrief}
            className="bg-scrim fixed inset-0 z-20 xl:hidden"
          />
        )}

        <BriefingRail region={region} state={briefState} onToggle={toggleBrief} />
      </div>

      <nav
        aria-label={tTabs('label')}
        className="border-line bg-surface tablet:hidden fixed inset-x-0 bottom-0 z-40 flex h-14 border-t"
      >
        {TABS.map((item) => (
          <button
            key={item}
            type="button"
            aria-pressed={tab === item}
            onClick={() => chooseTab(item)}
            className={`text-meta relative flex flex-1 flex-col items-center justify-center gap-0.5 font-medium ${
              tab === item ? 'text-ink' : 'text-ink-subtle'
            }`}
          >
            <span
              aria-hidden="true"
              className={`absolute top-0 h-0.5 w-8 rounded-b ${
                tab === item ? 'bg-ink' : 'bg-transparent'
              }`}
            />
            {tTabs(item)}
          </button>
        ))}
      </nav>

      <EvidenceDrawer
        open={evidenceOpen}
        onClose={() => setEvidenceOpen(false)}
        series={series}
        epochs={epochs}
        physics={workbench.physics}
        calibration={workbench.calibration}
        calendar={calendar}
      />
      {tourOpen && (
        <TourOverlay
          onClose={() => setTourOpen(false)}
          figures={tourFigures(dataset, workbench, region)}
        />
      )}
    </div>
  );
}
