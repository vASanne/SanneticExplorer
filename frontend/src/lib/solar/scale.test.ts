import { describe, expect, it } from "vitest";
import { CATALOG, MOON } from "./catalog";
import {
  DEFAULT_SCALE_MODE,
  SUN_SCENE_RADIUS,
  TRUE_AU,
  auToScene,
  bloomFor,
  orbitalOmega,
  pickRadius,
  positionFromEccentricAnomaly,
  sceneRadius,
  solarCorona,
  sunSceneRadius,
  visualRadiusKm,
} from "./scale";

describe("orrery scale", () => {
  it("defaults to one physical scale", () => {
    expect(DEFAULT_SCALE_MODE).toBe("true");
    expect(auToScene(1)).toBe(TRUE_AU);
    expect(auToScene(30) / auToScene(0.387)).toBeCloseTo(30 / 0.387, 5);
  });

  it("keeps orbital distances in solar-system order", () => {
    const distances = CATALOG.map((body) =>
      auToScene(body.distanceAu, "showcase")
    );
    const sorted = [...distances].sort((a, b) => a - b);
    expect(distances).toEqual(sorted);
    expect(distances[distances.length - 1] / distances[0]).toBeGreaterThan(15);
  });

  it("keeps Mercury outside the Sun at perihelion", () => {
    const mercury = CATALOG[0];
    const perihelion = sceneRadius(
      positionFromEccentricAnomaly(mercury, 0, "showcase")
    );
    const aphelion = sceneRadius(
      positionFromEccentricAnomaly(mercury, Math.PI, "showcase")
    );
    expect(perihelion).toBeGreaterThan(SUN_SCENE_RADIUS + 1);
    expect(perihelion).toBeLessThan(aphelion);
  });

  it("uses true distance and size ratios in true scale", () => {
    const mercury = auToScene(0.387, "true");
    const neptune = auToScene(30.069, "true");
    expect(neptune / mercury).toBeCloseTo(30.069 / 0.387, 4);
    const earthRadius = visualRadiusKm(6371, "true");
    expect(sunSceneRadius("true") / earthRadius).toBeCloseTo(696340 / 6371, 3);
    expect(
      auToScene(30, "showcase") / auToScene(0.387, "showcase")
    ).toBeLessThan(40);
  });

  it("keeps showcase enlargement out of true-scale radii", () => {
    const sun = sunSceneRadius("true");
    for (const body of CATALOG) {
      const visual = visualRadiusKm(body.radiusKm, "true");
      expect(visual / sun).toBeCloseTo(body.radiusKm / 696340, 5);
      expect(visualRadiusKm(body.radiusKm, "showcase")).toBeGreaterThan(
        visual * 20
      );
    }
    const moon = visualRadiusKm(MOON.radiusKm, "true");
    expect(moon / visualRadiusKm(6371, "true")).toBeCloseTo(1737.4 / 6371, 5);
    const dust = visualRadiusKm(40, "true");
    expect(dust / visualRadiusKm(6371, "true")).toBeCloseTo(40 / 6371, 5);
    expect(pickRadius(dust, "true")).toBeGreaterThan(dust);
    expect(pickRadius(sun, "true")).toBeCloseTo(sun, 8);
    expect(pickRadius(visualRadiusKm(6371, "showcase"), "showcase")).toBe(
      visualRadiusKm(6371, "showcase")
    );
    expect(solarCorona("true").glow).toBeLessThan(1.5);
    expect(solarCorona("true").halo).toBeLessThan(1.6);
    expect(solarCorona("showcase").glow).toBeGreaterThan(4);
    expect(bloomFor("true").strength).toBeLessThan(
      bloomFor("showcase").strength
    );
  });

  it("moves inner planets faster than outer planets", () => {
    const mercury = orbitalOmega(88);
    const earth = orbitalOmega(365.25);
    const neptune = orbitalOmega(60190);
    expect(mercury).toBeGreaterThan(earth);
    expect(earth).toBeGreaterThan(neptune);
  });
});
