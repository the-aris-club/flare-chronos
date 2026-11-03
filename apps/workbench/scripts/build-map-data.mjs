/**
 * Build the static map data used by the Workbench map pane.
 *
 * Input: apps/workbench/.cache/map-points.json, produced by
 * scripts/flag-map-points.py from the real NASA FIRMS slices. That step owns
 * the physics flags (SZA, SAA, static sources and 60-minute de-duplication) so
 * the map and the harmonization core cannot drift. This script owns the
 * projection and the country geometry.
 *
 * Run from apps/workbench:
 *   ../../.venv/bin/python scripts/flag-map-points.py
 *   WORLD_ATLAS_PATH=/path/to/countries-110m.json bun scripts/build-map-data.mjs
 *
 * Download the atlas once:
 *   curl -sSL -o countries-110m.json \
 *     https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import nodePath from 'node:path';
import { geoAzimuthalEqualArea, geoBounds, geoGraticule10, geoPath } from 'd3-geo';
import { feature, merge, mesh } from 'topojson-client';
import { REGION_DEFS } from '../src/lib/workbench/regions';

const ROOT = nodePath.resolve(nodePath.dirname(fileURLToPath(import.meta.url)), '../../..');
const APP = nodePath.resolve(ROOT, 'apps/workbench');
const OUT = nodePath.resolve(APP, 'src/data/map-data.json');
const ATLAS = process.env.WORLD_ATLAS_PATH ?? nodePath.resolve(APP, 'countries-110m.json');
const POINTS = process.env.MAP_POINTS_PATH ?? nodePath.resolve(APP, '.cache/map-points.json');
const WIDTH = 1000;
const HEIGHT = 730;

const world = JSON.parse(readFileSync(ATLAS, 'utf8'));
const flagged = JSON.parse(readFileSync(POINTS, 'utf8'));

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
  const projectPath = geoPath(projection);
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

  return {
    bbox: region.bbox,
    projection,
    pxPerKm,
    saaPath: projectPath({ type: 'Polygon', coordinates: [saaRing] }),
    coveragePath: projectPath(coverage),
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
  saa: flagged.saaZone,
  regions: {},
};

for (const [region, config] of Object.entries(REGION_DEFS)) {
  const base = buildBase(config);
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
    pxPerKm: base.pxPerKm,
    saaPath: base.saaPath,
    coveragePath: base.coveragePath,
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
  console.log(`${region}: ${base.countries.length} countries · ${summary}`);
}

writeFileSync(OUT, JSON.stringify(output));
console.log(`wrote ${OUT} (${Math.round(JSON.stringify(output).length / 1024)} KB)`);
