import raw from '@/data/map-data.json';

export type MapPoint = {
  i: number;
  x: number;
  y: number;
  s: 'm' | 'v';
  f: number;
  sc: number;
  tr: number;
  ang: number;
  pf: string;
  dn: string;
};

export type MapHover = {
  point: MapPoint;
  status: 'keep' | 'sza' | 'saa' | 'static' | 'dup';
  clientX: number;
  clientY: number;
};

export type MapCounts = {
  total: number;
  sza: number;
  saa: number;
  static: number;
  dup: number;
  sampled: number;
};

export type MapCountry = {
  id: string;
  d: string;
  focus: boolean;
};

export type MapRegion = {
  bbox: number[];
  pxPerKm: number;
  saaPath: string;
  coveragePath: string;
  staticSources: { id: string; x: number; y: number }[];
  islands: {
    id: string;
    boxPath: string;
    label: { x: number; y: number } | null;
    points: { name: string; x: number; y: number }[];
  }[];
  countries: MapCountry[];
  borders: string;
  graticule: string;
  epochs: Record<string, MapPoint[]>;
  counts: Record<string, MapCounts>;
};

export type MapData = {
  width: number;
  height: number;
  saa: { lon: number; lat: number; rx: number; ry: number };
  regions: Record<'mekong' | 'amazon', MapRegion>;
};

export const MAP_DATA = raw as MapData;

export const MAP_FLAGS = {
  sza: 1,
  saa: 2,
  static: 4,
  dup: 8,
} as const;
