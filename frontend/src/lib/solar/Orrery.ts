import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import {
  CSS2DObject,
  CSS2DRenderer,
} from "three/examples/jsm/renderers/CSS2DRenderer.js";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { OutputPass } from "three/examples/jsm/postprocessing/OutputPass.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js";
import { bodyName } from "$lib/i18n/copy";
import { locale as localeStore } from "svelte-i18n";
import { MOON, SUN } from "./catalog";
import { heliocentricEcliptic, keplerState, moonGeocentricAu } from "./kepler";
import type { ResolvedBody } from "./resolve";
import {
  EARTH_YEAR_SECONDS,
  bloomFor,
  eclipticToScene,
  moonSceneOffset,
  pickRadius,
  solarCorona,
  sunSceneRadius,
  visualRadiusKm,
  type ScaleMode,
} from "./scale";
import { spinPose } from "./spin";
import { julianNow, stepJulianDay } from "./time";

export interface OrreryOptions {
  onSelect?: (name: string | null) => void;
  onTime?: (julianDay: number) => void;
}

interface MoonNode {
  anchor: THREE.Group;
  tilt: THREE.Group;
  spin: THREE.Group;
  mesh: THREE.Mesh;
  material: THREE.MeshStandardMaterial;
  pick: THREE.Mesh;
  reticle: THREE.Sprite;
  label: CSS2DObject;
  orbit: THREE.LineLoop;
  orbitPositions: Float32Array;
  orbitMaterial: THREE.LineBasicMaterial;
  radius: number;
}

interface BodyNode {
  body: ResolvedBody;
  anchor: THREE.Group;
  tilt: THREE.Group;
  spin: THREE.Group;
  mesh: THREE.Mesh;
  material: THREE.MeshStandardMaterial;
  pick: THREE.Mesh;
  reticle: THREE.Sprite;
  clouds?: THREE.Mesh;
  rings?: THREE.Mesh;
  ringSun?: { value: THREE.Vector3 };
  label: CSS2DObject;
  orbit: THREE.LineLoop;
  orbitPositions: Float32Array;
  orbitMaterial: THREE.LineBasicMaterial;
  radius: number;
  nightUniform?: { value: THREE.Vector3 };
  displaySpin: number;
  moon?: MoonNode;
}

const SKY_RADIUS = 2200;
const ORBIT_SAMPLES = 160;
const MOON_SAMPLES = 96;
/** Earth spin while time is compressed, radians per real second. Other planets keep their sidereal ratio. */
const EARTH_VISUAL_SPIN = 0.55;
const EARTH_SIDEREAL_HOURS = 23.9344696;
const Y_AXIS = new THREE.Vector3(0, 1, 0);

const MOON_EPOCH = {
  semiMajorKm: MOON.distanceKm,
  eccentricity: MOON.eccentricity,
  inclinationDeg: MOON.inclinationDeg,
  periodDays: MOON.periodDays,
};

export class Orrery {
  private scene = new THREE.Scene();
  private camera: THREE.PerspectiveCamera;
  private renderer: THREE.WebGLRenderer;
  private composer: EffectComposer;
  private bloom: UnrealBloomPass;
  private labels: CSS2DRenderer;
  private controls: OrbitControls;
  private clock = new THREE.Clock();
  private raycaster = new THREE.Raycaster();
  private pointer = new THREE.Vector2();
  private animation = 0;
  private disposed = false;
  private resizeObserver: ResizeObserver;
  private textureCache = new Map<string, THREE.Texture>();
  private loader = new THREE.TextureLoader();
  private textureQueue: Array<() => void> = [];
  private pumping = false;
  private planets = new Map<string, BodyNode>();
  private signature = "";
  private sunMesh: THREE.Mesh;
  private sunMaterial: THREE.MeshBasicMaterial;
  private sunGlow: THREE.Sprite;
  private sunHalo: THREE.Sprite;
  private sunPick: THREE.Mesh;
  private sunReticle: THREE.Sprite;
  private starfield: THREE.Mesh;
  private starMaterial: THREE.MeshBasicMaterial;
  private starPointTexture: THREE.Texture | null = null;
  private reticleTexture: THREE.Texture | null = null;
  private localeUnsub: () => void = () => {};
  private playing = false;
  private speed = 1;
  private showOrbits = true;
  private showLabels = true;
  private selected: string | null = null;
  private follow: string | null = null;
  private snap = false;
  private snapSpin = true;
  private lastFrame: "inner" | "system" = "inner";
  private scaleMode: ScaleMode = "showcase";
  private julianDay = julianNow();
  private pointerDown = { x: 0, y: 0 };
  private onSelect: (name: string | null) => void;
  private onTime: (julianDay: number) => void;
  private poleTarget = new THREE.Vector3();
  private worldPoint = new THREE.Vector3();
  private blankRing = new THREE.DataTexture(
    new Uint8Array([255, 255, 255, 255]),
    1,
    1
  );
  private cameraOffset = new THREE.Vector3();

