export type BBox = readonly [west: number, south: number, east: number, north: number];

export type RegionDef = {
  bbox: BBox;
  /** The box FIRMS was actually queried with; mirrors `firms_ingestion.BBOX_*`. */
  queryBox: BBox;
  anchor: readonly [lon: number, lat: number];
  focus: readonly string[];
  staticSources: readonly { id: string; lon: number; lat: number }[];
  fit?: readonly (readonly [lon: number, lat: number])[];
  islands?: readonly {
    id: string;
    box: readonly [west: number, south: number, east: number, north: number];
    label: readonly [lon: number, lat: number];
    points: readonly { name: string; lon: number; lat: number }[];
  }[];
};

/**
 * The two measured regions. Shared by the map and globe build scripts and by
 * the globe UI so the boxes and anchors never drift between the two surfaces.
 */
export const REGION_DEFS = {
  mekong: {
    bbox: [97, 5.4, 110, 23.6],
    queryBox: [100, 8.5, 109.5, 23.5],
    anchor: [105.8, 16.0],
    focus: ['704', '418', '116', '764'],
    staticSources: [
      { id: 'S-01', lon: 106.68, lat: 20.86 },
      { id: 'S-02', lon: 106.42, lat: 18.08 },
      { id: 'S-03', lon: 101.15, lat: 12.68 },
      { id: 'S-04', lon: 105.75, lat: 21.05 },
    ],
    fit: [
      [117.4, 6.3],
      [113.3, 17.7],
    ],
    islands: [
      {
        id: 'hs',
        box: [111.0, 15.7, 113.0, 17.25],
        label: [112.0, 17.45],
        points: [
          { name: 'Phú Lâm', lon: 112.338, lat: 16.835 },
          { name: 'Đảo Bắc', lon: 112.305, lat: 16.966 },
          { name: 'Đảo Hoàng Sa', lon: 111.611, lat: 16.533 },
          { name: 'Quang Hòa', lon: 111.711, lat: 16.446 },
          { name: 'Tri Tôn', lon: 111.196, lat: 15.784 },
          { name: 'Gò Nổi', lon: 112.89, lat: 16.828 },
        ],
      },
      {
        id: 'ts',
        box: [111.5, 6.5, 117.2, 12.0],
        label: [114.4, 12.25],
        points: [
          { name: 'Song Tử Tây', lon: 114.331, lat: 11.429 },
          { name: 'Thị Tứ', lon: 114.283, lat: 11.053 },
          { name: 'Ba Bình', lon: 114.365, lat: 10.376 },
          { name: 'Nam Yết', lon: 114.366, lat: 10.179 },
          { name: 'Sinh Tồn', lon: 114.316, lat: 9.883 },
          { name: 'Trường Sa Lớn', lon: 111.931, lat: 8.641 },
          { name: 'Đá Lát', lon: 111.67, lat: 8.678 },
          { name: 'Tiên Nữ', lon: 114.655, lat: 8.855 },
          { name: 'Thuyền Chài', lon: 113.3, lat: 8.166 },
          { name: 'An Bang', lon: 112.921, lat: 7.891 },
        ],
      },
    ],
  },
  amazon: {
    bbox: [-79.5, -20.5, -49, 5.2],
    queryBox: [-62, -14, -50, -4],
    anchor: [-63.0, -6.5],
    focus: ['076', '604', '068', '170', '218', '862', '328', '740'],
    staticSources: [
      { id: 'S-01', lon: -50.18, lat: -6.07 },
      { id: 'S-02', lon: -55.51, lat: -11.86 },
      { id: 'S-03', lon: -56.09, lat: -9.88 },
    ],
  },
} as const satisfies Record<'mekong' | 'amazon', RegionDef>;
