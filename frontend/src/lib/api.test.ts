import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('$env/dynamic/public', () => ({
	env: { PUBLIC_API_URL: 'http://localhost:13800' }
}));

import { browserApiBase, getPlanets } from './api';

describe('browser API base', () => {
	it('uses the public URL from the environment', () => {
		expect(browserApiBase()).toBe('http://localhost:13800');
	});
});

describe('getPlanets', () => {
	beforeEach(() => {
		vi.stubGlobal(
			'fetch',
			vi.fn(async () => ({
				ok: true,
				json: async () => [{ id: '1', name: 'Earth', type: 'planet', data_quality: 'good' }]
			}))
		);
	});

	it('reads a bare list from the given base URL', async () => {
		const planets = await getPlanets('http://backend:8000');
		expect(planets).toHaveLength(1);
		expect(fetch).toHaveBeenCalledWith('http://backend:8000/planets', expect.any(Object));
	});

	it('accepts a wrapped data list and rejects anything else', async () => {
		vi.stubGlobal(
			'fetch',
			vi.fn(async () => ({
				ok: true,
				json: async () => ({ data: [] })
			}))
		);
		await expect(getPlanets('http://localhost:13800')).resolves.toEqual([]);

		vi.stubGlobal(
			'fetch',
			vi.fn(async () => ({
				ok: false,
				status: 500,
				json: async () => ({})
			}))
		);
		await expect(getPlanets('http://localhost:13800')).rejects.toThrow(/HTTP 500/);
	});
});