  constructor(private container: HTMLElement, options: OrreryOptions = {}) {
    this.onSelect = options.onSelect ?? (() => {});
    this.onTime = options.onTime ?? (() => {});
    const width = Math.max(container.clientWidth, 1);
    const height = Math.max(container.clientHeight, 1);

    this.camera = new THREE.PerspectiveCamera(48, width / height, 0.05, 8000);
    this.camera.position.set(12, 16, 34);

    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: false,
      powerPreference: "high-performance",
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
    this.renderer.setSize(width, height);
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.05;
    this.renderer.setClearColor(0x000000, 1);
    this.renderer.domElement.style.display = "block";
    this.renderer.domElement.style.width = "100%";
    this.renderer.domElement.style.height = "100%";
    this.renderer.domElement.style.touchAction = "none";
    this.container.appendChild(this.renderer.domElement);

    this.composer = new EffectComposer(this.renderer);
    this.composer.addPass(new RenderPass(this.scene, this.camera));
    this.bloom = new UnrealBloomPass(
      new THREE.Vector2(width / 2, height / 2),
      0.22,
      0.42,
      1.55
    );
    this.composer.addPass(this.bloom);
    this.composer.addPass(new OutputPass());

    this.labels = new CSS2DRenderer();
    this.labels.setSize(width, height);
    this.labels.domElement.style.position = "absolute";
    this.labels.domElement.style.inset = "0";
    this.labels.domElement.style.pointerEvents = "none";
    this.container.appendChild(this.labels.domElement);

    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.08;
    this.controls.minDistance = 2.2;
    this.controls.maxDistance = 900;
    this.controls.zoomSpeed = 0.75;
    this.controls.target.set(0, 0, 0);
    this.controls.addEventListener("start", () => {
      this.follow = null;
    });

    this.blankRing.needsUpdate = true;
    this.blankRing.colorSpace = THREE.SRGBColorSpace;

    this.addLights();
    const sky = this.addStarfield();
    this.starfield = sky.mesh;
    this.starMaterial = sky.material;
    const sun = this.addSun();
    this.sunMesh = sun.mesh;
    this.sunMaterial = sun.material;
    this.sunGlow = sun.glow;
    this.sunHalo = sun.halo;
    this.sunPick = sun.pick;
    this.sunReticle = sun.reticle;
    this.layoutSun();

    this.resizeObserver = new ResizeObserver(() => this.resize());
    this.resizeObserver.observe(this.container);
    this.renderer.domElement.addEventListener(
      "pointerdown",
      this.onPointerDown
    );
    this.renderer.domElement.addEventListener("pointerup", this.onPointerUp);
    this.animate = this.animate.bind(this);
    this.localeUnsub = localeStore.subscribe(() => {
      queueMicrotask(() => {
        if (!this.disposed) this.refreshLabels();
      });
    });
    this.animation = requestAnimationFrame(this.animate);
    this.pumpTextures();
    this.onTime(this.julianDay);
  }

  setPlanets(planets: ResolvedBody[]) {
    const signature = planets
      .map((planet) =>
        [
          planet.id,
          planet.name,
          planet.radiusKm,
          planet.epoch.semiMajorAu ?? "",
          planet.epoch.eccentricity ?? "",
          planet.epoch.inclinationDeg ?? "",
          planet.epoch.ascendingNodeDeg ?? "",
          planet.epoch.argPeriapsisDeg ?? "",
          planet.epoch.meanAnomalyDeg ?? "",
          planet.hasRings,
        ].join(":")
      )
      .join("|");
    if (signature === this.signature) return;
    this.clearPlanets();
    this.signature = signature;
    for (const planet of planets) {
      this.planets.set(planet.name, this.createPlanet(planet));
    }
    this.layoutBodies();
    this.sampleOrbits(this.julianDay);
    this.applyVisibility();
    this.applySelection();
    this.pumpTextures();
  }

  setPlaying(playing: boolean) {
    if (this.playing && !playing) this.snapSpin = true;
    this.playing = playing;
  }

  setSpeed(speed: number) {
    this.speed = speed;
  }

  setScale(mode: ScaleMode) {
    if (this.scaleMode === mode) return;
    this.scaleMode = mode;
    this.layoutBodies();
    this.sampleOrbits(this.julianDay);
    if (this.follow) this.snap = true;
    else this.frame(this.lastFrame);
  }

  setJulianDay(jd: number) {
    if (!Number.isFinite(jd)) return;
    this.julianDay = jd;
    this.snapSpin = true;
    this.sampleOrbits(jd);
    this.onTime(jd);
  }

  setOrbitsVisible(visible: boolean) {
    this.showOrbits = visible;
    this.applyVisibility();
  }

  setLabelsVisible(visible: boolean) {
    this.showLabels = visible;
    this.applyVisibility();
  }

  setSelected(name: string | null) {
    this.selected = name;
    this.applySelection();
  }

  focus(name: string) {
    if (name !== "Sun" && name !== "Moon" && !this.planets.has(name)) return;
    if (name === "Moon" && !this.earthNode()?.moon) return;
    this.follow = name;
    this.snap = true;
    this.selected = name;
    this.applySelection();
  }

  frame(mode: "inner" | "system") {
    this.lastFrame = mode;
    this.follow = null;
    const span = this.sceneSpan(mode === "system" ? 42 : 2.6);
    this.controls.target.set(0, 0, 0);
    const elevated = mode === "system" ? 0.16 : 0.36;
    const depth = mode === "system" ? 1.08 : 0.92;
    this.camera.position.set(span * 0.05, span * elevated, span * depth);
    this.applyCameraLimits(span);
    this.controls.update();
  }

  resize() {
    if (this.disposed) return;
    const width = Math.max(this.container.clientWidth, 1);
    const height = Math.max(this.container.clientHeight, 1);
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
    this.composer.setSize(width, height);
    this.bloom.setSize(Math.max(1, width / 2), Math.max(1, height / 2));
    this.labels.setSize(width, height);
  }

