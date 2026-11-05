import { waitLocale } from "svelte-i18n";
import "$lib/i18n";
import type { LayoutLoad } from "./$types";

export const load: LayoutLoad = async () => {
  await waitLocale();
};
