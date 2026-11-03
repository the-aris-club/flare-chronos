import * as THREE from 'three';

const VERTEX = /* glsl */ `
  varying vec3 vDirection;
  void main() {
    vDirection = normalize(position);
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

// Equirectangular lookup plus a screen-space dim so no bright Milky Way core
// ever sits behind the landing copy. Output is converted to sRGB by three.
const FRAGMENT = /* glsl */ `
  uniform sampler2D uMap;
  uniform float uExposure;
  uniform vec2 uViewport;
  uniform float uDimWidth;
  uniform float uDimFloor;
  varying vec3 vDirection;

  const float PI = 3.14159265359;

  void main() {
    vec3 d = normalize(vDirection);
    vec2 uv = vec2(atan(d.z, d.x) / (2.0 * PI) + 0.5, asin(clamp(d.y, -1.0, 1.0)) / PI + 0.5);
    vec3 color = pow(texture2D(uMap, uv).rgb, vec3(1.45)) * uExposure;

    float x = gl_FragCoord.x / uViewport.x;
    float dim = mix(uDimFloor, 1.0, smoothstep(0.0, uDimWidth, x));
    gl_FragColor = vec4(color * dim, 1.0);
    #include <colorspace_fragment>
  }
`;

const STAR_VERTEX = /* glsl */ `
  attribute float aBrightness;
  attribute vec3 aTint;
  uniform float uPixelRatio;
  varying float vBrightness;
  varying vec3 vTint;
  void main() {
    vBrightness = aBrightness;
    vTint = aTint;
    gl_PointSize = (0.9 + 1.7 * smoothstep(0.1, 0.9, aBrightness)) * uPixelRatio;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const STAR_FRAGMENT = /* glsl */ `
  uniform vec2 uViewport;
  uniform float uDimWidth;
  uniform float uDimFloor;
  varying float vBrightness;
  varying vec3 vTint;
  void main() {
    float r = length(gl_PointCoord - 0.5) * 2.0;
    float falloff = 1.0 - smoothstep(0.0, 1.0, r);
    float x = gl_FragCoord.x / uViewport.x;
    float dim = mix(uDimFloor, 1.0, smoothstep(0.0, uDimWidth, x));
    float level = (0.25 + 0.75 * vBrightness) * falloff * falloff * dim;
    gl_FragColor = vec4(mix(vec3(1.0), vTint, 0.55) * level, 1.0);
    #include <colorspace_fragment>
  }
`;

export type Sky = {
  mesh: THREE.Mesh;
  load: (anisotropy: number, maxTextureSize: number) => void;
  resize: (drawingWidth: number, drawingHeight: number, desktop: boolean) => void;
  update: (delta: number) => void;
  setVisible: (visible: boolean) => void;
  dispose: () => void;
};

export function createSky(reducedMotion: boolean): Sky {
  const material = new THREE.ShaderMaterial({
    uniforms: {
      uMap: { value: null },
      uExposure: { value: 1.1 },
      uViewport: { value: new THREE.Vector2(1, 1) },
      uDimWidth: { value: 0.55 },
      uDimFloor: { value: 0.3 },
    },
    vertexShader: VERTEX,
    fragmentShader: FRAGMENT,
    side: THREE.BackSide,
    depthWrite: false,
    depthTest: false,
  });
  const starMaterial = new THREE.ShaderMaterial({
    uniforms: {
      uPixelRatio: { value: Math.min(window.devicePixelRatio, 2) },
      uViewport: material.uniforms.uViewport,
      uDimWidth: material.uniforms.uDimWidth,
      uDimFloor: material.uniforms.uDimFloor,
    },
    vertexShader: STAR_VERTEX,
    fragmentShader: STAR_FRAGMENT,
    transparent: false,
    depthWrite: false,
    depthTest: false,
    blending: THREE.AdditiveBlending,
  });
  let starPoints: THREE.Points | null = null;
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(90, 48, 24), material);
  mesh.renderOrder = -2;
  mesh.visible = false;
  // Bright galactic core toward the upper right of the landing frame.
  mesh.rotation.set(0.6, 3.9, 0.2);
  let texture: THREE.Texture | null = null;
  let disposed = false;
  let wanted = true;
  let requested = false;

  return {
    mesh,
    load(anisotropy, maxTextureSize) {
      if (requested || disposed) return;
      requested = true;
      const warn = (what: string) => () => console.warn(`Globe: could not load the sky ${what}`);
      new THREE.TextureLoader().load(
        maxTextureSize >= 8192 ? '/globe/sky.jpg' : '/globe/sky-4k.jpg',
        (loaded) => {
          if (disposed) {
            loaded.dispose();
            return;
          }
          loaded.colorSpace = THREE.SRGBColorSpace;
          loaded.anisotropy = anisotropy;
          texture = loaded;
          material.uniforms.uMap.value = loaded;
          mesh.visible = wanted;
        },
        undefined,
        warn('texture'),
      );

      // Real stars extracted from the same NASA map: [lon, lat, brightness, r, g, b].
      fetch('/globe/stars.json')
        .then((response) => {
          if (!response.ok) throw new Error(String(response.status));
          return response.json() as Promise<number[][]>;
        })
        .then((rows) => {
          if (disposed) return;
          const positions = new Float32Array(rows.length * 3);
          const brightness = new Float32Array(rows.length);
          const tints = new Float32Array(rows.length * 3);
          rows.forEach(([lon, lat, value, r, g, b], index) => {
            const radius = 89;
            positions.set(
              [
                radius * Math.cos(lat) * Math.cos(lon),
                radius * Math.sin(lat),
                radius * Math.cos(lat) * Math.sin(lon),
              ],
              index * 3,
            );
            brightness[index] = value;
            tints.set([r, g, b], index * 3);
          });
          const geometry = new THREE.BufferGeometry();
          geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
          geometry.setAttribute('aBrightness', new THREE.BufferAttribute(brightness, 1));
          geometry.setAttribute('aTint', new THREE.BufferAttribute(tints, 3));
          starPoints = new THREE.Points(geometry, starMaterial);
          starPoints.frustumCulled = false;
          starPoints.renderOrder = -1;
          mesh.add(starPoints);
        })
        .catch(warn('stars'));
    },
    resize(drawingWidth, drawingHeight, desktop) {
      material.uniforms.uViewport.value.set(drawingWidth, drawingHeight);
      starMaterial.uniforms.uPixelRatio.value = Math.min(window.devicePixelRatio, 2);
      // Desktop: copy sits in the left third. Smaller screens: a sheet covers it.
      material.uniforms.uDimWidth.value = desktop ? 0.55 : 1.0;
      material.uniforms.uDimFloor.value = desktop ? 0.22 : 0.7;
    },
    update(delta) {
      if (!reducedMotion) mesh.rotation.y += delta * 0.004;
    },
    setVisible(visible) {
      wanted = visible;
      mesh.visible = visible && texture !== null;
    },
    dispose() {
      disposed = true;
      texture?.dispose();
      starPoints?.geometry.dispose();
      starMaterial.dispose();
      mesh.geometry.dispose();
      material.dispose();
    },
  };
}
