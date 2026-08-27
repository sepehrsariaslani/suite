import './index.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { spritePlugin } from 'frappe-ui/experimental'

import App from '@/App.vue'
import router from '@/router'
import { configureFrappeUI } from '@/boot/config'
import { initializeTranslations, translationPlugin } from '@/boot/translation'
import { userResource, getSessionUser } from '@/boot/session'
import { initSentry } from '@/boot/sentry'

// One frappe-ui resource/session configuration for the whole suite.
configureFrappeUI()
if (getSessionUser()) {
  userResource.fetch()
}

async function bootstrap() {
  await initializeTranslations()

  const app = createApp(App)
  await initSentry(app, router)

  app.use(createPinia())
  app.use(router)
  app.use(spritePlugin)
  app.use(translationPlugin)

  await router.isReady()
  app.mount('#app')
}

bootstrap()
