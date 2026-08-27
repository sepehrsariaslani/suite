import type { App } from 'vue'

interface TranslationResponse {
  language?: string
  direction?: 'ltr' | 'rtl'
  messages?: Record<string, string>
}

/**
 * Shared frappe-style translation for the whole suite.
 *
 * The standalone apps (calendar, mail, …) each shipped their own translation
 * plugin that installed a global `__()` onto `app.config.globalProperties` (so
 * bare `__('text')` resolves inside templates) and onto `window.__` (so plain
 * `<script>`/util code can call it too). Since several ported apps use `__()`
 * the same way, the suite registers ONE generic translation plugin here instead
 * of per-app copies.
 *
 * This boot is intentionally endpoint-agnostic: `translate()` only looks up
 * `window.translatedMessages`. WHO populates that map is an app concern — an app
 * route module can fetch its own translations on load (e.g. mail/calendar's
 * `suite.mail.api.get_translations`) and assign the result to `window.translatedMessages`.
 * Until then `translate()` is an identity function, so untranslated UI still
 * renders the source string.
 */
export function translate(message: string, replace?: Array<string | number>): string {
  const messages = window.translatedMessages || {}
  let translated = messages[message] || message

  const hasPlaceholders = /{\d+}/.test(translated) && Array.isArray(replace)
  if (!hasPlaceholders) return translated

  return translated.replace(/{(\d+)}/g, (match: string, index: string) => {
    const value = replace![Number(index)]
    return value !== undefined ? String(value) : match
  })
}

export async function initializeTranslations(): Promise<void> {
  try {
    const response = await fetch('/api/method/suite.api.get_translations', {
      credentials: 'same-origin',
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) return

    const payload = (await response.json()) as { message?: TranslationResponse }
    const data = payload.message
    if (!data) return

    window.translatedMessages = data.messages || {}
    window.language = data.language || 'en'
    window.textDirection = data.direction || 'ltr'

    document.documentElement.lang = window.language
    document.documentElement.dir = window.textDirection
  } catch (error) {
    console.warn('Unable to load translations:', error)
  }
}

export const translationPlugin = {
  install(app: App) {
    app.config.globalProperties.__ = translate
    window.__ = translate
  },
}

export default translationPlugin
