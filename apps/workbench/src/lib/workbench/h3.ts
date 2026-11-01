import type { MapPoint } from './map-data';

/** Uber H3 cell edge length in km at the equator (resolution 4–8). */
const EDGE_KM: Record<number, number> = {
  4: 22.61,
  5: 8.54,
  6: 3.23,
  7: 1.22,
  8: 0.46,
};

export type HexBin = { x: number; y: number; count: number };

export function displayResolution(zoom: number, grid: number): number {
  const natural = zoom < 3 ? 4 : zoom < 8 ? 5 : zoom < 22 ? 6 : zoom < 58 ? 7 : 8;
  return Math.min(natural, grid);
}

export function hexEdge(resolution: number, pxPerKm: number): number {
  return (EDGE_KM[resolution] ?? EDGE_KM[7]) * pxPerKm;
}

function cubeRound(q: number, r: number): [number, number] {
  const x = q;
  const z = r;
  const y = -x - z;
  let rx = Math.round(x);
  let ry = Math.round(y);
  let rz = Math.round(z);
  const dx = Math.abs(rx - x);
  const dy = Math.abs(ry - y);
  const dz = Math.abs(rz - z);

  if (dx > dy && dx > dz) rx = -ry - rz;
  else if (dy > dz) ry = -rx - rz;
  else rz = -rx - ry;

  return [rx, rz];
}

export function binDetections(points: MapPoint[], edge: number): HexBin[] {
  if (edge <= 0) return [];
  const root = Math.sqrt(3);
  const bins = new Map<string, number>();

  for (const point of points) {
    const q = ((root / 3) * point.x - point.y / 3) / edge;
    const r = ((2 / 3) * point.y) / edge;
    const [a, b] = cubeRound(q, r);
    const key = `${a},${b}`;
    bins.set(key, (bins.get(key) ?? 0) + 1);
  }

  const result: HexBin[] = [];
  for (const [key, count] of bins) {
    const [a, b] = key.split(',').map(Number);
    result.push({ x: edge * root * (a + b / 2), y: edge * 1.5 * b, count });
  }
  return result;
}

export function hexPath(edge: number): string {
  const corners: string[] = [];
  for (let index = 0; index < 6; index += 1) {
    const angle = ((60 * index - 30) * Math.PI) / 180;
    corners.push(`${(edge * Math.cos(angle)).toFixed(2)},${(edge * Math.sin(angle)).toFixed(2)}`);
  }
  return `M${corners.join('L')}Z`;
}

const RAMP = [0.16, 0.3, 0.45, 0.6, 0.78] as const;

export function hexOpacity(count: number, max: number): number {
  if (max <= 0) return 0;
  const step = Math.min(RAMP.length - 1, Math.floor(Math.sqrt(count / max) * RAMP.length));
  return RAMP[step];
}
