export const indexedTabs = <T extends Record<string, unknown>>(tabs: readonly T[]) =>
	tabs.map((tab, value) => ({ ...tab, value }))
