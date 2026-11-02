import { describe, expect, test } from 'bun:test';
import results from '../../../../../data/processed/empirical_results.json';
import { FACTS_B } from './review-facts';

const physics = results.scan_angle_physics;

describe('sample brief facts agree with the published physics', () => {
  test('VIIRS nadir pixel area is the core value', () => {
    expect(Number(FACTS_B.viirs.raw)).toBeCloseTo(physics.viirs_nadir_area_km2, 4);
  });

  test('the MODIS-edge to VIIRS-nadir ratio is the core value', () => {
    expect(Number(FACTS_B.reduction.raw)).toBeCloseTo(
      physics.max_area_ratio_modis_edge_to_viirs_nadir,
      2,
    );
  });

  test('the ratio follows from the two published areas', () => {
    const ratio = physics.modis_edge_55deg_area_km2 / physics.viirs_nadir_area_km2;
    expect(Number(FACTS_B.reduction.raw)).toBeCloseTo(ratio, 1);
  });

  test('the duplicate window is the 60 minutes the core clusters with', () => {
    expect(FACTS_B.cluster.raw).toBe('60');
  });
});
