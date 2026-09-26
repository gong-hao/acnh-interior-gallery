// ACNH Interior Gallery Service Worker (Cache Storage)
const CACHE_NAME = 'acnh-gallery-v2';
const STATIC_ASSETS = [
    './index.html',
    './wallpapers.html',
    './floors.html',
    './rugs.html'
];

self.addEventListener('install', (event) => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(STATIC_ASSETS).catch((err) => {
                console.warn('Initial static asset cache partial fail:', err);
            });
        })
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.map((key) => {
                    if (key !== CACHE_NAME) {
                        return caches.delete(key);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (event) => {
    const req = event.request;
    if (req.method !== 'GET') return;

    const url = new URL(req.url);

    // Image assets: Cache-First strategy (Instant 0ms retrieval, cache on miss)
    if (req.destination === 'image' || url.pathname.match(/\.(webp|jpg|jpeg|png|gif|svg)$/i) || url.pathname.includes('/images/')) {
        event.respondWith(
            caches.open(CACHE_NAME).then((cache) => {
                return cache.match(req).then((cachedResponse) => {
                    if (cachedResponse) {
                        return cachedResponse;
                    }
                    return fetch(req).then((networkResponse) => {
                        if (networkResponse && networkResponse.status === 200) {
                            cache.put(req, networkResponse.clone());
                        }
                        return networkResponse;
                    }).catch(() => {
                        return cachedResponse || Response.error();
                    });
                });
            })
        );
        return;
    }

    // HTML / JS / Other: Stale-While-Revalidate / Network-First
    event.respondWith(
        fetch(req).then((networkResponse) => {
            if (networkResponse && networkResponse.status === 200) {
                const responseClone = networkResponse.clone();
                caches.open(CACHE_NAME).then((cache) => {
                    cache.put(req, responseClone);
                });
            }
            return networkResponse;
        }).catch(() => {
            return caches.match(req);
        })
    );
});
