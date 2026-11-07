/**
 * Heliocentric positions from Keplerian elements and secular rates.
 *
 * Rates and the fallback epoch are the JPL / Standish tables
 * "Keplerian Elements for Approximate Positions of the Major Planets"
 * (mean ecliptic and equinox of J2000). 1800–2050 uses their short-period fit.
 * Outside that window the 3000 BC–3000 AD fit is used, including the extra
 * terms in mean anomaly for Jupiter–Neptune.
 *
 * Epoch angles supplied by the live API (Data/ at J2000) replace the table
 * epoch. Rates are not in Data/, so they always come from the reference table.
 * Earth is the Earth–Moon barycenter, which is within a few thousand km of
 * the geocenter — inside the published accuracy of this approximation.
 */

import { J2000_JD } from "./time";

export interface AuPoint {
  x: number;
  y: number;
  z: number;
}

/** Null fields are missing from the live payload and fall back to the reference table. */
export interface EpochElements {
  semiMajorAu: number | null;
  eccentricity: number | null;
  inclinationDeg: number | null;
  ascendingNodeDeg: number | null;
  argPeriapsisDeg: number | null;
  meanAnomalyDeg: number | null;
}

export interface KeplerState {
  semiMajorAu: number;
  eccentricity: number;
  inclinationDeg: number;
  argPeriapsisDeg: number;
  ascendingNodeDeg: number;
  meanAnomalyDeg: number;
}

interface RateRow {
  a0: number;
  adot: number;
  e0: number;
  edot: number;
  I0: number;
  Idot: number;
  L0: number;
  Ldot: number;
  p0: number;
  pdot: number;
  O0: number;
  Odot: number;
  b: number;
  c: number;
  s: number;
  f: number;
}

function row(
  a0: number,
  adot: number,
  e0: number,
  edot: number,
  I0: number,
  Idot: number,
  L0: number,
  Ldot: number,
  p0: number,
  pdot: number,
  O0: number,
  Odot: number,
  b = 0,
  c = 0,
  s = 0,
  f = 0
): RateRow {
  return {
    a0,
    adot,
    e0,
    edot,
    I0,
    Idot,
    L0,
    Ldot,
    p0,
    pdot,
    O0,
    Odot,
    b,
    c,
    s,
    f,
  };
}

/** Table 1, valid 1800 AD – 2050 AD. Extra mean-anomaly terms are zero. */
const TABLE_1800: Record<string, RateRow> = {
  Mercury: row(
    0.38709927,
    0.00000037,
    0.20563593,
    0.00001906,
    7.00497902,
    -0.00594749,
    252.2503235,
    149472.67411175,
    77.45779628,
    0.16047689,
    48.33076593,
    -0.12534081
  ),
  Venus: row(
    0.72333566,
    0.0000039,
    0.00677672,
    -0.00004107,
    3.39467605,
    -0.0007889,
    181.9790995,
    58517.81538729,
    131.60246718,
    0.00268329,
    76.67984255,
    -0.27769418
  ),
  Earth: row(
    1.00000261,
    0.00000562,
    0.01671123,
    -0.00004392,
    -0.00001531,
    -0.01294668,
    100.46457166,
    35999.37244981,
    102.93768193,
    0.32327364,
    0,
    0
  ),
  Mars: row(
    1.52371034,
    0.00001847,
    0.0933941,
    0.00007882,
    1.84969142,
    -0.00813131,
    -4.55343205,
    19140.30268499,
    -23.94362959,
    0.44441088,
    49.55953891,
    -0.29257343
  ),
  Jupiter: row(
    5.202887,
    -0.00011607,
    0.04838624,
    -0.00013253,
    1.30439695,
    -0.00183714,
    34.39644051,
    3034.74612775,
    14.72847983,
    0.21252668,
    100.47390909,
    0.20469106
  ),
  Saturn: row(
    9.53667594,
    -0.0012506,
    0.05386179,
    -0.00050991,
    2.48599187,
    0.00193609,
    49.95424423,
    1222.49362201,
    92.59887831,
    -0.41897216,
    113.66242448,
    -0.28867794
  ),
  Uranus: row(
    19.18916464,
    -0.00196176,
    0.04725744,
    -0.00004397,
    0.77263783,
    -0.00242939,
    313.23810451,
    428.48202785,
    170.9542763,
    0.40805281,
    74.01692503,
    0.04240589
  ),
  Neptune: row(
    30.06992276,
    0.00026291,
    0.00859048,
    0.00005105,
    1.77004347,
    0.00035372,
    -55.12002969,
    218.45945325,
    44.96476227,
    -0.32241464,
    131.78422574,
    -0.00508664
  ),
};

