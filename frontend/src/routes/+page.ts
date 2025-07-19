import type { PageLoad } from './$types';
import { getBodies, type CelestialBody } from '$lib/api';

export const load: PageLoad = async () => {
	try {
		const bodies: CelestialBody[] = await getBodies();
		return {
			bodies
		};
	} catch (error) {
		console.error('Failed to load celestial bodies:', error);
		return {
			bodies: [],
			error: error instanceof Error ? error.message : 'Failed to load data'
		};
	}
}; 