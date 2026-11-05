import { describe, expect, it } from "vitest";
import { locale } from "svelte-i18n";
import de from "./de.json";
import en from "./en.json";
import { t } from "./copy";

function leaves(value: unknown, prefix = ""): string[] {
  if (value == null || typeof value !== "object" || Array.isArray(value)) {
    return [prefix];
  }
  return Object.entries(value as Record<string, unknown>).flatMap(
    ([key, entry]) => {
      const path = prefix ? `${prefix}.${key}` : key;
      if (entry != null && typeof entry === "object" && !Array.isArray(entry)) {
        return leaves(entry, path);
      }
      return [path];
    }
  );
}

describe("message catalogs", () => {
  it("gives German and English the same ids", () => {
    expect(leaves(de).sort()).toEqual(leaves(en).sort());
  });

  it("falls back to German and can switch to English", () => {
    locale.set("de");
    expect(t("dock.showcase")).toBe("Schaustück");
    expect(t("bodies.Earth")).toBe("Erde");
    expect(t("status.live", { count: 1 })).toBe("Live · 1 Planet");
    expect(t("status.live", { count: 8 })).toBe("Live · 8 Planeten");
    locale.set("en");
    expect(t("dock.showcase")).toBe("Showcase");
    expect(t("bodies.Neptune")).toBe("Neptune");
    expect(t("status.live", { count: 8 })).toBe("Live · 8 planets");
    locale.set("de");
  });
});
