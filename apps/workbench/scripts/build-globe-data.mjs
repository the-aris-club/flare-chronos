/**
 * Build the static globe data used by the landing page.
 *
 * Output: src/data/globe-data.json — equirectangular SVG paths for the land
 * mask, country borders, graticule and the two measured-region silhouettes.
 * The runtime draws them into canvas textures; no d3 or topojson ships.
 *
 * Run from apps/workbench:
 *   WORLD_ATLAS_PATH=/path/to/countries-110m.json \
 *     bun scripts/build-globe-data.mjs
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import nodePath from 'node:path';
import { geoEquirectangular, geoGraticule10, geoPath } from 'd3-geo';
import { feature, merge, mesh } from 'topojson-client';
import { REGION_DEFS } from '../src/lib/workbench/regions';

const ROOT = nodePath.resolve(nodePath.dirname(fileURLToPath(import.meta.url)), '../../..');
const APP = nodePath.resolve(ROOT, 'apps/workbench');
const OUT = nodePath.resolve(APP, 'src/data/globe-data.json');
const ATLAS =
  process.env.WORLD_ATLAS_PATH ?? nodePath.resolve(ROOT, 'apps/workbench/countries-110m.json');

const WIDTH = 2048;
const HEIGHT = 1024;

const world = JSON.parse(readFileSync(ATLAS, 'utf8'));
const projection = geoEquirectangular()
  .scale(WIDTH / (2 * Math.PI))
  .translate([WIDTH / 2, HEIGHT / 2]);
const path = geoPath(projection);

const land = feature(world, world.objects.land);
const borders = mesh(world, world.objects.countries, (a, b) => a !== b);
const graticule = geoGraticule10();

const output = {
  width: WIDTH,
  height: HEIGHT,
  land: path(land),
  borders: path(borders),
  graticule: path(graticule),
  regions: {},
};

for (const [id, config] of Object.entries(REGION_DEFS)) {
  const geometries = world.objects.countries.geometries.filter((geometry) =>
    config.focus.includes(String(geometry.id)),
  );
  const coverage = merge(world, geometries);

  output.regions[id] = {
    bbox: config.bbox,
    anchor: config.anchor,
    coverage: path(coverage),
  };
}

writeFileSync(OUT, JSON.stringify(output));
const kb = Math.round(JSON.stringify(output).length / 1024);
console.log(`wrote ${OUT} (${kb} KB)`);
