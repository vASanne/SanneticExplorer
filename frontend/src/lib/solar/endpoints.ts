/** Browser calls use the published host port. Never the Docker DNS name. */
export function getBrowserApiBase(publicUrl?: string | null): string {
	const trimmed = (publicUrl ?? '').trim().replace(/\/$/, '');
	return trimmed || 'http://localhost:13800';
}

/**
 * Server-side fetches run inside the frontend container, where `localhost:13800`
 * is not the API. Prefer the Compose DNS name (`http://backend:8000`).
 */
export function getServerApiBase(internal?: string | null, publicUrl?: string | null): string {
	const internalUrl = (internal ?? '').trim().replace(/\/$/, '');
	if (internalUrl) return internalUrl;
	return getBrowserApiBase(publicUrl);
}
