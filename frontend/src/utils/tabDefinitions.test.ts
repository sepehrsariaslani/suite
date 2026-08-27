import { describe, expect, it } from 'vitest'

import { indexedTabs } from './tabDefinitions'

describe('indexedTabs', () => {
	it('adds stable numeric values without changing tab metadata', () => {
		const tabs = indexedTabs([{ label: 'Users' }, { label: 'Invites', disabled: true }])

		expect(tabs).toEqual([
			{ label: 'Users', value: 0 },
			{ label: 'Invites', disabled: true, value: 1 },
		])
	})
})
