import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, writeFile, readFile, rm, utimes, access } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { publishStatic } from "./publish-static.mjs";

const root = fileURLToPath(new URL("../", import.meta.url));
async function fixture(t) {
  const dir = await mkdtemp(path.join(root, ".static-test-"));
  t.after(async () => {
    assert.ok(path.resolve(dir).startsWith(path.resolve(root) + path.sep));
    await rm(dir, { recursive: true, force: true });
  });
  const dist = path.join(dir, "dist"), site = path.join(dir, "site");
  for (const directory of [dist, site]) await mkdir(path.join(directory, "assets"), { recursive: true });
  await writeFile(path.join(site, "index.html"), "old index");
  await writeFile(path.join(site, "assets/old-hash.js"), "old dependency");
  await writeFile(path.join(dist, "assets/new-hash.js"), "new dependency");
  await writeFile(path.join(dist, "index.html"), "new index");
  return { dist, site };
}

test("new index is published last; open clients keep old dependencies", async t => {
  const { dist, site } = await fixture(t);
  const order = [];
  const result = await publishStatic(dist, site, { onPublished: name => order.push(name) });
  assert.equal(order.at(-1), "index.html");
  assert.equal(await readFile(path.join(site, "assets/old-hash.js"), "utf8"), "old dependency");
  assert.equal(await readFile(path.join(site, "assets/new-hash.js"), "utf8"), "new dependency");
  assert.equal(await readFile(path.join(site, "index.html"), "utf8"), "new index");
  assert.equal(result.expiredAssets, 0);
});

test("failed copy leaves the previous index available", async t => {
  const { dist, site } = await fixture(t);
  await mkdir(path.join(site, "assets/new-hash.js"));
  await assert.rejects(publishStatic(dist, site));
  assert.equal(await readFile(path.join(site, "index.html"), "utf8"), "old index");
});

test("reject a changed immutable URL without replacing the live shell", async t => {
  const { dist, site } = await fixture(t);
  await writeFile(path.join(site, "assets/new-hash.js"), "different content");
  await assert.rejects(publishStatic(dist, site), /Immutable asset changed/);
  assert.equal(await readFile(path.join(site, "index.html"), "utf8"), "old index");
});

test("retention starts at retirement even if the previous build lived for months", async t => {
  const { dist, site } = await fixture(t);
  const now = new Date("2026-09-12T15:00:00Z"), old = new Date("2026-07-01T15:00:00Z");
  await writeFile(path.join(site, "assets/new-hash.js"), "new dependency");
  await writeFile(path.join(site, "assets/recent-hash.js"), "recent");
  for (const name of ["old-hash.js", "new-hash.js"]) await utimes(path.join(site, "assets", name), old, old);
  await utimes(path.join(site, "assets/recent-hash.js"), now, now);
  const result = await publishStatic(dist, site, { now });
  assert.equal(result.expiredAssets, 0);
  await access(path.join(site, "assets/old-hash.js"));
  const later = new Date(now.getTime() + 31 * 24 * 60 * 60 * 1000);
  const next = await publishStatic(dist, site, { now: later });
  assert.equal(next.expiredAssets, 2);
  await assert.rejects(access(path.join(site, "assets/old-hash.js")));
  await access(path.join(site, "assets/new-hash.js"));
  await assert.rejects(access(path.join(site, "assets/recent-hash.js")));
});

test("an interrupted index/retention marker pair resets retention conservatively", async t => {
  const { dist, site } = await fixture(t);
  const then = new Date("2026-07-01T15:00:00Z");
  await publishStatic(dist, site, { now: then });
  await writeFile(path.join(site, "index.html"), "shell from an interrupted publication");
  const result = await publishStatic(dist, site, { now: new Date("2026-09-12T15:00:00Z") });
  assert.equal(result.expiredAssets, 0);
  await access(path.join(site, "assets/old-hash.js"));
});

test("missing index never modifies a published site", async t => {
  const { dist, site } = await fixture(t);
  await rm(path.join(dist, "index.html"));
  await assert.rejects(publishStatic(dist, site), /index/);
  assert.equal(await readFile(path.join(site, "index.html"), "utf8"), "old index");
});
