import type { PlanetData } from '$lib/api';
import { CATALOG, CLASSICAL_PLANETS, catalogByName, type CatalogBody } from './catalog';
import { formatAtmosphere } from './format';

export type DataOrigin = 'live' | 'reference';
export type SystemOrigin = 'live' | 'reference' | 'partial';

export interface ResolvedBody {
	id: string;
	name: string;
	subtype: string;
	origin: DataOrigin;
	radiusKm: number;
	distanceAu: number;
	orbitalPeriodDays: number;
	eccentricity: number;
	inclinationDeg: number;
	ascendingNodeDeg: number;
	argPeriapsisDeg: number;
	meanAnomalyDeg: number;
	axialTiltDeg: number;
	rotationHours: number;
	massKg: number | null;
	gravityMs2: number | null;
	temperatureK: number | null;
	atmosphere: string | null;
	hasRings: boolean;
	colorHex: string;
	texture: string;
	clouds?: string;
	night?: string;
	ringTexture?: string;
	roughness: number;
}

export interface ResolvedSystem {
	origin: SystemOrigin;
	planets: ResolvedBody[];
	liveCount: number;
}

const AU_KM = 149597870.7;

function positive(value: number | null | undefined, fallback: number): number {
	return typeof value === 'number' && Number.isFinite(value) && value > 0 ? value : fallback;
}

function finite(value: number | null | undefined, fallback: number): number {
	return typeof value === 'number' && Number.isFinite(value) ? value : fallback;
}

function fromCatalog(body: CatalogBody, origin: DataOrigin, id?: string): ResolvedBody {
	return {
		id: id || `reference-${body.name.toLowerCase()}`,
		name: body.name,
		subtype: body.subtype,
		origin,
		radiusKm: body.radiusKm,
		distanceAu: body.distanceAu,
		orbitalPeriodDays: body.orbitalPeriodDays,
		eccentricity: body.eccentricity,
		inclinationDeg: body.inclinationDeg,
		ascendingNodeDeg: body.ascendingNodeDeg,
		argPeriapsisDeg: body.argPeriapsisDeg,
		meanAnomalyDeg: body.meanAnomalyDeg,
		axialTiltDeg: body.axialTiltDeg,
		rotationHours: body.rotationHours,
		massKg: body.massKg,
		gravityMs2: body.gravityMs2,
		temperatureK: body.temperatureK,
		atmosphere: formatAtmosphere(body.atmosphere),
		hasRings: body.hasRings,
		colorHex: body.colorHex,
		texture: body.texture,
		clouds: body.clouds,
		night: body.night,
		ringTexture: body.ringTexture,
		roughness: body.roughness
	};
}

function distanceAu(planet: PlanetData, fallback: number): number {
	if (typeof planet.mean_distance_au === 'number' && planet.mean_distance_au > 0) {
		return planet.mean_distance_au;
	}
	if (typeof planet.semi_major_axis_km === 'number' && planet.semi_major_axis_km > 0) {
		return planet.semi_major_axis_km / AU_KM;
	}
	return fallback;
}

function mergeLive(planet: PlanetData, catalog: CatalogBody | undefined): ResolvedBody {
	const base = catalog
		? fromCatalog(catalog, 'live', String(planet.id))
		: {
				id: String(planet.id),
				name: planet.name,
				subtype: planet.subtype || planet.type || 'planet',
				origin: 'live' as const,
				radiusKm: positive(planet.radius_km, 1000),
				distanceAu: distanceAu(planet, 1),
				orbitalPeriodDays: positive(planet.orbital_period_days, 365),
				eccentricity: finite(planet.eccentricity, 0.016),
				inclinationDeg: finite(planet.inclination_degrees, 0),
				ascendingNodeDeg: finite(planet.longitude_ascending_node_degrees, 0),
				argPeriapsisDeg: finite(planet.argument_periapsis_degrees, 0),
				meanAnomalyDeg: finite(planet.mean_anomaly_degrees, 0),
				axialTiltDeg: finite(planet.axial_tilt_degrees, 0),
				rotationHours: finite(planet.rotation_period_hours, 24),
				massKg: planet.mass_kg ?? null,
				gravityMs2: planet.surface_gravity_ms2 ?? null,
				temperatureK: planet.surface_temperature_k ?? null,
				atmosphere: formatAtmosphere(planet.atmospheric_composition),
				hasRings: Boolean(planet.has_rings),
				colorHex: planet.color_hex || '#c8c2b4',
				texture: '/textures/mercury.jpg',
				roughness: 0.8
			};

	if (!catalog) return base;

	return {
		...base,
		subtype: planet.subtype || base.subtype,
		radiusKm: positive(planet.radius_km, base.radiusKm),
		distanceAu: distanceAu(planet, base.distanceAu),
		orbitalPeriodDays: positive(planet.orbital_period_days, base.orbitalPeriodDays),
		eccentricity: finite(planet.eccentricity, base.eccentricity),
		inclinationDeg: finite(planet.inclination_degrees, base.inclinationDeg),
		ascendingNodeDeg: finite(planet.longitude_ascending_node_degrees, base.ascendingNodeDeg),
		argPeriapsisDeg: finite(planet.argument_periapsis_degrees, base.argPeriapsisDeg),
		meanAnomalyDeg: finite(planet.mean_anomaly_degrees, base.meanAnomalyDeg),
		axialTiltDeg: finite(planet.axial_tilt_degrees, base.axialTiltDeg),
		rotationHours: finite(planet.rotation_period_hours, base.rotationHours),
		massKg: planet.mass_kg ?? base.massKg,
		gravityMs2: planet.surface_gravity_ms2 ?? base.gravityMs2,
		temperatureK: planet.surface_temperature_k ?? base.temperatureK,
		atmosphere: formatAtmosphere(planet.atmospheric_composition) ?? base.atmosphere,
		hasRings: Boolean(planet.has_rings) || base.hasRings,
		colorHex: planet.color_hex || base.colorHex
	};
}

function isPlanet(planet: PlanetData): boolean {
	const kind = (planet.type || 'planet').toLowerCase();
	return kind === 'planet' && Boolean(planet.name?.trim());
}

/**
 * Empty /planets is not a successful solar system. Fill the classical eight
 * from the reference catalog, and keep any live rows that did arrive.
 */
export function resolvePlanets(live: PlanetData[] | null | undefined): ResolvedSystem {
	const planets = (live ?? []).filter(isPlanet);
	if (planets.length === 0) {
		return {
			origin: 'reference',
			liveCount: 0,
			planets: CATALOG.map((body) => fromCatalog(body, 'reference'))
		};
	}

	const used = new Set<string>();
	const resolved: ResolvedBody[] = [];

	for (const name of CLASSICAL_PLANETS) {
		const match = planets.find((planet) => planet.name.trim().toLowerCase() === name.toLowerCase());
		if (match) {
			used.add(match.name.trim().toLowerCase());
			resolved.push(mergeLive(match, catalogByName(name)));
		} else {
			const catalog = catalogByName(name);
			if (catalog) resolved.push(fromCatalog(catalog, 'reference'));
		}
	}

	for (const planet of planets) {
		const key = planet.name.trim().toLowerCase();
		if (used.has(key)) continue;
		resolved.push(mergeLive(planet, catalogByName(planet.name)));
	}

	const liveCount = resolved.filter((body) => body.origin === 'live').length;
	const missingClassical = CLASSICAL_PLANETS.some(
		(name) => !planets.some((planet) => planet.name.trim().toLowerCase() === name.toLowerCase())
	);

	return {
		origin: missingClassical ? 'partial' : 'live',
		liveCount,
		planets: resolved
	};
}
