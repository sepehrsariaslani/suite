/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<Record<string, unknown>, Record<string, unknown>, unknown>
  export default component
}

declare global {
  interface Window {
    csrf_token?: string
    site_name?: string
    socketio_port?: string | number
    sfu_enabled?: boolean
    /** Frappe translation map (message -> translated), loaded at SPA bootstrap. */
    translatedMessages?: Record<string, string>
    /** Active Frappe language and writing direction. */
    language?: string
    textDirection?: 'ltr' | 'rtl'
    /** Global translate helper installed by the suite translation plugin. */
    __?: (message: string, replace?: Array<string | number>) => string
  }

  /** Bare `__('text')` available in templates via globalProperties. */
  const __: (message: string, replace?: Array<string | number>) => string

  /** Injected by Vite from sites/common_site_config.json. */
  const __SITE_NAME__: string

  /** Injected by Vite from sites/common_site_config.json. */
  const __SOCKETIO_PORT__: string | number
}

export {}
