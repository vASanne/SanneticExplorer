import { get } from "svelte/store";
import { format, locale, unwrapFunctionStore } from "svelte-i18n";

const translate = unwrapFunctionStore(format);

export function t(
  id: string,
  values?: Record<string, string | number | boolean>
): string {
  const result = values ? translate(id, { values }) : translate(id);
  return typeof result === "string" ? result : id;
}

/** Translated message, or `fallback` when the catalog has no such id. */
export function tOr(id: string, fallback: string): string {
  const value = t(id);
  return !value || value === id ? fallback : value;
}

export function bodyName(name: string): string {
  return tOr(`bodies.${name}`, name);
}

export function subtypeName(name: string): string {
  return tOr(`subtypes.${name}`, name);
}

export function intlLocale(): string {
  return get(locale) === "en" ? "en-US" : "de-DE";
}
