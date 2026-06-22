const MEDIA_CACHE_NAME = 'slides-media'
const API_CACHE_NAME = 'slides-api'

const MAX_AGE = 24 * 60 * 60 * 1000 // 1 day

self.addEventListener('install', () => {
    self.skipWaiting()
})

const cleanupOldCacheEntry = async (cache, request, response) => {
    const now = Date.now()

    const cachedTimeHeader = response.headers.get('x-cached-time')
    if (!cachedTimeHeader) return

    const cachedTime = parseInt(cachedTimeHeader, 10)
    if (isNaN(cachedTime)) return

    const age = now - cachedTime

    if (age > MAX_AGE) {
        await cache.delete(request)
    }
}

const cleanupOldMediaCache = async () => {
    const cache = await caches.open(MEDIA_CACHE_NAME)
    const keys = await cache.keys()

    await Promise.all(
        keys.map(async (request) => {
            const response = await cache.match(request)
            if (!response) return

            return cleanupOldCacheEntry(cache, request, response)
        }),
    )
}

const handleSWActivate = async () => {
    cleanupOldMediaCache()
    // this takes control of all client pages that are already open
    await self.clients.claim()
}

self.addEventListener('activate', (event) => {
    event.waitUntil(handleSWActivate())
})

const getModifiedResponse = (response) => {
    const responseToCache = response.clone()
    const headers = new Headers(responseToCache.headers)
    headers.set('x-cached-time', Date.now().toString())

    return new Response(responseToCache.body, {
        status: responseToCache.status,
        statusText: responseToCache.statusText,
        headers: headers,
    })
}

// Slides-only matchers. `/assets/` (shared SPA bundle) is never matched.
// Media is either the slides-namespaced proxy (non-owner/public viewers) or a
// /private/files/ request tagged with the `slides_media` marker that
// getAttachmentUrl() adds for the owner — so we cache slides' own files without
// ever touching another app's /private/files/ traffic (Drive, Mail, ...).
const isMedia = (url) =>
    url.pathname.startsWith('/api/method/suite.slides.api.file.get_media_file') ||
    (url.pathname.startsWith('/private/files/') && url.searchParams.has('slides_media'))
const isAPI = (url) => url.pathname.startsWith('/api/method/suite.slides.')

const getCacheObject = async (type) => {
    switch (type) {
        case 'media':
            return await caches.open(MEDIA_CACHE_NAME)
        case 'api':
            return await caches.open(API_CACHE_NAME)
        default:
            return null
    }
}

const addCacheEntry = async (type, cache, request, response) => {
    if (type === 'media') {
        const contentType = response.headers.get('Content-Type') || ''
        const validContentTypes = ['image/', 'video/']
        if (!validContentTypes.some((ct) => contentType.startsWith(ct))) return
    }

    // clone response and add cache timestamp header
    const modifiedResponse = getModifiedResponse(response)
    await cache.put(request, modifiedResponse)
}

const fetchAndCache = async (request, type, cache) => {
    const response = await fetch(request)
    if (response.ok && response.status === 200) {
        await addCacheEntry(type, cache, request, response)
    }
    return response
}

const getResponseForRequest = async (request, type) => {
    const cache = await getCacheObject(type)

    if (type === 'api') {
        // network-first: keep API data fresh, fall back to cache only offline
        try {
            await fetchAndCache(request, type, cache)
        } catch {
            const cached = await cache.match(request)
            if (cached) return cached
            throw new Error('No cached response available')
        }
    }

    // media (and the revalidated api response): cache-first
    const cached = await cache.match(request)
    if (cached) return cached
    return await fetchAndCache(request, type, cache)
}

const getRequestType = (url) => {
    if (isMedia(url)) return 'media'
    if (isAPI(url)) return 'api'
    return 'other'
}

const handleSWFetch = async (event) => {
    const request = event.request
    const url = new URL(request.url)

    if (request.method !== 'GET' || url.origin !== self.location.origin) return

    const requestType = getRequestType(url)
    const isAffectedByCache = ['media', 'api'].includes(requestType)
    // Not a slides request -> do nothing, let the browser fetch it normally.
    // This is what keeps the other 6 apps completely unaffected.
    if (!isAffectedByCache) return

    const response = getResponseForRequest(request, requestType)
    event.respondWith(response)
}

self.addEventListener('fetch', (event) => {
    handleSWFetch(event)
})
