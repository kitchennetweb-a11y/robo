// Offline: precache the core, then cache everything else (three.js CDN, faces, sounds, audio) as it is first used.
// Bump V after changing any file so iPads pick up the new version.
const V = 'robo-v2';
const CORE = ['./', 'index.html', 'game.js', 'phrases.json', 'robo.glb', 'manifest.json', 'icon.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(V).then(c => c.addAll(CORE))); self.skipWaiting(); });
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k))))));
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(res => {
    if (res.ok) { const copy = res.clone(); caches.open(V).then(c => c.put(e.request, copy)); }
    return res;
  })));
});
