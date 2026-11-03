import type { Camera, Scene, WebGLRenderer } from 'three';
import { css } from './textures';

/** Render the current frame and return a JPEG data URL for the route morph. */
export function captureFrame(
  renderer: WebGLRenderer,
  scene: Scene,
  camera: Camera,
  canvas: HTMLCanvasElement,
): string | null {
  renderer.render(scene, camera);
  if (canvas.width === 0 || canvas.height === 0) return null;

  const offscreen = document.createElement('canvas');
  offscreen.width = canvas.width;
  offscreen.height = canvas.height;
  const context = offscreen.getContext('2d');
  if (!context) return null;
  context.fillStyle = css('--bg');
  context.fillRect(0, 0, offscreen.width, offscreen.height);
  context.drawImage(canvas, 0, 0);

  try {
    return offscreen.toDataURL('image/jpeg', 0.84);
  } catch {
    return null;
  }
}
