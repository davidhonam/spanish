/* Service worker: offline app shell + on-demand audio caching.
   Bump VERSION to force clients to refetch the shell after an update. */
const VERSION = 'v1';
const SHELL_CACHE = 'spanish-shell-' + VERSION;
const AUDIO_CACHE = 'spanish-audio-v1';   // audio is immutable; keep across shell updates
const SHELL = [
  './',
  'index.html',
  'manifest.webmanifest',
  'icon-192.png',
  'icon-512.png',
  'apple-touch-icon.png'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(SHELL_CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== SHELL_CACHE && k !== AUDIO_CACHE).map(k => caches.delete(k))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // Audio: cache-first, store on first play so it works offline thereafter.
  if (url.pathname.includes('/audio/') && url.pathname.endsWith('.mp3')) {
    e.respondWith(
      caches.open(AUDIO_CACHE).then(cache =>
        cache.match(req).then(hit => hit || fetch(req).then(res => {
          if (res.ok) cache.put(req, res.clone());
          return res;
        }).catch(() => hit))
      )
    );
    return;
  }

  // Shell / everything else: cache-first, fall back to network, then to cached index.
  e.respondWith(
    caches.match(req).then(hit => hit || fetch(req).catch(() =>
      req.mode === 'navigate' ? caches.match('index.html') : undefined
    ))
  );
});
