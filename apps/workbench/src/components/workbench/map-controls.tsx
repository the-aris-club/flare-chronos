'use client';

import { useTranslations } from 'next-intl';
import { Icon, ICON } from '@/components/ui/icon';
import type { MapLayers } from '@/lib/workbench/types';

export const DEFAULT_LAYERS: MapLayers = {
  footprints: true,
  hex: false,
  overlay: true,
  lens: true,
};

type MapControlsProps = {
  layers: MapLayers;
  onLayer: (layer: keyof MapLayers) => void;
  grid: number;
  onGrid: (grid: number) => void;
};

const LAYERS: (keyof MapLayers)[] = ['footprints', 'hex', 'overlay', 'lens'];

export function MapControls({ layers, onLayer, grid, onGrid }: MapControlsProps) {
  const t = useTranslations('Map');
  const labels: Record<keyof MapLayers, string> = {
    footprints: t('footprints'),
    hex: t('hexes'),
    overlay: t('staticSaa'),
    lens: t('lens'),
  };

  return (
    <div className="ml-auto flex flex-wrap items-center gap-1.5">
      <div
        role="group"
        aria-label={t('h3Grid')}
        className="border-line-strong inline-flex items-center gap-1 rounded-md border p-0.5"
      >
        <span className="text-micro text-ink-subtle px-1 font-mono tracking-widest uppercase">
          H3
        </span>
        {[7, 8].map((resolution) => (
          <button
            key={resolution}
            type="button"
            aria-pressed={grid === resolution}
            aria-label={t('resLabel', { resolution })}
            onClick={() => onGrid(resolution)}
            className={`text-micro h-6 min-w-6 rounded-sm px-1.5 font-mono font-semibold ${
              grid === resolution ? 'bg-seg text-ink' : 'text-ink-subtle hover:text-ink'
            }`}
          >
            {resolution}
          </button>
        ))}
      </div>

      <div
        role="group"
        aria-label={t('layers')}
        className="border-line-strong inline-flex gap-0.5 rounded-md border p-0.5"
      >
        {LAYERS.map((layer) => (
          <button
            key={layer}
            type="button"
            aria-pressed={layers[layer]}
            onClick={() => onLayer(layer)}
            className={`text-meta h-6 rounded-sm px-2 font-medium transition-colors ${
              layers[layer] ? 'bg-seg text-ink' : 'text-ink-subtle hover:text-ink'
            }`}
          >
            {labels[layer]}
          </button>
        ))}
      </div>
    </div>
  );
}

export function MapZoom({
  onZoom,
  onReset,
}: {
  onZoom: (factor: number) => void;
  onReset: () => void;
}) {
  const t = useTranslations('Map');

  return (
    <div className="border-line-strong bg-panel absolute top-2 right-2 flex flex-col overflow-hidden rounded-md border">
      <button
        type="button"
        aria-label={t('zoomIn')}
        onClick={() => onZoom(2)}
        className="text-ink-muted hover:bg-chip hover:text-ink inline-flex size-7 items-center justify-center"
      >
        <Icon icon={ICON.plus} size="sm" />
      </button>
      <button
        type="button"
        aria-label={t('zoomOut')}
        onClick={() => onZoom(0.5)}
        className="border-line text-ink-muted hover:bg-chip hover:text-ink inline-flex size-7 items-center justify-center border-t"
      >
        <Icon icon={ICON.minus} size="sm" />
      </button>
      <button
        type="button"
        aria-label={t('zoomReset')}
        onClick={onReset}
        className="border-line text-ink-muted hover:bg-chip hover:text-ink inline-flex size-7 items-center justify-center border-t"
      >
        <Icon icon={ICON.reset} size="sm" />
      </button>
    </div>
  );
}
