// Offline copy of the page: the page itself is fetched fresh when online (cached for offline), everything else
// (screenshots, logos, fonts, icon CSS) comes from the cache once it has been seen, and is refreshed when online.
const CACHE = "bomberman-v1";
const CORE = ["./", "index.html", "manifest.webmanifest", "docs/img/icon-192.png"];

self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE))); self.skipWaiting(); });
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener("fetch", e => {
  const r = e.request;
  if (r.method !== "GET" || r.url.includes("googletagmanager")) return;
  const put = res => { if (res.ok || res.type === "opaque") { const copy = res.clone(); caches.open(CACHE).then(c => c.put(r, copy)); } return res; };
  if (r.mode === "navigate") {   // the page: network first, so updates show up; the cached copy when offline
    e.respondWith(fetch(r).then(put).catch(() => caches.match(r).then(m => m || caches.match("index.html"))));
    return;
  }
  // everything else: the cached copy at once, refreshed in the background for next time; the refresh asks the server
  // (no-cache), so a changed image isn't answered again from the browser's own HTTP cache
  e.respondWith(caches.match(r).then(m => { const net = fetch(r, { cache: "no-cache" }).then(put).catch(() => m); return m || net; }));
});
