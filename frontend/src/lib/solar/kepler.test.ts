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
  type AuPoint,
  type EpochElements,
} from "./kepler";
import { spinPose, spinSummary } from "./spin";
import {
  EARTH_YEAR_SECONDS,
  SIDEREAL_YEAR_DAYS,
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

function delta(a: AuPoint, b: AuPoint): AuPoint {
  return { x: a.x - b.x, y: a.y - b.y, z: a.z - b.z };
}

function angleBetween(a: AuPoint, b: AuPoint): number {
  const dot = a.x * b.x + a.y * b.y + a.z * b.z;
  const denom = distanceAu(a) * distanceAu(b);
  if (denom <= 0) return 180;
  return (Math.acos(Math.min(1, Math.max(-1, dot / denom))) * 180) / Math.PI;
}

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

  it("matches Horizons for Venus and the Moon on sampled TDB dates", () => {
    // Geometric states, no light-time or aberration.
    // Planets: Sun body center (500@10), mean ecliptic of J2000.
    // Moon: Earth body center (500@399), same plane.
    // Our Earth is the Earth–Moon barycenter from the JPL Keplerian table,
    // so a few thousand km versus Horizons geocenter 399 is expected.
    // The Moon is Schlyter's truncated series, not DE441.
    const moonElements = {
      semiMajorKm: 384400,
      eccentricity: 0.0549,
      inclinationDeg: 5.145,
      periodDays: 27.322,
    };
    const samples: Array<{
      jd: number;
      venus: AuPoint;
      moon: AuPoint;
    }> = [
      {
        jd: 2451545.0,
        venus: {
          x: -7.18302296345389e-1,
          y: -3.265430819980606e-2,
          z: 4.101418202684621e-2,
        },
        moon: {
          x: -1.949281649686695e-3,
          y: -1.838126040073046e-3,
          z: 2.424579738820632e-4,
        },
      },
      {
        jd: 2460760.5,
        venus: {
          x: -7.139430875163638e-1,
          y: -8.870957079388866e-2,
          z: 3.997553584484202e-2,
        },
        moon: {
          x: 1.854329456175498e-3,
          y: -1.660861974270432e-3,
          z: -1.446577605487008e-4,
        },
      },
      {
        jd: 2461349.5,
        venus: {
          x: 4.706736086844561e-1,
          y: 5.480009408357099e-1,
          z: -1.962666810317525e-2,
        },
        moon: {
          x: -2.534815131222421e-3,
          y: 3.738832188452365e-4,
          z: -9.579422279496562e-5,
        },
      },
    ];
    for (const sample of samples) {
      const venus = planetPositionAu("Venus", sample.jd, null);
      const moon = moonGeocentricAu(sample.jd, moonElements);
      const venusKm = distanceAu(delta(venus, sample.venus)) * AU_IN_KM;
      const moonKm = distanceAu(delta(moon, sample.moon)) * AU_IN_KM;
      const moonAngle = angleBetween(moon, sample.moon);
      // Measured 2000-01-01, 2025-03-26 and 2026-11-05: Venus under 8,200 km,
      // Moon under 2,600 km and 0.4°. The old J2000 epoch was about 20°.
      expect(venusKm, `Venus ${sample.jd}`).toBeLessThan(12000);
      expect(moonKm, `Moon ${sample.jd}`).toBeLessThan(8000);
      expect(moonAngle, `Moon angle ${sample.jd}`).toBeLessThan(1);
    }
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

  it("covers one sidereal year in 180 seconds at rate 1, whatever the frame size", () => {
    const start = 2451545;
    const whole = stepJulianDay(start, EARTH_YEAR_SECONDS, 1);
    expect(EARTH_YEAR_SECONDS).toBe(180);
    expect(whole - start).toBeCloseTo(SIDEREAL_YEAR_DAYS, 8);

    let coarse = start;
    coarse = stepJulianDay(coarse, 90, 1);
    coarse = stepJulianDay(coarse, 90, 1);
    expect(coarse).toBeCloseTo(whole, 8);

    const frame = 1 / 60;
    const frames = Math.round(EARTH_YEAR_SECONDS / frame);
    let fine = start;
    for (let i = 0; i < frames; i += 1) fine = stepJulianDay(fine, frame, 1);
    expect(fine - start).toBeCloseTo(
      SIDEREAL_YEAR_DAYS * ((frames * frame) / EARTH_YEAR_SECONDS),
      5
    );
    expect(stepJulianDay(whole, EARTH_YEAR_SECONDS, -1)).toBeCloseTo(start, 8);
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
