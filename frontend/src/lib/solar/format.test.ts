import { describe, expect, it } from "vitest";
import {
  earthYearCaption,
  formatAtmosphere,
  formatMass,
  formatTemperature,
} from "./format";

describe("formatters", () => {
  it("formats atmosphere objects and empty values", () => {
    expect(formatAtmosphere({ N2: "78%", O2: "21%" })).toBe("N2 78% · O2 21%");
    expect(formatAtmosphere(null)).toBeNull();
    expect(formatAtmosphere("CO2")).toBe("CO2");
  });

  it("formats mass against Earth and temperature in both scales", () => {
    expect(formatMass(5.972e24)).toContain("1.000 Earth masses");
    expect(formatTemperature(288)).toBe("288 K · 15 °C");
    expect(formatMass(null)).toBe("—");
  });

  it("describes the playback time scale", () => {
    expect(earthYearCaption(10, 48)).toBe("Earth year ≈ 4.8 s");
    expect(earthYearCaption(1000, 48)).toBe("Earth year ≈ 0.05 s");
    expect(earthYearCaption(-10, 48)).toBe("Earth year ≈ 4.8 s · reverse");
  });
});
