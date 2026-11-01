import * as THREE from 'three';
import type { RegionId } from '@/lib/calendar/types';
import { GLOBE_DATA, vecToLonLat } from './data';

const REGION_IDS = Object.keys(GLOBE_DATA.regions) as RegionId[];

export class RegionPicker {
  private readonly raycaster = new THREE.Raycaster();
  private readonly pointer = new THREE.Vector2();
  private context: CanvasRenderingContext2D | null = null;
  private readonly paths = new Map<RegionId, Path2D>();

  pick(
    event: PointerEvent,
    canvas: HTMLCanvasElement,
    camera: THREE.Camera,
    surface: THREE.Object3D,
    earth: THREE.Object3D,
  ): RegionId | null {
    const rect = canvas.getBoundingClientRect();
    this.pointer.set(
      ((event.clientX - rect.left) / rect.width) * 2 - 1,
      -((event.clientY - rect.top) / rect.height) * 2 + 1,
    );
    this.raycaster.setFromCamera(this.pointer, camera);
    const hit = this.raycaster.intersectObject(surface, false)[0];
    if (!hit) return null;

    const local = earth.worldToLocal(hit.point.clone());
    const [lon, lat] = vecToLonLat(local.x, local.y, local.z);
    this.ensureContext();

    for (const id of REGION_IDS) {
      const [west, south, east, north] = GLOBE_DATA.regions[id].bbox;
      if (lon < west || lon > east || lat < south || lat > north) continue;
      if (!this.context || this.contains(id, lon, lat)) return id;
    }

    return null;
  }

  private ensureContext() {
    if (this.context) return;
    const canvas = document.createElement('canvas');
    canvas.width = GLOBE_DATA.width;
    canvas.height = GLOBE_DATA.height;
    this.context = canvas.getContext('2d');
  }

  private contains(id: RegionId, lon: number, lat: number): boolean {
    if (!this.context) return true;
    let path = this.paths.get(id);
    if (!path) {
      path = new Path2D(GLOBE_DATA.regions[id].coverage);
      this.paths.set(id, path);
    }
    const x = ((lon + 180) / 360) * GLOBE_DATA.width;
    const y = ((90 - lat) / 180) * GLOBE_DATA.height;

    return this.context.isPointInPath(path, x, y);
  }
}

type PointerOptions = {
  canvas: HTMLCanvasElement;
  picker: RegionPicker;
  camera: THREE.Camera;
  surface: THREE.Object3D;
  earth: THREE.Object3D;
  isIdle: () => boolean;
  onHover: (region: RegionId | null) => void;
  onSelect: (region: RegionId) => void;
};

export function bindRegionPointer({
  canvas,
  picker,
  camera,
  surface,
  earth,
  isIdle,
  onHover,
  onSelect,
}: PointerOptions): () => void {
  let down: { x: number; y: number } | null = null;

  const handleMove = (event: PointerEvent) => {
    if (!isIdle()) return;
    onHover(picker.pick(event, canvas, camera, surface, earth));
  };

  const handleLeave = () => {
    onHover(null);
  };

  const handleDown = (event: PointerEvent) => {
    down = { x: event.clientX, y: event.clientY };
  };

  const handleUp = (event: PointerEvent) => {
    const start = down;
    down = null;
    if (!isIdle() || !start) return;
    if (Math.hypot(event.clientX - start.x, event.clientY - start.y) > 6) return;
    const region = picker.pick(event, canvas, camera, surface, earth);
    if (region) onSelect(region);
  };

  canvas.addEventListener('pointermove', handleMove);
  canvas.addEventListener('pointerleave', handleLeave);
  canvas.addEventListener('pointerdown', handleDown);
  canvas.addEventListener('pointerup', handleUp);

  return () => {
    canvas.removeEventListener('pointermove', handleMove);
    canvas.removeEventListener('pointerleave', handleLeave);
    canvas.removeEventListener('pointerdown', handleDown);
    canvas.removeEventListener('pointerup', handleUp);
  };
}
