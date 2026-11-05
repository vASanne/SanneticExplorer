import { locale, readLocaleCookie } from "$lib/i18n";
import type { Handle } from "@sveltejs/kit";

export const handle: Handle = async ({ event, resolve }) => {
  const code = readLocaleCookie(event.request.headers.get("cookie"));
  locale.set(code);
  return resolve(event, {
    transformPageChunk: ({ html }) => html.replace("%lang%", code),
  });
};
