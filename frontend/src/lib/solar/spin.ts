/**
 * Axial orientation and sidereal spin from IAU cartographic poles
 * (Archinal et al. / WGCCRE; NAIF PCK-style linear terms).
 * The pole is the positive pole of the published W angle, so a negative
 * rate is retrograde (Venus, Uranus).
 */

import { J2000_JD } from "./time";

export interface SceneDirection {
  x: number;
  y: number;
  z: number;
}

export interface SpinPose {
  pole: SceneDirection;
  spinRadians: number;
  obliquityDeg: number;
  siderealHours: number;
}

interface PoleModel {
  ra: (t: number, d: number) => number;
  dec: (t: number, d: number) => number;
  w0: number;
  wdot: number;
}

const DEG = Math.PI / 180;
const OBLIQUITY = 23.4392911 * DEG;

function deg(radians: number): number {
  return radians / DEG;
}

const POLES: Record<string, PoleModel> = {
  Mercury: {
    ra: (t) => 281.0097 - 0.0328 * t,
    dec: (t) => 61.4143 - 0.0049 * t,
    w0: 329.5469,
    wdot: 6.1385025,
  },
  Venus: {
    ra: () => 272.76,
    dec: () => 67.16,
    w0: 160.2,
    wdot: -1.4813688,
  },
  Earth: {
    ra: (t) => -0.641 * t,
    dec: (t) => 90 - 0.557 * t,
    w0: 190.147,
    wdot: 360.9856235,
  },
  Mars: {
    ra: (t) => 317.68143 - 0.1061 * t,
    dec: (t) => 52.8865 - 0.0609 * t,
    w0: 176.63,
    wdot: 350.89198226,
  },
  Jupiter: {
    ra: (t) => 268.056595 - 0.006499 * t,
    dec: (t) => 64.495303 + 0.002413 * t,
    w0: 284.95,
    wdot: 870.536,
  },
  Saturn: {
    ra: (t) => 40.589 - 0.036 * t,
    dec: (t) => 83.537 - 0.004 * t,
    w0: 38.9,
    wdot: 810.7939024,
  },
  Uranus: {
    ra: () => 257.311,
    dec: () => -15.175,
    w0: 203.81,
    wdot: -501.1600928,
  },
  Neptune: {
    ra: (t) => 299.36 + 0.7 * Math.sin((357.85 + 52.316 * t) * DEG),
    dec: (t) => 43.46 - 0.51 * Math.cos((357.85 + 52.316 * t) * DEG),
    w0: 253.18,
    wdot: 536.3128492,
  },
  Moon: {
    ra: (t) => 269.9949 + 0.0031 * t,
    dec: (t) => 66.5392 + 0.013 * t,
    w0: 38.3213,
    wdot: 13.17635815,
  },
  Sun: {
    ra: () => 286.13,
    dec: () => 63.87,
    w0: 84.176,
    wdot: 14.1844,
  },
};

function equatorialToEcliptic(raDeg: number, decDeg: number): SceneDirection {
  const ra = raDeg * DEG;
  const dec = decDeg * DEG;
  const xeq = Math.cos(dec) * Math.cos(ra);
  const yeq = Math.cos(dec) * Math.sin(ra);
  const zeq = Math.sin(dec);
  return {
    x: xeq,
    y: Math.cos(OBLIQUITY) * yeq + Math.sin(OBLIQUITY) * zeq,
    z: -Math.sin(OBLIQUITY) * yeq + Math.cos(OBLIQUITY) * zeq,
  };
}

function scenePole(ecliptic: SceneDirection): SceneDirection {
  const x = ecliptic.x;
  const y = ecliptic.z;
  const z = -ecliptic.y;
  const length = Math.hypot(x, y, z) || 1;
  return { x: x / length, y: y / length, z: z / length };
}

function fallbackPose(
  jd: number,
  tiltDeg: number,
  rotationHours: number
): SpinPose {
  const tilt = tiltDeg * DEG;
  const hours = rotationHours === 0 ? 24 : rotationHours;
  const days = jd - J2000_JD;
  const turns = (days * 24) / hours;
  return {
    pole: { x: 0, y: Math.cos(tilt), z: -Math.sin(tilt) },
    spinRadians: turns * Math.PI * 2,
    obliquityDeg: Math.abs(tiltDeg),
    siderealHours: hours,
  };
}

export function spinPose(
  name: string,
  jd: number,
  fallback?: { tiltDeg: number; rotationHours: number }
): SpinPose {
  const model = POLES[name];
  if (!model)
    return fallbackPose(
      jd,
      fallback?.tiltDeg ?? 0,
      fallback?.rotationHours ?? 24
    );
  const centuries = (jd - J2000_JD) / 36525;
  const days = jd - J2000_JD;
  const ecliptic = equatorialToEcliptic(
    model.ra(centuries, days),
    model.dec(centuries, days)
  );
  const obliquity = Math.acos(Math.min(1, Math.max(-1, ecliptic.z)));
  return {
    pole: scenePole(ecliptic),
    spinRadians: (model.w0 + model.wdot * days) * DEG,
    obliquityDeg: deg(obliquity),
    siderealHours: (24 * 360) / model.wdot,
  };
}

export function spinSummary(
  name: string
): { obliquityDeg: number; siderealHours: number } | null {
  if (!POLES[name]) return null;
  const pose = spinPose(name, J2000_JD);
  // Retrograde bodies publish the right-hand obliquity, the supplement of the
  // cartographic-north angle. The mesh still points texture-north at the IAU pole.
  const obliquityDeg =
    pose.siderealHours < 0 ? 180 - pose.obliquityDeg : pose.obliquityDeg;
  return { obliquityDeg, siderealHours: pose.siderealHours };
}
