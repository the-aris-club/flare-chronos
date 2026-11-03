import * as THREE from 'three';
import type { RegionId } from '@/lib/calendar/types';
import { GLOBE_DATA } from './data';
import { css, makeBordersTexture, makeCoverageTextures, makeVectorSurface } from './textures';

type Coverage = {
  fill: THREE.MeshBasicMaterial;
  line: THREE.MeshBasicMaterial;
};

export type Earth = {
  group: THREE.Group;
  surface: THREE.Mesh<THREE.SphereGeometry, THREE.MeshStandardMaterial>;
  coverage: Record<RegionId, Coverage>;
  setTheme: (theme: 'dark' | 'light', photo: THREE.Texture | null) => void;
  applySurface: (theme: 'dark' | 'light', photo: THREE.Texture | null) => void;
  dispose: () => void;
};

const REGION_IDS = Object.keys(GLOBE_DATA.regions) as RegionId[];

export function createEarth(theme: 'dark' | 'light', anisotropy: number): Earth {
  const group = new THREE.Group();
  group.name = 'earth';

  let vector: THREE.CanvasTexture | null = null;
  let vectorTheme: 'dark' | 'light' | null = null;
  let borderTexture: THREE.CanvasTexture | null = null;

  const surface = new THREE.Mesh(
    new THREE.SphereGeometry(1, 128, 64),
    new THREE.MeshStandardMaterial({
      map: null,
      roughness: 0.95,
      metalness: 0,
      color: 'white',
    }),
  );
  surface.name = 'earth-surface';
  group.add(surface);

  const borderMaterial = new THREE.MeshBasicMaterial({
    transparent: true,
    depthWrite: false,
    side: THREE.DoubleSide,
  });
  const borderMesh = new THREE.Mesh(new THREE.SphereGeometry(1.002, 128, 64), borderMaterial);
  borderMesh.name = 'country-borders';
  group.add(borderMesh);

  const coverage = {} as Record<RegionId, Coverage>;
  for (const id of REGION_IDS) {
    const textures = makeCoverageTextures(GLOBE_DATA.regions[id].coverage, anisotropy);
    const fill = new THREE.MeshBasicMaterial({
      map: textures.fill,
      color: css('--amber'),
      transparent: true,
      opacity: 0.22,
      depthWrite: false,
      side: THREE.DoubleSide,
    });
    const line = new THREE.MeshBasicMaterial({
      map: textures.line,
      color: css('--amber'),
      transparent: true,
      opacity: 0.95,
      depthWrite: false,
      side: THREE.DoubleSide,
    });

    group.add(
      new THREE.Mesh(new THREE.SphereGeometry(1.004, 96, 48), fill),
      new THREE.Mesh(new THREE.SphereGeometry(1.005, 96, 48), line),
    );
    coverage[id] = { fill, line };
  }

  const atmosphere = new THREE.Mesh(
    new THREE.SphereGeometry(1.1, 64, 32),
    new THREE.ShaderMaterial({
      transparent: true,
      side: THREE.BackSide,
      depthWrite: false,
      uniforms: {
        color: { value: new THREE.Color(css('--brand')) },
        alpha: { value: 0.85 },
      },
      vertexShader:
        'varying vec3 vN;void main(){vN=normalize(normalMatrix*normal);gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',
      fragmentShader:
        'uniform vec3 color;uniform float alpha;varying vec3 vN;void main(){float i=pow(clamp(-vN.z,0.0,1.0),1.6);i*=smoothstep(0.0,0.35,-vN.z+0.02);gl_FragColor=vec4(color,i*alpha);}',
    }),
  );
  atmosphere.name = 'atmosphere';
  group.add(atmosphere);

  const sun = new THREE.DirectionalLight('white', 2.2);
  sun.position.set(2, 2, 5);
  const hemi = new THREE.HemisphereLight('white', css('--bg'), 1.0);
  group.add(sun, hemi);

  function applySurface(nextTheme: 'dark' | 'light', photo: THREE.Texture | null) {
    if (nextTheme === 'dark' && photo) {
      surface.material.map = photo;
      vector?.dispose();
      vector = null;
      vectorTheme = null;
    } else {
      if (!vector || vectorTheme !== nextTheme) {
        vector?.dispose();
        vector = makeVectorSurface(GLOBE_DATA, anisotropy);
        vectorTheme = nextTheme;
      }
      surface.material.map = vector;
    }
    surface.material.needsUpdate = true;
  }

  function setTheme(nextTheme: 'dark' | 'light', photo: THREE.Texture | null) {
    const dark = nextTheme === 'dark';
    applySurface(nextTheme, photo);

    borderTexture?.dispose();
    borderTexture = makeBordersTexture(GLOBE_DATA, anisotropy);
    borderMaterial.map = borderTexture;
    borderMaterial.opacity = dark ? 1 : 0.85;
    borderMaterial.needsUpdate = true;

    sun.intensity = dark ? 2.2 : 1.8;
    hemi.intensity = dark ? 1.0 : 1.3;
    hemi.groundColor.set(css('--bg'));
    atmosphere.material.uniforms.color.value.set(css('--brand'));
    atmosphere.material.uniforms.alpha.value = dark ? 0.85 : 0.45;

    for (const id of REGION_IDS) {
      coverage[id].fill.color.set(css('--amber'));
      coverage[id].line.color.set(css('--amber'));
    }
  }

  setTheme(theme, null);

  return {
    group,
    surface,
    coverage,
    setTheme,
    applySurface,
    dispose() {
      group.traverse((object) => {
        if (!(object instanceof THREE.Mesh)) return;
        object.geometry.dispose();
        const materials = Array.isArray(object.material) ? object.material : [object.material];
        for (const material of materials) {
          const map = (material as THREE.MeshBasicMaterial).map;
          if (map) map.dispose();
          material.dispose();
        }
      });
      vector?.dispose();
      borderTexture?.dispose();
    },
  };
}
