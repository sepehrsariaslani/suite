import type { App } from 'vue'

interface TranslationResponse {
  language?: string
  direction?: 'ltr' | 'rtl'
  messages?: Record<string, string>
}

/** Translate a Frappe message and replace positional placeholders. */
export function translate(message: string, replace?: Array<string | number>): string {
  const messages = window.translatedMessages || {}
  let translated = messages[message] || message

  if (!/{\d+}/.test(translated) || !Array.isArray(replace)) return translated

  return translated.replace(/{(\d+)}/g, (match: string, index: string) => {
    const value = replace[Number(index)]
    return value !== undefined ? String(value) : match
  })
}

/**
 * Load one translation catalogue before Vue mounts.
 *
 * A single bootstrap request avoids untranslated shell content and prevents
 * route modules from replacing each other's catalogue as apps are lazy-loaded.
 * Failure is deliberately non-fatal: source messages remain usable.
 */
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

    const html = document.documentElement
    html.lang = window.language
    html.dir = window.textDirection
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
