import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { CSS2DObject, CSS2DRenderer } from 'three/examples/jsm/renderers/CSS2DRenderer.js';
import { SUN } from './catalog';
import type { ResolvedBody } from './resolve';
import {
	EARTH_YEAR_SECONDS,
	SUN_SCENE_RADIUS,
	orbitSamples,
	orbitalOmega,
	orbitalPosition,
	visualRadiusKm,
	type OrbitElements
} from './scale';

export interface OrreryOptions {
	onSelect?: (name: string | null) => void;
}

interface BodyNode {
	body: ResolvedBody;
	anchor: THREE.Group;
	spin: THREE.Group;
	mesh: THREE.Mesh;
	material: THREE.MeshStandardMaterial;
	clouds?: THREE.Mesh;
	rings?: THREE.Mesh;
	label: CSS2DObject;
	orbit: THREE.LineLoop;
	orbitMaterial: THREE.LineBasicMaterial;
	meanAnomaly: number;
	radius: number;
	nightUniform?: { value: THREE.Vector3 };
}

const INNER_CAMERA = new THREE.Vector3(12, 16, 34);
const SYSTEM_CAMERA = new THREE.Vector3(0, 120, 280);

export class Orrery {
	private scene = new THREE.Scene();
	private camera: THREE.PerspectiveCamera;
	private renderer: THREE.WebGLRenderer;
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
	private planets = new Map<string, BodyNode>();
	private signature = '';
	private sunMesh: THREE.Mesh;
	private sunGlow: THREE.Sprite;
	private playing = true;
	private speed = 10;
	private showOrbits = true;
	private showLabels = true;
	private selected: string | null = null;
	private follow: string | null = null;
	private snap = false;
	private pointerDown = { x: 0, y: 0 };
	private onSelect: (name: string | null) => void;

