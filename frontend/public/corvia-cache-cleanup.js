/* Imported by Workbox. Never cache authenticated clinical API responses. */
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((names) => Promise.all(
      names
        .filter((name) => /^corvia-emergencia(?:-|$)/.test(name))
        .map((name) => caches.delete(name)),
    )),
  );
});
