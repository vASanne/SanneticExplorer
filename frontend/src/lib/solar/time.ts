import { t } from "$lib/i18n/copy";

/** J2000.0 = 2000-01-01 12:00 TT ≈ JD 2451545.0. Playback treats UTC as TDB; the difference is about a minute. */
export const J2000_JD = 2451545.0;

/**
 * Mean sidereal year at J2000, in days: one Earth revolution relative to the stars.
 * IAU value 365.256363 d. Earth's JPL mean motion in kepler.ts
 * (35999.37244981° per Julian century) is 365.25636 d, the same year.
 */
export const SIDEREAL_YEAR_DAYS = 365.256363;

/** Real seconds for one sidereal year at playback rate 1. One Earth year lasts three minutes. */
export const EARTH_YEAR_SECONDS = 180;

const UNIX_JD = 2440587.5;

export function julianDayFromUnixMs(ms: number): number {
  return ms / 86400000 + UNIX_JD;
}

export function julianNow(): number {
  return julianDayFromUnixMs(Date.now());
}

/**
 * Advance the simulation clock. Rate 1 covers one sidereal year in
 * EARTH_YEAR_SECONDS. The step is linear in real seconds, so the elapsed
 * simulation time does not depend on the frame size. Negative speed runs backwards.
 */
export function stepJulianDay(
  jd: number,
  deltaSeconds: number,
  speed: number,
  earthYearSeconds = EARTH_YEAR_SECONDS
): number {
  const days = deltaSeconds * speed * (SIDEREAL_YEAR_DAYS / earthYearSeconds);
  return jd + days;
}

export interface CalendarStamp {
  year: number;
  month: number;
  day: number;
  hours: number;
  minutes: number;
}

/** Gregorian calendar from a Julian day. Proleptic before 1582. */
export function calendarFromJulian(jd: number): CalendarStamp {
  let z = Math.floor(jd + 0.5);
  const f = jd + 0.5 - z;
  let a = z;
  if (z >= 2299161) {
    const alpha = Math.floor((z - 1867216.25) / 36524.25);
    a = z + 1 + alpha - Math.floor(alpha / 4);
  }
  const b = a + 1524;
  const c = Math.floor((b - 122.1) / 365.25);
  const d = Math.floor(365.25 * c);
  const e = Math.floor((b - d) / 30.6001);
  const day = b - d - Math.floor(30.6001 * e) + f;
  const month = e < 14 ? e - 1 : e - 13;
  const year = month > 2 ? c - 4716 : c - 4715;
  const dayInt = Math.floor(day);
  const hoursTotal = (day - dayInt) * 24;
  const hours = Math.floor(hoursTotal);
  const minutes = Math.floor((hoursTotal - hours) * 60 + 1e-6);
  return { year, month, day: dayInt, hours, minutes: Math.min(minutes, 59) };
}

export function formatSimDate(jd: number): string {
  if (!Number.isFinite(jd)) return "—";
  const stamp = calendarFromJulian(jd);
  const month = t(`date.month.${stamp.month}`);
  const hh = String(stamp.hours).padStart(2, "0");
  const mm = String(stamp.minutes).padStart(2, "0");
  const year =
    stamp.year > 0
      ? String(stamp.year)
      : t("date.bc", { year: Math.abs(stamp.year) });
  return t("date.stamp", {
    day: stamp.day,
    month,
    year,
    time: `${hh}:${mm}`,
  });
}
