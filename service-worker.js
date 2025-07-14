self.addEventListener('install', e => {
  e.waitUntil(caches.open('claerk').then(c => c.addAll([
    '/claerk.html','/admin.html','/lead_magnet.html','/terms.html','/privacy.html','/logo.svg'
  ])));
});
self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(resp => resp || fetch(e.request))
  );
});
