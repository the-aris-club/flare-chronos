/**
 * Build the static map data used by the Workbench map pane.
 *
 * Input: apps/workbench/.cache/map-points.json, produced by
 * scripts/flag-map-points.py from the real NASA FIRMS slices. That step owns
 * the physics flags (SZA, SAA, static sources and 60-minute de-duplication) so
 * the map and the harmonization core cannot drift. This script owns the
 * projection and the country geometry.
 *
 * The base layers are Natural Earth 1:10m (public domain): countries from world-atlas,
 * rivers and lakes from natural-earth-vector. Shaded relief is rendered separately by
 * scripts/build-map-relief.py from the grid this script writes, so it lands on exactly
 * the same Lambert projection as the points.
 *
 * Run from apps/workbench (download the inputs once into .cache/ne):
 *   ../../.venv/bin/python scripts/flag-map-points.py
 *   bun scripts/build-map-data.mjs
 *   ../../.venv/bin/python -I scripts/build-map-relief.py
 *
 *   curl -sSL -o .cache/ne/atlas/countries-10m.json \
 *     https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-10m.json
 *   curl -sSL -o .cache/ne/vector/ne_10m_rivers_lake_centerlines.geojson \
 *     https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_rivers_lake_centerlines.geojson
 *   curl -sSL -o .cache/ne/vector/ne_10m_lakes.geojson \
 *     https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_lakes.geojson
 *   (relief: SR_HR.zip from https://naturalearth.s3.amazonaws.com/10m_raster/, see build-map-relief.py)
 */
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import nodePath from 'node:path';
import { geoAzimuthalEqualArea, geoBounds, geoGraticule10, geoPath } from 'd3-geo';
import { feature, merge, mesh } from 'topojson-client';
import { REGION_DEFS } from '../src/lib/workbench/regions';

const ROOT = nodePath.resolve(nodePath.dirname(fileURLToPath(import.meta.url)), '../../..');
const APP = nodePath.resolve(ROOT, 'apps/workbench');
const OUT = nodePath.resolve(APP, 'src/data/map-data.json');
const NE = nodePath.resolve(APP, '.cache/ne');
const ATLAS = process.env.WORLD_ATLAS_PATH ?? nodePath.resolve(NE, 'atlas/countries-10m.json');
const RIVERS = nodePath.resolve(NE, 'vector/ne_10m_rivers_lake_centerlines.geojson');
const LAKES = nodePath.resolve(NE, 'vector/ne_10m_lakes.geojson');
const GRID_DIR = nodePath.resolve(APP, '.cache/relief-grid');
/** Relief is rendered at this multiple of the viewBox so it stays sharp when zoomed. */
const RELIEF_SCALE = 2;
/**
 * The pane is wider (or taller) than the 1000x730 viewBox, and `meet` shows the extra space.
 * Base layers are drawn this far past each edge so that space is map, not blank.
 */
const PAD = { x: 450, y: 260 };
const POINTS = process.env.MAP_POINTS_PATH ?? nodePath.resolve(APP, '.cache/map-points.json');
const WIDTH = 1000;
const HEIGHT = 730;

const world = JSON.parse(readFileSync(ATLAS, 'utf8'));
const flagged = JSON.parse(readFileSync(POINTS, 'utf8'));
const rivers = JSON.parse(readFileSync(RIVERS, 'utf8')).features;
const lakes = JSON.parse(readFileSync(LAKES, 'utf8')).features;

function haversineKm(a, b) {
  const radius = 6371;
  const dLat = ((b[1] - a[1]) * Math.PI) / 180;
  const dLon = ((b[0] - a[0]) * Math.PI) / 180;
  const lat1 = (a[1] * Math.PI) / 180;
  const lat2 = (b[1] * Math.PI) / 180;
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon / 2) ** 2;
  return 2 * radius * Math.asin(Math.min(1, Math.sqrt(h)));
}

function intersects(a, b) {
  return !(a[1][0] < b[0] || a[0][0] > b[2] || a[1][1] < b[1] || a[0][1] > b[3]);
}

function buildProjection(region) {
  const [west, south, east, north] = region.bbox;
  const fit = {
    type: 'MultiPoint',
    coordinates: [
      [west, south],
      [east, south],
      [east, north],
      [west, north],
      ...(region.fit ?? []),
    ],
  };
  return geoAzimuthalEqualArea()
    .rotate([-(west + east) / 2, -(south + north) / 2])
    .fitExtent(
      [
        [26, 26],
        [WIDTH - 26, HEIGHT - 26],
      ],
      fit,
    );
}

