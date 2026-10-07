// Offline support: network first (so updates always arrive), cache as the fallback when there is no connection.
// Everything the app fetches while online (three.js, robo.glb, faces, sounds, phrases) is stored as it is used.
const C = 'robo';
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(
  caches.keys().then(ks => Promise.all(ks.filter(k => k !== C).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(fetch(e.request).then(res => {  // GitHub Pages' own 10-min HTTP cache still applies
    if (res.ok) { const copy = res.clone(); caches.open(C).then(c => c.put(e.request, copy)); }
    return res;
  }).catch(() => caches.match(e.request)));
});