  dispose() {
    if (this.disposed) return;
    this.disposed = true;
    this.localeUnsub();
    cancelAnimationFrame(this.animation);
    this.resizeObserver.disconnect();
    this.renderer.domElement.removeEventListener(
      "pointerdown",
      this.onPointerDown
    );
    this.renderer.domElement.removeEventListener("pointerup", this.onPointerUp);
    this.clearPlanets();
    this.controls.dispose();
    this.textureCache.forEach((texture) => texture.dispose());
    this.blankRing.dispose();
    this.reticleTexture?.dispose();
    this.starPointTexture?.dispose();
    this.scene.traverse((object) => {
      const mesh = object as THREE.Mesh;
      mesh.geometry?.dispose();
      const material = mesh.material as
        | THREE.Material
        | THREE.Material[]
        | undefined;
      if (Array.isArray(material)) material.forEach((entry) => entry.dispose());
      else material?.dispose();
    });
    this.composer.dispose();
    this.renderer.dispose();
    this.renderer.domElement.remove();
    this.labels.domElement.remove();
  }

  private addLights() {
    const sun = new THREE.PointLight(0xfff4e0, 4.4, 0, 0);
    sun.position.set(0, 0, 0);
    this.scene.add(sun);
    this.scene.add(new THREE.AmbientLight(0x9aa6be, 0.05));
    this.scene.add(new THREE.HemisphereLight(0x243044, 0x000000, 0.07));
  }

  private addStarfield(): {
    mesh: THREE.Mesh;
    material: THREE.MeshBasicMaterial;
  } {
    const geometry = new THREE.SphereGeometry(SKY_RADIUS, 256, 128);
    const material = new THREE.MeshBasicMaterial({
      color: 0x07080e,
      side: THREE.BackSide,
      depthWrite: false,
      toneMapped: false,
    });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.frustumCulled = false;
    mesh.renderOrder = -2;
    mesh.add(this.makeStarPoints());
    this.scene.add(mesh);
    this.enqueueMap(SUN.starfield, THREE.SRGBColorSpace, (texture) => {
      texture.wrapS = THREE.RepeatWrapping;
      texture.wrapT = THREE.ClampToEdgeWrapping;
      texture.magFilter = THREE.LinearFilter;
      texture.minFilter = THREE.LinearMipmapLinearFilter;
      texture.generateMipmaps = true;
      texture.anisotropy = this.maxAnisotropy();
      texture.needsUpdate = true;
      material.map = texture;
      material.color.setRGB(1.45, 1.5, 1.7);
      material.needsUpdate = true;
    });
    return { mesh, material };
  }

  private maxAnisotropy() {
    return Math.min(16, this.renderer.capabilities.getMaxAnisotropy());
  }

  private makeStarPoints() {
    const count = 2200;
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    let seed = 0x51a77e;
    const rand = () => {
      seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
      return seed / 4294967296;
    };
    const radius = SKY_RADIUS - 40;
    for (let i = 0; i < count; i += 1) {
      const theta = Math.PI * 2 * rand();
      const phi = Math.acos(2 * rand() - 1);
      positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = radius * Math.cos(phi);
      positions[i * 3 + 2] = radius * Math.sin(phi) * Math.sin(theta);
      const tone = rand();
      const warm = tone > 0.84;
      const cool = tone < 0.1;
      colors[i * 3] = warm ? 1 : cool ? 0.72 : 0.94;
      colors[i * 3 + 1] = warm ? 0.88 : cool ? 0.84 : 0.95;
      colors[i * 3 + 2] = warm ? 0.72 : cool ? 1 : 1;
    }
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    this.starPointTexture = this.makeCanvasTexture(64, (context, size) => {
      const gradient = context.createRadialGradient(
        size / 2,
        size / 2,
        0,
        size / 2,
        size / 2,
        size / 2
      );
      gradient.addColorStop(0, "rgba(255,255,255,1)");
      gradient.addColorStop(0.18, "rgba(255,255,255,0.9)");
      gradient.addColorStop(0.42, "rgba(214,226,255,0.28)");
      gradient.addColorStop(1, "rgba(255,255,255,0)");
      context.fillStyle = gradient;
      context.fillRect(0, 0, size, size);
    });
    const material = new THREE.PointsMaterial({
      map: this.starPointTexture,
      size: 3.2,
      sizeAttenuation: false,
      transparent: true,
      depthWrite: false,
      toneMapped: false,
      vertexColors: true,
      blending: THREE.AdditiveBlending,
      opacity: 0.85,
    });
    const points = new THREE.Points(geometry, material);
    points.frustumCulled = false;
    points.renderOrder = -1;
    return points;
  }

  private makeCanvasTexture(
    size: number,
    draw: (context: CanvasRenderingContext2D, size: number) => void
  ) {
    const canvas = document.createElement("canvas");
    canvas.width = size;
    canvas.height = size;
    const context = canvas.getContext("2d");
    if (context) draw(context, size);
    const texture = new THREE.CanvasTexture(canvas);
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.magFilter = THREE.LinearFilter;
    texture.minFilter = THREE.LinearFilter;
    texture.generateMipmaps = false;
    return texture;
  }

  private reticleMap() {
    if (!this.reticleTexture) {
      this.reticleTexture = this.makeCanvasTexture(128, (context, size) => {
        context.strokeStyle = "rgba(240, 215, 164, 0.92)";
        context.lineWidth = size * 0.028;
        context.beginPath();
        context.arc(size / 2, size / 2, size * 0.36, 0, Math.PI * 2);
        context.stroke();
      });
    }
    return this.reticleTexture;
  }

  private makeReticle() {
    const sprite = new THREE.Sprite(
      new THREE.SpriteMaterial({
        map: this.reticleMap(),
        transparent: true,
        depthWrite: false,
        depthTest: false,
        toneMapped: false,
      })
    );
    sprite.visible = false;
    sprite.renderOrder = 3;
    return sprite;
  }

