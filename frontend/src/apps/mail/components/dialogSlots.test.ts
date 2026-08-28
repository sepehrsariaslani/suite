import { describe, expect, it } from 'vitest'

const components = import.meta.glob(['./**/*.vue', '../pages/**/*.vue'], {
	query: '?raw',
	import: 'default',
	eager: true,
}) as Record<string, string>

describe('Mail dialog content slots', () => {
	it('does not wrap default dialog content in an inert template element', () => {
		const offenders = Object.entries(components)
			.filter(([, source]) => /<Dialog\b[^>]*>\s*<template\s*>/.test(source))
			.map(([path]) => path)

		expect(offenders).toEqual([])
	})
})
