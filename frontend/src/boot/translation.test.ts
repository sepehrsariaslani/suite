import { afterEach, describe, expect, it, vi } from 'vitest'

import { initializeTranslations, translate } from './translation'

describe('translation bootstrap', () => {
  afterEach(() => {
    vi.restoreAllMocks()
    window.translatedMessages = {}
    document.documentElement.lang = ''
    document.documentElement.dir = ''
  })

  it('loads one catalogue and synchronizes document language and direction', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          message: {
            language: 'fa',
            direction: 'rtl',
            messages: { Settings: 'تنظیمات' },
          },
        }),
      }),
    )

    await initializeTranslations()

    expect(fetch).toHaveBeenCalledWith('/api/method/suite.api.get_translations', {
      credentials: 'same-origin',
      headers: { Accept: 'application/json' },
    })
    expect(translate('Settings')).toBe('تنظیمات')
    expect(document.documentElement.lang).toBe('fa')
    expect(document.documentElement.dir).toBe('rtl')
  })

  it('keeps source messages when catalogue loading fails', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')))
    const warning = vi.spyOn(console, 'warn').mockImplementation(() => undefined)

    await expect(initializeTranslations()).resolves.toBeUndefined()

    expect(translate('Settings')).toBe('Settings')
    expect(warning).toHaveBeenCalledOnce()
  })
})
