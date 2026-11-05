import type { PlanetData, SystemStats } from '$lib/api';

export interface ShowcaseLoad {
	planets: PlanetData[];
	publicApiUrl: string;
	health: string | null;
	error: string | null;
}

export interface StatusLoad {
	planets: PlanetData[];
	publicApiUrl: string;
	internalApiUrl: string;
	health: string | null;
	stats: SystemStats | null;
	error: string | null;
}
