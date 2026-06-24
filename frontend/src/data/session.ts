import { computed, reactive, ref } from 'vue'
import { call } from 'frappe-ui'
import { clear } from 'idb-keyval'

function getCookies() {
  return Object.fromEntries(
    document.cookie
      .split('; ')
      .map((cookie) => cookie.split('='))
      .map((entry) => [entry[0], decodeURIComponent(entry[1])]),
  )
}

function getSessionUserFromCookie(): string | null {
  const { user_id } = getCookies()
  if (!user_id || user_id === 'Guest') return null
  return user_id
}

const cookies = getCookies()

/** Cookie-derived session user id. Updated on login/logout. */
export const sessionUser = ref<string | null>(getSessionUserFromCookie())

export const fullName = ref(cookies.full_name || '')
export const imageURL = ref(cookies.user_image || '')
export const systemUser = ref(cookies.system_user === 'yes')

/**
 * Shared suite session — gameplan-style module singleton (no Vuex/Pinia).
 *
 * Drive and Writer read `session.user` for the legacy `{ id, fullName, ... }` shape.
 */
export const session = reactive({
  user: computed(() => ({
    id: sessionUser.value,
    systemUser: systemUser.value,
    fullName: fullName.value,
    imageURL: imageURL.value,
  })),
  isLoggedIn: computed(() => !!sessionUser.value),
  async logout() {
    await call('logout')
    clear()
    window.location.reload()
  },
})

export function isSessionUser(user: string) {
  return sessionUser.value === user
}

export function useSession() {
  return session
}