	constructor(
		private container: HTMLElement,
		options: OrreryOptions = {}
	) {
		this.onSelect = options.onSelect ?? (() => {});
		const width = Math.max(container.clientWidth, 1);
		const height = Math.max(container.clientHeight, 1);

		this.camera = new THREE.PerspectiveCamera(48, width / height, 0.05, 4000);
		this.camera.position.copy(INNER_CAMERA);

		this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'high-performance' });
		this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
		this.renderer.setSize(width, height);
		this.renderer.outputColorSpace = THREE.SRGBColorSpace;
		this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
		this.renderer.toneMappingExposure = 1.08;
		this.renderer.setClearColor(0x000000, 1);
		this.renderer.domElement.style.display = 'block';
		this.renderer.domElement.style.width = '100%';
		this.renderer.domElement.style.height = '100%';
		this.container.appendChild(this.renderer.domElement);

		this.labels = new CSS2DRenderer();
		this.labels.setSize(width, height);
		this.labels.domElement.style.position = 'absolute';
		this.labels.domElement.style.inset = '0';
		this.labels.domElement.style.pointerEvents = 'none';
		this.container.appendChild(this.labels.domElement);

		this.controls = new OrbitControls(this.camera, this.renderer.domElement);
		this.controls.enableDamping = true;
		this.controls.dampingFactor = 0.08;
		this.controls.minDistance = 2.2;
		this.controls.maxDistance = 900;
		this.controls.zoomSpeed = 0.7;
		this.controls.target.set(0, 0, 0);
		this.controls.addEventListener('start', () => {
			this.follow = null;
		});

		this.addLights();
		this.addStarfield();
		const sun = this.addSun();
		this.sunMesh = sun.mesh;
		this.sunGlow = sun.glow;

		this.resizeObserver = new ResizeObserver(() => this.resize());
		this.resizeObserver.observe(this.container);
		this.renderer.domElement.addEventListener('pointerdown', this.onPointerDown);
		this.renderer.domElement.addEventListener('pointerup', this.onPointerUp);
		this.animate = this.animate.bind(this);
		this.animation = requestAnimationFrame(this.animate);
	}

	setPlanets(planets: ResolvedBody[]) {
		const signature = planets
			.map((planet) =>
				[
					planet.id,
					planet.name,
					planet.origin,
					planet.distanceAu,
					planet.radiusKm,
					planet.orbitalPeriodDays,
					planet.eccentricity,
					planet.hasRings
				].join(':')
			)
			.join('|');
		if (signature === this.signature) return;
		const previous = new Map<string, number>();
		for (const [name, node] of this.planets) previous.set(name, node.meanAnomaly);
		this.clearPlanets();
		this.signature = signature;
		for (const planet of planets) {
			const node = this.createPlanet(planet, previous.get(planet.name));
			this.planets.set(planet.name, node);
		}
		this.applyVisibility();
		this.applySelection();
	}

	setPlaying(playing: boolean) {
		this.playing = playing;
	}

	setSpeed(speed: number) {
		this.speed = speed;
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
		if (name !== 'Sun' && !this.planets.has(name)) return;
		this.follow = name;
		this.snap = true;
		this.selected = name;
		this.applySelection();
	}

	frame(mode: 'inner' | 'system') {
		this.follow = null;
		this.controls.target.set(0, 0, 0);
		this.camera.position.copy(mode === 'system' ? SYSTEM_CAMERA : INNER_CAMERA);
		this.controls.update();
	}

	resize() {
		if (this.disposed) return;
		const width = Math.max(this.container.clientWidth, 1);
		const height = Math.max(this.container.clientHeight, 1);
		this.camera.aspect = width / height;
		this.camera.updateProjectionMatrix();
		this.renderer.setSize(width, height);
		this.labels.setSize(width, height);
	}

	dispose() {
		if (this.disposed) return;
		this.disposed = true;
		cancelAnimationFrame(this.animation);
		this.resizeObserver.disconnect();
		this.renderer.domElement.removeEventListener('pointerdown', this.onPointerDown);
		this.renderer.domElement.removeEventListener('pointerup', this.onPointerUp);
		this.clearPlanets();
		this.controls.dispose();
		this.textureCache.forEach((texture) => texture.dispose());
		this.scene.traverse((object) => {
			const mesh = object as THREE.Mesh;
			if (mesh.geometry) mesh.geometry.dispose();
			const material = mesh.material as THREE.Material | THREE.Material[] | undefined;
			if (Array.isArray(material)) material.forEach((entry) => entry.dispose());
			else material?.dispose();
		});
		this.renderer.dispose();
		this.renderer.domElement.remove();
		this.labels.domElement.remove();
	}

	private addLights() {
		const sun = new THREE.PointLight(0xfff4dd, 90, 0, 1.4);
		sun.position.set(0, 0, 0);
		this.scene.add(sun);
		const fill = new THREE.DirectionalLight(0xc5d4ff, 1.15);
		fill.position.set(-30, 18, 12);
		this.scene.add(fill);
		this.scene.add(new THREE.AmbientLight(0x8d97ad, 0.42));
		this.scene.add(new THREE.HemisphereLight(0x1a2744, 0x000000, 0.35));
	}

	private addStarfield() {
		const geometry = new THREE.SphereGeometry(1600, 48, 32);
		const material = new THREE.MeshBasicMaterial({
			map: this.loadMap(SUN.starfield, THREE.SRGBColorSpace),
			side: THREE.BackSide,
			depthWrite: false
		});
		this.scene.add(new THREE.Mesh(geometry, material));
	}

	private addSun(): { mesh: THREE.Mesh; glow: THREE.Sprite } {
		const geometry = new THREE.SphereGeometry(SUN_SCENE_RADIUS, 64, 48);
		const material = new THREE.MeshBasicMaterial({
			map: this.loadMap(SUN.texture, THREE.SRGBColorSpace),
			color: 0xffffff
		});
		const mesh = new THREE.Mesh(geometry, material);
		mesh.userData.name = 'Sun';
		this.scene.add(mesh);

		const canvas = document.createElement('canvas');
		canvas.width = 256;
		canvas.height = 256;
		const context = canvas.getContext('2d');
		if (context) {
			const gradient = context.createRadialGradient(128, 128, 18, 128, 128, 128);
			gradient.addColorStop(0, 'rgba(255, 246, 220, 0.95)');
			gradient.addColorStop(0.22, 'rgba(255, 186, 70, 0.45)');
			gradient.addColorStop(0.5, 'rgba(255, 110, 20, 0.12)');
			gradient.addColorStop(1, 'rgba(255, 80, 0, 0)');
			context.fillStyle = gradient;
			context.fillRect(0, 0, 256, 256);
		}
		const glowTexture = new THREE.CanvasTexture(canvas);
		const glow = new THREE.Sprite(
			new THREE.SpriteMaterial({
				map: glowTexture,
				transparent: true,
				blending: THREE.AdditiveBlending,
				depthWrite: false
			})
		);
		glow.scale.set(18, 18, 1);
		this.scene.add(glow);

		const label = this.makeLabel('Sun');
		label.position.set(0, SUN_SCENE_RADIUS * 1.8, 0);
		this.scene.add(label);
		mesh.userData.label = label;
		return { mesh, glow };
	}

	private createPlanet(body: ResolvedBody, meanAnomaly?: number): BodyNode {
		const radius = visualRadiusKm(body.radiusKm);
		const elements = elementsOf(body);
		const anchor = new THREE.Group();
		anchor.name = body.name;
		const tilt = new THREE.Group();
		tilt.rotation.z = (body.axialTiltDeg * Math.PI) / 180;
		const spin = new THREE.Group();
		tilt.add(spin);
		anchor.add(tilt);

		const material = new THREE.MeshStandardMaterial({
			color: 0xffffff,
			map: this.loadMap(body.texture, THREE.SRGBColorSpace),
			roughness: body.roughness,
			metalness: 0.04
		});
		const mesh = new THREE.Mesh(new THREE.SphereGeometry(radius, 64, 48), material);
		mesh.userData.name = body.name;
		spin.add(mesh);

		let nightUniform: { value: THREE.Vector3 } | undefined;
		if (body.night) {
			nightUniform = { value: new THREE.Vector3(1, 0, 0) };
			material.emissive = new THREE.Color(0xffffff);
			material.emissiveIntensity = 1.35;
			material.emissiveMap = this.loadMap(body.night, THREE.SRGBColorSpace);
			material.onBeforeCompile = (shader) => {
				shader.uniforms.uSunDir = nightUniform!;
				shader.fragmentShader = shader.fragmentShader
					.replace('#include <common>', '#include <common>\nuniform vec3 uSunDir;')
					.replace(
						'#include <emissivemap_fragment>',
						`#ifdef USE_EMISSIVEMAP
							vec4 emissiveColor = texture2D(emissiveMap, vEmissiveMapUv);
							vec3 sunView = normalize(mat3(viewMatrix) * uSunDir);
							float daylight = smoothstep(-0.05, 0.22, dot(normalize(normal), sunView));
							totalEmissiveRadiance *= emissiveColor.rgb * (1.0 - daylight);
						#endif`
					);
			};
			material.customProgramCacheKey = () => 'night-side';
		}

		let clouds: THREE.Mesh | undefined;
		if (body.clouds) {
			const cloudMaterial = new THREE.MeshStandardMaterial({
				alphaMap: this.loadMap(body.clouds, THREE.LinearSRGBColorSpace),
				transparent: true,
				depthWrite: false,
				opacity: 0.92,
				roughness: 1,
				metalness: 0,
				color: 0xffffff
			});
			clouds = new THREE.Mesh(new THREE.SphereGeometry(radius * 1.018, 64, 48), cloudMaterial);
			clouds.userData.name = body.name;
			spin.add(clouds);
		}

		let rings: THREE.Mesh | undefined;
		if (body.hasRings) {
			const inner = radius * (body.ringTexture ? 1.25 : 1.45);
			const outer = radius * (body.ringTexture ? 2.35 : 1.9);
			rings = this.createRings(inner, outer, body.ringTexture, body.name === 'Uranus' ? 0.45 : 0.95);
			tilt.add(rings);
		}

		if (body.name === 'Earth') {
			const atmosphere = new THREE.Mesh(
				new THREE.SphereGeometry(radius * 1.12, 48, 32),
				new THREE.ShaderMaterial({
					transparent: true,
					side: THREE.BackSide,
					depthWrite: false,
					uniforms: { glowColor: { value: new THREE.Color(0x7eb6ff) } },
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
							float fresnel = pow(1.0 - abs(dot(viewDir, normalize(vNormal))), 2.6);
							gl_FragColor = vec4(glowColor, fresnel * 0.7);
						}
					`
				})
			);
			anchor.add(atmosphere);
		}

		const anomaly = meanAnomaly ?? (body.meanAnomalyDeg * Math.PI) / 180;
		const position = orbitalPosition(elements, anomaly);
		anchor.position.set(position.x, position.y, position.z);

		const label = this.makeLabel(body.name);
		label.position.set(0, radius * 2.3, 0);
		anchor.add(label);

		const orbit = this.createOrbit(elements);
		this.scene.add(orbit.line);
		this.scene.add(anchor);

		return {
			body,
			anchor,
			spin,
			mesh,
			material,
			clouds,
			rings,
			label,
			orbit: orbit.line,
			orbitMaterial: orbit.material,
			meanAnomaly: anomaly,
			radius,
			nightUniform
		};
	}

	private createRings(inner: number, outer: number, textureUrl: string | undefined, opacity: number) {
		const geometry = new THREE.RingGeometry(inner, outer, 160);
		const position = geometry.attributes.position;
		const uv = geometry.attributes.uv;
		for (let i = 0; i < position.count; i += 1) {
			const x = position.getX(i);
			const y = position.getY(i);
			const radius = Math.hypot(x, y);
			uv.setXY(i, (radius - inner) / (outer - inner), 0.5);
		}
		uv.needsUpdate = true;
		const material = new THREE.MeshBasicMaterial({
			map: textureUrl ? this.loadMap(textureUrl, THREE.SRGBColorSpace) : null,
			color: textureUrl ? 0xffffff : 0xd5e4ff,
			side: THREE.DoubleSide,
			transparent: true,
			opacity,
			depthWrite: false
		});
		const mesh = new THREE.Mesh(geometry, material);
		mesh.rotation.x = Math.PI / 2;
		return mesh;
	}

	private createOrbit(elements: OrbitElements) {
		const points = orbitSamples(elements).map((point) => new THREE.Vector3(point.x, point.y, point.z));
		const geometry = new THREE.BufferGeometry().setFromPoints(points);
		const material = new THREE.LineBasicMaterial({
			color: 0xd7c4a1,
			transparent: true,
			opacity: 0.38
		});
		return { line: new THREE.LineLoop(geometry, material), material };
	}

	private makeLabel(text: string) {
		const element = document.createElement('div');
		element.className = 'sx-label';
		element.textContent = text;
		const label = new CSS2DObject(element);
		return label;
	}

	private clearPlanets() {
		for (const node of this.planets.values()) {
			this.scene.remove(node.anchor);
			this.scene.remove(node.orbit);
			node.orbit.geometry.dispose();
			node.orbitMaterial.dispose();
			node.mesh.geometry.dispose();
			node.material.dispose();
			disposeMesh(node.clouds);
			disposeMesh(node.rings);
			node.label.element.remove();
		}
		this.planets.clear();
	}

	private applyVisibility() {
		for (const node of this.planets.values()) {
			node.orbit.visible = this.showOrbits;
			node.label.visible = this.showLabels;
		}
		const sunLabel = this.sunMesh.userData.label as CSS2DObject | undefined;
		if (sunLabel) sunLabel.visible = this.showLabels;
	}

	private applySelection() {
		for (const node of this.planets.values()) {
			const active = node.body.name === this.selected;
			node.label.element.classList.toggle('is-selected', active);
			node.orbitMaterial.opacity = active ? 0.9 : 0.38;
			node.orbitMaterial.color.set(active ? 0xf3ddb0 : 0xd7c4a1);
		}
		const sunLabel = this.sunMesh.userData.label as CSS2DObject | undefined;
		sunLabel?.element.classList.toggle('is-selected', this.selected === 'Sun');
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
		const targets: THREE.Object3D[] = [this.sunMesh];
		for (const node of this.planets.values()) {
			targets.push(node.mesh);
			if (node.clouds) targets.push(node.clouds);
		}
		const hit = this.raycaster.intersectObjects(targets, false)[0];
		const name = (hit?.object.userData.name as string | undefined) ?? null;
		if (name) {
			this.focus(name);
		} else {
			this.selected = null;
			this.applySelection();
		}
		this.onSelect(name);
	};

	private animate() {
		if (this.disposed) return;
		this.animation = requestAnimationFrame(this.animate);
		const delta = Math.min(this.clock.getDelta(), 0.05);

		if (this.playing) {
			this.sunMesh.rotation.y += delta * 0.04 * Math.min(this.speed, 12);
			for (const node of this.planets.values()) {
				const omega = orbitalOmega(node.body.orbitalPeriodDays) * this.speed;
				node.meanAnomaly += omega * delta;
				const position = orbitalPosition(elementsOf(node.body), node.meanAnomaly);
				node.anchor.position.set(position.x, position.y, position.z);
				const hours = node.body.rotationHours || 24;
				const day = Math.abs(hours) / 24;
				const spinsPerYear = 365.25 / Math.max(day, 0.05);
				const radians = (spinsPerYear * Math.PI * 2 * this.speed) / EARTH_YEAR_SECONDS;
				const capped = Math.sign(hours) * Math.min(Math.abs(radians), 0.85);
				node.spin.rotation.y += capped * delta;
				if (node.clouds) node.clouds.rotation.y += delta * 0.02;
				if (node.nightUniform) {
					node.nightUniform.value.copy(node.anchor.position).multiplyScalar(-1).normalize();
				}
			}
		}

		if (this.follow === 'Sun') {
			this.controls.target.set(0, 0, 0);
			if (this.snap) {
				this.camera.position.set(0, SUN_SCENE_RADIUS * 1.4, SUN_SCENE_RADIUS * 5.5);
				this.snap = false;
			}
		} else if (this.follow) {
			const node = this.planets.get(this.follow);
			if (node) {
				this.controls.target.copy(node.anchor.position);
				if (this.snap) {
					this.camera.position
						.copy(node.anchor.position)
						.add(new THREE.Vector3(node.radius * 0.4, node.radius * 1.8, node.radius * 6.2));
					this.snap = false;
				}
			}
		}

		this.controls.update();
		this.renderer.render(this.scene, this.camera);
		this.labels.render(this.scene, this.camera);
	}

	private loadMap(url: string, colorSpace: THREE.ColorSpace) {
		const cached = this.textureCache.get(url);
		if (cached) return cached;
		const texture = this.loader.load(url);
		texture.colorSpace = colorSpace;
		texture.anisotropy = Math.min(8, this.renderer.capabilities.getMaxAnisotropy());
		this.textureCache.set(url, texture);
		return texture;
	}
}

function elementsOf(body: ResolvedBody): OrbitElements {
	return {
		distanceAu: body.distanceAu,
		eccentricity: body.eccentricity,
		inclinationDeg: body.inclinationDeg,
		ascendingNodeDeg: body.ascendingNodeDeg,
		argPeriapsisDeg: body.argPeriapsisDeg
	};
}

function disposeMesh(mesh?: THREE.Mesh) {
	if (!mesh) return;
	mesh.geometry.dispose();
	const material = mesh.material as THREE.Material;
	material.dispose();
}
