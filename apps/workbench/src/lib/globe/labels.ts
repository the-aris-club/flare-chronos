import type * as THREE from 'three';
import type { RegionId } from '@/lib/calendar/types';
import { GLOBE_DATA, lonLatToVec } from './data';

const widths = new WeakMap<HTMLDivElement, number>();

export function updateGlobeLabels(
  labels: Partial<Record<RegionId, HTMLDivElement | null>>,
  camera: THREE.Camera,
  earth: THREE.Object3D,
  width: number,
  height: number,
): void {
  const cameraDirection = camera.position.clone().normalize();
  const ids = Object.keys(GLOBE_DATA.regions) as RegionId[];

  for (const id of ids) {
    const element = labels[id];
    if (!element) continue;

    const [lon, lat] = GLOBE_DATA.regions[id].anchor;
    const point = camera.position.clone().set(...lonLatToVec(lon, lat, 1.01));
    earth.localToWorld(point);
    const facing = point.clone().normalize().dot(cameraDirection);
    const projected = point.project(camera);
    const x = ((projected.x + 1) / 2) * width;
    const y = ((1 - projected.y) / 2) * height;
    const labelWidth = widths.get(element) ?? element.offsetWidth;
    widths.set(element, labelWidth);
    const left = Math.min(Math.max(x + 12, 8), width - labelWidth - 8);
    const top = Math.min(Math.max(y, 24), height - 24);

    element.style.transform = `translate(${left}px, ${top}px) translateY(-50%)`;
    element.style.opacity = facing > 0.25 ? '1' : '0';
  }
}