  private makePick(name: string) {
    const material = new THREE.MeshBasicMaterial({
      transparent: true,
      opacity: 0,
      depthWrite: false,
    });
    material.colorWrite = false;
    const mesh = new THREE.Mesh(new THREE.SphereGeometry(1, 10, 8), material);
    mesh.userData.name = name;
    return mesh;
  }

  private addSun(): {
    mesh: THREE.Mesh;
    material: THREE.MeshBasicMaterial;
    glow: THREE.Sprite;
    halo: THREE.Sprite;
    pick: THREE.Mesh;
    reticle: THREE.Sprite;
  } {
    const geometry = new THREE.SphereGeometry(1, 64, 48);
    const material = new THREE.MeshBasicMaterial({
      color: new THREE.Color(1.9, 1.55, 1.15),
    });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.userData.name = "Sun";
    this.scene.add(mesh);
    const pick = this.makePick("Sun");
    this.scene.add(pick);
    const reticle = this.makeReticle();
    this.scene.add(reticle);
    this.enqueueMap(SUN.texture, THREE.SRGBColorSpace, (texture) => {
      material.map = texture;
      material.needsUpdate = true;
    });

    const glow = this.makeGlow(
      0.22,
      "rgba(255, 214, 140, 0.55)",
      "rgba(255, 120, 40, 0.16)"
    );
    const halo = this.makeGlow(
      0.08,
      "rgba(255, 186, 90, 0.28)",
      "rgba(255, 90, 20, 0)"
    );
    this.scene.add(glow);
    this.scene.add(halo);

    const label = this.makeLabel(bodyName("Sun"));
    label.position.set(0, 1.85, 0);
    mesh.add(label);
    mesh.userData.label = label;
    return { mesh, material, glow, halo, pick, reticle };
  }

  private makeGlow(innerAlpha: number, mid: string, edge: string) {
    const canvas = document.createElement("canvas");
    canvas.width = 256;
    canvas.height = 256;
    const context = canvas.getContext("2d");
    if (context) {
      const gradient = context.createRadialGradient(128, 128, 8, 128, 128, 128);
      gradient.addColorStop(0, `rgba(255, 250, 236, ${innerAlpha + 0.7})`);
      gradient.addColorStop(0.18, mid);
      gradient.addColorStop(0.45, edge);
      gradient.addColorStop(1, "rgba(255, 80, 0, 0)");
      context.fillStyle = gradient;
      context.fillRect(0, 0, 256, 256);
    }
    const texture = new THREE.CanvasTexture(canvas);
    const sprite = new THREE.Sprite(
      new THREE.SpriteMaterial({
        map: texture,
        transparent: true,
        blending: THREE.AdditiveBlending,
        depthWrite: false,
      })
    );
    return sprite;
  }

  private createPlanet(body: ResolvedBody): BodyNode {
    const anchor = new THREE.Group();
    anchor.name = body.name;
    const tilt = new THREE.Group();
    const spin = new THREE.Group();
    tilt.add(spin);
    anchor.add(tilt);

    const material = new THREE.MeshStandardMaterial({
      color: body.colorHex,
      roughness: body.roughness,
      metalness: 0.02,
    });
    const mesh = new THREE.Mesh(new THREE.SphereGeometry(1, 64, 48), material);
    mesh.userData.name = body.name;
    spin.add(mesh);
    this.enqueueMap(body.texture, THREE.SRGBColorSpace, (texture) => {
      material.map = texture;
      material.color.set(0xffffff);
      material.needsUpdate = true;
    });

    let nightUniform: { value: THREE.Vector3 } | undefined;
    if (body.night) {
      nightUniform = { value: new THREE.Vector3(1, 0, 0) };
      material.emissive = new THREE.Color(0x000000);
      material.emissiveIntensity = 0;
      material.onBeforeCompile = (shader) => {
        shader.uniforms.uSunDir = nightUniform!;
        shader.fragmentShader = shader.fragmentShader
          .replace(
            "#include <common>",
            "#include <common>\nuniform vec3 uSunDir;"
          )
          .replace(
            "#include <emissivemap_fragment>",
            `#ifdef USE_EMISSIVEMAP
							vec4 emissiveColor = texture2D(emissiveMap, vEmissiveMapUv);
							vec3 sunView = normalize(mat3(viewMatrix) * uSunDir);
							float daylight = smoothstep(-0.08, 0.28, dot(normalize(normal), sunView));
							totalEmissiveRadiance *= emissiveColor.rgb * (1.0 - daylight);
						#endif`
          );
      };
      material.customProgramCacheKey = () => "night-side";
      this.enqueueMap(body.night, THREE.SRGBColorSpace, (texture) => {
        material.emissiveMap = texture;
        material.emissive.set(0xffffff);
        material.emissiveIntensity = 2.1;
        material.needsUpdate = true;
      });
    }

    let clouds: THREE.Mesh | undefined;
    if (body.clouds) {
      const cloudMaterial = new THREE.MeshStandardMaterial({
        color: 0xffffff,
        transparent: true,
        opacity: 0,
        depthWrite: false,
        roughness: 1,
        metalness: 0,
      });
      clouds = new THREE.Mesh(
        new THREE.SphereGeometry(1, 64, 48),
        cloudMaterial
      );
      clouds.userData.name = body.name;
      spin.add(clouds);
      this.enqueueMap(body.clouds, THREE.NoColorSpace, (texture) => {
        cloudMaterial.alphaMap = texture;
        cloudMaterial.opacity = 0.88;
        cloudMaterial.needsUpdate = true;
      });
    }

    let rings: THREE.Mesh | undefined;
    let ringSun: { value: THREE.Vector3 } | undefined;
    if (body.hasRings || body.ringTexture) {
      const built = this.createRings(body);
      rings = built.mesh;
      ringSun = built.sunDir;
      tilt.add(rings);
    }

    if (body.name === "Earth") {
      const atmosphere = new THREE.Mesh(
        new THREE.SphereGeometry(1.08, 48, 32),
        new THREE.ShaderMaterial({
          transparent: true,
          side: THREE.BackSide,
          depthWrite: false,
          uniforms: { glowColor: { value: new THREE.Color(0x8ec2ff) } },
          vertexShader: `
						varying vec3 vNormal;
						varying vec3 vWorld;
						void main() {
							vNormal = normalize(normalMatrix * normal);
							vec4 world = modelMatrix * vec4(position, 1.0);
							vWorld = world.xyz;
							gl_Position = projectionMatrix * viewMatrix * world;
						}
					`,
          fragmentShader: `
						varying vec3 vNormal;
						varying vec3 vWorld;
						uniform vec3 glowColor;
						void main() {
							vec3 viewDir = normalize(cameraPosition - vWorld);
							float fresnel = pow(1.0 - abs(dot(viewDir, normalize(vNormal))), 2.4);
							gl_FragColor = vec4(glowColor, fresnel * 0.72);
						}
					`,
        })
      );
      atmosphere.name = "earth-air";
      anchor.add(atmosphere);
    }

    const pick = this.makePick(body.name);
    anchor.add(pick);
    const reticle = this.makeReticle();
    anchor.add(reticle);
    const label = this.makeLabel(bodyName(body.name));
    anchor.add(label);
    const orbit = this.createOrbitLine(ORBIT_SAMPLES, 0.38);
    this.scene.add(orbit.line);
    this.scene.add(anchor);

    const node: BodyNode = {
      body,
      anchor,
      tilt,
      spin,
      mesh,
      material,
      clouds,
      rings,
      ringSun,
      pick,
      reticle,
      label,
      orbit: orbit.line,
      orbitPositions: orbit.positions,
      orbitMaterial: orbit.material,
      radius: 1,
      nightUniform,
      displaySpin: 0,
    };
    if (body.name === "Earth") node.moon = this.createMoon(anchor);
    return node;
  }

