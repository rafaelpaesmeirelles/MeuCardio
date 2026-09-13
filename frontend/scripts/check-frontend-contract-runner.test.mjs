import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, mkdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { discoverFrontendContracts, runFrontendContracts } from './run-frontend-contracts.mjs';

function fixture(t) {
  const directory = mkdtempSync(path.join(tmpdir(), 'corvia-contract-runner-'));
  t.after(() => rmSync(directory, { recursive: true, force: true }));
  return directory;
}

test('new contract files are discovered once; standalone scripts and directories are excluded', t => {
  const directory = fixture(t);
  writeFileSync(path.join(directory, 'b.test.mjs'), '');
  writeFileSync(path.join(directory, 'browser-audit.mjs'), '');
  mkdirSync(path.join(directory, 'nested.test.mjs'));
  assert.deepEqual(discoverFrontendContracts(directory), [path.join(directory, 'b.test.mjs')]);
  writeFileSync(path.join(directory, 'a.test.mjs'), '');
  assert.deepEqual(discoverFrontendContracts(directory), ['a.test.mjs', 'b.test.mjs'].map(name => path.join(directory, name)));
});

test('an empty test directory cannot certify the build', t => {
  assert.throws(() => discoverFrontendContracts(fixture(t)), /No frontend contract tests/);
  assert.throws(() => runFrontendContracts([]), /empty frontend contract run/);
});

test('the runner propagates an actual test failure to its caller', t => {
  const directory = fixture(t);
  const file = path.join(directory, 'fixture.test.mjs');
  writeFileSync(file, "import test from 'node:test'; test('fixture', () => {});\n");
  assert.equal(runFrontendContracts([file], { stdio: 'pipe' }), 0);
  writeFileSync(file, "import test from 'node:test'; test('fixture', () => { throw Error('intentional regression'); });\n");
  assert.notEqual(runFrontendContracts([file], { stdio: 'pipe' }), 0);
});