/** Table 2a/2b, valid 3000 BC – 3000 AD. */
const TABLE_LONG: Record<string, RateRow> = {
  Mercury: row(
    0.38709843,
    0,
    0.20563661,
    0.00002123,
    7.00559432,
    -0.00590158,
    252.25166724,
    149472.67486623,
    77.45771895,
    0.15940013,
    48.33961819,
    -0.12214182
  ),
  Venus: row(
    0.72332102,
    -0.00000026,
    0.00676399,
    -0.00005107,
    3.39777545,
    0.00043494,
    181.9797085,
    58517.8156026,
    131.76755713,
    0.05679648,
    76.67261496,
    -0.27274174
  ),
  Earth: row(
    1.00000018,
    -0.00000003,
    0.01673163,
    -0.00003661,
    -0.00054346,
    -0.01337178,
    100.46691572,
    35999.37306329,
    102.93005885,
    0.3179526,
    -5.11260389,
    -0.24123856
  ),
  Mars: row(
    1.52371243,
    0.00000097,
    0.09336511,
    0.00009149,
    1.85181869,
    -0.00724757,
    -4.56813164,
    19140.29934243,
    -23.91744784,
    0.45223625,
    49.71320984,
    -0.26852431
  ),
  Jupiter: row(
    5.20248019,
    -0.00002864,
    0.0485359,
    0.00018026,
    1.29861416,
    -0.00322699,
    34.33479152,
    3034.90371757,
    14.27495244,
    0.18199196,
    100.29282654,
    0.13024619,
    -0.00012452,
    0.0606406,
    -0.35635438,
    38.35125
  ),
  Saturn: row(
    9.54149883,
    -0.00003065,
    0.05550825,
    -0.00032044,
    2.49424102,
    0.00451969,
    50.07571329,
    1222.11494724,
    92.86136063,
    0.54179478,
    113.63998702,
    -0.25015002,
    0.00025899,
    -0.13434469,
    0.87320147,
    38.35125
  ),
  Uranus: row(
    19.18797948,
    -0.00020455,
    0.0468574,
    -0.0000155,
    0.77298127,
    -0.00180155,
    314.20276625,
    428.49512595,
    172.43404441,
    0.09266985,
    73.96250215,
    0.05739699,
    0.00058331,
    -0.97731848,
    0.17689245,
    7.67025
  ),
  Neptune: row(
    30.06952752,
    0.00006447,
    0.00895439,
    0.00000818,
    1.7700552,
    0.000224,
    304.22289287,
    218.46515314,
    46.68158724,
    0.01009938,
    131.78635853,
    -0.00606302,
    -0.00041348,
    0.68346318,
    -0.10162547,
    7.67025
  ),
};

const AU_KM = 149597870.7;
const MOON_EARTH_RADIUS_KM = 6378.14;
/**
 * Paul Schlyter's lunar elements are for 1999-12-31 00:00 UT (JD 2451543.5).
 * J2000 is 1.5 days later. Using J2000 here shifts the Moon by about 20°.
 */
export const LUNAR_ELEMENT_JD = 2451543.5;
const LUNAR_ANOMALY_RATE = 13.0649929509;

function rad(degrees: number): number {
  return (degrees * Math.PI) / 180;
}

function deg(radians: number): number {
  return (radians * 180) / Math.PI;
}

function isNum(value: number | null | undefined): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function pick(value: number | null | undefined, fallback: number): number {
  return isNum(value) ? value : fallback;
}

export function referenceTable(jd: number): Record<string, RateRow> {
  const year = 2000 + (jd - J2000_JD) / 365.25;
  return year >= 1800 && year <= 2050 ? TABLE_1800 : TABLE_LONG;
}

export function eccentricAnomaly(
  meanAnomalyRad: number,
  eccentricity: number
): number {
  const e = Math.min(Math.max(eccentricity, 0), 0.9);
  let mean = Math.atan2(Math.sin(meanAnomalyRad), Math.cos(meanAnomalyRad));
  let eccentric = mean + e * Math.sin(mean);
  for (let i = 0; i < 15; i += 1) {
    const deltaMean = mean - (eccentric - e * Math.sin(eccentric));
    const delta = deltaMean / (1 - e * Math.cos(eccentric));
    eccentric += delta;
    if (Math.abs(delta) < 1e-12) break;
  }
  return eccentric;
}

