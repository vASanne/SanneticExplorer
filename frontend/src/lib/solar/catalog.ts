/**
 * Reference solar system used when /planets is empty, and the visual layer
 * (maps, colors) that the live payload does not carry.
 * Distances and masses match Data/Planets and Data/Stars/sun.json.
 * Positions themselves come from kepler.ts: live J2000 elements where the API
 * has them, otherwise the JPL secular-rate tables.
 */

export interface CatalogBody {
  name: string;
  subtype: string;
  radiusKm: number;
  distanceAu: number;
  orbitalPeriodDays: number;
  eccentricity: number;
  inclinationDeg: number;
  ascendingNodeDeg: number;
  argPeriapsisDeg: number;
  meanAnomalyDeg: number;
  axialTiltDeg: number;
  /** Negative hours spin retrograde. */
  rotationHours: number;
  massKg: number;
  gravityMs2: number;
  temperatureK: number;
  atmosphere: Record<string, string> | null;
  hasRings: boolean;
  colorHex: string;
  texture: string;
  clouds?: string;
  night?: string;
  ringTexture?: string;
  roughness: number;
}

export const TEXTURE_FILES = [
  "sun.jpg",
  "mercury.jpg",
  "venus.jpg",
  "earth_day.jpg",
  "earth_clouds.jpg",
  "earth_night.jpg",
  "mars.jpg",
  "jupiter.jpg",
  "saturn.jpg",
  "saturn_ring.png",
  "uranus.jpg",
  "neptune.jpg",
  "moon.jpg",
  "stars.jpg",
] as const;

export const CLASSICAL_PLANETS = [
  "Mercury",
  "Venus",
  "Earth",
  "Mars",
  "Jupiter",
  "Saturn",
  "Uranus",
  "Neptune",
] as const;

export const SUN = {
  name: "Sun",
  subtype: "G2V star",
  radiusKm: 696340,
  massKg: 1.9885e30,
  temperatureK: 5778,
  colorHex: "#FDB813",
  texture: "/textures/sun.jpg",
  starfield: "/textures/stars.jpg",
  summary:
    "The Sun is drawn in the scene. Planet sizes and orbital elements come from the live /planets API when the database has rows. Missing elements fall back to the JPL J2000 tables.",
};

/** Moon figures that Data/Planets/earth.json actually carries. Angles and rates are filled in kepler.ts. */
export const MOON = {
  name: "Moon",
  radiusKm: 1737.4,
  distanceKm: 384400,
  periodDays: 27.322,
  eccentricity: 0.0549,
  inclinationDeg: 5.145,
  texture: "/textures/moon.jpg",
  summary:
    "Distance, size, eccentricity, inclination and sidereal period follow Data/Planets/earth.json. Node, perigee and the main perturbations are the reference model, because those angles are not in Data/.",
};

