import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
	// PUBLIC_* is the project convention for browser-facing settings (see PUBLIC_API_URL).
	envPrefix: ['VITE_', 'PUBLIC_'],
	plugins: [sveltekit()],
	resolve: {
		alias: {
			$lib: path.resolve('./src/lib')
		}
	}
}); 