'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useLocale, useTranslations } from 'next-intl';
import { MAP_DATA, MAP_FLAGS, type MapHover } from '@/lib/workbench/map-data';
import { displayResolution } from '@/lib/workbench/h3';
import { clampView, MAP_VIEW, zoomAt, type MapView } from '@/lib/workbench/map-view';
import type { Epoch, MapFilters, MapLayers, MapPhysics } from '@/lib/workbench/types';
import { formatEpochDate, formatEpochDays } from '@/lib/workbench/format';
import type { RegionId } from '@/lib/calendar/types';
import { MapGuide } from './map-guide';
import { DEFAULT_LAYERS, MapControls, MapZoom } from './map-controls';
import { MapFooter, MapScale } from './map-legend';
import { MapTooltip } from './map-tooltip';
import { WorkbenchMap } from './workbench-map';

type MapPaneProps = {
  region: RegionId;
  regionLabel: string;
  epochs: Epoch[];
  physics: MapPhysics;
  year: number;
  filters: MapFilters;
  onFilter: (key: keyof MapFilters) => void;
  onYear: (year: number) => void;
};

export function MapPane({
  region,
  regionLabel,
  epochs,
  physics,
  year,
  filters,
  onFilter,
  onYear,
}: MapPaneProps) {
  const t = useTranslations('Map');
  const locale = useLocale();
  const [layers, setLayers] = useState<MapLayers>(DEFAULT_LAYERS);
  const [grid, setGrid] = useState(7);
  const [view, setView] = useState<MapView>(MAP_VIEW);
  const [hover, setHover] = useState<MapHover | null>(null);
  const clamped = useMemo(() => clampView(view, MAP_DATA.width, MAP_DATA.height), [view]);
  const mapArea = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const element = mapArea.current;
    if (!element) return;
    const observer = new ResizeObserver(() =>
      setSize({ width: element.clientWidth, height: element.clientHeight }),
    );
    observer.observe(element);
    return () => observer.disconnect();
  }, []);

  const scrollSelected = useCallback((node: HTMLButtonElement | null) => {
    const viewport = node?.parentElement;
    if (!node || !viewport) return;
    const box = node.getBoundingClientRect();
    const bounds = viewport.getBoundingClientRect();
    if (box.left >= bounds.left && box.right <= bounds.right) return;
    node.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
  }, []);

  const data = MAP_DATA.regions[region];
  const points = useMemo(() => data.epochs[String(year)] ?? [], [data, year]);
  const date = formatEpochDate(epochs.find((epoch) => epoch.year === year)?.date ?? null, locale);
  const resolution = displayResolution(view.k, grid);
  const drawnCount = useMemo(
    () => points.filter((point) => !(point.f & MAP_FLAGS.dup)).length,
    [points],
  );
  const scale =
    size.width > 0 ? Math.min(size.width / MAP_DATA.width, size.height / MAP_DATA.height) : 0;
  const pxPerKm = data.pxPerKm * scale * view.k;

  function zoom(factor: number) {
    setView(
      zoomAt(
        view,
        factor,
        MAP_DATA.width / 2,
        MAP_DATA.height / 2,
        MAP_DATA.width,
        MAP_DATA.height,
      ),
    );
  }

  function toggleLayer(layer: keyof MapLayers) {
    setLayers((current) => ({ ...current, [layer]: !current[layer] }));
  }

  return (
    <section
      data-tour="map"
      aria-labelledby="map-title"
      className="fc-map-pane border-line bg-panel flex flex-col overflow-hidden rounded-lg border"
    >
      <header className="border-line flex flex-wrap items-center gap-x-3 gap-y-1.5 border-b px-3 py-2">
        <h2 id="map-title" className="text-body font-semibold">
          {t('title')}
        </h2>
        <span className="text-micro text-ink-subtle max-tablet:hidden font-mono tracking-widest uppercase">
          {t('equalArea')}
        </span>
        <MapControls layers={layers} onLayer={toggleLayer} grid={grid} onGrid={setGrid} />
      </header>

      <div className="border-line flex items-center gap-2 overflow-x-auto border-b px-3 py-1.5">
        <span className="text-micro text-ink-subtle shrink-0 font-mono tracking-widest uppercase">
          {t('epochs')}
        </span>
        <span className="text-meta shrink-0 font-mono font-semibold">
          {t('of26', { count: epochs.length })}
        </span>
        <div className="fc-epoch-wrap min-w-0 flex-1">
          <span
            aria-hidden="true"
            className="fc-epoch-fade pointer-events-none absolute inset-y-0 left-0 z-10"
          />
          <div
            className="fc-epoch-scroll flex gap-1.5 overflow-x-auto"
            onScroll={(event) => {
              event.currentTarget.dataset.scrolled =
                event.currentTarget.scrollLeft > 4 ? 'true' : 'false';
            }}
          >
            {epochs.map((epoch) => {
              const pressed = epoch.year === year;

              return (
                <button
                  key={epoch.year}
                  ref={pressed ? scrollSelected : undefined}
                  type="button"
                  aria-pressed={pressed}
                  onClick={() => {
                    setHover(null);
                    onYear(epoch.year);
                  }}
                  className={`flex shrink-0 flex-col items-start rounded-md border px-2 py-1 text-left transition-colors ${
                    pressed
                      ? 'border-line-strong bg-seg text-ink'
                      : 'border-line text-ink-muted hover:bg-chip hover:text-ink'
                  }`}
                >
                  <span className="text-meta font-mono font-semibold">{epoch.year}</span>
                  <span className="text-micro text-ink-subtle max-tablet:hidden font-mono">
                    {formatEpochDays(epoch.date, locale)}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      <div ref={mapArea} className="relative min-h-0 flex-1">
        <WorkbenchMap
          region={region}
          year={year}
          view={clamped}
          grid={grid}
          filters={filters}
          layers={layers}
          label={t('aria', { region: regionLabel, year })}
          onView={setView}
          onHover={setHover}
        />

        <div className="absolute top-2 right-12 left-2 flex flex-wrap gap-1.5">
          <span className="border-line bg-panel/90 text-micro text-ink-muted max-tablet:hidden rounded-md border px-2 py-1 font-mono">
            {t('projection')}
          </span>
          <span className="border-line bg-panel/90 text-micro text-ink-muted rounded-md border px-2 py-1 font-mono">
            {t('sampled', { count: drawnCount })}
          </span>
          {layers.hex && (
            <span className="border-line bg-panel/90 text-micro text-ink-muted rounded-md border px-2 py-1 font-mono">
              {t('hexShown', { grid, resolution })}
            </span>
          )}
          <span className="border-line bg-panel/90 text-micro text-ink-muted max-tablet:hidden rounded-md border px-2 py-1 font-mono">
            {t('queryBox')} {data.queryBox.join(' · ')}
          </span>
          <span className="border-line bg-panel/90 text-micro text-ink-muted rounded-md border px-2 py-1 font-mono">
            {date}
          </span>
        </div>

        <MapZoom onZoom={zoom} onReset={() => setView(MAP_VIEW)} />

        {pxPerKm > 0 && <MapScale pxPerKm={pxPerKm} />}
        <MapGuide
          physics={physics}
          overlay={layers.overlay}
          epoch={epochs.find((epoch) => epoch.year === year)}
          filters={filters}
          onFilterAction={onFilter}
          onOverlayAction={() => toggleLayer('overlay')}
          hex={layers.hex}
          grid={grid}
          resolution={resolution}
          saa={region === 'amazon'}
          islands={region === 'mekong'}
        />
        <MapFooter />
        <MapTooltip hover={hover} container={mapArea} />
      </div>
    </section>
  );
}
