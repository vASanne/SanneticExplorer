import { describe, expect, it } from "vitest";
import type { PlanetData } from "$lib/api";
import { resolvePlanets } from "./resolve";

function planet(
  partial: Partial<PlanetData> & Pick<PlanetData, "name">
): PlanetData {
  return {
    id: partial.id ?? partial.name,
    type: "planet",
    data_quality: "good",
    ...partial,
  };
}

describe("resolvePlanets", () => {
  it("treats an empty payload as the reference catalog, not a Sun-only success", () => {
    const resolved = resolvePlanets([]);
    expect(resolved.origin).toBe("reference");
    expect(resolved.planets.map((body) => body.name)).toEqual([
      "Mercury",
      "Venus",
      "Earth",
      "Mars",
      "Jupiter",
      "Saturn",
      "Uranus",
      "Neptune",
    ]);
    expect(resolved.planets.every((body) => body.origin === "reference")).toBe(
      true
    );
  });

  it("uses live radii and fills missing classical planets", () => {
    const resolved = resolvePlanets([
      planet({
        name: "Earth",
        radius_km: 100,
        mean_distance_au: 1.01,
        eccentricity: 0.02,
      }),
    ]);
    expect(resolved.origin).toBe("partial");
    const earth = resolved.planets.find((body) => body.name === "Earth");
    const mercury = resolved.planets.find((body) => body.name === "Mercury");
    expect(earth?.origin).toBe("live");
    expect(earth?.radiusKm).toBe(100);
    expect(earth?.distanceAu).toBe(1.01);
    expect(earth?.eccentricity).toBe(0.02);
    expect(mercury?.origin).toBe("reference");
    expect(resolved.planets).toHaveLength(8);
  });

  it("marks a full classical set as live and derives AU from kilometres", () => {
    const resolved = resolvePlanets(
      [
        "Mercury",
        "Venus",
        "Earth",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
      ].map((name) =>
        planet({
          name,
          semi_major_axis_km: name === "Earth" ? 149597870.7 : undefined,
          mean_distance_au: name === "Earth" ? undefined : 1,
        })
      )
    );
    expect(resolved.origin).toBe("live");
    expect(
      resolved.planets.find((body) => body.name === "Earth")?.distanceAu
    ).toBeCloseTo(1, 5);
    expect(
      resolved.planets.find((body) => body.name === "Mercury")?.eccentricity
    ).toBeCloseTo(0.2056, 4);
  });

  it("keeps live J2000 elements and leaves missing angles for the reference table", () => {
    const resolved = resolvePlanets([
      planet({
        name: "Earth",
        semi_major_axis_km: 149597870.7,
        eccentricity: 0.0167,
        inclination_degrees: 0,
        longitude_ascending_node_degrees: -11.26064,
        argument_periapsis_degrees: 114.20783,
        mean_anomaly_degrees: 357.51716,
      }),
      planet({ name: "Mercury", mean_distance_au: 0.387 }),
    ]);
    const earth = resolved.planets.find((body) => body.name === "Earth");
    const mercury = resolved.planets.find((body) => body.name === "Mercury");
    expect(earth?.epoch.semiMajorAu).toBeCloseTo(1, 5);
    expect(earth?.epoch.inclinationDeg).toBe(0);
    expect(earth?.epoch.meanAnomalyDeg).toBeCloseTo(357.51716, 4);
    expect(mercury?.origin).toBe("live");
    expect(mercury?.epoch.semiMajorAu).toBeCloseTo(0.387, 3);
    expect(mercury?.epoch.eccentricity).toBeNull();
    expect(mercury?.epoch.ascendingNodeDeg).toBeNull();
    expect(
      resolved.planets.find((body) => body.name === "Mars")?.epoch
        .argPeriapsisDeg
    ).toBeNull();
  });
});
