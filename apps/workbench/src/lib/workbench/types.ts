export type AnnualSeries = {
  years: number[];
  raw: number[];
  harmonized: number[];
  measured: number[];
  /** Raw growth between two Measured Epochs, in percent. */
  rawGrowthPct: number;
  /** The two Measured Epochs `rawGrowthPct` is read between. */
  growthWindow: readonly [from: number, to: number];
  trendPct: number;
};

export type Epoch = {
  year: number;
  date: string | null;
  raw: number;
  episodes: number | null;
  harmonized: number;
  sensors: number;
  saa: number;
  szaPct: number;
};

export type MapPhysics = {
  modisNadir: number;
  modisEdge: number;
  viirsNadir: number;
  viirsEdge: number;
  ratio: number;
};

export type MapFilters = {
  sza: boolean;
  saa: boolean;
  static: boolean;
  dedup: boolean;
};

export type MapLayers = {
  footprints: boolean;
  hex: boolean;
  overlay: boolean;
};

export type Calibration = {
  r2Raw: number;
  r2Harmonized: number;
  rmseRaw: number;
  rmseHarmonized: number;
  ksBefore: number;
  ksAfter: number;
  pairs: number;
  /** The held-out check: RMSE gain in MW on years after `trainLastYear`, with its 95% interval. */
  holdout: {
    gainMw: number;
    ciLowMw: number;
    ciHighMw: number;
    trainLastYear: number;
  };
};

export type SfaiPeak = {
  value: number | null;
  pentad: number | null;
};

export type WorkbenchData = {
  series: Record<'mekong' | 'amazon', AnnualSeries>;
  epochs: Record<'mekong' | 'amazon', Epoch[]>;
  sfai: Record<'mekong' | 'amazon', Record<number, SfaiPeak>>;
  physics: MapPhysics;
  calibration: Calibration;
};
