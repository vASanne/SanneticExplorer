// Utility functions for the Sannetic Explorer frontend

export function formatNumber(num: number): string {
	return new Intl.NumberFormat().format(num);
}

export function formatDistance(km: number): string {
	if (km >= 1000000) {
		return `${(km / 1000000).toFixed(2)}M km`;
	} else if (km >= 1000) {
		return `${(km / 1000).toFixed(2)}k km`;
	}
	return `${km.toFixed(2)} km`;
}

export function formatMass(kg: number): string {
	if (kg >= 1e24) {
		return `${(kg / 1e24).toFixed(2)}×10²⁴ kg`;
	} else if (kg >= 1e21) {
		return `${(kg / 1e21).toFixed(2)}×10²¹ kg`;
	}
	return `${kg.toFixed(2)} kg`;
}

export function debounce<T extends (...args: any[]) => any>(
	func: T,
	wait: number
): (...args: Parameters<T>) => void {
	let timeout: number;
	return (...args: Parameters<T>) => {
		clearTimeout(timeout);
		timeout = setTimeout(() => func(...args), wait);
	};
} 