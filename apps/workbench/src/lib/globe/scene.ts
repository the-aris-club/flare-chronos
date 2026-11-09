import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import type { RegionId } from '@/lib/calendar/types';
import { GLOBE_DATA, lonLatToVec, vecToLonLat } from './data';
import { createEarth, type Earth } from './earth';
import { CameraFlight } from './flight';
import { updateGlobeLabels } from './labels';
import { createOrbits } from './orbits';
import { RegionPicker, bindRegionPointer } from './picking';
import { captureFrame } from './snapshot';
import { createSky } from './sky';
import { loadEarthPhoto } from './textures';
import type { BootStep } from './types';
const DEG = Math.PI / 180;
const IDLE_SPEED = 0.25;
const HOVER_SPEED = 0.05;
type Options = {
  canvas: HTMLCanvasElement;
  labels: Partial<Record<RegionId, HTMLDivElement | null>>;
  theme: 'dark' | 'light';
  reducedMotion: boolean;
  onProgress: (step: BootStep) => void;
  onHover: (region: RegionId | null) => void;
  onSelect: (region: RegionId) => void;
  onArrive: (region: RegionId) => void;
};
const REGION_IDS = Object.keys(GLOBE_DATA.regions) as RegionId[];
export class GlobeScene {
  private readonly canvas: HTMLCanvasElement;
  private readonly labels: Partial<Record<RegionId, HTMLDivElement | null>>;
  private readonly reducedMotion: boolean;
  private readonly onProgress: Options['onProgress'];
  private readonly onHover: Options['onHover'];
  private readonly onSelect: Options['onSelect'];
  private readonly onArrive: Options['onArrive'];
  private readonly renderer: THREE.WebGLRenderer;
  private readonly scene = new THREE.Scene();
  private readonly camera: THREE.PerspectiveCamera;
  private readonly controls: OrbitControls;
  private readonly earth: Earth;
  private readonly flight: CameraFlight;
  private readonly sky: ReturnType<typeof createSky>;
  private readonly orbits = createOrbits();
  private photo: THREE.Texture | null = null;
  private theme: 'dark' | 'light';
  private hovered: RegionId | null = null;
  private peekTarget = 0;
  private mode: 'idle' | 'flying' | 'arrived' = 'idle';
  private width = 1;
  private height = 1;
  private breakpoint = '';
  private offset = { x: 0, y: 0 };
  private idleDistance = 4.3;
  private last = performance.now();
  private disposed = false;
  private readonly picker = new RegionPicker();
  private readonly unbindPointer: () => void;
  private resumeTimer = 0;
  constructor(options: Options) {
    this.canvas = options.canvas;
    this.labels = options.labels;
    this.reducedMotion = options.reducedMotion;
    this.onProgress = options.onProgress;
    this.onHover = options.onHover;
    this.onSelect = options.onSelect;
    this.onArrive = options.onArrive;
    this.theme = options.theme;

    this.renderer = new THREE.WebGLRenderer({
      canvas: options.canvas,
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance',
      preserveDrawingBuffer: true,
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;

    this.camera = new THREE.PerspectiveCamera(30, 1, 0.01, 200);
    this.camera.position.set(...lonLatToVec(-38, 8, 1));
    this.controls = new OrbitControls(this.camera, options.canvas);
    this.controls.enablePan = false;
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.08;
    this.controls.rotateSpeed = 0.45;
    this.controls.zoomSpeed = 0.6;
    this.controls.minDistance = 1.5;
    this.controls.maxDistance = 14;
    this.controls.autoRotate = !this.reducedMotion;
    this.controls.autoRotateSpeed = IDLE_SPEED;

    this.sky = createSky(this.reducedMotion);
    this.sky.setVisible(this.theme === 'dark');
    this.earth = createEarth(this.theme, this.maxAnisotropy());
    this.flight = new CameraFlight(
      this.camera,
      () => ({ width: this.width, height: this.height }),
      (x, y) => this.setOffset(x, y),
      (region) => {
        this.mode = 'arrived';
        this.onArrive(region);
      },
      this.reducedMotion,
    );
    this.scene.add(this.sky.mesh, this.earth.group, this.orbits.group);

    this.bindControls();
    this.unbindPointer = bindRegionPointer({
      canvas: this.canvas,
      picker: this.picker,
      camera: this.camera,
      surface: this.earth.surface,
      earth: this.earth.group,
      isIdle: () => this.mode === 'idle',
      onHover: (region) => this.setHighlight(region),
      onSelect: (region) => this.onSelect(region),
    });
    this.resize();
    this.onProgress('borders');

    loadEarthPhoto(
      this.maxAnisotropy(),
      (texture) => {
        this.photo = texture;
        if (this.disposed) return;
        if (this.theme === 'dark') this.earth.applySurface(this.theme, texture);
        this.onProgress('photo');
      },
      () => {
        if (!this.disposed) this.onProgress('photo');
      },
    );

    if (this.theme === 'dark') this.loadSky();

    this.renderer.setAnimationLoop(this.frame);
  }

  private maxAnisotropy(): number {
    return Math.min(8, this.renderer.capabilities.getMaxAnisotropy());
  }

  private bindControls() {
    this.controls.addEventListener('start', this.handleControlStart);
    this.controls.addEventListener('end', this.handleControlEnd);
  }

  private handleControlStart = () => {
    this.controls.autoRotate = false;
  };

  private handleControlEnd = () => {
    window.clearTimeout(this.resumeTimer);
    this.resumeTimer = window.setTimeout(() => {
      if (this.disposed || this.mode !== 'idle' || this.hovered) return;
      this.controls.autoRotate = !this.reducedMotion;
    }, 3500);
  };

  peek(region: RegionId | null) {
    if (this.mode !== 'idle' || !region) {
      this.peekTarget = 0;
      return;
    }

    const [lon] = GLOBE_DATA.regions[region].anchor;
    const [cameraLon] = vecToLonLat(
      this.camera.position.x,
      this.camera.position.y,
      this.camera.position.z,
    );
    const diff = ((lon - cameraLon + 540) % 360) - 180;
    this.peekTarget = ((diff * Math.PI) / 180) * 0.22;
  }

  setHighlight(region: RegionId | null) {
    if (this.hovered === region) return;
    this.hovered = region;
    this.controls.autoRotateSpeed = region ? HOVER_SPEED : IDLE_SPEED;
    this.onHover(region);
    this.canvas.classList.toggle('cursor-pointer', region !== null);
    this.canvas.classList.toggle('cursor-grab', region === null);
  }

  private loadSky() {
    this.sky.load(this.maxAnisotropy(), this.renderer.capabilities.maxTextureSize);
  }

  setTheme(theme: 'dark' | 'light') {
    if (this.theme === theme) return;
    this.theme = theme;
    this.earth.setTheme(theme, this.photo);
    this.orbits.setTheme(theme);
    this.sky.setVisible(theme === 'dark');
    if (theme === 'dark') this.loadSky();
  }

  flyTo(region: RegionId): boolean {
    if (this.mode !== 'idle' || this.flight.active) return false;
    this.earth.group.rotation.y = 0;
    this.peekTarget = 0;
    this.mode = 'flying';
    this.controls.enabled = false;
    this.controls.autoRotate = false;
    this.hovered = null;
    this.flight.start(region, this.offset);

    return true;
  }

  snapshot(): string | null {
    if (this.disposed) return null;
    return captureFrame(this.renderer, this.scene, this.camera, this.canvas);
  }

  resize() {
    const width = this.canvas.clientWidth;
    const height = this.canvas.clientHeight;
    if (width === 0 || height === 0) return;

    const breakpoint = width >= 1280 ? 'desktop' : width >= 720 ? 'tablet' : 'mobile';
    const changed = breakpoint !== this.breakpoint;
    this.breakpoint = breakpoint;
    this.width = width;
    this.height = height;

    this.renderer.setSize(width, height, false);
    this.camera.aspect = width / height;
    const buffer = this.renderer.getDrawingBufferSize(new THREE.Vector2());
    this.sky.resize(buffer.x, buffer.y, breakpoint === 'desktop');

    const f = width < height ? 0.9 : 0.82;
    this.idleDistance = height / (f * Math.min(width, height) * Math.tan(15 * DEG));

    if (changed && this.mode === 'idle') {
      const direction = this.camera.position.clone().normalize();
      if (direction.lengthSq() < 0.5) direction.set(0, 0, 1);
      this.camera.position.copy(direction.multiplyScalar(this.idleDistance));
    }

    this.offset =
      breakpoint === 'desktop' ? { x: 0.17, y: 0 } : { x: 0, y: width < height ? 0.2 : 0.17 };
    if (this.mode === 'idle') this.setOffset(this.offset.x, this.offset.y);
    this.camera.updateProjectionMatrix();
  }

  private setOffset(x: number, y: number) {
    this.camera.setViewOffset(
      this.width,
      this.height,
      -x * this.width,
      y * this.height,
      this.width,
      this.height,
    );
  }

  private frame = () => {
    if (this.disposed) return;
    const now = performance.now();
    const delta = Math.min((now - this.last) / 1000, 0.1);
    this.last = now;

    if (this.mode === 'flying') {
      this.flight.step(now);
    } else {
      if (this.controls.enabled) this.controls.update();
      this.earth.group.rotation.y = this.reducedMotion
        ? this.peekTarget
        : this.earth.group.rotation.y + (this.peekTarget - this.earth.group.rotation.y) * 0.08;
      if (!this.reducedMotion) this.orbits.update(delta);
    }

    this.sky.update(delta);

    for (const id of REGION_IDS) {
      const target = this.hovered === id ? 0.42 : 0.22;
      const material = this.earth.coverage[id].fill;
      material.opacity = this.reducedMotion
        ? target
        : material.opacity + (target - material.opacity) * 0.18;
    }

    if (this.mode === 'idle')
      updateGlobeLabels(this.labels, this.camera, this.earth.group, this.width, this.height);
    this.orbits.group.visible = this.mode === 'idle';
    this.renderer.render(this.scene, this.camera);
  };

  dispose() {
    this.disposed = true;
    this.renderer.setAnimationLoop(null);
    window.clearTimeout(this.resumeTimer);
    this.unbindPointer();
    this.controls.removeEventListener('start', this.handleControlStart);
    this.controls.removeEventListener('end', this.handleControlEnd);
    this.controls.dispose();
    this.earth.dispose();
    this.orbits.dispose();
    this.sky.dispose();
    this.photo?.dispose();
    this.renderer.dispose();
  }
}