export const CATALOG: CatalogBody[] = [
  {
    name: "Mercury",
    subtype: "terrestrial planet",
    radiusKm: 2439.5,
    distanceAu: 0.387,
    orbitalPeriodDays: 88,
    eccentricity: 0.2056,
    inclinationDeg: 7.0,
    ascendingNodeDeg: 48.33,
    argPeriapsisDeg: 29.12,
    meanAnomalyDeg: 174.8,
    axialTiltDeg: 0.03,
    rotationHours: 1407.6,
    massKg: 3.301e23,
    gravityMs2: 3.7,
    temperatureK: 440,
    atmosphere: null,
    hasRings: false,
    colorHex: "#8c7853",
    texture: "/textures/mercury.jpg",
    roughness: 0.95,
  },
  {
    name: "Venus",
    subtype: "terrestrial planet",
    radiusKm: 6052,
    distanceAu: 0.723,
    orbitalPeriodDays: 225,
    eccentricity: 0.0068,
    inclinationDeg: 3.39,
    ascendingNodeDeg: 76.68,
    argPeriapsisDeg: 54.88,
    meanAnomalyDeg: 50.12,
    axialTiltDeg: 2.64,
    rotationHours: -5832.5,
    massKg: 4.867e24,
    gravityMs2: 8.87,
    temperatureK: 737,
    atmosphere: { CO2: "96.5%", N2: "3.5%" },
    hasRings: false,
    colorHex: "#e7cdcd",
    texture: "/textures/venus.jpg",
    roughness: 0.88,
  },
  {
    name: "Earth",
    subtype: "terrestrial planet",
    radiusKm: 6371,
    distanceAu: 1,
    orbitalPeriodDays: 365.25,
    eccentricity: 0.0167,
    inclinationDeg: 0,
    ascendingNodeDeg: -11.26,
    argPeriapsisDeg: 114.21,
    meanAnomalyDeg: 358.62,
    axialTiltDeg: 23.44,
    rotationHours: 23.934,
    massKg: 5.972e24,
    gravityMs2: 9.81,
    temperatureK: 288,
    atmosphere: { N2: "78%", O2: "21%", Ar: "0.93%" },
    hasRings: false,
    colorHex: "#6b93d6",
    texture: "/textures/earth_day.jpg",
    clouds: "/textures/earth_clouds.jpg",
    night: "/textures/earth_night.jpg",
    roughness: 0.72,
  },
  {
    name: "Mars",
    subtype: "terrestrial planet",
    radiusKm: 3389.5,
    distanceAu: 1.524,
    orbitalPeriodDays: 687,
    eccentricity: 0.0934,
    inclinationDeg: 1.85,
    ascendingNodeDeg: 49.56,
    argPeriapsisDeg: 286.5,
    meanAnomalyDeg: 19.37,
    axialTiltDeg: 25.19,
    rotationHours: 24.623,
    massKg: 6.417e23,
    gravityMs2: 3.71,
    temperatureK: 210,
    atmosphere: { CO2: "95.3%", N2: "2.7%", Ar: "1.6%" },
    hasRings: false,
    colorHex: "#c1440e",
    texture: "/textures/mars.jpg",
    roughness: 0.94,
  },
  {
    name: "Jupiter",
    subtype: "gas giant",
    radiusKm: 69910,
    distanceAu: 5.203,
    orbitalPeriodDays: 4333,
    eccentricity: 0.0489,
    inclinationDeg: 1.3,
    ascendingNodeDeg: 100.46,
    argPeriapsisDeg: 273.87,
    meanAnomalyDeg: 20.02,
    axialTiltDeg: 3.13,
    rotationHours: 9.925,
    massKg: 1.898e27,
    gravityMs2: 24.79,
    temperatureK: 165,
    atmosphere: { H2: "90%", He: "10%" },
    hasRings: false,
    colorHex: "#d8ca9d",
    texture: "/textures/jupiter.jpg",
    roughness: 0.55,
  },
  {
    name: "Saturn",
    subtype: "gas giant",
    radiusKm: 58230,
    distanceAu: 9.537,
    orbitalPeriodDays: 10759,
    eccentricity: 0.0565,
    inclinationDeg: 2.49,
    ascendingNodeDeg: 113.67,
    argPeriapsisDeg: 339.39,
    meanAnomalyDeg: 317.02,
    axialTiltDeg: 26.73,
    rotationHours: 10.656,
    massKg: 5.683e26,
    gravityMs2: 10.44,
    temperatureK: 134,
    atmosphere: { H2: "96.3%", He: "3.25%" },
    hasRings: true,
    colorHex: "#fad5a5",
    texture: "/textures/saturn.jpg",
    ringTexture: "/textures/saturn_ring.png",
    roughness: 0.5,
  },
  {
    name: "Uranus",
    subtype: "ice giant",
    radiusKm: 25362,
    distanceAu: 19.191,
    orbitalPeriodDays: 30687,
    eccentricity: 0.0457,
    inclinationDeg: 0.77,
    ascendingNodeDeg: 74.01,
    argPeriapsisDeg: 97.0,
    meanAnomalyDeg: 142.24,
    axialTiltDeg: 97.77,
    rotationHours: -17.24,
    massKg: 8.681e25,
    gravityMs2: 8.69,
    temperatureK: 76,
    atmosphere: { H2: "82.5%", He: "15.2%", CH4: "2.3%" },
    hasRings: true,
    colorHex: "#d5f6f8",
    texture: "/textures/uranus.jpg",
    roughness: 0.48,
  },
  {
    name: "Neptune",
    subtype: "ice giant",
    radiusKm: 24622,
    distanceAu: 30.069,
    orbitalPeriodDays: 60190,
    eccentricity: 0.0113,
    inclinationDeg: 1.77,
    ascendingNodeDeg: 131.78,
    argPeriapsisDeg: 276.34,
    meanAnomalyDeg: 256.23,
    axialTiltDeg: 28.32,
    rotationHours: 16.11,
    massKg: 1.024e26,
    gravityMs2: 11.15,
    temperatureK: 72,
    atmosphere: { H2: "80%", He: "19%", CH4: "1%" },
    hasRings: false,
    colorHex: "#4b70dd",
    texture: "/textures/neptune.jpg",
    roughness: 0.48,
  },
];

const BY_NAME = new Map(CATALOG.map((body) => [body.name.toLowerCase(), body]));

export function catalogByName(name: string): CatalogBody | undefined {
  return BY_NAME.get(name.trim().toLowerCase());
}
