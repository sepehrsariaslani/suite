import { initializeApp } from 'firebase/app'
import { getMessaging, onBackgroundMessage } from 'firebase/messaging/sw'
import { parseWebConfigParam } from '@/apps/mail/utils/pushNotificationConfig'

// Firebase Cloud Messaging service worker. Bundled to `sw.js` by vite-plugin-pwa
// (injectManifest) and emitted at /assets/suite/frontend/sw.js, where
// MailLayout.registerServiceWorker() registers it with `?config=<fcm-web-config>`.
//
// No workbox precaching on purpose: the suite is a shared 7-app SPA and we
// only want FCM background notifications here, not a precaching PWA.

declare const self: ServiceWorkerGlobalScope

export function getFirebaseWebConfigFromLocation(href: string) {
	return parseWebConfigParam(new URL(href).searchParams.get('config'))
}

const firebaseConfig = getFirebaseWebConfigFromLocation(location.href)

// Firebase config initialization
try {
	if (!firebaseConfig) throw new Error('Push notification config is missing')

	const firebaseApp = initializeApp(firebaseConfig)
	const messaging = getMessaging(firebaseApp)

	const isChrome = () => navigator.userAgent.toLowerCase().includes('chrome')

	onBackgroundMessage(messaging, (payload: import('firebase/messaging').MessagePayload) => {
		const notificationTitle = payload.data?.title ?? ''
		const notificationOptions: NotificationOptions = { body: payload.data?.body || '' }
		if (payload.data?.notification_icon)
			notificationOptions.icon = payload.data.notification_icon

		if (isChrome()) notificationOptions.data = { url: payload.data?.click_action }
		else if (payload.data?.click_action)
			notificationOptions.actions = [
				{ action: payload.data.click_action, title: 'مشاهده جزئیات' },
			]

		self.registration.showNotification(notificationTitle, notificationOptions)
	})

	if (isChrome()) {
		self.addEventListener('notificationclick', (event: NotificationEvent) => {
			event.stopImmediatePropagation()
			event.notification.close()
			if (event.notification.data && (event.notification.data as { url?: string }).url)
				clients.openWindow((event.notification.data as { url: string }).url)
		})
	}
} catch (error) {
	console.log('Failed to initialize Firebase:', error)
}

self.addEventListener('install', (event: ExtendableEvent) => {
	event.waitUntil(self.skipWaiting())
})

self.addEventListener('activate', (event: ExtendableEvent) => {
	event.waitUntil(self.clients.claim())
})
console.log('Service Worker Initialized')
