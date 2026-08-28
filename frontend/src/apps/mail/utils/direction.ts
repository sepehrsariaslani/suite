const RTL_CHARACTER = /[\u0590-\u08ff]/
const LTR_CHARACTER = /[A-Za-z]/

/** Resolve mixed content from its first strong Persian/Latin character. */
export function contentDirection(value: string): 'rtl' | 'ltr' | 'auto' {
	const rtl = value.search(RTL_CHARACTER)
	const ltr = value.search(LTR_CHARACTER)
	if (rtl < 0 && ltr < 0) return 'auto'
	if (rtl < 0) return 'ltr'
	if (ltr < 0) return 'rtl'
	return rtl < ltr ? 'rtl' : 'ltr'
}
