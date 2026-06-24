import { createStore } from 'vuex'
import { call } from 'frappe-ui'
import { clear } from 'idb-keyval'

let getCookies = () => {
  return Object.fromEntries(
    document.cookie
      .split('; ')
      .map((cookie) => cookie.split('='))
      .map((entry) => [entry[0], decodeURIComponent(entry[1])])
  )
}
const { user_id, system_user, full_name, user_image } = getCookies()

const store = createStore({
  state: {
    user: {
      id: user_id,
      systemUser: system_user === 'yes',
      fullName: full_name,
      imageURL: user_image,
    },
    uploads: [],
    activeEntity: null,
  },
  getters: {
    isLoggedIn: (state) => {
      return state.user.id && state.user.id !== 'Guest'
    },
    uploadsInProgress: (state) => state.uploads.filter((u) => !u.completed && !u.completed),
    uploadsCompleted: (state) => state.uploads.filter((u) => u.completed && !u.error),
    uploadsFailed: (state) => state.uploads.filter((u) => u.error),
  },
  mutations: {
    addUpload(state, payload) {
      state.uploads.push(payload)
    },
    updateUpload(state, payload) {
      const idx = state.uploads.findIndex((u) => u.uuid === payload.uuid)
      if (idx > -1) {
        state.uploads[idx] = { ...state.uploads[idx], ...payload }
      }
    },
    clearUploads(state) {
      state.uploads = []
    },
    removeUpload(state, uuid) {
      state.uploads = state.uploads.filter((u) => u.uuid !== uuid)
    },
    setActiveEntity(state, payload) {
      state.activeEntity = payload
    },
  },
  actions: {
    async logout() {
      await call('logout')
      clear()
      window.location.reload()
    },
  },
})

export default store
