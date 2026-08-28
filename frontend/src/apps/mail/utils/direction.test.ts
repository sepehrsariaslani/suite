import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { describe, expect, it } from 'vitest'

import { contentDirection } from './direction'

const mailRoot = resolve(import.meta.dirname, '..')
const readMailSource = (path: string) => readFileSync(resolve(mailRoot, path), 'utf8')

describe('contentDirection', () => {
	it('uses the first strong character for Persian and English content', () => {
		expect(contentDirection('سلام، این یک پیام است')).toBe('rtl')
		expect(contentDirection('Hello, this is a message')).toBe('ltr')
		expect(contentDirection('12345')).toBe('auto')
		expect(contentDirection('123 - سلام')).toBe('rtl')
		expect(contentDirection('123 - Hello')).toBe('ltr')
	})

	it('keeps received and composed message content direction-aware', () => {
		expect(readMailSource('components/PlainTextBody.vue')).toContain('dir="auto"')
		expect(readMailSource('components/ComposeMailEditor.vue')).toContain('dir="auto"')
		expect(readMailSource('components/EmailContent.vue')).toContain(
			'<html dir="${messageDirection}">',
		)
	})

	it('isolates DNS values and uses logical composer spacing in RTL', () => {
		expect(readMailSource('components/DNSRecords.vue')).toContain('class="dir-ltr truncate"')

		const composer = readMailSource('components/ComposeMailEditor.vue')
		expect(composer).toContain('class="me-1 font-medium"')
		expect(composer).toContain('class="ms-auto h-3.5 w-3.5"')
		expect(composer).not.toMatch(/class="m[lr]-/)
	})
})
