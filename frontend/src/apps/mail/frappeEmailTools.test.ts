import { describe, expect, it } from 'vitest'

import { FRAPPE_EMAIL_TOOLS } from './frappeEmailTools'

describe('FRAPPE_EMAIL_TOOLS', () => {
	it('links every native Frappe email subsystem from Suite Mail', () => {
		expect(FRAPPE_EMAIL_TOOLS).toEqual({
			accounts: '/desk/email-account',
			communications: '/desk/communication',
			queue: '/desk/email-queue',
			templates: '/desk/email-template',
			unhandled: '/desk/unhandled-email',
		})
	})
})