  private createMoon(earth: THREE.Group): MoonNode {
    const anchor = new THREE.Group();
    anchor.name = "Moon";
    const tilt = new THREE.Group();
    const spin = new THREE.Group();
    tilt.add(spin);
    anchor.add(tilt);
    const material = new THREE.MeshStandardMaterial({
      color: 0xc8c2b4,
      roughness: 0.95,
      metalness: 0.02,
    });
    const mesh = new THREE.Mesh(new THREE.SphereGeometry(1, 48, 32), material);
    mesh.userData.name = "Moon";
    spin.add(mesh);
    this.enqueueMap(MOON.texture, THREE.SRGBColorSpace, (texture) => {
      material.map = texture;
      material.color.set(0xffffff);
      material.needsUpdate = true;
    });
    const pick = this.makePick("Moon");
    anchor.add(pick);
    const reticle = this.makeReticle();
    anchor.add(reticle);
    const label = this.makeLabel(bodyName("Moon"));
    anchor.add(label);
    const orbit = this.createOrbitLine(MOON_SAMPLES, 0.45);
    earth.add(anchor);
    earth.add(orbit.line);
    return {
      anchor,
      tilt,
      spin,
      mesh,
      material,
      pick,
      reticle,
      label,
      orbit: orbit.line,
      orbitPositions: orbit.positions,
      orbitMaterial: orbit.material,
      radius: 1,
    };
  }

  private createRings(body: ResolvedBody) {
    const shape = ringShape(body.name);
    const geometry = new THREE.RingGeometry(shape.inner, shape.outer, 160);
    const position = geometry.attributes.position;
    const uv = geometry.attributes.uv;
    for (let i = 0; i < position.count; i += 1) {
      const radius = Math.hypot(position.getX(i), position.getY(i));
      uv.setXY(i, (radius - shape.inner) / (shape.outer - shape.inner), 0.5);
    }
    uv.needsUpdate = true;
    const sunDir = { value: new THREE.Vector3(1, 0, 0) };
    const material = new THREE.ShaderMaterial({
      transparent: true,
      side: THREE.DoubleSide,
      depthWrite: false,
      uniforms: {
        map: { value: body.ringTexture ? this.blankRing : this.blankRing },
        useMap: { value: body.ringTexture ? 1 : 0 },
        tint: {
          value: new THREE.Color(body.ringTexture ? 0xffffff : 0xd5e2f2),
        },
        sunDir,
        opacity: { value: shape.opacity },
      },
      vertexShader: `
				varying vec2 vUv;
				varying vec3 vNormal;
				void main() {
					vUv = uv;
					vNormal = normalize(mat3(modelMatrix) * normal);
					gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
				}
			`,
      fragmentShader: `
				uniform sampler2D map;
				uniform float useMap;
				uniform vec3 tint;
				uniform vec3 sunDir;
				uniform float opacity;
				varying vec2 vUv;
				varying vec3 vNormal;
				void main() {
					vec4 tex = useMap > 0.5 ? texture2D(map, vUv) : vec4(1.0);
					if (useMap > 0.5 && tex.a < 0.04) discard;
					float light = abs(dot(normalize(vNormal), normalize(sunDir))) * 0.65 + 0.4;
					gl_FragColor = vec4(tex.rgb * tint * light, tex.a * opacity);
				}
			`,
    });
    if (body.ringTexture) {
      this.enqueueMap(body.ringTexture, THREE.SRGBColorSpace, (texture) => {
        material.uniforms.map.value = texture;
        material.uniformsNeedUpdate = true;
      });
    }
    const mesh = new THREE.Mesh(geometry, material);
    mesh.rotation.x = Math.PI / 2;
    return { mesh, sunDir };
  }

