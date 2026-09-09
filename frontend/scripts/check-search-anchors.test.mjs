import { test } from 'node:test';
import assert from 'node:assert/strict';
import { exactSearchAnchors } from '../src/lib/searchAnchors.ts';

test('lexical hits cannot expand unrelated second-hop neighbours', () => {
  const hits = [
    { title: 'Holter 24h', slug: 'holter-24h' },
    { title: 'Investigação de síncope: Holter e tilt', slug: 'sincope-investigacao' },
    { title: 'Fibrilação atrial em usuários de antineoplásicos', slug: 'fa-oncologia' },
  ];
  assert.deepEqual(exactSearchAnchors(hits, 'holter 24h'), [hits[0]]);
  assert.deepEqual(exactSearchAnchors(hits, 'sincope'), []);
  assert.deepEqual(exactSearchAnchors(hits, 'FA'), []);
});

test('identity normalization preserves accents, punctuation and exact titles', () => {
  const hits = [{title: 'Fibrilação atrial', slug: 'fibrilacao-atrial'}];
  assert.deepEqual(exactSearchAnchors(hits, '  FIBRILACAO-ATRIAL  '), hits);
  assert.deepEqual(exactSearchAnchors(hits, ''), []);
});


test('subscript score names preserve exact numeric identity', () => {
  const hits = [{ title: 'CHA₂DS₂-VASc', slug: 'cha2ds2-vasc' }];
  assert.deepEqual(exactSearchAnchors(hits, 'CHA2DS2-VASc'), hits);
  assert.deepEqual(exactSearchAnchors(hits, 'CHA₂DS₂-VASc'), hits);
  assert.deepEqual(exactSearchAnchors(hits, 'CHADS-VASc'), []);
});
