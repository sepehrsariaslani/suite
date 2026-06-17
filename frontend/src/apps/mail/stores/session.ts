import { computed } from 'vue'
import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'

import { getSessionUser, useSessionStore } from '@/boot/session'
import router from '@/apps/mail/router'
import { raiseToast } from '@/apps/mail/utils'
import { userStore } from '@/apps/mail/stores/user'

export const sessionStore = defineStore('mail-session', () => {
	const session = useSessionStore()
	const { userResource, mailboxes } = userStore()

	const login = createResource({
		url: 'login',
		onError: () => {
			throw new Error('Invalid email or password')
		},
		onSuccess: () => {
			userResource.reload()
			session.user = getSessionUser()
			login.reset()

			if (session.user === 'Administrator') window.location.replace('/app')
			else router.replace({ name: 'mail-root-shortcut' })
		},
	})

	const logout = createResource({
		url: 'logout',
		onSuccess() {
			userResource.reset()
			mailboxes.reset()
			session.user = null
			window.location.reload()
		},
	})

	const branding = createResource({
		url: 'suite.mail.api.get_branding',
		cache: 'brand',
		auto: true,
		onSuccess: (data) => (document.querySelector("link[rel='icon']").href = data.favicon),
	})

	// Called when a request fails with an auth/permission error. Returns true if the session
	// is actually gone (so the caller can swallow the error and avoid a duplicate toast),
	// false if the session is still alive — i.e. a genuine PermissionError that should surface
	// normally. Frappe resets the user_id cookie to Guest on a dead session, so the cookie is
	// the discriminator. Signs out + notifies + redirects once; later concurrent calls just
	// report handled.
	const handleSessionExpired = (): boolean => {
		// Still logged in — this is a real permission error, not a logout.
		if (getSessionUser()) return false

		if (session.user) {
			session.user = null
			userResource.reset()
			mailboxes.reset()
			raiseToast(__('You have been signed out. Please sign in again.'), 'error')
			if (router.currentRoute.value.name !== 'mail-login') router.replace({ name: 'mail-login' })
		}

		return true
	}

	return {
		isLoggedIn: computed(() => session.isLoggedIn),
		login,
		logout,
		branding,
		handleSessionExpired,
	}
})