export function keplerState(
  name: string,
  jd: number,
  epoch: EpochElements | null,
  periodDays: number | null = null
): KeplerState {
  const ref = referenceTable(jd)[name];
  const T = (jd - J2000_JD) / 36525;
  if (!ref) {
    const a = pick(epoch?.semiMajorAu, 1);
    const e = Math.min(Math.max(pick(epoch?.eccentricity, 0), 0), 0.9);
    const days = periodDays && periodDays > 0 ? periodDays : 365.25;
    const mean =
      pick(epoch?.meanAnomalyDeg, 0) + (360 * (jd - J2000_JD)) / days;
    return {
      semiMajorAu: a,
      eccentricity: e,
      inclinationDeg: pick(epoch?.inclinationDeg, 0),
      argPeriapsisDeg: pick(epoch?.argPeriapsisDeg, 0),
      ascendingNodeDeg: pick(epoch?.ascendingNodeDeg, 0),
      meanAnomalyDeg: mean,
    };
  }

  const a0 =
    isNum(epoch?.semiMajorAu) && epoch.semiMajorAu > 0
      ? epoch.semiMajorAu
      : ref.a0;
  const e0 = pick(epoch?.eccentricity, ref.e0);
  const I0 = pick(epoch?.inclinationDeg, ref.I0);
  let L0 = ref.L0;
  let peri0 = ref.p0;
  let node0 = ref.O0;
  if (
    isNum(epoch?.ascendingNodeDeg) &&
    isNum(epoch?.argPeriapsisDeg) &&
    isNum(epoch?.meanAnomalyDeg)
  ) {
    node0 = epoch.ascendingNodeDeg;
    peri0 = epoch.argPeriapsisDeg + node0;
    L0 = epoch.meanAnomalyDeg + peri0;
  }

  const semiMajorAu = a0 + ref.adot * T;
  const eccentricity = Math.min(Math.max(e0 + ref.edot * T, 0), 0.9);
  const inclinationDeg = I0 + ref.Idot * T;
  const peri = peri0 + ref.pdot * T;
  const node = node0 + ref.Odot * T;
  const arg = ref.f * T;
  const mean =
    L0 +
    ref.Ldot * T -
    peri +
    ref.b * T * T +
    ref.c * Math.cos(rad(arg)) +
    ref.s * Math.sin(rad(arg));

  return {
    semiMajorAu,
    eccentricity,
    inclinationDeg,
    argPeriapsisDeg: peri - node,
    ascendingNodeDeg: node,
    meanAnomalyDeg: mean,
  };
}

/** Orbital-plane coordinates rotated into the J2000 mean ecliptic. */
export function heliocentricEcliptic(
  state: KeplerState,
  eccentricOverride?: number
): AuPoint {
  const e = Math.min(Math.max(state.eccentricity, 0), 0.9);
  const eccentric =
    eccentricOverride ?? eccentricAnomaly(rad(state.meanAnomalyDeg), e);
  const xOrb = state.semiMajorAu * (Math.cos(eccentric) - e);
  const yOrb = state.semiMajorAu * Math.sqrt(1 - e * e) * Math.sin(eccentric);
  const w = rad(state.argPeriapsisDeg);
  const i = rad(state.inclinationDeg);
  const node = rad(state.ascendingNodeDeg);
  const cw = Math.cos(w);
  const sw = Math.sin(w);
  const ci = Math.cos(i);
  const si = Math.sin(i);
  const co = Math.cos(node);
  const so = Math.sin(node);
  return {
    x: (cw * co - sw * so * ci) * xOrb + (-sw * co - cw * so * ci) * yOrb,
    y: (cw * so + sw * co * ci) * xOrb + (-sw * so + cw * co * ci) * yOrb,
    z: sw * si * xOrb + cw * si * yOrb,
  };
}

export function planetPositionAu(
  name: string,
  jd: number,
  epoch: EpochElements | null,
  periodDays: number | null = null
): AuPoint {
  return heliocentricEcliptic(keplerState(name, jd, epoch, periodDays));
}

export interface MoonElements {
  semiMajorKm?: number | null;
  eccentricity?: number | null;
  inclinationDeg?: number | null;
  periodDays?: number | null;
}

/**
 * Geocentric ecliptic position of the Moon (mean ecliptic of J2000).
 * Size, eccentricity and inclination come from the caller
 * (Data/Planets/earth.json). Node, perigee and the main perturbations are
 * Paul Schlyter's truncated series at JD 2451543.5 — Data/ does not carry
 * those angles. This is not a JPL ephemeris: a few thousand kilometres of
 * position error is normal, which is still far inside the Earth–Venus gap.
 */
