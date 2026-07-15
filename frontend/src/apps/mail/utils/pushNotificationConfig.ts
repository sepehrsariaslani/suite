export type WebConfigType = {
	projectId: string;
	appId: string;
	apiKey: string;
	authDomain: string;
	messagingSenderId: string;
};

const REQUIRED_WEB_CONFIG_KEYS = [
	"projectId",
	"appId",
	"apiKey",
	"authDomain",
	"messagingSenderId",
] as const;

export function hasPushRelayServerURL(value: unknown): value is string {
	return typeof value === "string" && value.trim().length > 0;
}

export function isValidWebConfig(value: unknown): value is WebConfigType {
	if (!value || typeof value !== "object") return false;

	return REQUIRED_WEB_CONFIG_KEYS.every((key) => {
		const field = (value as Record<string, unknown>)[key];
		return typeof field === "string" && field.trim().length > 0;
	});
}

export function parseWebConfigParam(raw: string | null): WebConfigType | null {
	if (!raw || raw === "undefined" || raw === "null") return null;

	const candidates = raw.includes("%") ? [decodeURIComponent(raw), raw] : [raw];

	for (const candidate of candidates) {
		try {
			const parsed = JSON.parse(candidate);
			if (isValidWebConfig(parsed)) return parsed;
		} catch {
			// Ignore invalid payloads and keep trying fallbacks.
		}
	}

	return null;
}

export function buildServiceWorkerURL(baseURL: string, config: unknown): string {
	if (!isValidWebConfig(config)) return baseURL;
	return `${baseURL}?config=${encodeURIComponent(JSON.stringify(config))}`;
}

export function isMailServiceWorkerScriptURL(value: string): boolean {
	try {
		const url = new URL(value);
		return url.pathname === "/assets/suite/frontend/sw.js";
	} catch {
		return false;
	}
}

export function isInvalidServiceWorkerScriptURL(value: string): boolean {
	try {
		const url = new URL(value);
		if (!isMailServiceWorkerScriptURL(value)) return false;
		const config = url.searchParams.get("config");
		return config === "undefined" || config === "null";
	} catch {
		return false;
	}
}
