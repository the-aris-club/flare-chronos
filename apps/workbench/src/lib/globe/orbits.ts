import * as THREE from 'three';
import { css } from './textures';

const DEG = Math.PI / 180;

const ORBITS = [
  { radius: 1.13, inclination: 98.2, raan: 20, phase: 0, speed: 0.22 },
  { radius: 1.15, inclination: 98.7, raan: 75, phase: 2.1, speed: 0.19 },
  { radius: 1.17, inclination: 98.7, raan: 130, phase: 4.2, speed: 0.205 },
];

type Satellite = {
  mesh: THREE.Mesh;
  radius: number;
  angle: number;
  speed: number;
};

export type Orbits = {
  group: THREE.Group;
  update: (delta: number) => void;
  setTheme: (theme: 'dark' | 'light') => void;
  dispose: () => void;
};

export function createOrbits(): Orbits {
  const group = new THREE.Group();
  group.name = 'satellite-orbits';

  const lineMaterial = new THREE.LineDashedMaterial({
    color: css('--text-subtle'),
    dashSize: 0.025,
    gapSize: 0.022,
    transparent: true,
    opacity: 0.5,
  });
  const bodyMaterial = new THREE.MeshBasicMaterial({
    color: css('--text'),
    transparent: true,
    opacity: 0.95,
  });

  const satellites: Satellite[] = [];
  const geometries: THREE.BufferGeometry[] = [];

  for (const orbit of ORBITS) {
    const ring = new THREE.Group();
    ring.rotation.order = 'YXZ';
    ring.rotation.y = orbit.raan * DEG;
    ring.rotation.x = (orbit.inclination - 90) * DEG;

    const points: THREE.Vector3[] = [];
    for (let step = 0; step <= 180; step += 1) {
      const angle = (step / 180) * Math.PI * 2;
      points.push(
        new THREE.Vector3(orbit.radius * Math.cos(angle), orbit.radius * Math.sin(angle), 0),
      );
    }

    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const path = new THREE.Line(geometry, lineMaterial);
    path.computeLineDistances();
    path.name = 'orbit-ring';

    const bodyGeometry = new THREE.BoxGeometry(0.018, 0.018, 0.018);
    const panelGeometry = new THREE.BoxGeometry(0.05, 0.003, 0.014);
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
    const panel = new THREE.Mesh(panelGeometry, bodyMaterial);
    body.name = 'satellite';
    body.add(panel);
    body.position.set(
      orbit.radius * Math.cos(orbit.phase),
      orbit.radius * Math.sin(orbit.phase),
      0,
    );

    geometries.push(geometry, bodyGeometry, panelGeometry);
    ring.add(path, body);
    group.add(ring);
    satellites.push({
      mesh: body,
      radius: orbit.radius,
      angle: orbit.phase,
      speed: orbit.speed,
    });
  }

  return {
    group,
    update(delta) {
      for (const satellite of satellites) {
        satellite.angle += delta * satellite.speed;
        satellite.mesh.position.set(
          satellite.radius * Math.cos(satellite.angle),
          satellite.radius * Math.sin(satellite.angle),
          0,
        );
        satellite.mesh.rotation.z = satellite.angle;
      }
    },
    setTheme(theme) {
      lineMaterial.color.set(css('--text-subtle'));
      lineMaterial.opacity = theme === 'dark' ? 0.5 : 0.4;
      bodyMaterial.color.set(css('--text'));
    },
    dispose() {
      for (const geometry of geometries) geometry.dispose();
      lineMaterial.dispose();
      bodyMaterial.dispose();
    },
  };
}
