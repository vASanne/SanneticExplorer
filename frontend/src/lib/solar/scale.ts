/** One Earth year at 1× playback. Higher speeds divide this. Negative speed runs backwards. */
export const EARTH_YEAR_SECONDS = 48;

const AU_KM = 149597870.7;
const AU_SCALE = 16;
const DISTANCE_POWER = 0.72;
/** Scene units per astronomical unit when sizes and distances are linear. */
export const TRUE_AU = 50;

export type ScaleMode = "showcase" | "true";

/** The scene the visitor sees first. Illustrative sizes are an explicit opt-in. */
export const DEFAULT_SCALE_MODE: ScaleMode = "true";

/**
 * Map astronomical units into the scene.
 * A power below 1 keeps true order and a wide Neptune/Mercury ratio while
 * leaving the inner planets outside the Sun and inside one camera frame.
 * Real AU ratio Neptune/Mercury is ~78; this curve is ~23.
 */
export function auToScene(
  au: number,
  mode: ScaleMode = DEFAULT_SCALE_MODE
): number {
  const safe = Math.max(au, 0);
  if (mode === "true") return safe * TRUE_AU;
  return AU_SCALE * Math.pow(Math.max(safe, 0.02), DISTANCE_POWER);
}

/**
 * Kilometres to scene units when distances and radii are both linear.
 * Showcase mode must not use this factor.
 */
const TRUE_KM = TRUE_AU / AU_KM;

/**
 * Planet radii are enlarged versus true scale so maps read in an orrery.
 * True mode is the physical radius in the same units as auToScene: no power
 * curve and no minimum that would make a small body look larger than it is.
 */
export function visualRadiusKm(
  radiusKm: number,
  mode: ScaleMode = DEFAULT_SCALE_MODE
): number {
  if (mode === "true") {
    const radius = Number.isFinite(radiusKm) && radiusKm > 0 ? radiusKm : 0;
    return radius * TRUE_KM;
  }
  const earthKm = 6371;
  return 0.7 * Math.pow(Math.max(radiusKm, 200) / earthKm, 0.5);
}

export const SUN_SCENE_RADIUS = 3.35;
const SUN_RADIUS_KM = 696340;

export function sunSceneRadius(mode: ScaleMode = DEFAULT_SCALE_MODE): number {
  if (mode === "true") return SUN_RADIUS_KM * TRUE_KM;
  return SUN_SCENE_RADIUS;
}

/**
 * Showcase draws a wide corona so the Sun reads as a star.
 * True mode keeps that glow inside a thin limb so the photosphere stays the visual radius.
 */
export function solarCorona(mode: ScaleMode): { glow: number; halo: number } {
  if (mode === "true") return { glow: 1.16, halo: 1.38 };
  return { glow: 4.4, halo: 8.5 };
}

/** Screen-space bloom inflates a bright disc. True mode keeps it from painting a larger Sun. */
export function bloomFor(mode: ScaleMode): {
  strength: number;
  threshold: number;
} {
  if (mode === "true") return { strength: 0.045, threshold: 1.25 };
  return { strength: 0.22, threshold: 1.55 };
}

/**
 * Raycast radius. True mode may grow a tiny body so it can be clicked.
 * The mesh scale stays on visualRadiusKm.
 */
export function pickRadius(visualRadius: number, mode: ScaleMode): number {
  if (mode !== "true") return visualRadius;
  return Math.max(visualRadius, 0.02);
}

/**
 * Scene units per astronomical unit for one body's orbit.
 * True scale is linear for every body. Showcase compresses each semi-major
 * axis on its own curve, then keeps that body's ellipse linear in those units.
 */
export function linearAuScale(semiMajorAu: number, mode: ScaleMode): number {
  if (mode === "true") return TRUE_AU;
  const axis = Math.max(semiMajorAu, 1e-8);
  return auToScene(axis, "showcase") / axis;
}

/** Ecliptic J2000 (x, y, z) to scene Y-up, in the same units as auToScene. */
export function eclipticToScene(
  ecliptic: { x: number; y: number; z: number },
  semiMajorAu: number,
  mode: ScaleMode
): ScenePoint {
  const scale = linearAuScale(semiMajorAu, mode);
  return {
    x: ecliptic.x * scale,
    y: ecliptic.z * scale,
    z: -ecliptic.y * scale,
  };
}

