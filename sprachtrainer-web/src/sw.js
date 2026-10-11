// Service Worker: App-Shell offline verfügbar. Die Claude-API (anderer Origin) wird nie angefasst.
const VERSION = "__VERSION__";
const FILES = __FILES__;

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (e) => {
  const r = e.request;
  if (r.method !== "GET" || new URL(r.url).origin !== location.origin) return;
  e.respondWith(
    caches.open(VERSION).then(async (c) => {
      const hit = await c.match(r, { ignoreSearch: true });
      const net = fetch(r)
        .then((res) => { if (res.ok) c.put(r, res.clone()); return res; })
        .catch(() => hit || (r.mode === "navigate" ? c.match("./") : Response.error()));
      return hit || net;
    }),
  );
});
