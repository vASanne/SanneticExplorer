/** One Earth year at 1× playback. Higher speeds divide this. */
export const EARTH_YEAR_SECONDS = 48;

const AU_SCALE = 16;
const DISTANCE_POWER = 0.72;

/**
 * Map astronomical units into the scene.
 * A power below 1 keeps true order and a wide Neptune/Mercury ratio while
 * leaving the inner planets outside the Sun and inside one camera frame.
 * Real AU ratio Neptune/Mercury is ~78; this curve is ~23.
 */
export function auToScene(au: number): number {
	const safe = Math.max(au, 0.02);
	return AU_SCALE * Math.pow(safe, DISTANCE_POWER);
}

/** Planet radii are enlarged versus true scale so maps read in an orrery. */
export function visualRadiusKm(radiusKm: number): number {
	const earthKm = 6371;
	return 0.7 * Math.pow(Math.max(radiusKm, 200) / earthKm, 0.5);
}

export const SUN_SCENE_RADIUS = 3.35;

export function orbitalOmega(periodDays: number): number {
	const years = Math.max(periodDays, 1) / 365.25;
	return (Math.PI * 2) / (years * EARTH_YEAR_SECONDS);
}

export interface OrbitElements {
	distanceAu: number;
	eccentricity: number;
	inclinationDeg: number;
	ascendingNodeDeg: number;
	argPeriapsisDeg: number;
}

export interface ScenePoint {
	x: number;
	y: number;
	z: number;
}

function solveEccentricAnomaly(meanAnomaly: number, eccentricity: number): number {
	let eccentric = meanAnomaly;
	for (let i = 0; i < 8; i += 1) {
		const delta =
			(eccentric - eccentricity * Math.sin(eccentric) - meanAnomaly) /
			(1 - eccentricity * Math.cos(eccentric));
		eccentric -= delta;
	}
	return eccentric;
}

/** Position from eccentric anomaly so orbit lines are evenly sampled. */
export function positionFromEccentricAnomaly(elements: OrbitElements, eccentricAnomaly: number): ScenePoint {
	const eccentricity = Math.min(Math.max(elements.eccentricity, 0), 0.95);
	const semiMajor = auToScene(elements.distanceAu);
	const cosE = Math.cos(eccentricAnomaly);
	const sinE = Math.sin(eccentricAnomaly);
	const xOrb = semiMajor * (cosE - eccentricity);
	const zOrb = semiMajor * Math.sqrt(1 - eccentricity * eccentricity) * sinE;

	const peri = (elements.argPeriapsisDeg * Math.PI) / 180;
	const x1 = xOrb * Math.cos(peri) - zOrb * Math.sin(peri);
	const z1 = xOrb * Math.sin(peri) + zOrb * Math.cos(peri);

	const inclination = (elements.inclinationDeg * Math.PI) / 180;
	const y2 = -z1 * Math.sin(inclination);
	const z2 = z1 * Math.cos(inclination);

	const node = (elements.ascendingNodeDeg * Math.PI) / 180;
	return {
		x: x1 * Math.cos(node) - z2 * Math.sin(node),
		y: y2,
		z: x1 * Math.sin(node) + z2 * Math.cos(node)
	};
}

export function orbitalPosition(elements: OrbitElements, meanAnomaly: number): ScenePoint {
	const eccentricity = Math.min(Math.max(elements.eccentricity, 0), 0.95);
	const eccentric = solveEccentricAnomaly(meanAnomaly, eccentricity);
	return positionFromEccentricAnomaly(elements, eccentric);
}

export function orbitSamples(elements: OrbitElements, count = 192): ScenePoint[] {
	const samples: ScenePoint[] = [];
	for (let i = 0; i <= count; i += 1) {
		const eccentric = (i / count) * Math.PI * 2;
		samples.push(positionFromEccentricAnomaly(elements, eccentric));
	}
	return samples;
}

export function sceneRadius(point: ScenePoint): number {
	return Math.hypot(point.x, point.y, point.z);
}
