import { describe, expect, it } from 'vitest'

import { shouldFetchMeetingPreviewPresence } from './useMeetingPreviewPresence'

describe('shouldFetchMeetingPreviewPresence', () => {
	it('requires both an authenticated session and configured SFU', () => {
		expect(shouldFetchMeetingPreviewPresence(true, true)).toBe(true)
		expect(shouldFetchMeetingPreviewPresence(true, false)).toBe(false)
		expect(shouldFetchMeetingPreviewPresence(false, true)).toBe(false)
	})
})
