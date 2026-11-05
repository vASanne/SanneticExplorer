import { browser } from "$app/environment";
import {
  addMessages,
  init,
  locale as localeStore,
  waitLocale,
} from "svelte-i18n";
import de from "./de.json";
import en from "./en.json";

export const LOCALES = ["de", "en"] as const;
export type AppLocale = (typeof LOCALES)[number];
export const DEFAULT_LOCALE: AppLocale = "de";
const COOKIE = "sx-locale";

export function isLocale(value: string | null | undefined): value is AppLocale {
  return value === "de" || value === "en";
}

/** Cookie value wins. Anything else, including a missing cookie, is German. */
export function readLocaleCookie(cookie: string | null | undefined): AppLocale {
  const match = cookie?.match(/(?:^|;\s*)sx-locale=(de|en)(?:\s*;|$)/);
  return match?.[1] === "en" ? "en" : DEFAULT_LOCALE;
}

function initialLocale(): AppLocale {
  if (!browser) return DEFAULT_LOCALE;
  return readLocaleCookie(document.cookie);
}

addMessages("de", de);
addMessages("en", en);

init({
  fallbackLocale: DEFAULT_LOCALE,
  initialLocale: initialLocale(),
  handleMissingMessage: ({ id }) => id,
});

export function setAppLocale(next: AppLocale) {
  localeStore.set(next);
  if (!browser) return;
  document.cookie = `${COOKIE}=${next}; Path=/; Max-Age=31536000; SameSite=Lax`;
  document.documentElement.lang = next;
}

export async function prepareLocale(code: AppLocale = DEFAULT_LOCALE) {
  localeStore.set(code);
  await waitLocale(code);
}

export { localeStore as locale };
