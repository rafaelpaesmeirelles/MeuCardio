import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const read = (path) => readFileSync(new URL(path, import.meta.url), 'utf8');
const canvas = read('../src/components/MiniUniverseCanvas.tsx');
const toggle = read('../src/components/GalaxyThemeToggle.tsx');
const home = read('../src/pages/CardiologySpacesHome.tsx');
const css = read('../src/styles/corvia-internal-final-approved-20260904.css');
test('a escolha informa explicitamente seu contexto ao miniuniverso', () => {
  assert.match(home, /className="spaces-choice__theme-toggle" context="choice"/);
});
test('somente a escolha escura muda para sentido horario', () => {
  assert.match(toggle, /context === "choice" && theme === "dark" \? "clockwise" : "counterclockwise"/);
  assert.match(toggle, /context = "internal"/);
});
test('o canvas aplica a direcao e preserva o ciclo lento de 120 segundos', () => {
  assert.match(canvas, /direction === "clockwise" \? 1 : -1/);
  assert.match(canvas, /rotationSign \* \(\(\(now - startedAt\)/);
  assert.match(canvas, /durationMs = 120_000/);
  assert.match(canvas, /\}, \[direction\]\)/);
});
test('a escolha mobile nao reserva mais 138px vazios antes do conteudo', () => {
  assert.doesNotMatch(css, /padding-top:\s*138px/);
  assert.match(css, /\.spaces-choice__content \{[^}]*padding-top: 24px !important/);
});
