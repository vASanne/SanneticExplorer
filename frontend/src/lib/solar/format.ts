import { intlLocale, t, tOr } from "$lib/i18n/copy";

const EARTH_MASS_KG = 5.972e24;

export function formatAtmosphere(value: unknown): string | null {
  if (value == null || value === "") return null;
  if (typeof value === "string") return value;
  if (typeof value === "object") {
    const parts = Object.entries(value as Record<string, unknown>)
      .filter(([, entry]) => entry != null && entry !== "")
      .map(([key, entry]) => {
        const label = tOr(`atmosphere.${key}`, key);
        const raw = String(entry);
        const value = tOr(`atmosphereValues.${raw}`, raw);
        return `${label} ${value}`;
      });
    return parts.length ? parts.join(" · ") : null;
  }
  return null;
}

function fixed(value: number, digits: number): string {
  return value.toLocaleString(intlLocale(), {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

export function formatMass(kg: number | null): string {
  if (kg == null || !Number.isFinite(kg) || kg <= 0) return "—";
  const exp = Math.floor(Math.log10(kg));
  const mantissa = kg / 10 ** exp;
  const earth = kg / EARTH_MASS_KG;
  const earthText = t("units.earthMasses", {
    value:
      earth >= 0.01
        ? fixed(earth, earth >= 10 ? 1 : 3)
        : earth.toExponential(2),
  });
  return `${fixed(mantissa, 3)} × 10^${exp} kg · ${earthText}`;
}

export function formatDistance(au: number): string {
  if (!Number.isFinite(au)) return "—";
  return t("units.au", { value: fixed(au, au >= 10 ? 2 : 3) });
}

export function formatPeriod(days: number): string {
  if (!Number.isFinite(days) || days <= 0) return "—";
  const years = days / 365.25;
  if (years >= 1) {
    return t("units.daysYears", {
      days: Math.round(days).toLocaleString(intlLocale(), {
        maximumFractionDigits: 0,
      }),
      years: fixed(years, years >= 10 ? 1 : 2),
    });
  }
  return t("units.days", { days: fixed(days, 1) });
}

export function formatTemperature(kelvin: number | null): string {
  if (kelvin == null || !Number.isFinite(kelvin)) return "—";
  const celsius = kelvin - 273.15;
  return t("units.temperature", {
    kelvin: fixed(kelvin, 0),
    celsius: fixed(celsius, 0),
  });
}

export function formatGravity(gravity: number | null): string {
  if (gravity == null || !Number.isFinite(gravity)) return "—";
  return t("units.gravity", { value: fixed(gravity, 2) });
}

export function formatRadius(km: number | null): string {
  if (km == null || !Number.isFinite(km)) return "—";
  return t("units.km", {
    value: km.toLocaleString(intlLocale(), { maximumFractionDigits: 0 }),
  });
}

export function formatSigned(
  value: number | null,
  digits = 2,
  unit = ""
): string {
  if (value == null || !Number.isFinite(value)) return "—";
  const text = value.toLocaleString(intlLocale(), {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
  return unit ? `${text} ${unit}` : text;
}

export function earthYearCaption(speed: number, earthYearSeconds = 48): string {
  const seconds = earthYearSeconds / Math.max(Math.abs(speed), 0.001);
  const digits = seconds >= 10 ? 0 : seconds >= 1 ? 1 : 2;
  const body = t("units.earthYear", { seconds: fixed(seconds, digits) });
  return speed < 0 ? `${body} · ${t("units.reverse")}` : body;
}

export function formatSidereal(hours: number): string {
  if (!Number.isFinite(hours) || hours === 0) return "—";
  const sign = hours < 0 ? "−" : "";
  const abs = Math.abs(hours);
  if (abs >= 48) {
    const days = abs / 24;
    return t("units.siderealDays", {
      value: `${sign}${fixed(days, days >= 10 ? 1 : 2)}`,
    });
  }
  return t("units.hours", { value: `${sign}${fixed(abs, 2)}` });
}
