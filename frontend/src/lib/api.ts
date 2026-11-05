// API client for the Sannetic Explorer showcase.
// The browser uses the published host port. SvelteKit loads inside the
// frontend container use INTERNAL_API_URL (http://backend:8000).

import { browser } from '$app/environment';
import { getBrowserApiBase } from '$lib/solar/endpoints';

/** Browser-only base. Never returns the Compose DNS name. */
export function browserApiBase(): string {
	const pub = import.meta.env.PUBLIC_API_URL || import.meta.env.VITE_API_URL;
	return getBrowserApiBase(typeof pub === 'string' ? pub : undefined);
}

/**
 * Browser calls the published host port (PUBLIC_API_URL).
 * SvelteKit load functions run inside the frontend container, where localhost
 * is the container itself. Those requests use INTERNAL_API_URL (http://backend:8000).
 */
export function getApiBaseUrl(): string {
	if (browser) return browserApiBase();
	const env = (globalThis as { process?: { env?: Record<string, string | undefined> } }).process?.env;
	const internal = env?.INTERNAL_API_URL;
	if (internal) return internal.replace(/\/$/, '');
	return 'http://localhost:8000';
}

export interface CelestialBody {
	id: number | string;
	name: string;
	body_type?: string;
	type?: string;
	mass_kg?: number;
	radius_km?: number;
	mean_distance_au?: number;
	orbital_period_days?: number;
	rotation_period_hours?: number;
	axial_tilt_degrees?: number;
	surface_gravity_ms2?: number;
	escape_velocity_kms?: number;
	albedo?: number;
	surface_temperature_k?: number;
	atmospheric_composition?: string;
	discovery_date?: string;
	discoverer?: string;
	mission_count?: number;
	last_updated?: string;
	created_at?: string;
}

export interface PlanetData {
	id: string;
	name: string;
	type: string;
	subtype?: string;
	mass_kg?: number;
	radius_km?: number;
	mean_distance_au?: number;
	orbital_speed_kms?: number;
	surface_gravity_ms2?: number;
	color_hex?: string;
	data_quality: string;

	orbital_period_days?: number;
	semi_major_axis_km?: number;
	eccentricity?: number;
	inclination_degrees?: number;
	longitude_ascending_node_degrees?: number;
	argument_periapsis_degrees?: number;
	mean_anomaly_degrees?: number;
	axial_tilt_degrees?: number;
	rotation_period_hours?: number;

	has_atmosphere?: boolean;
	atmospheric_composition?: Record<string, unknown> | string | null;
	has_rings?: boolean;
	surface_temperature_k?: number;
}

export interface BuildInfo {
	build_time: string;
	component: string;
	build_timestamp: string;
}

export interface HealthStatus {
	status: string;
	timestamp?: string;
}

export interface SystemStats {
	total_celestial_bodies: number;
	by_type: Record<string, number>;
	by_data_quality?: Record<string, number>;
	database_size?: string;
}

function unwrapList<T>(payload: unknown): T[] {
	if (Array.isArray(payload)) return payload as T[];
	if (payload && typeof payload === 'object' && Array.isArray((payload as { data?: unknown }).data)) {
		return (payload as { data: T[] }).data;
	}
	throw new Error('Unexpected list payload');
}

async function getJson<T>(url: string): Promise<T> {
	const response = await fetch(url, { signal: AbortSignal.timeout(8000) });
	if (!response.ok) {
		throw new Error(`HTTP ${response.status} for ${url}`);
	}
	return (await response.json()) as T;
}

export async function getPlanets(base = getApiBaseUrl()): Promise<PlanetData[]> {
	const payload = await getJson<unknown>(`${base}/planets`);
	return unwrapList<PlanetData>(payload);
}

export async function getHealth(base = getApiBaseUrl()): Promise<HealthStatus> {
	return getJson<HealthStatus>(`${base}/health`);
}

export async function getStats(base = getApiBaseUrl()): Promise<SystemStats> {
	return getJson<SystemStats>(`${base}/stats`);
}

/** Canonical list route. `/bodies` remains as a backend alias. */
export async function getBodies(base = getApiBaseUrl()): Promise<CelestialBody[]> {
	const payload = await getJson<unknown>(`${base}/celestial-bodies`);
	const list = unwrapList<CelestialBody>(payload);
	return list.map((body) => ({
		...body,
		body_type: body.body_type || body.type || 'unknown'
	}));
}

export async function getBody(id: number | string, base = getApiBaseUrl()): Promise<CelestialBody> {
	const payload = await getJson<CelestialBody | { data: CelestialBody }>(`${base}/celestial-bodies/${id}`);
	if (payload && typeof payload === 'object' && 'data' in payload && payload.data) return payload.data;
	return payload as CelestialBody;
}

export async function getBodiesByType(bodyType: string, base = getApiBaseUrl()): Promise<CelestialBody[]> {
	const payload = await getJson<unknown>(
		`${base}/celestial-bodies?type=${encodeURIComponent(bodyType)}`
	);
	const list = unwrapList<CelestialBody>(payload);
	return list.map((body) => ({
		...body,
		body_type: body.body_type || body.type || 'unknown'
	}));
}

export async function getBuildInfo(component = 'frontend', base = getApiBaseUrl()): Promise<BuildInfo> {
	return getJson<BuildInfo>(`${base}/build-info?component=${encodeURIComponent(component)}`);
}

export async function getAllBuildInfo(base = getApiBaseUrl()): Promise<Record<string, BuildInfo>> {
	const components = ['frontend', 'backend', 'worker'];
	const buildInfos: Record<string, BuildInfo> = {};
	await Promise.all(
		components.map(async (component) => {
			try {
				buildInfos[component] = await getBuildInfo(component, base);
			} catch (error) {
				console.warn(`Failed to fetch build info for ${component}:`, error);
				buildInfos[component] = {
					build_time: 'N/A',
					component,
					build_timestamp: new Date().toISOString()
				};
			}
		})
	);
	return buildInfos;
}
