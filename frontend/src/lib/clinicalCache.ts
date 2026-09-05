/** Purge private clinical responses left by older service workers. */
export async function clearLegacyClinicalCaches(): Promise<void> {
  if (typeof caches === "undefined") return;
  const names = await caches.keys();
  await Promise.all(
    names.filter((name) => /^corvia-emergencia(?:-|$)/.test(name))
      .map((name) => caches.delete(name)),
  );
}