  private createOrbitLine(count: number, opacity: number) {
    const positions = new Float32Array(count * 3);
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    const material = new THREE.LineBasicMaterial({
      color: 0xd7c4a1,
      transparent: true,
      opacity,
    });
    return {
      line: new THREE.LineLoop(geometry, material),
      positions,
      material,
    };
  }

  private layoutSun() {
    const radius = sunSceneRadius(this.scaleMode);
    const corona = solarCorona(this.scaleMode);
    const bloom = bloomFor(this.scaleMode);
    this.sunMesh.scale.setScalar(radius);
    this.sunPick.scale.setScalar(pickRadius(radius, this.scaleMode));
    this.sunGlow.scale.set(radius * corona.glow, radius * corona.glow, 1);
    this.sunHalo.scale.set(radius * corona.halo, radius * corona.halo, 1);
    if (this.scaleMode === "true") this.sunMaterial.color.setRGB(1, 0.97, 0.9);
    else this.sunMaterial.color.setRGB(1.9, 1.55, 1.15);
    this.bloom.strength = bloom.strength;
    this.bloom.threshold = bloom.threshold;
    const sky = this.scaleMode === "true" ? 50 : 1;
    this.starfield.scale.setScalar(sky);
  }

  private layoutBodies() {
    this.layoutSun();
    for (const node of this.planets.values()) {
      node.radius = visualRadiusKm(node.body.radiusKm, this.scaleMode);
      node.mesh.scale.setScalar(node.radius);
      node.pick.scale.setScalar(pickRadius(node.radius, this.scaleMode));
      if (node.clouds) node.clouds.scale.setScalar(node.radius * 1.015);
      node.label.position.set(0, node.radius * 2.35, 0);
      const air = node.anchor.getObjectByName("earth-air");
      if (air) air.scale.setScalar(node.radius);
      if (node.rings) node.rings.scale.setScalar(node.radius);
      if (node.moon) {
        node.moon.radius = visualRadiusKm(MOON.radiusKm, this.scaleMode);
        node.moon.mesh.scale.setScalar(node.moon.radius);
        node.moon.pick.scale.setScalar(
          pickRadius(node.moon.radius, this.scaleMode)
        );
        node.moon.label.position.set(0, node.moon.radius * 2.8, 0);
      }
    }
  }

  private sampleOrbits(jd: number) {
    for (const node of this.planets.values()) {
      const state = keplerState(
        node.body.name,
        jd,
        node.body.epoch,
        node.body.orbitalPeriodDays
      );
      writeOrbit(node.orbitPositions, ORBIT_SAMPLES, (index) => {
        const eccentric = (index / ORBIT_SAMPLES) * Math.PI * 2;
        return eclipticToScene(
          heliocentricEcliptic(state, eccentric),
          state.semiMajorAu,
          this.scaleMode
        );
      });
      node.orbit.geometry.attributes.position.needsUpdate = true;
      if (node.moon) {
        const earthRadius = node.radius;
        writeOrbit(node.moon.orbitPositions, MOON_SAMPLES, (index) => {
          const sample = jd + (index / MOON_SAMPLES) * MOON.periodDays;
          return moonSceneOffset(
            moonGeocentricAu(sample, MOON_EPOCH),
            earthRadius,
            this.scaleMode
          );
        });
        node.moon.orbit.geometry.attributes.position.needsUpdate = true;
      }
    }
  }

  private sceneSpan(au: number) {
    return this.scaleMode === "true"
      ? au * 50
      : 16 * Math.pow(Math.max(au, 0.02), 0.72);
  }

  private applyCameraLimits(span: number) {
    const far = this.scaleMode === "true" ? 140000 : Math.max(8000, span * 30);
    this.camera.near = this.scaleMode === "true" ? 0.0004 : 0.05;
    this.camera.far = far;
    this.camera.updateProjectionMatrix();
    this.controls.minDistance = this.scaleMode === "true" ? 0.004 : 2.2;
    this.controls.maxDistance = Math.max(
      span * 8,
      this.scaleMode === "true" ? 8000 : 900
    );
  }

  private placeBodies(jd: number, delta: number, simDays: number) {
    const earthRadPerDay = (Math.PI * 2) / (EARTH_SIDEREAL_HOURS / 24);
    const trueRate =
      delta > 0 ? (Math.abs(simDays) * earthRadPerDay) / delta : 0;
    const gear =
      !this.playing || this.snapSpin
        ? 1
        : Math.min(1, EARTH_VISUAL_SPIN / Math.max(trueRate, 1e-6));
    const sunPose = spinPose("Sun", jd);
    this.sunMesh.rotation.y = wrapAngle(sunPose.spinRadians);

    for (const node of this.planets.values()) {
      const state = keplerState(
        node.body.name,
        jd,
        node.body.epoch,
        node.body.orbitalPeriodDays
      );
      const place = eclipticToScene(
        heliocentricEcliptic(state),
        state.semiMajorAu,
        this.scaleMode
      );
      node.anchor.position.set(place.x, place.y, place.z);
      const pose = spinPose(node.body.name, jd, {
        tiltDeg: node.body.axialTiltDeg,
        rotationHours: node.body.rotationHours,
      });
      this.poleTarget.set(pose.pole.x, pose.pole.y, pose.pole.z);
      node.tilt.quaternion.setFromUnitVectors(Y_AXIS, this.poleTarget);
      if (this.snapSpin || !this.playing) node.displaySpin = pose.spinRadians;
      else
        node.displaySpin +=
          simDays * Math.PI * 2 * (24 / pose.siderealHours) * gear;
      node.displaySpin = wrapAngle(node.displaySpin);
      node.spin.rotation.y = node.displaySpin;
      if (node.clouds) node.clouds.rotation.y = node.displaySpin * 1.04;
      if (node.nightUniform) {
        node.nightUniform.value.set(-place.x, -place.y, -place.z).normalize();
      }
      if (node.ringSun)
        node.ringSun.value.set(-place.x, -place.y, -place.z).normalize();
      if (node.moon) this.placeMoon(node, jd);
    }
    this.snapSpin = false;
  }

