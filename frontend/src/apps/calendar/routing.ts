type Params = Record<string, string | string[]>;

export function resolveCalendarRouteTarget(
	name: string | symbol | null | undefined,
	params: Params,
	accountId: string,
) {
	if (!accountId) return { name: "calendar-setup" };

	const defaultRoute = { name: "calendar-month", params: { accountId } };

	switch (name) {
		case "calendar-month-shortcut":
			return { name: "calendar-month", params: { accountId, ...params } };
		case "calendar-week-shortcut":
			return { name: "calendar-week", params: { accountId, ...params } };
		case "calendar-day-shortcut":
			return { name: "calendar-day", params: { accountId, ...params } };
		default:
			return defaultRoute;
	}
}
