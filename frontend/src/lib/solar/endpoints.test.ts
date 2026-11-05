import { describe, expect, it } from 'vitest';
import { TEXTURE_FILES } from './catalog';
import { getBrowserApiBase, getServerApiBase } from './endpoints';

describe('API base URLs', () => {
	it('sends the browser to the published host port', () => {
		expect(getBrowserApiBase(undefined)).toBe('http://localhost:13800');
		expect(getBrowserApiBase('')).toBe('http://localhost:13800');
		expect(getBrowserApiBase('http://localhost:13810/')).toBe('http://localhost:13810');
		expect(getBrowserApiBase('http://localhost:13800')).not.toContain('backend');
	});

	it('prefers the Compose DNS name for server loads', () => {
		expect(getServerApiBase('http://backend:8000/', 'http://localhost:13800')).toBe('http://backend:8000');
		expect(getServerApiBase('  ', 'http://localhost:13800/')).toBe('http://localhost:13800');
		expect(getServerApiBase(null, null)).toBe('http://localhost:13800');
	});
});

describe('texture files', () => {
	it('lists a map for every classical body plus the starfield', () => {
		expect(TEXTURE_FILES).toEqual(
			expect.arrayContaining([
				'sun.jpg',
				'earth_day.jpg',
				'earth_clouds.jpg',
				'earth_night.jpg',
				'saturn_ring.png',
				'stars.jpg'
			])
		);
		expect(new Set(TEXTURE_FILES).size).toBe(TEXTURE_FILES.length);
	});
});