/**
 * Geocentric ecliptic offset of the Moon, in the same scene units as Earth.
 * The length is the physical distance. It is not stretched toward a visual
 * Earth radius — that stretch reached Venus in the illustrative scale.
 */
export function moonSceneOffset(
  ecliptic: { x: number; y: number; z: number },
  mode: ScaleMode = DEFAULT_SCALE_MODE,
  earthSemiMajorAu = 1
): ScenePoint {
  const scale = linearAuScale(earthSemiMajorAu, mode);
  return {
    x: ecliptic.x * scale,
    y: ecliptic.z * scale,
    z: -ecliptic.y * scale,
  };
}

/**
 * Showcase enlarges Earth by hundreds of times, so a real lunar distance sits
 * inside that mesh. Drawing the Moon there would be a false collision.
 * The Moon is part of the physical scene only.
 */
export function moonShownInScene(mode: ScaleMode): boolean {
  return mode === "true";
}

export function orbitalOmega(periodDays: number): number {
  const years = Math.max(periodDays, 1) / 365.25;
  return (Math.PI * 2) / (years * EARTH_YEAR_SECONDS);
}

export interface OrbitElements {
  distanceAu: number;
  eccentricity: number;
  inclinationDeg: number;
  ascendingNodeDeg: number;
  argPeriapsisDeg: number;
}

export interface ScenePoint {
  x: number;
  y: number;
  z: number;
}

function solveEccentricAnomaly(
  meanAnomaly: number,
  eccentricity: number
): number {
  let eccentric = meanAnomaly;
  for (let i = 0; i < 8; i += 1) {
    const delta =
      (eccentric - eccentricity * Math.sin(eccentric) - meanAnomaly) /
      (1 - eccentricity * Math.cos(eccentric));
    eccentric -= delta;
  }
  return eccentric;
}

/** Position from eccentric anomaly so orbit lines are evenly sampled. */
export function positionFromEccentricAnomaly(
  elements: OrbitElements,
  eccentricAnomaly: number,
  mode: ScaleMode = DEFAULT_SCALE_MODE
): ScenePoint {
  const eccentricity = Math.min(Math.max(elements.eccentricity, 0), 0.95);
  const semiMajor = auToScene(elements.distanceAu, mode);
  const cosE = Math.cos(eccentricAnomaly);
  const sinE = Math.sin(eccentricAnomaly);
  const xOrb = semiMajor * (cosE - eccentricity);
  const zOrb = semiMajor * Math.sqrt(1 - eccentricity * eccentricity) * sinE;

  const peri = (elements.argPeriapsisDeg * Math.PI) / 180;
  const x1 = xOrb * Math.cos(peri) - zOrb * Math.sin(peri);
  const z1 = xOrb * Math.sin(peri) + zOrb * Math.cos(peri);

  const inclination = (elements.inclinationDeg * Math.PI) / 180;
  const y2 = -z1 * Math.sin(inclination);
  const z2 = z1 * Math.cos(inclination);

  const node = (elements.ascendingNodeDeg * Math.PI) / 180;
  return {
    x: x1 * Math.cos(node) - z2 * Math.sin(node),
    y: y2,
    z: x1 * Math.sin(node) + z2 * Math.cos(node),
  };
}

export function orbitalPosition(
  elements: OrbitElements,
  meanAnomaly: number,
  mode: ScaleMode = DEFAULT_SCALE_MODE
): ScenePoint {
  const eccentricity = Math.min(Math.max(elements.eccentricity, 0), 0.95);
  const eccentric = solveEccentricAnomaly(meanAnomaly, eccentricity);
  return positionFromEccentricAnomaly(elements, eccentric, mode);
}

export function orbitSamples(
  elements: OrbitElements,
  count = 192,
  mode: ScaleMode = DEFAULT_SCALE_MODE
): ScenePoint[] {
  const samples: ScenePoint[] = [];
  for (let i = 0; i <= count; i += 1) {
    const eccentric = (i / count) * Math.PI * 2;
    samples.push(positionFromEccentricAnomaly(elements, eccentric, mode));
  }
  return samples;
}

export function sceneRadius(point: ScenePoint): number {
  return Math.hypot(point.x, point.y, point.z);
}
