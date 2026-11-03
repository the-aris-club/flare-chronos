import * as THREE from 'three';
import { css } from './textures';

function seeded(seed: number): () => number {
  let state = seed;
  return () => {
    state |= 0;
    state = (state + 0x6d2b79f5) | 0;
    let value = Math.imul(state ^ (state >>> 15), 1 | state);
    value = (value + Math.imul(value ^ (value >>> 7), 61 | value)) ^ value;
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
}

export function createStars(): THREE.Points {
  const random = seeded(20261101);
  const positions: number[] = [];

  for (let index = 0; index < 1400; index += 1) {
    const u = random() * 2 - 1;
    const theta = random() * Math.PI * 2;
    const radius = 60;
    const scale = Math.sqrt(1 - u * u);
    positions.push(radius * scale * Math.cos(theta), radius * u, radius * scale * Math.sin(theta));
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));

  return new THREE.Points(
    geometry,
    new THREE.PointsMaterial({
      color: css('--text-subtle'),
      size: 1.1,
      sizeAttenuation: false,
      transparent: true,
      opacity: 0.55,
    }),
  );
}
