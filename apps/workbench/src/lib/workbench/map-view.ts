export type MapView = { x: number; y: number; k: number };

export const MAP_VIEW: MapView = { x: 0, y: 0, k: 1 };
export const MIN_ZOOM = 1;
export const MAX_ZOOM = 64;

export function clampView(view: MapView, width: number, height: number): MapView {
  const k = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, view.k));
  const marginX = width * 0.35;
  const marginY = height * 0.35;
  return {
    k,
    x: Math.min(marginX, Math.max(width - width * k - marginX, view.x)),
    y: Math.min(marginY, Math.max(height - height * k - marginY, view.y)),
  };
}

export function zoomAt(
  view: MapView,
  factor: number,
  anchorX: number,
  anchorY: number,
  width: number,
  height: number,
): MapView {
  const nextK = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, view.k * factor));
  const ratio = nextK / view.k;
  return clampView(
    {
      k: nextK,
      x: anchorX - (anchorX - view.x) * ratio,
      y: anchorY - (anchorY - view.y) * ratio,
    },
    width,
    height,
  );
}

export function panView(
  view: MapView,
  dx: number,
  dy: number,
  width: number,
  height: number,
): MapView {
  return clampView({ ...view, x: view.x + dx, y: view.y + dy }, width, height);
}
