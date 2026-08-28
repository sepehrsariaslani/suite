import { translate as __ } from '@/boot/translation'

export type FrappeEmailTool = {
	key: 'accounts' | 'communications' | 'queue' | 'templates' | 'unhandled'
	label: string
	route: string
	icon: string
}

export const FRAPPE_EMAIL_TOOLS = [
	{ key: 'accounts', label: __('Email Accounts'), route: '/desk/email-account', icon: 'user' },
	{ key: 'communications', label: __('Communications'), route: '/desk/communication', icon: 'mails' },
	{ key: 'queue', label: __('Email Queue'), route: '/desk/email-queue', icon: 'clock' },
	{ key: 'templates', label: __('Email Templates'), route: '/desk/email-template', icon: 'scroll-text' },
	{ key: 'unhandled', label: __('Unhandled Email'), route: '/desk/unhandled-email', icon: 'mailbox' },
] as const satisfies readonly FrappeEmailTool[]
