import { describe, expect, it } from "vitest";
import { locale } from "svelte-i18n";
import {
  AU_IN_KM,
  distanceAu,
  eclipticLongitudeDeg,
  heliocentricEcliptic,
  keplerState,
  moonGeocentricAu,
  planetPositionAu,
  type EpochElements,
} from "./kepler";
import { spinPose, spinSummary } from "./spin";
import {
  calendarFromJulian,
  formatSimDate,
  julianDayFromUnixMs,
  stepJulianDay,
} from "./time";

/** Horizons Earth (399) geometric state, Sun body center, ecliptic of J2000, 2026-11-05 00:00 TDB. */
const HORIZONS_EARTH = {
  jd: 2461349.5,
  x: 7.345398824596405e-1,
  y: 6.662568034211095e-1,
  z: -4.432009202127348e-5,
};

/** J2000 elements as stored in Data/Planets/earth.json and returned by /planets. */
const EARTH_DATA: EpochElements = {
  semiMajorAu: 1,
  eccentricity: 0.0167,
  inclinationDeg: 0,
  ascendingNodeDeg: -11.26064,
  argPeriapsisDeg: 114.20783,
  meanAnomalyDeg: 357.51716,
};

function angleDelta(a: number, b: number): number {
  const raw = Math.abs(((((a - b) % 360) + 540) % 360) - 180);
  return raw;
}

describe("keplerian positions", () => {
  it("matches Horizons for Earth on 2026-11-05 within the JPL approximation", () => {
    const pure = planetPositionAu("Earth", HORIZONS_EARTH.jd, null);
    const fromData = planetPositionAu("Earth", HORIZONS_EARTH.jd, EARTH_DATA);
    for (const point of [pure, fromData]) {
      const km =
        distanceAu({
          x: point.x - HORIZONS_EARTH.x,
          y: point.y - HORIZONS_EARTH.y,
          z: point.z - HORIZONS_EARTH.z,
        }) * AU_IN_KM;
      const lon = eclipticLongitudeDeg(point);
      const horizonsLon = eclipticLongitudeDeg(HORIZONS_EARTH);
      expect(km).toBeLessThan(20000);
      expect(angleDelta(lon, horizonsLon)).toBeLessThan(0.02);
    }
  });

  it("lifts Mercury off the ecliptic", () => {
    const state = keplerState("Mercury", HORIZONS_EARTH.jd, null);
    let maxZ = 0;
    for (let i = 0; i < 36; i += 1) {
      const point = heliocentricEcliptic(state, (i / 36) * Math.PI * 2);
      maxZ = Math.max(maxZ, Math.abs(point.z));
    }
    expect(maxZ).toBeGreaterThan(0.03);
    expect(state.inclinationDeg).toBeGreaterThan(6);
  });

  it("uses a live semi-major axis and JPL angles when the node is missing", () => {
    const state = keplerState("Mars", 2451545, {
      semiMajorAu: 1.6,
      eccentricity: null,
      inclinationDeg: null,
      ascendingNodeDeg: null,
      argPeriapsisDeg: null,
      meanAnomalyDeg: null,
    });
    expect(state.semiMajorAu).toBeCloseTo(1.6, 6);
    const reference = keplerState("Mars", 2451545, null);
    expect(state.ascendingNodeDeg).toBeCloseTo(reference.ascendingNodeDeg, 6);
    expect(state.meanAnomalyDeg).toBeCloseTo(reference.meanAnomalyDeg, 4);
  });

  it("keeps the Moon near 384,400 km and out of the ecliptic", () => {
    const moon = moonGeocentricAu(HORIZONS_EARTH.jd, {
      semiMajorKm: 384400,
      eccentricity: 0.0549,
      inclinationDeg: 5.145,
      periodDays: 27.322,
    });
    const km = distanceAu(moon) * AU_IN_KM;
    expect(km).toBeGreaterThan(350000);
    expect(km).toBeLessThan(430000);
    expect(Math.abs(moon.z)).toBeGreaterThan(1e-6);
  });
});

describe("simulation clock", () => {
  it("converts J2000 and formats 2026-11-05", () => {
    expect(julianDayFromUnixMs(Date.UTC(2000, 0, 1, 12, 0, 0))).toBeCloseTo(
      2451545,
      6
    );
    locale.set("de");
    expect(formatSimDate(2461349.5)).toBe("5. Nov. 2026 · 00:00 UTC");
    locale.set("en");
    expect(formatSimDate(2461349.5)).toBe("5 Nov 2026 · 00:00 UTC");
    locale.set("de");
    expect(calendarFromJulian(2451545).year).toBe(2000);
  });

  it("runs time backwards when speed is negative", () => {
    const forward = stepJulianDay(2451545, 2, 10, 48);
    const reverse = stepJulianDay(2451545, 2, -10, 48);
    expect(forward).toBeGreaterThan(2451545);
    expect(reverse).toBeLessThan(2451545);
    expect(forward - 2451545).toBeCloseTo(2451545 - reverse, 8);
  });
});

describe("sidereal orientation", () => {
  it("tilts Earth by the obliquity and spins Venus backwards", () => {
    const earth = spinSummary("Earth");
    const venus = spinSummary("Venus");
    const uranus = spinSummary("Uranus");
    expect(earth?.obliquityDeg).toBeGreaterThan(23);
    expect(earth?.obliquityDeg).toBeLessThan(24);
    expect(earth?.siderealHours).toBeCloseTo(23.93, 1);
    expect(venus?.siderealHours).toBeLessThan(0);
    expect(uranus?.obliquityDeg).toBeGreaterThan(90);
    const pose = spinPose("Earth", 2451545);
    expect(pose.pole.y).toBeGreaterThan(0.9);
  });
});
