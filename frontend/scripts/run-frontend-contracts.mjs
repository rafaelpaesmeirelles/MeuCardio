import { readdirSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const scriptsDirectory = fileURLToPath(new URL('./', import.meta.url));

// Only Node test files belong here. Standalone browser/visual/audit scripts
// retain their own entry points and must never be executed by discovery.
export function discoverFrontendContracts(directory = scriptsDirectory) {
  const files = readdirSync(directory, { withFileTypes: true })
    .filter(entry => entry.isFile() && entry.name.endsWith('.test.mjs'))
    .map(entry => path.join(directory, entry.name)).sort();
  if (!files.length) throw new Error('No frontend contract tests were discovered.');
  return files;
}

export function runFrontendContracts(files, { stdio = 'inherit' } = {}) {
  if (!files.length) throw new Error('Refusing an empty frontend contract run.');
  // This is an independent CLI run, including when the runner itself is
  // exercised from node:test. Its worker protocol must not leak into children.
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  const result = spawnSync(process.execPath, ['--test', '--test-concurrency=4', ...files], { stdio, env });
  if (result.error) throw result.error;
  return result.status ?? 1;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const files = discoverFrontendContracts();
  if (process.argv.slice(2).length) {
    if (process.argv.length !== 3 || process.argv[2] !== '--list') throw new Error('Supported argument: --list');
    for (const file of files) console.log(path.basename(file));
  } else {
    console.log(`Frontend contracts: ${files.length} test files (automatic discovery).`);
    process.exitCode = runFrontendContracts(files);
  }
}
