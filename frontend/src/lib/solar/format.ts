const EARTH_MASS_KG = 5.972e24;

export function formatAtmosphere(value: unknown): string | null {
	if (value == null || value === '') return null;
	if (typeof value === 'string') return value;
	if (typeof value === 'object') {
		const parts = Object.entries(value as Record<string, unknown>)
			.filter(([, entry]) => entry != null && entry !== '')
			.map(([key, entry]) => `${key} ${entry}`);
		return parts.length ? parts.join(' · ') : null;
	}
	return null;
}

export function formatMass(kg: number | null): string {
	if (kg == null || !Number.isFinite(kg) || kg <= 0) return '—';
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
	if (!Number.isFinite(au)) return '—';
	return `${au.toFixed(au >= 10 ? 2 : 3)} AU`;
}

export function formatPeriod(days: number): string {
	if (!Number.isFinite(days) || days <= 0) return '—';
	const years = days / 365.25;
	if (years >= 1) {
		return `${days.toLocaleString('en-US', { maximumFractionDigits: 0 })} days · ${years.toFixed(years >= 10 ? 1 : 2)} yr`;
	}
	return `${days.toFixed(1)} days`;
}

export function formatTemperature(kelvin: number | null): string {
	if (kelvin == null || !Number.isFinite(kelvin)) return '—';
	const celsius = kelvin - 273.15;
	return `${kelvin.toFixed(0)} K · ${celsius.toFixed(0)} °C`;
}

export function formatGravity(gravity: number | null): string {
	if (gravity == null || !Number.isFinite(gravity)) return '—';
	return `${gravity.toFixed(2)} m/s²`;
}

export function formatRadius(km: number | null): string {
	if (km == null || !Number.isFinite(km)) return '—';
	return `${km.toLocaleString('en-US', { maximumFractionDigits: 0 })} km`;
}

export function formatSigned(value: number | null, digits = 2, unit = ''): string {
	if (value == null || !Number.isFinite(value)) return '—';
	const text = value.toFixed(digits);
	return unit ? `${text} ${unit}` : text;
}

export function earthYearCaption(speed: number, earthYearSeconds = 48): string {
	const seconds = earthYearSeconds / Math.max(speed, 0.001);
	if (seconds >= 10) return `Earth year ≈ ${seconds.toFixed(0)} s`;
	if (seconds >= 1) return `Earth year ≈ ${seconds.toFixed(1)} s`;
	return `Earth year ≈ ${seconds.toFixed(2)} s`;
}
