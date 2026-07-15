import { describe, expect, it } from "vitest";

import { resolveCalendarRouteTarget } from "./routing";

describe("calendar routing", () => {
	it("redirects shortcut routes to setup when no account exists", () => {
		expect(resolveCalendarRouteTarget("calendar-root-shortcut", {}, "")).toEqual({
			name: "calendar-setup",
		});
	});

	it("redirects shortcut routes to the scoped month view when an account exists", () => {
		expect(
			resolveCalendarRouteTarget(
				"calendar-week-shortcut",
				{ year: "2026", month: "7", day: "15" },
				"acc-1",
			),
		).toEqual({
			name: "calendar-week",
			params: { accountId: "acc-1", year: "2026", month: "7", day: "15" },
		});
	});
});
