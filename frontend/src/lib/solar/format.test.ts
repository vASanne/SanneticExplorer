import { describe, expect, it } from "vitest";
import { locale } from "svelte-i18n";
import {
  earthYearCaption,
  formatAtmosphere,
  formatMass,
  formatTemperature,
} from "./format";

describe("formatters", () => {
  it("formats atmosphere objects and empty values", () => {
    expect(formatAtmosphere({ N2: "78%", O2: "21%" })).toBe("N2 78% · O2 21%");
    locale.set("de");
    expect(
      formatAtmosphere({ nitrogen: "78%", other: "trace amounts" })
    ).toBe("Stickstoff 78% · Sonstiges Spuren");
    locale.set("en");
    expect(formatAtmosphere({ carbonDioxide: "0.04%" })).toBe(
      "carbon dioxide 0.04%"
    );
    locale.set("de");
    expect(formatAtmosphere(null)).toBeNull();
    expect(formatAtmosphere("CO2")).toBe("CO2");
  });

  it("formats mass against Earth and temperature in both scales", () => {
    locale.set("de");
    expect(formatMass(5.972e24)).toContain("1,000 Erdmassen");
    expect(formatTemperature(288)).toBe("288 K · 15 °C");
    expect(formatMass(null)).toBe("—");
    locale.set("en");
    expect(formatMass(5.972e24)).toContain("1.000 Earth masses");
    locale.set("de");
  });

  it("describes the playback time scale", () => {
    locale.set("de");
    expect(earthYearCaption(10, 48)).toBe("Erdjahr ≈ 4,8 s");
    expect(earthYearCaption(1000, 48)).toBe("Erdjahr ≈ 0,05 s");
    expect(earthYearCaption(-10, 48)).toBe("Erdjahr ≈ 4,8 s · rückwärts");
    locale.set("en");
    expect(earthYearCaption(10, 48)).toBe("Earth year ≈ 4.8 s");
    expect(earthYearCaption(-10, 48)).toBe("Earth year ≈ 4.8 s · reverse");
    locale.set("de");
  });
});
