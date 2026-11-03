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
  /** The box FIRMS was queried with, and its projected outline. */
  queryBox: number[];
  queryBoxPath: string;
  pxPerKm: number;
  saaPath: string;
  coveragePath: string;
  /** Every drawn country merged: the area the shaded relief is clipped to. */
  landPath: string;
  rivers: string;
  lakes: string;
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
  /** How far past the viewBox the base layers and relief are drawn, on each side. */
  pad: { x: number; y: number };
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
