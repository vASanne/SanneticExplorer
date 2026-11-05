import { loadShowcase } from '$lib/server/showcase';
import type { PageServerLoad } from './$types';

export const prerender = false;

export const load: PageServerLoad = async () => loadShowcase();
