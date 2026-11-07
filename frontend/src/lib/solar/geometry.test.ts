import { describe, expect, it } from "vitest";
import { CATALOG, MOON } from "./catalog";
import {
  AU_IN_KM,
  distanceAu,
  keplerState,
  moonGeocentricAu,
  planetPositionAu,
  type AuPoint,
} from "./kepler";
import {
  TRUE_AU,
  eclipticToScene,
  linearAuScale,
  moonSceneOffset,
  moonShownInScene,
  sceneRadius,
  sunSceneRadius,
  visualRadiusKm,
  type ScenePoint,
} from "./scale";

const MOON_ELEMENTS = {
  semiMajorKm: MOON.distanceKm,
  eccentricity: MOON.eccentricity,
  inclinationDeg: MOON.inclinationDeg,
  periodDays: MOON.periodDays,
};

const VENUS_RADIUS_KM =
  CATALOG.find((body) => body.name === "Venus")?.radiusKm ?? 0;
const EARTH_RADIUS_KM = 6371;

function add(a: ScenePoint, b: ScenePoint): ScenePoint {
  return { x: a.x + b.x, y: a.y + b.y, z: a.z + b.z };
}

function apart(a: AuPoint, b: AuPoint): number {
  return Math.hypot(a.x - b.x, a.y - b.y, a.z - b.z);
}

function sceneApart(a: ScenePoint, b: ScenePoint): number {
  return Math.hypot(a.x - b.x, a.y - b.y, a.z - b.z);
}

/** Dates spanning the 2025-03-26 showcase collision and several years around it. */
function sampleDays(): number[] {
  const days = [2451545, 2460760.5, 2461349.5, 2461350.5];
  for (let jd = 2459215.5; jd <= 2462515.5; jd += 17) days.push(jd);
  return days;
}

describe("shared scene geometry", () => {
  it("keeps Sun, planets and the Moon in one kilometre scale", () => {
    const kmPerUnit = AU_IN_KM / TRUE_AU;
    expect(sunSceneRadius("true") * kmPerUnit).toBeCloseTo(696340, 0);
    expect(visualRadiusKm(EARTH_RADIUS_KM, "true") * kmPerUnit).toBeCloseTo(
      EARTH_RADIUS_KM,
      2
    );
    expect(visualRadiusKm(VENUS_RADIUS_KM, "true") * kmPerUnit).toBeCloseTo(
      VENUS_RADIUS_KM,
      2
    );
    expect(visualRadiusKm(MOON.radiusKm, "true") * kmPerUnit).toBeCloseTo(
      MOON.radiusKm,
      2
    );
    expect(auLength(1)).toBeCloseTo(AU_IN_KM, 0);
  });

  it("anchors the Moon to Earth in the same units as Earth's orbit", () => {
    for (const jd of [2451545, 2460760.5, 2461349.5]) {
      const earth = planetPositionAu("Earth", jd, null);
      const moon = moonGeocentricAu(jd, MOON_ELEMENTS);
      const axis = keplerState("Earth", jd, null).semiMajorAu;
      const earthScene = eclipticToScene(earth, axis, "true");
      const offset = moonSceneOffset(moon, "true", axis);
      expect(offset.x / TRUE_AU).toBeCloseTo(moon.x, 8);
      expect(offset.y / TRUE_AU).toBeCloseTo(moon.z, 8);
      expect(offset.z / TRUE_AU).toBeCloseTo(-moon.y, 8);
      const kilometres = sceneRadius(offset) * (AU_IN_KM / TRUE_AU);
      expect(kilometres).toBeGreaterThan(330000);
      expect(kilometres).toBeLessThan(460000);
      expect(kilometres).toBeCloseTo(distanceAu(moon) * AU_IN_KM, 3);
      const heliocentric = {
        x: earth.x + moon.x,
        y: earth.y + moon.y,
        z: earth.z + moon.z,
      };
      const rebuilt = add(earthScene, offset);
      expect(rebuilt.x / TRUE_AU).toBeCloseTo(heliocentric.x, 8);
      expect(rebuilt.y / TRUE_AU).toBeCloseTo(heliocentric.z, 8);
      expect(rebuilt.z / TRUE_AU).toBeCloseTo(-heliocentric.y, 8);
      expect(sceneApart(rebuilt, earthScene)).toBeGreaterThan(
        visualRadiusKm(EARTH_RADIUS_KM, "true") +
          visualRadiusKm(MOON.radiusKm, "true")
      );
    }
  });

  it("does not let the Moon or its orbit intersect Venus", () => {
    expect(moonShownInScene("true")).toBe(true);
    expect(moonShownInScene("showcase")).toBe(false);
    let closestKm = Infinity;
    for (const jd of sampleDays()) {
      const earthState = keplerState("Earth", jd, null);
      const venusState = keplerState("Venus", jd, null);
      const earthAu = planetPositionAu("Earth", jd, null);
      const venusAu = planetPositionAu("Venus", jd, null);
      for (let step = 0; step < 12; step += 1) {
        const moonAu = moonGeocentricAu(
          jd + (step / 12) * MOON.periodDays,
          MOON_ELEMENTS
        );
        const world = {
          x: earthAu.x + moonAu.x,
          y: earthAu.y + moonAu.y,
          z: earthAu.z + moonAu.z,
        };
        const kilometres =
          apart(world, venusAu) * AU_IN_KM - VENUS_RADIUS_KM - MOON.radiusKm;
        closestKm = Math.min(closestKm, kilometres);
        expect(kilometres).toBeGreaterThan(20_000_000);

        for (const mode of ["true", "showcase"] as const) {
          const earthScene = eclipticToScene(
            earthAu,
            earthState.semiMajorAu,
            mode
          );
          const venusScene = eclipticToScene(
            venusAu,
            venusState.semiMajorAu,
            mode
          );
          const moonScene = add(
            earthScene,
            moonSceneOffset(moonAu, mode, earthState.semiMajorAu)
          );
          const gap =
            sceneApart(moonScene, venusScene) -
            visualRadiusKm(VENUS_RADIUS_KM, mode) -
            visualRadiusKm(MOON.radiusKm, mode);
          expect(gap, `${mode} ${jd}`).toBeGreaterThan(0);
          const reach = sceneRadius(
            moonSceneOffset(moonAu, mode, earthState.semiMajorAu)
          );
          expect(reach).toBeCloseTo(
            distanceAu(moonAu) * linearAuScale(earthState.semiMajorAu, mode),
            6
          );
          expect(reach).toBeLessThan(0.2);
        }
      }
    }
    expect(closestKm).toBeGreaterThan(30_000_000);
  });

  it("would hide a real Moon inside the enlarged showcase Earth", () => {
    const moon = moonGeocentricAu(2460760.5, MOON_ELEMENTS);
    const reach = sceneRadius(moonSceneOffset(moon, "showcase", 1));
    expect(reach).toBeLessThan(visualRadiusKm(EARTH_RADIUS_KM, "showcase"));
    expect(reach).toBeGreaterThan(0);
  });
});

function auLength(au: number): number {
  return au * TRUE_AU * (AU_IN_KM / TRUE_AU);
}
