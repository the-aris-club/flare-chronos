import * as THREE from 'three';
import type { RegionId } from '@/lib/calendar/types';
import { GLOBE_DATA, lonLatToVec } from './data';

type Flight = {
  id: RegionId;
  start: number;
  duration: number;
  fromDirection: THREE.Vector3;
  toDirection: THREE.Vector3;
  fromDistance: number;
  toDistance: number;
  fromOffset: { x: number; y: number };
};

function ease(value: number): number {
  return value < 0.5 ? 4 * value ** 3 : 1 - (-2 * value + 2) ** 3 / 2;
}

export class CameraFlight {
  private flight: Flight | null = null;

  constructor(
    private readonly camera: THREE.PerspectiveCamera,
    private readonly size: () => { width: number; height: number },
    private readonly setOffset: (x: number, y: number) => void,
    private readonly onArrive: (region: RegionId) => void,
    private readonly reducedMotion: boolean,
  ) {}

  get active(): boolean {
    return this.flight !== null;
  }

  start(region: RegionId, fromOffset: { x: number; y: number }) {
    if (this.flight) return;
    const data = GLOBE_DATA.regions[region];
    const { width, height } = this.size();
    const aspect = Math.max(1, height / Math.max(1, width));
    const base = region === 'mekong' ? 2.15 : 2.4;

    this.flight = {
      id: region,
      start: performance.now(),
      duration: this.reducedMotion ? 200 : 1700,
      fromDirection: this.camera.position.clone().normalize(),
      toDirection: new THREE.Vector3(...lonLatToVec(data.anchor[0], data.anchor[1], 1)).normalize(),
      fromDistance: this.camera.position.length(),
      toDistance: 1 + (base - 1) * aspect,
      fromOffset: { ...fromOffset },
    };
  }

  step(now: number) {
    const flight = this.flight;
    if (!flight) return;

    const progress = Math.min(1, (now - flight.start) / flight.duration);
    const eased = ease(progress);
    const rotation = new THREE.Quaternion().setFromUnitVectors(
      flight.fromDirection,
      flight.toDirection,
    );
    const partial = new THREE.Quaternion().slerp(rotation, eased);
    const direction = flight.fromDirection.clone().applyQuaternion(partial).normalize();

    this.camera.position.copy(
      direction.multiplyScalar(
        flight.fromDistance + (flight.toDistance - flight.fromDistance) * eased,
      ),
    );
    this.camera.lookAt(0, 0, 0);
    this.setOffset(
      flight.fromOffset.x + (0 - flight.fromOffset.x) * eased,
      flight.fromOffset.y + (0 - flight.fromOffset.y) * eased,
    );

    if (progress >= 1) {
      this.flight = null;
      this.onArrive(flight.id);
    }
  }
}
