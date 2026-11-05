import { describe, expect, it } from "vitest";
import { CATALOG } from "./catalog";
import {
  SUN_SCENE_RADIUS,
  auToScene,
  orbitalOmega,
  positionFromEccentricAnomaly,
  sceneRadius,
  sunSceneRadius,
  visualRadiusKm,
} from "./scale";

describe("orrery scale", () => {
  it("keeps orbital distances in solar-system order", () => {
    const distances = CATALOG.map((body) => auToScene(body.distanceAu));
    const sorted = [...distances].sort((a, b) => a - b);
    expect(distances).toEqual(sorted);
    expect(distances[distances.length - 1] / distances[0]).toBeGreaterThan(15);
  });

  it("keeps Mercury outside the Sun at perihelion", () => {
    const mercury = CATALOG[0];
    const perihelion = sceneRadius(positionFromEccentricAnomaly(mercury, 0));
    const aphelion = sceneRadius(
      positionFromEccentricAnomaly(mercury, Math.PI)
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

  it("moves inner planets faster than outer planets", () => {
    const mercury = orbitalOmega(88);
    const earth = orbitalOmega(365.25);
    const neptune = orbitalOmega(60190);
    expect(mercury).toBeGreaterThan(earth);
    expect(earth).toBeGreaterThan(neptune);
  });
});
