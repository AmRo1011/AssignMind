// AssignMind Service Worker — v3
// Network-only for all navigation; strictly never caches non-200 responses.
const CACHE_NAME = "assignmind-v3";

// ─── Install ────────────────────────────────────────────────────────────────
// Skip waiting so the new SW activates immediately without waiting for all
// tabs using the old SW to be closed.
self.addEventListener("install", () => {
    self.skipWaiting();
});

// ─── Activate ───────────────────────────────────────────────────────────────
// Delete ALL caches from previous versions so stale/404 entries are evicted.
self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches
            .keys()
            .then((keys) => Promise.all(keys.map((key) => caches.delete(key))))
            .then(() => self.clients.claim())
    );
});

// ─── Fetch ──────────────────────────────────────────────────────────────────
// Navigation requests (HTML pages): always go to the network.
// Non-navigation requests (JS, CSS, images): network-first, cache fallback,
// but ONLY cache responses with ok=true (status 200–299).
self.addEventListener("fetch", (event) => {
    // Let the browser handle non-GET requests normally (POST, etc.)
    if (event.request.method !== "GET") return;

    if (event.request.mode === "navigate") {
        // SPA: always fetch from network; no caching of HTML responses.
        // On network failure, do nothing — Cloudflare _redirects already
        // handles SPA routing, so a hard offline state is expected.
        event.respondWith(fetch(event.request));
        return;
    }

    // For other requests: network-first, fallback to cache
    event.respondWith(
        fetch(event.request)
            .then((response) => {
                // Strictly ONLY cache successful GET responses (status 200)
                if (!response || response.status !== 200) {
                    return response;
                }

                const clone = response.clone();
                caches
                    .open(CACHE_NAME)
                    .then((cache) => cache.put(event.request, clone));
                return response;
            })
            .catch(() => caches.match(event.request))
    );
});