  private placeMoon(earth: BodyNode, jd: number) {
    const moon = earth.moon;
    if (!moon) return;
    const offset = moonSceneOffset(
      moonGeocentricAu(jd, MOON_EPOCH),
      earth.radius,
      this.scaleMode
    );
    moon.anchor.position.set(offset.x, offset.y, offset.z);
    const pose = spinPose("Moon", jd);
    this.poleTarget.set(pose.pole.x, pose.pole.y, pose.pole.z);
    moon.tilt.quaternion.setFromUnitVectors(Y_AXIS, this.poleTarget);
    moon.spin.rotation.y = wrapAngle(pose.spinRadians);
  }

  private refreshLabels() {
    const sunLabel = this.sunMesh?.userData.label as CSS2DObject | undefined;
    if (sunLabel) sunLabel.element.textContent = bodyName("Sun");
    for (const node of this.planets.values()) {
      node.label.element.textContent = bodyName(node.body.name);
      if (node.moon) node.moon.label.element.textContent = bodyName("Moon");
    }
  }

  private updateReticles() {
    const show = this.scaleMode === "true";
    const height = Math.max(this.renderer.domElement.clientHeight, 1);
    const vFov = (this.camera.fov * Math.PI) / 180;
    const place = (
      object: THREE.Object3D,
      sprite: THREE.Sprite,
      visual: number,
      active: boolean
    ) => {
      if (!show || !active) {
        sprite.visible = false;
        return;
      }
      object.getWorldPosition(this.worldPoint);
      const distance = Math.max(
        this.camera.position.distanceTo(this.worldPoint),
        1e-4
      );
      const worldPerPixel = (2 * Math.tan(vFov / 2) * distance) / height;
      const ringRadius = Math.max(visual * 1.22, worldPerPixel * 7);
      const spriteSize = ringRadius / 0.36;
      sprite.scale.set(spriteSize, spriteSize, 1);
      sprite.visible = true;
    };
    place(
      this.sunMesh,
      this.sunReticle,
      sunSceneRadius(this.scaleMode),
      this.selected === "Sun"
    );
    for (const node of this.planets.values()) {
      place(
        node.anchor,
        node.reticle,
        node.radius,
        this.selected === node.body.name
      );
      if (node.moon) {
        place(
          node.moon.anchor,
          node.moon.reticle,
          node.moon.radius,
          this.selected === "Moon"
        );
      }
    }
  }

  private makeLabel(text: string) {
    const element = document.createElement("div");
    element.className = "sx-label";
    element.textContent = text;
    return new CSS2DObject(element);
  }

  private enqueueMap(
    url: string,
    colorSpace: THREE.ColorSpace,
    assign: (texture: THREE.Texture) => void
  ) {
    const cached = this.textureCache.get(url);
    if (cached) {
      assign(cached);
      return;
    }
    this.textureQueue.push(() => {
      if (this.disposed || this.textureCache.has(url)) {
        const existing = this.textureCache.get(url);
        if (existing) assign(existing);
        return;
      }
      const texture = this.loader.load(url, () => {
        if (!this.disposed) assign(texture);
      });
      texture.colorSpace = colorSpace;
      texture.magFilter = THREE.LinearFilter;
      texture.minFilter = THREE.LinearMipmapLinearFilter;
      texture.generateMipmaps = true;
      texture.anisotropy = this.maxAnisotropy();
      this.textureCache.set(url, texture);
    });
  }

  private pumpTextures() {
    if (this.pumping) return;
    this.pumping = true;
    const step = () => {
      if (this.disposed) return;
      const first = this.textureQueue.shift();
      const second = this.textureQueue.shift();
      first?.();
      second?.();
      if (this.textureQueue.length) requestAnimationFrame(step);
      else this.pumping = false;
    };
    requestAnimationFrame(step);
  }

  private clearPlanets() {
    for (const node of this.planets.values()) {
      this.scene.remove(node.anchor);
      this.scene.remove(node.orbit);
      disposeObject(node.anchor);
      node.orbit.geometry.dispose();
      node.orbitMaterial.dispose();
      node.label.element.remove();
      node.moon?.label.element.remove();
    }
    this.planets.clear();
  }

  private earthNode() {
    return this.planets.get("Earth");
  }

  private applyVisibility() {
    for (const node of this.planets.values()) {
      node.orbit.visible = this.showOrbits;
      node.label.visible = this.showLabels;
      if (node.moon) {
        node.moon.orbit.visible = this.showOrbits;
        node.moon.label.visible = this.showLabels;
      }
    }
    const sunLabel = this.sunMesh.userData.label as CSS2DObject | undefined;
    if (sunLabel) sunLabel.visible = this.showLabels;
  }

