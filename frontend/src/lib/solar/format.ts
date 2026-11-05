const EARTH_MASS_KG = 5.972e24;

export function formatAtmosphere(value: unknown): string | null {
  if (value == null || value === "") return null;
  if (typeof value === "string") return value;
  if (typeof value === "object") {
    const parts = Object.entries(value as Record<string, unknown>)
      .filter(([, entry]) => entry != null && entry !== "")
      .map(([key, entry]) => `${key} ${entry}`);
    return parts.length ? parts.join(" · ") : null;
  }
  return null;
}

export function formatMass(kg: number | null): string {
  if (kg == null || !Number.isFinite(kg) || kg <= 0) return "—";
  const exp = Math.floor(Math.log10(kg));
  const mantissa = kg / 10 ** exp;
  const earth = kg / EARTH_MASS_KG;
  const earthText =
    earth >= 0.01
      ? `${earth.toFixed(earth >= 10 ? 1 : 3)} Earth masses`
      : `${earth.toExponential(2)} Earth masses`;
  return `${mantissa.toFixed(3)} × 10^${exp} kg · ${earthText}`;
}

export function formatDistance(au: number): string {
  if (!Number.isFinite(au)) return "—";
  return `${au.toFixed(au >= 10 ? 2 : 3)} AU`;
}

export function formatPeriod(days: number): string {
  if (!Number.isFinite(days) || days <= 0) return "—";
  const years = days / 365.25;
  if (years >= 1) {
    return `${days.toLocaleString("en-US", {
      maximumFractionDigits: 0,
    })} days · ${years.toFixed(years >= 10 ? 1 : 2)} yr`;
  }
  return `${days.toFixed(1)} days`;
}

export function formatTemperature(kelvin: number | null): string {
  if (kelvin == null || !Number.isFinite(kelvin)) return "—";
  const celsius = kelvin - 273.15;
  return `${kelvin.toFixed(0)} K · ${celsius.toFixed(0)} °C`;
}

export function formatGravity(gravity: number | null): string {
  if (gravity == null || !Number.isFinite(gravity)) return "—";
  return `${gravity.toFixed(2)} m/s²`;
}

export function formatRadius(km: number | null): string {
  if (km == null || !Number.isFinite(km)) return "—";
  return `${km.toLocaleString("en-US", { maximumFractionDigits: 0 })} km`;
}

export function formatSigned(
  value: number | null,
  digits = 2,
  unit = ""
): string {
  if (value == null || !Number.isFinite(value)) return "—";
  const text = value.toFixed(digits);
  return unit ? `${text} ${unit}` : text;
}

export function earthYearCaption(speed: number, earthYearSeconds = 48): string {
  const seconds = earthYearSeconds / Math.max(Math.abs(speed), 0.001);
  const body =
    seconds >= 10
      ? `Earth year ≈ ${seconds.toFixed(0)} s`
      : seconds >= 1
      ? `Earth year ≈ ${seconds.toFixed(1)} s`
      : `Earth year ≈ ${seconds.toFixed(2)} s`;
  return speed < 0 ? `${body} · reverse` : body;
}

export function formatSidereal(hours: number): string {
  if (!Number.isFinite(hours) || hours === 0) return "—";
  const sign = hours < 0 ? "−" : "";
  const abs = Math.abs(hours);
  if (abs >= 48) {
    const days = abs / 24;
    return `${sign}${days.toFixed(days >= 10 ? 1 : 2)} days`;
  }
  return `${sign}${abs.toFixed(2)} h`;
}
