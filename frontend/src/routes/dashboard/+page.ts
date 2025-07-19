import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
  // The dashboard loads data client-side, so we don't need to preload anything
  return {};
}; 