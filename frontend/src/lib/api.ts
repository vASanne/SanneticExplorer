// API configuration and functions for Sannetic Explorer frontend

// Base URL from environment variable  
// For browser requests, use localhost since the browser runs on the host
const API_BASE_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:3000';

// CelestialBody interface mirroring backend DTO
export interface CelestialBody {
	id: number;
	name: string;
	body_type: string;
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
	last_updated: string;
	created_at: string;
	
	// Orbital parameters
	orbital_parameters?: {
		semi_major_axis_au: number;
		eccentricity: number;
		inclination_degrees: number;
		longitude_of_ascending_node_degrees: number;
		argument_of_periapsis_degrees: number;
		mean_anomaly_degrees: number;
		epoch_jd: number;
	};
	
	// Physical characteristics
	physical_characteristics?: {
		mean_density_gcm3: number;
		surface_area_km2: number;
		volume_km3: number;
		flattening: number;
		equatorial_radius_km: number;
		polar_radius_km: number;
	};
	
	// Stellar characteristics (for stars)
	stellar_characteristics?: {
		spectral_type: string;
		luminosity_solar: number;
		absolute_magnitude: number;
		apparent_magnitude: number;
		surface_temperature_k: number;
		age_billion_years: number;
		metallicity: number;
	};
}

// API response wrapper
interface ApiResponse<T> {
	data: T;
	message?: string;
	status: string;
}

/**
 * Fetch all celestial bodies from the FastAPI backend
 * @returns Promise<CelestialBody[]> Array of celestial bodies
 */
export async function getBodies(): Promise<CelestialBody[]> {
	try {
		const response = await fetch(`${API_BASE_URL}/bodies`);
		
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		
		const result: ApiResponse<CelestialBody[]> = await response.json();
		return result.data || result;
	} catch (error) {
		console.error('Error fetching celestial bodies:', error);
		throw new Error(`Failed to fetch celestial bodies: ${error instanceof Error ? error.message : 'Unknown error'}`);
	}
}

/**
 * Fetch a single celestial body by ID
 * @param id The celestial body ID
 * @returns Promise<CelestialBody> The celestial body
 */
export async function getBody(id: number): Promise<CelestialBody> {
	try {
		const response = await fetch(`${API_BASE_URL}/bodies/${id}`);
		
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		
		const result: ApiResponse<CelestialBody> = await response.json();
		return result.data || result;
	} catch (error) {
		console.error(`Error fetching celestial body ${id}:`, error);
		throw new Error(`Failed to fetch celestial body: ${error instanceof Error ? error.message : 'Unknown error'}`);
	}
}

/**
 * Fetch celestial bodies by type
 * @param bodyType The type of celestial body (planet, moon, star, etc.)
 * @returns Promise<CelestialBody[]> Array of celestial bodies of the specified type
 */
export async function getBodiesByType(bodyType: string): Promise<CelestialBody[]> {
	try {
		const response = await fetch(`${API_BASE_URL}/bodies?body_type=${encodeURIComponent(bodyType)}`);
		
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		
		const result: ApiResponse<CelestialBody[]> = await response.json();
		return result.data || result;
	} catch (error) {
		console.error(`Error fetching ${bodyType} bodies:`, error);
		throw new Error(`Failed to fetch ${bodyType} bodies: ${error instanceof Error ? error.message : 'Unknown error'}`);
	}
}

// Planet-specific interface for the 3D scene
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
	
	// Orbital parameters
	orbital_period_days?: number;
	semi_major_axis_km?: number;
	eccentricity?: number;
	inclination_degrees?: number;
	
	// Physical characteristics
	has_atmosphere?: boolean;
	atmospheric_composition?: Record<string, any>;
	has_rings?: boolean;
	surface_temperature_k?: number;
	surface_temperature_min_k?: number;
	surface_temperature_max_k?: number;
	atmospheric_pressure_pa?: number;
	
	// Additional data
	moons?: number;
}

// Build info interface
export interface BuildInfo {
	build_time: string;
	component: string;
	build_timestamp: string;
}

/**
 * Fetch all planets with their orbital and physical characteristics
 * @returns Promise<PlanetData[]> Array of planets
 */
export async function getPlanets(): Promise<PlanetData[]> {
	try {
		const response = await fetch(`${API_BASE_URL}/planets`);
		
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		
		const planets: PlanetData[] = await response.json();
		return planets;
	} catch (error) {
		console.error('Error fetching planets:', error);
		throw new Error(`Failed to fetch planets: ${error instanceof Error ? error.message : 'Unknown error'}`);
	}
}

/**
 * Fetch build information from database
 * @param component Component to get build info for (default: frontend)
 * @returns Promise<BuildInfo> Build information
 */
export async function getBuildInfo(component: string = 'frontend'): Promise<BuildInfo> {
	try {
		const response = await fetch(`${API_BASE_URL}/build-info?component=${encodeURIComponent(component)}`);
		
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		
		const buildInfo: BuildInfo = await response.json();
		return buildInfo;
	} catch (error) {
		console.error('Error fetching build info:', error);
		throw new Error(`Failed to fetch build info: ${error instanceof Error ? error.message : 'Unknown error'}`);
	}
}

/**
 * Fetch build information for all components
 * @returns Promise<Record<string, BuildInfo>> Build information for all components
 */
export async function getAllBuildInfo(): Promise<Record<string, BuildInfo>> {
	try {
		const components = ['frontend', 'backend', 'worker'];
		const buildInfos: Record<string, BuildInfo> = {};
		
		await Promise.all(
			components.map(async (component) => {
				try {
					buildInfos[component] = await getBuildInfo(component);
				} catch (error) {
					console.warn(`Failed to fetch build info for ${component}:`, error);
					// Create fallback entry
					buildInfos[component] = {
						build_time: 'N/A',
						component,
						build_timestamp: new Date().toISOString()
					};
				}
			})
		);
		
		return buildInfos;
	} catch (error) {
		console.error('Error fetching all build info:', error);
		throw new Error(`Failed to fetch all build info: ${error instanceof Error ? error.message : 'Unknown error'}`);
	}
} 