  private applySelection() {
    for (const node of this.planets.values()) {
      const active = node.body.name === this.selected;
      node.label.element.classList.toggle("is-selected", active);
      node.orbitMaterial.opacity = active ? 0.9 : 0.34;
      node.orbitMaterial.color.set(active ? 0xf3ddb0 : 0xd7c4a1);
      if (node.moon) {
        const moonActive = this.selected === "Moon";
        node.moon.label.element.classList.toggle("is-selected", moonActive);
        node.moon.orbitMaterial.opacity = moonActive ? 0.95 : 0.4;
        node.moon.orbitMaterial.color.set(moonActive ? 0xf3ddb0 : 0xc8d0dc);
      }
    }
    const sunLabel = this.sunMesh.userData.label as CSS2DObject | undefined;
    sunLabel?.element.classList.toggle("is-selected", this.selected === "Sun");
  }

  private onPointerDown = (event: PointerEvent) => {
    this.pointerDown = { x: event.clientX, y: event.clientY };
  };

  private onPointerUp = (event: PointerEvent) => {
    const dx = event.clientX - this.pointerDown.x;
    const dy = event.clientY - this.pointerDown.y;
    if (dx * dx + dy * dy > 16) return;
    const rect = this.renderer.domElement.getBoundingClientRect();
    this.pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    this.pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    this.raycaster.setFromCamera(this.pointer, this.camera);
    const targets: THREE.Object3D[] = [this.sunMesh, this.sunPick];
    for (const node of this.planets.values()) {
      targets.push(node.mesh, node.pick);
      if (node.clouds) targets.push(node.clouds);
      if (node.moon) targets.push(node.moon.mesh, node.moon.pick);
    }
    const hit = this.raycaster.intersectObjects(targets, false)[0];
    const name = (hit?.object.userData.name as string | undefined) ?? null;
    if (name) this.focus(name);
    else {
      this.selected = null;
      this.applySelection();
    }
    this.onSelect(name);
  };

  private followTarget() {
    if (this.follow === "Sun") {
      this.controls.target.set(0, 0, 0);
      if (this.snap) {
        const radius = sunSceneRadius(this.scaleMode);
        this.camera.position.set(0, radius * 1.6, radius * 6);
        this.snap = false;
      }
      return;
    }
    if (this.follow === "Moon") {
      const moon = this.earthNode()?.moon;
      if (!moon) return;
      moon.anchor.getWorldPosition(this.worldPoint);
      this.controls.target.copy(this.worldPoint);
      if (this.snap) {
        this.cameraOffset.set(
          moon.radius * 0.6,
          moon.radius * 1.4,
          Math.max(moon.radius * 8, 0.2)
        );
        this.camera.position.copy(this.worldPoint).add(this.cameraOffset);
        this.snap = false;
      }
      return;
    }
    if (!this.follow) return;
    const node = this.planets.get(this.follow);
    if (!node) return;
    this.controls.target.copy(node.anchor.position);
    if (this.snap) {
      const distance = Math.max(
        node.radius * 6.4,
        this.scaleMode === "true" ? 0.08 : node.radius * 6.4
      );
      this.cameraOffset.set(node.radius * 0.4, distance * 0.35, distance);
      this.camera.position.copy(node.anchor.position).add(this.cameraOffset);
      this.snap = false;
    }
  }

  private animate() {
    if (this.disposed) return;
    this.animation = requestAnimationFrame(this.animate);
    const delta = Math.min(this.clock.getDelta(), 0.05);
    const before = this.julianDay;
    if (this.playing) {
      this.julianDay = stepJulianDay(
        this.julianDay,
        delta,
        this.speed,
        EARTH_YEAR_SECONDS
      );
    }
    const simDays = this.julianDay - before;
    if (this.playing || this.snapSpin) this.onTime(this.julianDay);
    this.placeBodies(this.julianDay, delta, simDays);
    if (Math.abs(simDays) > 2) this.sampleOrbits(this.julianDay);
    this.followTarget();
    this.updateReticles();
    this.updateClipping();
    this.controls.update();
    this.composer.render();
    this.labels.render(this.scene, this.camera);
  }

  private updateClipping() {
    if (this.scaleMode !== "true") return;
    const dist = Math.max(
      this.camera.position.distanceTo(this.controls.target),
      1e-4
    );
    const near = Math.min(Math.max(dist * 0.001, 0.00005), 1);
    if (Math.abs(this.camera.near - near) / this.camera.near > 0.3) {
      this.camera.near = near;
      this.camera.far = Math.max(140000, dist * 40);
      this.camera.updateProjectionMatrix();
    }
  }
}

function wrapAngle(radians: number) {
  if (!Number.isFinite(radians)) return 0;
  return Math.atan2(Math.sin(radians), Math.cos(radians));
}

function ringShape(name: string) {
  if (name === "Saturn") return { inner: 1.15, outer: 2.32, opacity: 1 };
  if (name === "Jupiter") return { inner: 1.69, outer: 1.86, opacity: 0.32 };
  if (name === "Uranus") return { inner: 1.6, outer: 2.05, opacity: 0.42 };
  if (name === "Neptune") return { inner: 1.68, outer: 2.55, opacity: 0.26 };
  return { inner: 1.45, outer: 2.1, opacity: 0.3 };
}

function writeOrbit(
  positions: Float32Array,
  count: number,
  sample: (index: number) => { x: number; y: number; z: number }
) {
  for (let i = 0; i < count; i += 1) {
    const point = sample(i);
    positions[i * 3] = point.x;
    positions[i * 3 + 1] = point.y;
    positions[i * 3 + 2] = point.z;
  }
}

function disposeObject(object: THREE.Object3D) {
  object.traverse((child) => {
    const mesh = child as THREE.Mesh;
    mesh.geometry?.dispose();
    const material = mesh.material as
      | THREE.Material
      | THREE.Material[]
      | undefined;
    if (Array.isArray(material)) material.forEach((entry) => entry.dispose());
    else material?.dispose();
  });
}
