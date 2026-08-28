import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { describe, expect, it } from 'vitest'

import { FRAPPE_EMAIL_TOOLS } from './frappeEmailTools'

describe('FRAPPE_EMAIL_TOOLS', () => {
	it('links every native Frappe email subsystem from Suite Mail', () => {
		expect(FRAPPE_EMAIL_TOOLS.map(({ key, label, route, icon }) => [key, label, route, icon])).toEqual([
			['accounts', 'Email Accounts', '/desk/email-account', 'user'],
			['communications', 'Communications', '/desk/communication', 'mails'],
			['queue', 'Email Queue', '/desk/email-queue', 'clock'],
			['templates', 'Email Templates', '/desk/email-template', 'scroll-text'],
			['unhandled', 'Unhandled Email', '/desk/unhandled-email', 'mailbox'],
		])
	})

	it('renders the native tools card on the admin overview', () => {
		const overview = readFileSync(
			resolve(import.meta.dirname, 'pages/dashboard/OverviewView.vue'),
			'utf8',
		)
		expect(overview).toContain('<FrappeEmailToolsCard />')
	})
})
