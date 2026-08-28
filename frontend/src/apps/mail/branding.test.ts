import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { describe, expect, it } from 'vitest'

const frontendRoot = resolve(import.meta.dirname, '../../..')
const suiteRoot = resolve(frontendRoot, '..')

const readFrontend = (path: string) => readFileSync(resolve(frontendRoot, path), 'utf8')
const readSuite = (path: string) => readFileSync(resolve(suiteRoot, path), 'utf8')

describe('Payam Yar visible branding', () => {
	it('identifies the installable Mail app as Payam Yar', () => {
		const manifest = JSON.parse(readFrontend('public/pwa/mail/manifest.webmanifest'))

		expect(manifest.name).toBe('Payam Yar')
		expect(manifest.short_name).toBe('Payam Yar')
	})

	it('does not expose the former product name on scoped Mail surfaces', () => {
		const visibleSurfaces = [
			readFrontend('src/apps/mail/components/LoginLayout.vue'),
			readFrontend('src/apps/mail/components/InstallPrompt.vue'),
			readSuite('suite/templates/emails/base.html'),
			readSuite('suite/templates/emails/_event_base.html'),
			readSuite('suite/templates/emails/drive_invitation.html'),
			readSuite('suite/templates/emails/drive_share.html'),
		]

		for (const source of visibleSurfaces) {
			expect(source).not.toContain('Frappe Mail')
		}
	})
})
