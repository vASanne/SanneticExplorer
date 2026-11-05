<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import * as THREE from 'three';
	import { getPlanets, type PlanetData } from '../api';
	
	// Props from parent
	export let showStars = false; // Disabled by default since we're removing fake stars
	export let ambientLightIntensity = 0.4;
	export let showOrbits = true;
	export let showPlanetNames = true;
	export let showSunName = true;
	export let isAnimationPlaying = true; // Animation play/pause state
	export let animationSpeed = 0.5; // Animation speed (0.5 = 50% slower than original)
	export let onReset: () => void = () => {}; // Reset callback from parent
	export let onObjectClick: (objectData: any) => void = () => {}; // Object click callback
	
	let container: HTMLDivElement;
	let scene: THREE.Scene;
	let camera: THREE.PerspectiveCamera;
	let renderer: THREE.WebGLRenderer;
	let animationId: number;
	let sun: THREE.Mesh;
	let planets: THREE.Mesh[] = [];
	let orbits: THREE.Object3D[] = [];
	let planetLabels: THREE.Sprite[] = [];
	let sunLabel: THREE.Sprite | null = null;
	let raycaster: THREE.Raycaster;
	let mouse: THREE.Vector2;
	
	// Camera controls
	let cameraDistance = 100;
	let cameraAngle = 0;
	let cameraHeight = 50;
	let autoRotate = true;
	
	// Zoom limits
	const MIN_ZOOM = 20;
	const MAX_ZOOM = 500;
	const ZOOM_SPEED = 0.1;
	
	// Real astronomical data from API
	// Sun radius: 696,340 km
	// Scaling: 1 unit = 100,000 km for visualization
	const SUN_RADIUS_KM = 696340;
	const SCALE_FACTOR = 100000; // 1 unit = 100,000 km
	const AU_IN_KM = 149597870.7; // 1 AU in km
	
	// Planet data will be loaded from API
	let realPlanetsData: PlanetData[] = [];
	let planetsLoaded = false;
	
	// Toggle animation play/pause
	export function toggleAnimation() {
		isAnimationPlaying = !isAnimationPlaying;
	}

	// Reset function
	export function resetScene() {
		cameraDistance = 100;
		cameraAngle = 0;
		cameraHeight = 50;
		autoRotate = true;
		ambientLightIntensity = 0.4;
		showOrbits = true;
		showPlanetNames = true;
		showSunName = true;
		isAnimationPlaying = true;
		animationSpeed = 0.5;
		
		// Update lighting and visibility
		updateLighting();
		updateOrbitsVisibility();
		updatePlanetLabelsVisibility();
		updateSunLabelVisibility();
		
		// Trigger parent reset
		onReset();
	}

	// Focus on specific celestial object
	export function focusOnObject(objectName: string) {
		autoRotate = false; // Stop auto-rotation when focusing
		
		if (objectName.toLowerCase() === 'sonne' || objectName.toLowerCase() === 'sun') {
			// Focus on Sun
			cameraDistance = 30;
			cameraAngle = 0;
			cameraHeight = 10;
		} else {
			// Find planet by name
			const planet = planets.find(p => 
				(p as any).userData.name.toLowerCase() === objectName.toLowerCase()
			);
			
			if (planet) {
				const userData = (planet as any).userData;
				// Set camera to follow the planet
				cameraDistance = Math.max(userData.orbitalDistance * 0.3, 20);
				
				// Calculate angle to planet's current position
				cameraAngle = Math.atan2(-planet.position.z, planet.position.x);
				cameraHeight = 20;
				
				console.log(`Focusing on ${objectName}:`, {
					distance: cameraDistance,
					angle: cameraAngle,
					height: cameraHeight,
					planetPosition: { x: planet.position.x, z: planet.position.z }
				});
			}
		}
	}
	
	function fallbackPlanets(): PlanetData[] {
		return [
			{ id: '1', name: 'Mercury', type: 'planet', radius_km: 2439.5, mean_distance_au: 0.387, orbital_period_days: 88, color_hex: '#8c7853', data_quality: 'fallback' },
			{ id: '2', name: 'Venus', type: 'planet', radius_km: 6052, mean_distance_au: 0.723, orbital_period_days: 225, color_hex: '#e7cdcd', data_quality: 'fallback' },
			{ id: '3', name: 'Earth', type: 'planet', radius_km: 6371, mean_distance_au: 1.0, orbital_period_days: 365.25, color_hex: '#6b93d6', data_quality: 'fallback' },
			{ id: '4', name: 'Mars', type: 'planet', radius_km: 3389.5, mean_distance_au: 1.524, orbital_period_days: 687, color_hex: '#c1440e', data_quality: 'fallback' },
			{ id: '5', name: 'Jupiter', type: 'planet', radius_km: 69911, mean_distance_au: 5.203, orbital_period_days: 4333, color_hex: '#d8ca9d', data_quality: 'fallback' },
			{ id: '6', name: 'Saturn', type: 'planet', radius_km: 58232, mean_distance_au: 9.537, orbital_period_days: 10759, color_hex: '#fad5a5', has_rings: true, data_quality: 'fallback' },
			{ id: '7', name: 'Uranus', type: 'planet', radius_km: 25362, mean_distance_au: 19.191, orbital_period_days: 30687, color_hex: '#4fd0e7', data_quality: 'fallback' },
			{ id: '8', name: 'Neptune', type: 'planet', radius_km: 24622, mean_distance_au: 30.069, orbital_period_days: 60190, color_hex: '#4b70dd', data_quality: 'fallback' }
		];
	}

	async function initializeScene() {
		// Load planet data from API first. An empty list is not a usable solar system.
		console.log('Starting to load planets from API...');
		try {
			console.log('Calling getPlanets()...');
			const loaded = await getPlanets();
			if (!loaded || loaded.length === 0) {
				console.warn('Planet API returned no planets; using the eight-planet fallback');
				realPlanetsData = fallbackPlanets();
			} else {
				realPlanetsData = loaded;
				console.log('Successfully loaded planets from API:', realPlanetsData.length, realPlanetsData);
			}
		} catch (error) {
			console.error('Failed to load planets from API:', error);
			console.log('Using fallback planet data...');
			realPlanetsData = fallbackPlanets();
		}
		planetsLoaded = true;
		
		initThreeJS();
		createSolarSystem();
		animate();
		
		// Setup mouse controls after everything is initialized
		setupMouseControls();
		
		// Setup object clicking
		setupObjectClicking();
	}
	
	onMount(() => {
		initializeScene();
		
		// Handle window resize
		const handleResize = () => {
			if (camera && renderer) {
				camera.aspect = window.innerWidth / window.innerHeight;
				camera.updateProjectionMatrix();
				renderer.setSize(window.innerWidth, window.innerHeight);
			}
		};
		
		window.addEventListener('resize', handleResize);
		
		return () => {
			window.removeEventListener('resize', handleResize);
		};
	});
	
	onDestroy(() => {
		if (animationId) {
			cancelAnimationFrame(animationId);
		}
		if (renderer) {
			renderer.dispose();
		}
	});
	
	// React to prop changes
	$: if (scene) updateLighting();
	$: if (orbits.length > 0) updateOrbitsVisibility();
	$: if (planetLabels.length > 0) updatePlanetLabelsVisibility();
	$: if (sunLabel) updateSunLabelVisibility();
	
	// Debug: Log prop changes
	$: console.log('Scene3D Props Update:', { showStars, ambientLightIntensity, showOrbits, showPlanetNames, showSunName });
	
	function updateOrbitsVisibility() {
		console.log('Updating orbits visibility:', showOrbits, 'Number of orbits:', orbits.length);
		orbits.forEach((orbit, index) => {
			orbit.visible = showOrbits;
			console.log(`Orbit ${index} visibility set to:`, orbit.visible);
		});
	}
	
	function updateLighting() {
		const ambientLight = scene.getObjectByName('ambientLight') as THREE.AmbientLight;
		if (ambientLight) {
			ambientLight.intensity = ambientLightIntensity;
		}
	}
	
	function updatePlanetLabelsVisibility() {
		console.log('Updating planet labels visibility:', showPlanetNames, 'Number of labels:', planetLabels.length);
		planetLabels.forEach((label, index) => {
			label.visible = showPlanetNames;
			console.log(`Planet label ${index} visibility set to:`, label.visible);
		});
	}
	
	function updateSunLabelVisibility() {
		if (sunLabel) {
			console.log('Updating sun label visibility:', showSunName);
			sunLabel.visible = showSunName;
		}
	}
	
	function setupMouseControls() {
		if (!container) return;
		
		// Wait for renderer to be available
		const setupControls = () => {
			if (!renderer) {
				setTimeout(setupControls, 100);
				return;
			}
			
			const canvas = renderer.domElement;
			
			// Mouse wheel zoom
			const handleWheel = (event: WheelEvent) => {
				event.preventDefault();
				event.stopPropagation();
				
				const delta = event.deltaY;
				const zoomFactor = delta > 0 ? 1 + ZOOM_SPEED : 1 - ZOOM_SPEED;
				
				cameraDistance *= zoomFactor;
				cameraDistance = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, cameraDistance));
				
				// Update label scales immediately when zooming
				updateLabelScales();
				
				// Pause auto-rotation when user is zooming
				autoRotate = false;
				
				// Resume auto-rotation after 3 seconds of no interaction
				setTimeout(() => {
					autoRotate = true;
				}, 3000);
			};
			
			// Mouse drag to rotate
			let isDragging = false;
			let previousMousePosition = { x: 0, y: 0 };
			
			const handleMouseDown = (event: MouseEvent) => {
				event.preventDefault();
				event.stopPropagation();
				isDragging = true;
				previousMousePosition = { x: event.clientX, y: event.clientY };
				autoRotate = false;
				canvas.style.cursor = 'grabbing';
			};
			
			const handleMouseMove = (event: MouseEvent) => {
				if (!isDragging) return;
				event.preventDefault();
				event.stopPropagation();
				
				const deltaMove = {
					x: event.clientX - previousMousePosition.x,
					y: event.clientY - previousMousePosition.y
				};
				
				cameraAngle += deltaMove.x * 0.01;
				cameraHeight += deltaMove.y * 0.5;
				cameraHeight = Math.max(-100, Math.min(100, cameraHeight));
				
				previousMousePosition = { x: event.clientX, y: event.clientY };
			};
			
			const handleMouseUp = (event: MouseEvent) => {
				if (!isDragging) return;
				event.preventDefault();
				event.stopPropagation();
				isDragging = false;
				canvas.style.cursor = 'grab';
				// Resume auto-rotation after 3 seconds
				setTimeout(() => {
					autoRotate = true;
				}, 3000);
			};
			
			// Add event listeners to canvas
			canvas.addEventListener('wheel', handleWheel, { passive: false });
			canvas.addEventListener('mousedown', handleMouseDown);
			canvas.addEventListener('mousemove', handleMouseMove);
			canvas.addEventListener('mouseup', handleMouseUp);
			canvas.addEventListener('mouseleave', handleMouseUp);
			
			// Global mouse events for drag outside canvas
			document.addEventListener('mousemove', handleMouseMove);
			document.addEventListener('mouseup', handleMouseUp);
			
			// Set initial cursor
			canvas.style.cursor = 'grab';
			
			// Return cleanup function
			return () => {
				canvas.removeEventListener('wheel', handleWheel);
				canvas.removeEventListener('mousedown', handleMouseDown);
				canvas.removeEventListener('mousemove', handleMouseMove);
				canvas.removeEventListener('mouseup', handleMouseUp);
				canvas.removeEventListener('mouseleave', handleMouseUp);
				document.removeEventListener('mousemove', handleMouseMove);
				document.removeEventListener('mouseup', handleMouseUp);
			};
		};
		
		return setupControls();
	}
	
	function setupObjectClicking() {
		if (!container) return;
		
		const handleClick = (event: MouseEvent) => {
			// Prevent default behavior
			event.preventDefault();
			
			// Calculate mouse position in normalized device coordinates (-1 to +1)
			const rect = renderer.domElement.getBoundingClientRect();
			mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
			mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
			
			// Update the picking ray with the camera and mouse position
			raycaster.setFromCamera(mouse, camera);
			
			// Calculate objects intersecting the picking ray
			const clickableObjects = [...planets];
			if (sun) clickableObjects.push(sun);
			
			const intersects = raycaster.intersectObjects(clickableObjects);
			
			if (intersects.length > 0) {
				const clickedObject = intersects[0].object;
				
				// Determine if it's the sun or a planet
				if (clickedObject === sun) {
					const sunData = {
						type: 'star',
						name: 'Sonne',
						radius: `${SUN_RADIUS_KM.toLocaleString()} km`,
						mass: formatMass(1.989e30), // Sun mass in kg
						temperature: formatTemperature(5778), // Surface temperature in Kelvin
						composition: '73% Wasserstoff, 25% Helium',
						age: '4.6 Milliarden Jahre',
						luminosity: '3.828 × 10²⁶ W',
						spectralClass: 'G2V'
					};
					onObjectClick(sunData);
				} else {
					// Find the planet data
					const planetIndex = planets.indexOf(clickedObject as THREE.Mesh);
					if (planetIndex !== -1) {
											const planetData = realPlanetsData[planetIndex];
					const userData = (clickedObject as any).userData;
					
					const diameter = (planetData.radius_km || 0) * 2;
					const distance_au = planetData.mean_distance_au || 0;
					const orbital_period = planetData.orbital_period_days || 0;
					
					const planetInfo = {
						type: 'planet',
						name: planetData.name,
						diameter: `${diameter.toLocaleString()} km`,
						radius: `${(planetData.radius_km || 0).toLocaleString()} km`,
						distanceFromSun: `${distance_au} AU (${(distance_au * AU_IN_KM).toLocaleString()} km)`,
						orbitalPeriod: `${orbital_period} Erdtage`,
						orbitalSpeed: `${(planetData.orbital_speed_kms || 0).toFixed(1)} km/s`,
						currentAngle: `${(userData.angle * 180 / Math.PI).toFixed(1)}°`,
						mass: formatMass(planetData.mass_kg),
						gravity: `${(planetData.surface_gravity_ms2 || 0).toFixed(2)} m/s²`,
						temperature: formatTemperature(planetData.surface_temperature_k),
						atmosphere: formatAtmosphere(planetData.atmospheric_composition),
						moons: getMoonCount(planetData.name)
					};
						onObjectClick(planetInfo);
					}
				}
			}
		};
		
		const canvas = renderer.domElement;
		canvas.addEventListener('click', handleClick);
		
		return () => {
			canvas.removeEventListener('click', handleClick);
		};
	}
	
	function formatMass(mass_kg?: number): string {
		if (!mass_kg) return 'Unbekannt';
		
		// Convert kg to tons
		const mass_tons = mass_kg / 1000;
		
		// Earth mass in kg for comparison
		const earth_mass_kg = 5.972e24;
		const earth_masses = mass_kg / earth_mass_kg;
		
		// Format in scientific notation for tons
		const exponent = Math.floor(Math.log10(mass_tons));
		const mantissa = mass_tons / Math.pow(10, exponent);
		
		return `${mantissa.toFixed(3)} × 10^${exponent} t (${earth_masses.toFixed(3)} Erdmassen)`;
	}
	
	function formatAtmosphere(composition?: Record<string, any>): string {
		if (!composition) return 'Keine Atmosphäre';
		
		const components = Object.entries(composition)
			.map(([element, percentage]) => `${element}: ${percentage}`)
			.join(', ');
		
		return components || 'Unbekannt';
	}
	
	function formatTemperature(tempK?: number): string {
		if (!tempK) return 'Unbekannt';
		
		// Convert Kelvin to Celsius
		const tempC = tempK - 273.15;
		return `${tempC.toFixed(1)}°C`;
	}
	
	function getMoonCount(planetName: string): string {
		// This could be enhanced to get moon count from API
		const moonCounts: { [key: string]: string } = {
			'Mercury': '0',
			'Venus': '0',
			'Earth': '1',
			'Mars': '2',
			'Jupiter': '95',
			'Saturn': '146',
			'Uranus': '27',
			'Neptune': '14'
		};
		return moonCounts[planetName] || '0';
	}
	
	function getPlanetGravity(planetName: string): string {
		const gravities: { [key: string]: string } = {
			'Mercury': '3.7 m/s²',
			'Venus': '8.87 m/s²',
			'Earth': '9.81 m/s²',
			'Mars': '3.71 m/s²',
			'Jupiter': '24.79 m/s²',
			'Saturn': '10.44 m/s²',
			'Uranus': '8.69 m/s²',
			'Neptune': '11.15 m/s²'
		};
		return gravities[planetName] || 'Unbekannt';
	}
	
	function getPlanetAtmosphere(planetName: string): string {
		const atmospheres: { [key: string]: string } = {
			'Mercury': 'Praktisch keine Atmosphäre',
			'Venus': '96% CO₂, 3.5% N₂, sehr dicht',
			'Earth': '78% N₂, 21% O₂, 1% andere',
			'Mars': '95% CO₂, 3% N₂, sehr dünn',
			'Jupiter': 'H₂, He, Methan, Ammoniak',
			'Saturn': 'H₂, He, Methan, Ammoniak',
			'Uranus': 'H₂, He, Methan',
			'Neptune': 'H₂, He, Methan'
		};
		return atmospheres[planetName] || 'Unbekannt';
	}
	
	function getPlanetMoons(planetName: string): string {
		const moons: { [key: string]: string } = {
			'Mercury': '0',
			'Venus': '0',
			'Earth': '1 (Mond)',
			'Mars': '2 (Phobos, Deimos)',
			'Jupiter': '95+ bekannte Monde',
			'Saturn': '146+ bekannte Monde',
			'Uranus': '27+ bekannte Monde',
			'Neptune': '14+ bekannte Monde'
		};
		return moons[planetName] || 'Unbekannt';
	}
	
	function initThreeJS() {
		// Scene with space background
		scene = new THREE.Scene();
		scene.background = new THREE.Color(0x000011); // Deep space color
		
		// Camera - positioned for solar system view
		camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 10000);
		updateCameraPosition();
		
		// Renderer - Full screen
		renderer = new THREE.WebGLRenderer({ antialias: true });
		renderer.setSize(window.innerWidth, window.innerHeight);
		renderer.shadowMap.enabled = true;
		renderer.shadowMap.type = THREE.PCFSoftShadowMap;
		
		container.appendChild(renderer.domElement);
		
		// Initialize raycaster and mouse for object clicking
		raycaster = new THREE.Raycaster();
		mouse = new THREE.Vector2();
		
		// Sun lighting - realistic intensity
		const sunLight = new THREE.PointLight(0xffffff, 2, 1000);
		sunLight.position.set(0, 0, 0);
		sunLight.castShadow = true;
		sunLight.shadow.mapSize.width = 2048;
		sunLight.shadow.mapSize.height = 2048;
		scene.add(sunLight);
		
		const ambientLight = new THREE.AmbientLight(0x404040, ambientLightIntensity);
		ambientLight.name = 'ambientLight';
		scene.add(ambientLight);
		
		// Directional light for better visibility
		const directionalLight = new THREE.DirectionalLight(0xffffff, 0.3);
		directionalLight.position.set(20, 20, 10);
		scene.add(directionalLight);
	}
	
	function updateCameraPosition() {
		if (!camera) return;
		
		camera.position.x = Math.cos(cameraAngle) * cameraDistance;
		camera.position.z = Math.sin(cameraAngle) * cameraDistance;
		camera.position.y = cameraHeight;
		camera.lookAt(0, 0, 0);
	}
	
	function createPlanetTexture(planetData: PlanetData): THREE.MeshPhongMaterial {
		// Create canvas for procedural texture
		const canvas = document.createElement('canvas');
		canvas.width = 512;
		canvas.height = 256;
		const context = canvas.getContext('2d')!;
		
		// Create gradient based on planet
		const gradient = context.createLinearGradient(0, 0, 512, 256);
		const colorHex = planetData.color_hex || '#ffffff';
		const color = new THREE.Color(colorHex);
		
		// Add texture patterns based on planet type
		switch (planetData.name) {
			case 'Earth':
				gradient.addColorStop(0, '#4a90e2');
				gradient.addColorStop(0.3, '#7ed321');
				gradient.addColorStop(0.7, '#4a90e2');
				gradient.addColorStop(1, '#2e5c8a');
				break;
			case 'Mars':
				gradient.addColorStop(0, '#cd5c5c');
				gradient.addColorStop(0.5, '#a0522d');
				gradient.addColorStop(1, '#8b4513');
				break;
			case 'Jupiter':
				gradient.addColorStop(0, '#daa520');
				gradient.addColorStop(0.3, '#cd853f');
				gradient.addColorStop(0.6, '#daa520');
				gradient.addColorStop(1, '#b8860b');
				break;
			case 'Saturn':
				gradient.addColorStop(0, '#fad5a5');
				gradient.addColorStop(0.5, '#deb887');
				gradient.addColorStop(1, '#d2b48c');
				break;
			case 'Venus':
				gradient.addColorStop(0, '#e7cdcd');
				gradient.addColorStop(0.5, '#f5deb3');
				gradient.addColorStop(1, '#dda0dd');
				break;
			case 'Mercury':
				gradient.addColorStop(0, '#8c7853');
				gradient.addColorStop(0.5, '#a0522d');
				gradient.addColorStop(1, '#696969');
				break;
			case 'Uranus':
				gradient.addColorStop(0, '#4fd0e7');
				gradient.addColorStop(0.5, '#87ceeb');
				gradient.addColorStop(1, '#4682b4');
				break;
			case 'Neptune':
				gradient.addColorStop(0, '#4b70dd');
				gradient.addColorStop(0.5, '#0000cd');
				gradient.addColorStop(1, '#191970');
				break;
			default:
				gradient.addColorStop(0, `#${color.getHexString()}`);
				gradient.addColorStop(0.5, `#${color.clone().multiplyScalar(0.8).getHexString()}`);
				gradient.addColorStop(1, `#${color.clone().multiplyScalar(1.2).getHexString()}`);
		}
		
		context.fillStyle = gradient;
		context.fillRect(0, 0, 512, 256);
		
		// Add some surface details
		for (let i = 0; i < 30; i++) {
			context.beginPath();
			context.fillStyle = `rgba(${Math.random() * 50}, ${Math.random() * 50}, ${Math.random() * 50}, 0.2)`;
			context.arc(Math.random() * 512, Math.random() * 256, Math.random() * 8, 0, Math.PI * 2);
			context.fill();
		}
		
		const texture = new THREE.CanvasTexture(canvas);
		texture.wrapS = THREE.RepeatWrapping;
		texture.wrapT = THREE.RepeatWrapping;
		
		return new THREE.MeshPhongMaterial({ 
			map: texture,
			shininess: planetData.name === 'Earth' ? 100 : 30,
			specular: planetData.name === 'Earth' ? 0x111111 : 0x000000
		});
	}
	
	function createSunTexture(): THREE.MeshBasicMaterial {
		const canvas = document.createElement('canvas');
		canvas.width = 512;
		canvas.height = 256;
		const context = canvas.getContext('2d')!;
		
		// Create sun gradient
		const gradient = context.createRadialGradient(256, 128, 0, 256, 128, 256);
		gradient.addColorStop(0, '#ffff44');
		gradient.addColorStop(0.5, '#ffaa00');
		gradient.addColorStop(1, '#ff6600');
		
		context.fillStyle = gradient;
		context.fillRect(0, 0, 512, 256);
		
		// Add solar flares
		for (let i = 0; i < 20; i++) {
			context.beginPath();
			context.fillStyle = `rgba(255, 255, ${Math.random() * 100 + 155}, ${Math.random() * 0.5 + 0.3})`;
			context.arc(Math.random() * 512, Math.random() * 256, Math.random() * 15, 0, Math.PI * 2);
			context.fill();
		}
		
		const texture = new THREE.CanvasTexture(canvas);
		texture.wrapS = THREE.RepeatWrapping;
		texture.wrapT = THREE.RepeatWrapping;
		
		return new THREE.MeshBasicMaterial({
			map: texture,
			color: 0xffff00
		});
	}
	
	function createTextLabel(text: string, color: string = '#ffffff'): THREE.Sprite {
		const canvas = document.createElement('canvas');
		const context = canvas.getContext('2d')!;
		
		// Set canvas size - larger for better readability
		canvas.width = 1024;
		canvas.height = 256;
		
		// Set font - significantly larger for better visibility
		context.font = 'Bold 96px Arial';
		context.fillStyle = color;
		context.textAlign = 'center';
		context.textBaseline = 'middle';
		
		// No background - 100% transparent as requested
		// Clear the canvas to be fully transparent
		context.clearRect(0, 0, canvas.width, canvas.height);
		
		// Draw text with outline for better visibility
		context.strokeStyle = 'rgba(0, 0, 0, 0.9)';
		context.lineWidth = 12;
		context.strokeText(text, canvas.width / 2, canvas.height / 2);
		
		// Draw the main text
		context.fillStyle = color;
		context.fillText(text, canvas.width / 2, canvas.height / 2);
		
		// Create texture and sprite
		const texture = new THREE.CanvasTexture(canvas);
		const spriteMaterial = new THREE.SpriteMaterial({ map: texture, transparent: true });
		const sprite = new THREE.Sprite(spriteMaterial);
		
		// Base scale - will be adjusted dynamically based on camera distance
		sprite.scale.set(12, 3, 1);
		
		return sprite;
	}
	
	function updateLabelScales() {
		// Calculate scale factor based on camera distance
		// Base distance is 100, scale labels proportionally
		const scaleFactor = cameraDistance / 100;
		const baseScale = 12;
		const baseHeight = 3;
		
		// Update all planet labels with consistent size regardless of distance
		planetLabels.forEach((label) => {
			label.scale.set(baseScale * scaleFactor, baseHeight * scaleFactor, 1);
		});
		
		// Update sun label
		if (sunLabel) {
			sunLabel.scale.set(baseScale * scaleFactor, baseHeight * scaleFactor, 1);
		}
	}
	
	function createSolarSystem() {
		// Create Sun with correct scale
		// Sun radius scaled down for visualization: 696,340 km / 100,000 = ~7 units
		const sunRadius = SUN_RADIUS_KM / SCALE_FACTOR;
		const sunGeometry = new THREE.SphereGeometry(sunRadius * 0.1, 32, 32); // Further scaled for visibility
		const sunMaterial = createSunTexture();
		sun = new THREE.Mesh(sunGeometry, sunMaterial);
		scene.add(sun);
		
		// Create Sun label
		sunLabel = createTextLabel('Sonne', '#ffff00');
		sunLabel.position.set(0, sunRadius * 0.15, 0); // Position above the sun
		sunLabel.visible = showSunName;
		scene.add(sunLabel);
		
		// Create planets with real astronomical data
		realPlanetsData.forEach((planetData, index) => {
			// Calculate planet radius: radius scaled down
			const planetRadius = (planetData.radius_km || 1000) / SCALE_FACTOR;
			// Scale down further for visibility but maintain relative sizes
			const scaledRadius = Math.max(planetRadius * 0.05, 0.1); // Minimum visible size
			
			const planetGeometry = new THREE.SphereGeometry(scaledRadius, 24, 24);
			const planetMaterial = createPlanetTexture(planetData);
			const planet = new THREE.Mesh(planetGeometry, planetMaterial);
			
			// Calculate orbital distance: AU converted to scene units
			const orbitalDistance = (planetData.mean_distance_au || 1) * 10; // 1 AU = 10 scene units
			planet.position.x = orbitalDistance;
			planet.castShadow = true;
			planet.receiveShadow = true;
			
			// Create orbit ring with LineLoop for consistent thin lines
			const orbitPoints = [];
			const segments = 128;
			for (let i = 0; i <= segments; i++) {
				const angle = (i / segments) * Math.PI * 2;
				orbitPoints.push(new THREE.Vector3(
					Math.cos(angle) * orbitalDistance,
					0,
					Math.sin(angle) * orbitalDistance
				));
			}
			const orbitGeometry = new THREE.BufferGeometry().setFromPoints(orbitPoints);
			const orbitMaterial = new THREE.LineBasicMaterial({ 
				color: 0x444444, 
				transparent: true,
				opacity: 0.4
			});
			const orbit = new THREE.LineLoop(orbitGeometry, orbitMaterial);
			orbit.visible = showOrbits;
			orbits.push(orbit);
			scene.add(orbit);
			
			// Add Saturn's rings
			if (planetData.has_rings) {
				const ringGeometry = new THREE.RingGeometry(scaledRadius * 1.5, scaledRadius * 2.5, 32);
				const ringMaterial = new THREE.MeshBasicMaterial({ 
					color: 0xcccccc, 
					side: THREE.DoubleSide,
					transparent: true,
					opacity: 0.6
				});
				const ring = new THREE.Mesh(ringGeometry, ringMaterial);
				ring.rotation.x = Math.PI / 2;
				planet.add(ring);
			}
			
			planets.push(planet);
			scene.add(planet);
			
			// Create planet label
			const planetLabel = createTextLabel(planetData.name, '#ffffff');
			planetLabel.position.set(orbitalDistance, scaledRadius + 1, 0); // Position above the planet
			planetLabel.visible = showPlanetNames;
			planetLabels.push(planetLabel);
			scene.add(planetLabel);
			
			// Store planet data with realistic orbital speed
			// Convert orbital period to angular velocity (slower = longer period)
			const angularVelocity = (2 * Math.PI) / ((planetData.orbital_period_days || 365) * 10); // Scaled for animation
			(planet as any).userData = { 
				...planetData, 
				angle: Math.random() * Math.PI * 2,
				angularVelocity: angularVelocity,
				orbitalDistance: orbitalDistance
			};
			
			// Store label reference in planet userData for animation
			(planet as any).userData.label = planetLabel;
		});
	}
	
	function animate() {
		animationId = requestAnimationFrame(animate);
		
		// Only animate if animation is playing
		if (isAnimationPlaying) {
			// Rotate sun
			if (sun) {
				sun.rotation.y += 0.01 * animationSpeed;
			}
			
			// Animate planets with realistic orbital mechanics
			planets.forEach((planet) => {
				const data = (planet as any).userData;
				// All planets orbit counter-clockwise (positive angular velocity)
				// Use consistent positive direction for all planets
				data.angle += Math.abs(data.angularVelocity) * animationSpeed;
				
				// Update planet position based on orbital mechanics (counter-clockwise)
				// Ensure consistent counter-clockwise motion for all planets
				planet.position.x = Math.cos(data.angle) * data.orbitalDistance;
				planet.position.z = -Math.sin(data.angle) * data.orbitalDistance; // Negative Z for counter-clockwise
				
				// Update planet label position to follow the planet
				if (data.label) {
					data.label.position.x = planet.position.x;
					data.label.position.z = planet.position.z;
					data.label.position.y = planet.position.y + 1.5; // Position above the planet
				}
				
				// Rotate planet on its axis (faster than orbital motion)
				planet.rotation.y += 0.02 * animationSpeed;
			});
			
			// Auto-rotate camera if enabled
			if (autoRotate) {
				cameraAngle += 0.0001 * animationSpeed;
			}
		}
		
		// Update camera position
		updateCameraPosition();
		
		// Update label scales based on current zoom level
		updateLabelScales();
		
		renderer.render(scene, camera);
	}
</script>

<!-- Full screen container -->
<div bind:this={container} class="w-full h-full absolute inset-0" style="width: 100vw; height: 100vh;">
	<!-- Three.js canvas will be mounted here -->
	
	<!-- Play/Pause Button -->
	<div class="absolute bottom-6 left-1/2 transform -translate-x-1/2 z-50">
		<button 
			class="btn btn-circle btn-lg bg-black/70 backdrop-blur-sm border-gray-600 hover:bg-black/80 text-white shadow-lg"
			on:click={toggleAnimation}
			title={isAnimationPlaying ? 'Animation pausieren' : 'Animation starten'}
		>
			{#if isAnimationPlaying}
				<!-- Pause Icon -->
				<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
					<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd"></path>
				</svg>
			{:else}
				<!-- Play Icon -->
				<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
					<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"></path>
				</svg>
			{/if}
		</button>
	</div>
</div>

<style>
	:global(canvas) {
		display: block !important;
		width: 100vw !important;
		height: 100vh !important;
	}
</style> 