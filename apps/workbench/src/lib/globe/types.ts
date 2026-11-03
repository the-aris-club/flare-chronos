import type { RegionId } from '@/lib/calendar/types';

export type GlobeRegion = {
  bbox: number[];
  anchor: [number, number];
  coverage: string;
};

export type GlobeData = {
  width: number;
  height: number;
  land: string;
  borders: string;
  graticule: string;
  regions: Record<RegionId, GlobeRegion>;
};

export type BootStep = 'fonts' | 'page' | 'photo' | 'borders';

export const BOOT_STEPS: BootStep[] = ['fonts', 'page', 'photo', 'borders'];

export type GlobeHandle = {
  flyTo: (region: RegionId) => boolean;
  highlight: (region: RegionId | null) => void;
  peek: (region: RegionId | null) => void;
  snapshot: () => string | null;
};
