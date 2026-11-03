'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useLocale, useTranslations } from 'next-intl';
import { useTheme } from '@/components/ui/theme-provider';
import type { RegionId } from '@/lib/calendar/types';
import { formatQueryBox } from '@/lib/workbench/query-box';
import { REGION_DEFS } from '@/lib/workbench/regions';
import { BOOT_STEPS, type BootStep, type GlobeHandle } from '@/lib/globe/types';
import { BootOverlay } from './boot-overlay';
import dynamic from 'next/dynamic';
import type { GlobeLabel } from './globe-canvas';
const GlobeCanvas = dynamic(() => import('./globe-canvas').then((m) => m.GlobeCanvas), {
  ssr: false,
  loading: () => <div className="bg-canvas absolute inset-0" />,
});
import { LandingHeader } from './landing-header';
import { LandingPanel } from './landing-panel';

export type LandingRegion = {
  id: RegionId;
  measured: number[];
  lastEpoch: number;
};

type GlobeLandingProps = {
  period: { start: number; end: number };
  yearStart: number;
  total: number;
  growth: Record<RegionId, number>;
  regions: LandingRegion[];
};

export function GlobeLanding({ period, yearStart, total, growth, regions }: GlobeLandingProps) {
  const t = useTranslations('Globe');
  const locale = useLocale();
  const regionNames = useTranslations('Header.regions');
  const router = useRouter();
  const { theme } = useTheme();
  const globeRef = useRef<GlobeHandle>(null);
  const [hovered, setHovered] = useState<RegionId | null>(null);
  const [collapsed, setCollapsed] = useState(false);
  const leavingRef = useRef(false);
  const [booting, setBooting] = useState(true);
  const [done, setDone] = useState<BootStep[]>([]);

  const mark = useCallback((step: BootStep) => {
    setDone((current) => (current.includes(step) ? current : [...current, step]));
  }, []);

  const finishBoot = useCallback(() => setBooting(false), []);

  useEffect(() => {
    let cancelled = false;
    const frame = requestAnimationFrame(() =>
      requestAnimationFrame(() => {
        if (!cancelled) mark('page');
      }),
    );

    document.fonts.ready.then(() => {
      if (!cancelled) mark('fonts');
    });

    const fallback = window.setTimeout(() => {
      if (!cancelled) BOOT_STEPS.forEach(mark);
    }, 15000);

    return () => {
      cancelled = true;
      cancelAnimationFrame(frame);
      window.clearTimeout(fallback);
    };
  }, [mark]);

  const enterNow = useCallback(
    (region: RegionId) => {
      const target = regions.find((entry) => entry.id === region);
      router.push(`/workbench/${region}?epoch=${target?.lastEpoch ?? 2024}`);
    },
    [regions, router],
  );

  const beginEnter = useCallback(
    (region: RegionId) => {
      if (leavingRef.current) return;
      leavingRef.current = true;
      setHovered(null);
      const started = globeRef.current?.flyTo(region) ?? false;
      if (!started) enterNow(region);
    },
    [enterNow],
  );

  const handleToggle = useCallback(() => setCollapsed((value) => !value), []);

  const handleExplore = useCallback(() => router.push('/workbench/mekong'), [router]);

  const handleTour = useCallback(() => router.push('/workbench/mekong?tour=1'), [router]);

  const cards = useMemo(
    () =>
      regions.map((region) => ({
        id: region.id,
        name: regionNames(`${region.id}Long`),
        coverage: t(`coverage.${region.id}`, {
          box: formatQueryBox(REGION_DEFS[region.id].queryBox, locale),
        }),
        measured: region.measured,
        lastEpoch: region.lastEpoch,
      })),
    [regions, regionNames, t, locale],
  );

  const labels = useMemo<GlobeLabel[]>(
    () =>
      regions.map((region) => ({
        id: region.id,
        name: t(`short.${region.id}`),
        measured: region.measured,
        yearStart,
        total,
      })),
    [regions, t, yearStart, total],
  );

  return (
    <div className="fc-globe-bg text-ink relative h-dvh overflow-hidden">
      <LandingHeader years={total} />

      <main className="absolute inset-0">
        <GlobeCanvas
          ref={globeRef}
          labels={labels}
          theme={theme}
          hovered={hovered}
          onHover={setHovered}
          onSelect={beginEnter}
          onArrive={enterNow}
          onProgress={mark}
        />

        <LandingPanel
          regions={cards}
          growth={growth}
          period={period}
          yearStart={yearStart}
          total={total}
          collapsed={collapsed}
          hovered={hovered}
          onToggle={handleToggle}
          onHover={setHovered}
          onSelect={beginEnter}
          onExplore={handleExplore}
          onTour={handleTour}
        />
      </main>

      <span className="text-meta text-ink-subtle pointer-events-none fixed bottom-4 left-14 z-10 hidden font-mono xl:block">
        {t('drag')}
      </span>

      <div className="border-line bg-panel/80 text-label text-ink-muted pointer-events-none fixed right-5 bottom-10 z-10 hidden items-center gap-2 rounded-md border px-2 py-1 backdrop-blur-sm xl:flex">
        <svg width={26} height={10} viewBox="0 0 26 10" aria-hidden="true">
          <line
            x1={1}
            y1={5}
            x2={25}
            y2={5}
            stroke="currentColor"
            strokeWidth={1.2}
            strokeDasharray="3 3"
            opacity={0.7}
          />
          <circle cx={18} cy={5} r={2.4} fill="currentColor" />
        </svg>
        <b className="text-ink font-medium">{t('orbit')}</b>
        <span className="text-ink-subtle uppercase">{t('illustration')}</span>
      </div>

      <span className="text-micro text-ink-subtle pointer-events-none fixed right-5 bottom-4 z-10 hidden font-mono xl:block">
        {t('credit')}
      </span>

      {booting && <BootOverlay done={done} onDone={finishBoot} />}
    </div>
  );
}
