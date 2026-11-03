import raw from '@/data/globe-data.json';
import type { GlobeData } from './types';

const DEG = Math.PI / 180;

export const GLOBE_DATA = raw as GlobeData;

/** Spherical position for a lon/lat pair at radius `r`, matching the texture UV. */
export function lonLatToVec(lon: number, lat: number, r = 1): [x: number, y: number, z: number] {
  const phi = (lon + 180) * DEG;
  const theta = (90 - lat) * DEG;

  return [
    -r * Math.cos(phi) * Math.sin(theta),
    r * Math.cos(theta),
    r * Math.sin(phi) * Math.sin(theta),
  ];
}

export function vecToLonLat(x: number, y: number, z: number): [lon: number, lat: number] {
  const r = Math.hypot(x, y, z);
  const lat = 90 - Math.acos(y / r) / DEG;
  let lon = Math.atan2(z, -x) / DEG - 180;

  if (lon < -180) lon += 360;
  return [lon, lat];
}