export function moonGeocentricAu(
  jd: number,
  elements: MoonElements = {}
): AuPoint {
  const d = jd - LUNAR_ELEMENT_JD;
  const node = rad(125.1228 - 0.0529538083 * d);
  const inclination = rad(pick(elements.inclinationDeg, 5.1454));
  const peri = rad(318.0634 + 0.1643573223 * d);
  const aEarthRadii =
    pick(elements.semiMajorKm, 60.2666 * MOON_EARTH_RADIUS_KM) /
    MOON_EARTH_RADIUS_KM;
  const eccentricity = Math.min(
    Math.max(pick(elements.eccentricity, 0.0549), 0),
    0.2
  );
  // Data/ records the sidereal month as 27.322 days. That rounding drifts
  // about 1.6° by 2026 if it replaces the rate these angles were published with.
  // A clearly different period (another moon) still overrides the reference rate.
  const fromPeriod =
    elements.periodDays && elements.periodDays > 0
      ? 360 / elements.periodDays - 0.1643573223 + 0.0529538083
      : LUNAR_ANOMALY_RATE;
  const anomalyRate =
    Math.abs(fromPeriod - LUNAR_ANOMALY_RATE) > 0.01
      ? fromPeriod
      : LUNAR_ANOMALY_RATE;
  const mean = rad(115.3654 + anomalyRate * d);
  const eccentric = eccentricAnomaly(mean, eccentricity);
  const xv = aEarthRadii * (Math.cos(eccentric) - eccentricity);
  const yv =
    aEarthRadii *
    Math.sqrt(1 - eccentricity * eccentricity) *
    Math.sin(eccentric);
  const v = Math.atan2(yv, xv);
  const radius = Math.hypot(xv, yv);
  const angle = v + peri;
  const xh =
    radius *
    (Math.cos(node) * Math.cos(angle) -
      Math.sin(node) * Math.sin(angle) * Math.cos(inclination));
  const yh =
    radius *
    (Math.sin(node) * Math.cos(angle) +
      Math.cos(node) * Math.sin(angle) * Math.cos(inclination));
  const zh = radius * Math.sin(angle) * Math.sin(inclination);

  const sunMean = rad(356.047 + 0.9856002585 * d);
  const sunPeri = rad(282.9404 + 4.70935e-5 * d);
  const moonLong = mean + peri + node;
  const elongation = moonLong - (sunMean + sunPeri);
  const latitudeArg = moonLong - node;
  const sin = Math.sin;
  const cos = Math.cos;

  let lon = Math.atan2(yh, xh);
  let lat = Math.atan2(zh, Math.hypot(xh, yh));
  let distance = radius;
  lon += rad(
    -1.274 * sin(mean - 2 * elongation) +
      0.658 * sin(2 * elongation) -
      0.186 * sin(sunMean) -
      0.059 * sin(2 * mean - 2 * elongation) -
      0.057 * sin(mean - 2 * elongation + sunMean) +
      0.053 * sin(mean + 2 * elongation) +
      0.046 * sin(2 * elongation - sunMean) +
      0.041 * sin(mean - sunMean) -
      0.035 * sin(elongation) -
      0.031 * sin(mean + sunMean) -
      0.015 * sin(2 * latitudeArg - 2 * elongation) +
      0.011 * sin(mean - 4 * elongation)
  );
  lat += rad(
    -0.173 * sin(latitudeArg - 2 * elongation) -
      0.055 * sin(mean - latitudeArg - 2 * elongation) -
      0.046 * sin(mean + latitudeArg - 2 * elongation) +
      0.033 * sin(latitudeArg + 2 * elongation) +
      0.017 * sin(2 * mean + latitudeArg)
  );
  distance += -0.58 * cos(mean - 2 * elongation) - 0.46 * cos(2 * elongation);

  const au = MOON_EARTH_RADIUS_KM / AU_KM;
  return {
    x: distance * Math.cos(lat) * Math.cos(lon) * au,
    y: distance * Math.cos(lat) * Math.sin(lon) * au,
    z: distance * Math.sin(lat) * au,
  };
}

export function eclipticLongitudeDeg(point: AuPoint): number {
  return deg(Math.atan2(point.y, point.x));
}

export function distanceAu(point: AuPoint): number {
  return Math.hypot(point.x, point.y, point.z);
}

export const AU_IN_KM = AU_KM;
