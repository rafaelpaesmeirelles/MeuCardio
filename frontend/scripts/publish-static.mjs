import { copyFile, mkdir, readdir, readFile, rename, unlink, utimes, writeFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import path from "node:path";
import { pathToFileURL } from "node:url";

const RETENTION_MS = 30 * 24 * 60 * 60 * 1000;
const RETENTION_FILE = ".corvia-static-retention.json";
const digest = value => createHash("sha256").update(value).digest("hex");

async function filesUnder(directory, prefix = "") {
  const files = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const relative = path.join(prefix, entry.name);
    if (entry.isSymbolicLink()) throw new Error(`Symlink not allowed in static build: ${relative}`);
    if (entry.isDirectory()) files.push(...await filesUnder(path.join(directory, entry.name), relative));
    else if (entry.isFile()) files.push(relative);
  }
  return files;
}

/** Keep the old shell usable while its replacement and every dependency are copied. */
export async function publishStatic(dist, site, { now = new Date(), onPublished = () => {} } = {}) {
  dist = path.resolve(dist);
  site = path.resolve(site);
  if (dist === site || site.startsWith(dist + path.sep) || dist.startsWith(site + path.sep)) {
    throw new Error("Build and published directory must be separate");
  }
  const files = await filesUnder(dist);
  if (!files.includes("index.html") || !(await readFile(path.join(dist, "index.html"), "utf8")).trim()) {
    throw new Error("Build has no valid index.html");
  }
  await mkdir(site, { recursive: true });
  const previousIndex = await readFile(path.join(site, "index.html")).catch(error => { if (error.code === "ENOENT") return null; throw error; });
  const previousState = await readFile(path.join(site, RETENTION_FILE), "utf8")
    .then(value => { try { return JSON.parse(value); } catch { return null; } })
    .catch(error => { if (error.code === "ENOENT") return null; throw error; });
  // After an interrupted publication or the first migration, keep all prior
  // assets for a fresh retention period rather than guessing from file age.
  const previousRetired = previousIndex && previousState?.indexHash === digest(previousIndex)
    ? previousState.retiredAt || {} : {};
  const isAsset = relative => relative.startsWith("assets" + path.sep);
  const order = files.filter(isAsset).concat(files.filter(f => !isAsset(f) && f !== "index.html"), "index.html");
  for (const relative of order) {
    const source = path.join(dist, relative);
    const target = path.join(site, relative);
    await mkdir(path.dirname(target), { recursive: true });
    if (isAsset(relative)) {
      const previous = await readFile(target).catch(error => { if (error.code === "ENOENT") return null; throw error; });
      if (previous) {
        if (!previous.equals(await readFile(source))) throw new Error(`Immutable asset changed: ${relative}`);
        await utimes(target, now, now);
        onPublished(relative);
        continue;
      }
    }
    const temporary = `${target}.publishing-${process.pid}`;
    try {
      await copyFile(source, temporary);
      await rename(temporary, target);
      if (isAsset(relative)) await utimes(target, now, now);
    } finally {
      await unlink(temporary).catch(error => { if (error.code !== "ENOENT") throw error; });
    }
    onPublished(relative);
  }
  // Retention starts when a dependency leaves the live build, not when its
  // file was first copied (the preceding release may have lived for months).
  const assetsRoot = path.join(site, "assets");
  const current = new Set(files.filter(isAsset));
  const oldAssets = await filesUnder(assetsRoot).catch(error => { if (error.code === "ENOENT") return []; throw error; });
  const retiredAt = {};
  const expired = [];
  for (const relative of oldAssets) {
    if (current.has(path.join("assets", relative))) continue;
    const recorded = previousRetired[relative];
    retiredAt[relative] = typeof recorded === "number" && Number.isFinite(recorded) ? recorded : now.getTime();
    if (retiredAt[relative] < now.getTime() - RETENTION_MS) expired.push(relative);
  }
  const marker = path.join(site, RETENTION_FILE);
  const markerTemp = `${marker}.publishing-${process.pid}`;
  try {
    await writeFile(markerTemp, JSON.stringify({ indexHash: digest(await readFile(path.join(site, "index.html"))), retiredAt }));
    await rename(markerTemp, marker);
  } finally {
    await unlink(markerTemp).catch(error => { if (error.code !== "ENOENT") throw error; });
  }
  let removed = 0;
  for (const relative of expired) {
    await unlink(path.join(assetsRoot, relative));
    removed++;
  }
  return { published: order.length, expiredAssets: removed, retentionDays: 30 };
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  const result = await publishStatic(process.argv[2] || "/dist", process.argv[3] || "/site");
  console.log(JSON.stringify(result));
}
