import type { Audience, ToolCall } from './review';

export const BRIEF_A: Record<Audience, string[]> = {
  rangers: [
    'Fire activity across the Mekong is at crisis level.',
    'Satellites recorded {nrt} — MODIS {modis}, Suomi NPP {snpp}, NOAA-20 {n20} and NOAA-21 {n21} — grouped into {episodes}.',
    'After correcting for how many satellites are watching (Ω {omega}), the activity index is {sfai}, above the {crisis} crisis line.',
    'A Tier-1 flash alert is proposed for 24 hours.',
  ],
  leaders: [
    'The Mekong has crossed the crisis threshold.',
    'The harmonized index stands at {sfai} against a {crisis} crisis threshold.',
    'It rests on {nrt} in near real time (MODIS {modis}, Suomi NPP {snpp}, NOAA-20 {n20}, NOAA-21 {n21}) forming {episodes}, with sensor overlap corrected by Ω {omega}.',
    'Recommended: a Tier-1 flash alert for 24 hours.',
  ],
  scientists: [
    'NRT window, Mekong 2026: {nrt} (MODIS {modis}; VIIRS Suomi NPP {snpp}, NOAA-20 {n20}, NOAA-21 {n21}), collapsed to {episodes} after de-duplication.',
    'Constellation overlap factor Ω = {omega}.',
    'SFAI = {sfai}, exceeding the {crisis} crisis threshold.',
    'Proposed action: Tier-1 flash alert, 24 h.',
  ],
};

export const BRIEF_B: Record<Audience, string[]> = {
  rangers: [
    'Send two teams to the {cells} marked on the map at the next satellite pass.',
    'An older MODIS pixel at the edge of its swath covers {modis_edge} — {scan} across and {track} along the track — so it cannot show where in that area the fire is.',
    'A VIIRS pixel covers {viirs}, which makes the search area {reduction} smaller.',
    'A satellite passes about every {revisit}, and detections within {cluster} of each other are treated as one fire.',
  ],
  leaders: [
    'Recommendation: dispatch two teams to {cells} at the next overpass.',
    'The case rests on footprint size, not fire count.',
    'A MODIS edge pixel spans {modis_edge} ({scan} by {track}); a VIIRS pixel spans {viirs}, a {reduction} reduction in the area a team has to search.',
    'With a {revisit} revisit and a {cluster} clustering window, the target cells are current to within one overpass.',
  ],
  scientists: [
    'Footprint comparison for the Mekong 2024 measured epoch.',
    'MODIS edge-of-swath pixel area is {modis_edge} (scan {scan}, track {track}); VIIRS I-band pixel area is {viirs}, an area ratio of {reduction}.',
    'Detections were clustered over a {cluster} window and assigned to {cells}.',
    'Median constellation revisit is {revisit}.',
    'Proposed action: dispatch two teams to those cells at the next overpass.',
  ],
};

export const TOOLS_A: ToolCall[] = [
  { id: '#1', name: 'firms.nrt_count', fields: 'total · by_sensor.*', time: '0.9 s' },
  { id: '#2', name: 'episodes.cluster', fields: 'episode_count', time: '1.6 s' },
  { id: '#3', name: 'harmonize.omega', fields: 'omega', time: '0.4 s' },
  { id: '#4', name: 'sfai.score', fields: 'z', time: '0.7 s' },
  { id: '#5', name: 'sfai.thresholds', fields: 'display_sigma · crisis_sigma', time: '0.1 s' },
];

export const TOOLS_B: ToolCall[] = [
  {
    id: '#1',
    name: 'footprint.modis_pixel',
    fields: 'edge_area_km2 · scan_km · track_km',
    time: '0.3 s',
  },
  { id: '#2', name: 'footprint.viirs_pixel', fields: 'area_km2', time: '0.2 s' },
  { id: '#3', name: 'footprint.compare', fields: 'area_ratio', time: '0.1 s' },
  { id: '#4', name: 'h3.polyfill', fields: 'cell_count', time: '0.8 s' },
  { id: '#5', name: 'orbit.revisit', fields: 'median_revisit_min', time: '0.6 s' },
  { id: '#6', name: 'episodes.cluster', fields: 'time_window_min', time: '1.9 s' },
];

export const ACTION_B = {
  en: 'Dispatch two teams to the 13 H3 Res 8 cells at the next overpass.',
  vi: 'Điều hai đội đến 13 ô H3 cấp 8 ở lượt bay qua kế tiếp.',
};

export const SCOPE_B = {
  en: 'Spatial · two teams · next overpass',
  vi: 'Theo không gian · hai đội · lượt bay kế tiếp',
};
