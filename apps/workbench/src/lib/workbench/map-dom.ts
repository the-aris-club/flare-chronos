export function screenToViewBox(
  svg: SVGSVGElement | null,
  clientX: number,
  clientY: number,
  width: number,
  height: number,
) {
  if (!svg) return { x: width / 2, y: height / 2 };
  const point = svg.createSVGPoint();
  point.x = clientX;
  point.y = clientY;
  const matrix = svg.getScreenCTM();
  if (!matrix) return { x: width / 2, y: height / 2 };
  const local = point.matrixTransform(matrix.inverse());
  return { x: local.x, y: local.y };
}