function buildBase(region) {
  const projection = buildProjection(region);
  // Detail beyond the canvas is dead weight in a 1:10m dataset; 0.01 viewBox units is far
  // below a pixel at the 64x maximum zoom.
  // Clipping only affects streamed geometry; projecting a single point is unchanged.
  projection.clipExtent([
    [-PAD.x, -PAD.y],
    [WIDTH + PAD.x, HEIGHT + PAD.y],
  ]);
  const projectPath = geoPath(projection).digits(2);
  const islands = (region.islands ?? []).map((island) => {
    const [west, south, east, north] = island.box;
    const ring = [
      [west, south],
      [west, north],
      [east, north],
      [east, south],
      [west, south],
    ];
    const label = projection(island.label);
    return {
      id: island.id,
      boxPath: projectPath({ type: 'Polygon', coordinates: [ring] }),
      label: label ? { x: label[0], y: label[1] } : null,
      points: island.points
        .map((point) => {
          const projected = projection([point.lon, point.lat]);
          return projected ? { name: point.name, x: projected[0], y: projected[1] } : null;
        })
        .filter(Boolean),
    };
  });
  const countries = feature(world, world.objects.countries).features;
  const visible = countries.filter((country) => intersects(geoBounds(country), region.bbox));
  const nearby = (country) => intersects(geoBounds(country), region.bbox);
  const land = merge(
    world,
    world.objects.countries.geometries.filter((geometry) =>
      visible.some((country) => String(country.id) === String(geometry.id)),
    ),
  );
  const coverage = merge(
    world,
    world.objects.countries.geometries.filter((geometry) =>
      region.focus.includes(String(geometry.id)),
    ),
  );
  const saaRing = [];
  for (let index = 0; index <= 72; index += 1) {
    const angle = (index / 72) * 2 * Math.PI;
    saaRing.push([
      flagged.saaZone.lon + flagged.saaZone.rx * Math.cos(angle),
      flagged.saaZone.lat + flagged.saaZone.ry * Math.sin(angle),
    ]);
  }

  const center = [(region.bbox[0] + region.bbox[2]) / 2, (region.bbox[1] + region.bbox[3]) / 2];
  const east = [center[0] + 0.01, center[1]];
  const p1 = projection(center);
  const p2 = projection(east);
  const pxPerKm = Math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / haversineKm(center, east);

  const [qw, qs, qe, qn] = region.queryBox;
  const queryRing = [
    [qw, qs],
    [qw, qn],
    [qe, qn],
    [qe, qs],
    [qw, qs],
  ];

  return {
    bbox: region.bbox,
    queryBox: region.queryBox,
    queryBoxPath: projectPath({ type: 'Polygon', coordinates: [queryRing] }),
    projection,
    pxPerKm,
    saaPath: projectPath({ type: 'Polygon', coordinates: [saaRing] }),
    coveragePath: projectPath(coverage),
    landPath: projectPath(land),
    rivers: projectPath({ type: 'FeatureCollection', features: rivers.filter(nearby) }),
    lakes: projectPath({ type: 'FeatureCollection', features: lakes.filter(nearby) }),
    islands,
    countries: visible.map((country) => ({
      id: String(country.id),
      d: projectPath(country),
      focus: region.focus.includes(String(country.id)),
    })),
    borders: projectPath(mesh(world, world.objects.countries, (a, b) => a !== b)),
    graticule: projectPath(geoGraticule10()),
  };
}

/** lon/lat under every relief pixel, for scripts/build-map-relief.py to sample the raster. */
function writeReliefGrid(name, projection) {
  const width = Math.round((WIDTH + 2 * PAD.x) * RELIEF_SCALE);
  const height = Math.round((HEIGHT + 2 * PAD.y) * RELIEF_SCALE);
  const grid = new Float32Array(width * height * 2).fill(Number.NaN);
  for (let row = 0; row < height; row += 1) {
    for (let column = 0; column < width; column += 1) {
      const lonLat = projection.invert([
        -PAD.x + ((column + 0.5) / width) * (WIDTH + 2 * PAD.x),
        -PAD.y + ((row + 0.5) / height) * (HEIGHT + 2 * PAD.y),
      ]);
      if (!lonLat) continue;
      const at = (row * width + column) * 2;
      grid[at] = lonLat[0];
      grid[at + 1] = lonLat[1];
    }
  }
  mkdirSync(GRID_DIR, { recursive: true });
  writeFileSync(nodePath.resolve(GRID_DIR, `${name}.f32`), Buffer.from(grid.buffer));
  writeFileSync(nodePath.resolve(GRID_DIR, `${name}.json`), JSON.stringify({ width, height }));
}

function projectPoints(epoch, projection) {
  const points = [];
  for (const [
    index,
    [lon, lat, sensor, flags, scan, track, angle, platform, daynight],
  ] of epoch.points.entries()) {
    const projected = projection([lon, lat]);
    if (!projected) continue;
    points.push({
      i: index,
      x: Math.round(projected[0] * 10) / 10,
      y: Math.round(projected[1] * 10) / 10,
      s: sensor,
      f: flags,
      sc: scan,
      tr: track,
      ang: angle,
      pf: platform,
      dn: daynight,
    });
  }
  return { points, counts: epoch.counts };
}

const output = {
  width: WIDTH,
  height: HEIGHT,
  pad: PAD,
  saa: flagged.saaZone,
  regions: {},
};

for (const [region, config] of Object.entries(REGION_DEFS)) {
  const base = buildBase(config);
  writeReliefGrid(region, base.projection);
  const staticSources = config.staticSources
    .map((source) => {
      const projected = base.projection([source.lon, source.lat]);
      return projected ? { id: source.id, x: projected[0], y: projected[1] } : null;
    })
    .filter(Boolean);
  const epochs = {};
  const counts = {};
  for (const [year, epoch] of Object.entries(flagged.regions[region] ?? {})) {
    const projected = projectPoints(epoch, base.projection);
    epochs[year] = projected.points;
    counts[year] = projected.counts;
  }

  output.regions[region] = {
    bbox: base.bbox,
    queryBox: base.queryBox,
    queryBoxPath: base.queryBoxPath,
    pxPerKm: base.pxPerKm,
    saaPath: base.saaPath,
    coveragePath: base.coveragePath,
    landPath: base.landPath,
    rivers: base.rivers,
    lakes: base.lakes,
    islands: base.islands,
    staticSources,
    countries: base.countries,
    borders: base.borders,
    graticule: base.graticule,
    epochs,
    counts,
  };

  const summary = Object.entries(epochs)
    .map(([year, points]) => `${year}:${points.length}`)
    .join(' ');
  console.warn(`${region}: ${base.countries.length} countries · ${summary}`);
}

writeFileSync(OUT, JSON.stringify(output));
console.warn(`wrote ${OUT} (${Math.round(JSON.stringify(output).length / 1024)} KB)`);
