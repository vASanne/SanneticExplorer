import { env as privateEnv } from '$env/dynamic/private';
import { env as publicEnv } from '$env/dynamic/public';
import { getHealth, getPlanets, getStats } from '$lib/api';
import { getServerApiBase } from '$lib/solar/endpoints';
import type { ShowcaseLoad, StatusLoad } from '$lib/solar/loads';

export type { ShowcaseLoad, StatusLoad };

function urls() {
	const publicApiUrl = (publicEnv.PUBLIC_API_URL || 'http://localhost:13800').replace(/\/$/, '');
	const internalApiUrl = getServerApiBase(privateEnv.INTERNAL_API_URL, publicApiUrl);
	return { publicApiUrl, internalApiUrl };
}

export async function loadShowcase(): Promise<ShowcaseLoad> {
	const { publicApiUrl, internalApiUrl } = urls();
	try {
		const [planets, health] = await Promise.all([getPlanets(internalApiUrl), getHealth(internalApiUrl)]);
		return { planets, publicApiUrl, health: health.status ?? null, error: null };
	} catch (error) {
		return {
			planets: [],
			publicApiUrl,
			health: null,
			error: error instanceof Error ? error.message : 'API unavailable'
		};
	}
}

export async function loadStatus(): Promise<StatusLoad> {
	const { publicApiUrl, internalApiUrl } = urls();
	const [healthResult, statsResult, planetsResult] = await Promise.allSettled([
		getHealth(internalApiUrl),
		getStats(internalApiUrl),
		getPlanets(internalApiUrl)
	]);
	const errors = [healthResult, statsResult, planetsResult]
		.filter((result): result is PromiseRejectedResult => result.status === 'rejected')
		.map((result) => (result.reason instanceof Error ? result.reason.message : 'Request failed'));
	return {
		publicApiUrl,
		internalApiUrl,
		health: healthResult.status === 'fulfilled' ? healthResult.value.status : null,
		stats: statsResult.status === 'fulfilled' ? statsResult.value : null,
		planets: planetsResult.status === 'fulfilled' ? planetsResult.value : [],
		error: errors.length ? errors.join(' ') : null
	};
}
