// Service worker ng Lost & Found Log.
// - Navigation (pagbukas ng page): network muna, cache kung offline.
// - Static files (JS, CSS, larawan, font): cache muna, tapos i-update sa background.
// - /api ay HINDI kailanman kine-cache, para laging bago ang data galing sa Django.
const VERSION = 'lf-v3';
const SHELL = ['/', '/index.html', '/manifest.webmanifest', '/logo.png', '/icons/favicon-64.png', '/icons/icon-192.png', '/icons/icon-512.png'];

// Kinukuha rin ang mga JS at CSS ng build (may hash ang pangalan) mula sa index.html,
// para gumana offline kahit sa unang bukas ng app.
async function precache() {
  const cache = await caches.open(VERSION);
  await cache.addAll(SHELL);
  try {
    const html = await (await fetch('/index.html', { cache: 'no-store' })).text();
    const assets = [...html.matchAll(/(?:src|href)="(\/assets\/[^"]+)"/g)].map((m) => m[1]);
    await cache.addAll(assets);
  } catch {
    /* sa dev mode walang /assets, okay lang */
  }
}

self.addEventListener('install', (event) => {
  event.waitUntil(precache().then(() => self.skipWaiting()));
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.pathname.startsWith('/api')) return;

  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const copy = response.clone();
          caches.open(VERSION).then((cache) => cache.put('/index.html', copy));
          return response;
        })
        .catch(() => caches.match('/index.html', { ignoreVary: true })),
    );
    return;
  }

  const sameOrigin = url.origin === self.location.origin;
  const isFont = url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com';
  if (!sameOrigin && !isFont) return;

  event.respondWith(
    caches.match(request, { ignoreVary: true }).then((cached) => {
      const network = fetch(request)
        .then((response) => {
          if (response && (response.ok || response.type === 'opaque')) {
            const copy = response.clone();
            caches.open(VERSION).then((cache) => cache.put(request, copy));
          }
          return response;
        })
        .catch(() => cached || Response.error());
      return cached || network;
    }),
  );
});
