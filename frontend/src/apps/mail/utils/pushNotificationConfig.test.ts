import { describe, expect, it } from "vitest";

import {
	buildServiceWorkerURL,
	hasPushRelayServerURL,
	isInvalidServiceWorkerScriptURL,
	isMailServiceWorkerScriptURL,
	isValidWebConfig,
	parseWebConfigParam,
} from "./pushNotificationConfig";

describe("pushNotificationConfig", () => {
	const validConfig = {
		projectId: "demo-project",
		appId: "demo-app",
		apiKey: "demo-key",
		authDomain: "demo.firebaseapp.com",
		messagingSenderId: "1234567890",
	};

	it("accepts a complete firebase web config", () => {
		expect(isValidWebConfig(validConfig)).toBe(true);
	});

	it("rejects missing or malformed firebase web configs", () => {
		expect(isValidWebConfig(null)).toBe(false);
		expect(isValidWebConfig({})).toBe(false);
		expect(
			isValidWebConfig({
				...validConfig,
				apiKey: "",
			}),
		).toBe(false);
	});

	it("treats undefined and null query params as absent config", () => {
		expect(parseWebConfigParam(null)).toBeNull();
		expect(parseWebConfigParam("undefined")).toBeNull();
		expect(parseWebConfigParam("null")).toBeNull();
	});

	it("parses a valid encoded config payload", () => {
		const encoded = encodeURIComponent(JSON.stringify(validConfig));
		expect(parseWebConfigParam(encoded)).toEqual(validConfig);
	});

	it("only builds a service worker URL when config is valid", () => {
		expect(buildServiceWorkerURL("/assets/suite/frontend/sw.js", validConfig)).toContain(
			"?config=",
		);
		expect(buildServiceWorkerURL("/assets/suite/frontend/sw.js", undefined)).toBe(
			"/assets/suite/frontend/sw.js",
		);
	});

	it("requires a non-empty relay server URL", () => {
		expect(hasPushRelayServerURL("https://relay.example.com")).toBe(true);
		expect(hasPushRelayServerURL("")).toBe(false);
		expect(hasPushRelayServerURL(undefined)).toBe(false);
	});

	it("detects the mail service worker script URL", () => {
		expect(
			isMailServiceWorkerScriptURL(
				"https://dehati.ir/assets/suite/frontend/sw.js?config=undefined",
			),
		).toBe(true);
		expect(isMailServiceWorkerScriptURL("https://dehati.ir/assets/other/sw.js")).toBe(
			false,
		);
	});

	it("detects stale invalid service worker registrations", () => {
		expect(
			isInvalidServiceWorkerScriptURL(
				"https://dehati.ir/assets/suite/frontend/sw.js?config=undefined",
			),
		).toBe(true);
		expect(
			isInvalidServiceWorkerScriptURL(
				"https://dehati.ir/assets/suite/frontend/sw.js?config=null",
			),
		).toBe(true);
		expect(
			isInvalidServiceWorkerScriptURL(
				"https://dehati.ir/assets/suite/frontend/sw.js?config=%7B%22projectId%22%3A%22x%22%7D",
			),
		).toBe(false);
	});
});
