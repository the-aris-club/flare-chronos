import * as THREE from 'three';
import type { GlobeData } from './types';

export function css(name: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function canvasTexture(
  width: number,
  height: number,
  anisotropy: number,
  paint: (context: CanvasRenderingContext2D) => void,
): THREE.CanvasTexture {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const context = canvas.getContext('2d');

  if (!context) throw new Error('Globe: 2D canvas is unavailable');

  paint(context);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = anisotropy;
  texture.needsUpdate = true;

  return texture;
}

export function makeVectorSurface(data: GlobeData, anisotropy: number): THREE.CanvasTexture {
  const ocean = css('--map-ocean');
  const land = css('--map-land');
  const grating = css('--map-grat');

  return canvasTexture(data.width, data.height, anisotropy, (context) => {
    context.fillStyle = ocean;
    context.fillRect(0, 0, data.width, data.height);

    context.fillStyle = land;
    context.fill(new Path2D(data.land), 'evenodd');

    context.strokeStyle = grating;
    context.lineWidth = 1;
    context.stroke(new Path2D(data.graticule));
  });
}

export function makeBordersTexture(data: GlobeData, anisotropy: number): THREE.CanvasTexture {
  const color = css('--map-border');

  return canvasTexture(data.width, data.height, anisotropy, (context) => {
    context.strokeStyle = color;
    context.lineWidth = 1.4;
    context.lineJoin = 'round';
    context.stroke(new Path2D(data.borders));
  });
}

export function makeCoverageTextures(
  coverage: string,
  anisotropy: number,
): { fill: THREE.CanvasTexture; line: THREE.CanvasTexture } {
  const shape = new Path2D(coverage);

  const fill = canvasTexture(2048, 1024, anisotropy, (context) => {
    context.fillStyle = 'white';
    context.fill(shape, 'evenodd');
  });

  const line = canvasTexture(2048, 1024, anisotropy, (context) => {
    context.strokeStyle = 'white';
    context.lineWidth = 2.4;
    context.lineJoin = 'round';
    context.stroke(shape);
  });

  return { fill, line };
}

export function loadEarthPhoto(
  anisotropy: number,
  onLoad: (texture: THREE.Texture) => void,
  onError: () => void,
): THREE.Texture {
  const texture = new THREE.TextureLoader().load(
    '/globe/earth.jpg',
    (loaded) => {
      loaded.colorSpace = THREE.SRGBColorSpace;
      loaded.anisotropy = anisotropy;
      onLoad(loaded);
    },
    undefined,
    onError,
  );

  return texture;
}
