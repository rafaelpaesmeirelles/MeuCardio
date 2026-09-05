/* Remove only legacy clinical-response caches, never the static app shell. */
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((names) => Promise.all(
      names.filter((name) => /^corvia-emergencia(?:-|$)/.test(name))
        .map((name) => caches.delete(name))
    ))
  );
});
