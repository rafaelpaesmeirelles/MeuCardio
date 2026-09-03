import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const read = (path) => readFileSync(new URL(`../${path}`, import.meta.url), "utf8");
const entrar = read("src/pages/Entrar.tsx");
const styles = read("src/styles/cardiology-spaces-login.css");
const publicStart = styles.indexOf("Gateway público — primeira impressão");
const publicStyles = styles.slice(publicStart);

test("gateway pré-login oferece somente claro e escuro", () => {
  assert.ok(publicStart >= 0, "a composição pública compartilhada precisa estar isolada");
  assert.deepEqual(
    [...entrar.matchAll(/id: "(light|dark)"/g)].map((match) => match[1]),
    ["light", "dark"],
  );
  assert.doesNotMatch(entrar, /id: "(?:complete|essential|scientific)"/);
});

test("tema é preferência visual e a escolha de experiência ocorre após autenticar", () => {
  assert.match(entrar, /sessionStorage\.setItem\(CORVIA_LOGIN_THEME_KEY, temaPublico\)/);
  assert.match(entrar, /sessionStorage\.removeItem\("corvia:cardiology-spaces:mode"\)/);
  assert.doesNotMatch(entrar, /plano\s*=|permiss(?:ao|ão)\s*=|autoriz(?:acao|ação)\s*=/i);
  assert.match(entrar, /Seu acesso e suas permissões não mudam/);
});

test("seletor mantém semântica nativa, teclado e estado anunciado", () => {
  assert.match(entrar, /<fieldset className="login-gateway__theme-choice" aria-describedby="login-theme-note">/);
  assert.match(entrar, /<legend>Escolha a aparência<\/legend>/);
  assert.match(entrar, /type="radio"\s*name="tema-publico"/s);
  assert.match(entrar, /checked=\{temaPublico === opcao\.id\}/);
  assert.match(entrar, /onChange=\{\(\) => selecionarTemaPublico\(opcao\.id\)\}/);
  assert.match(publicStyles, /label:has\(input:focus-visible\)/);
  assert.match(publicStyles, /\.login-gateway__theme-choice-options label\s*\{[^}]*min-height:\s*94px;/s);
  assert.match(publicStyles, /@media \(max-width: 560px\)[\s\S]*?\.login-gateway--public \.login-gateway__theme-choice-options label\s*\{[^}]*min-height:\s*64px;/);
});

test("as duas aparências preservam o mesmo login, links e garantias", () => {
  assert.match(entrar, /login-gateway--\$\{temaPublico\}/);
  assert.equal((entrar.match(/<form className="login-gateway__form"/g) || []).length, 1);
  assert.match(entrar, /id="email"[\s\S]*?autoComplete="username"/);
  assert.match(entrar, /id="senha"[\s\S]*?autoComplete="current-password"/);
  assert.match(entrar, /to="\/esqueci-senha"/);
  assert.match(entrar, /to="\/solicitar-acesso"/);
  assert.match(entrar, /to="\/privacidade"/);
  assert.match(entrar, /to="\/termos"/);
  assert.match(entrar, /Ambiente protegido/);
  assert.match(entrar, /Acesso profissional · LGPD/);
});

test("claro e escuro compartilham a geometria e mudam somente a cromia", () => {
  assert.match(publicStyles, /\.login-gateway--public\s*\{/);
  assert.match(publicStyles, /\.login-gateway--dark\s*\{/);
  const darkStyles = publicStyles.slice(publicStyles.indexOf(".login-gateway--dark"));
  assert.doesNotMatch(darkStyles, /^\s*(?:width|height|min-height|max-width|grid-template(?:-columns|-rows)?|padding|margin|inset|top|right|bottom|left)\s*:/gm,
    "a variante escura não pode alterar geometria, fluxo ou alvos");
  assert.doesNotMatch(`${entrar}\n${publicStyles}`, /telesc[oó]pio|observat[oó]rio|montanha|planeta|lua cheia/i);
  assert.match(publicStyles, /@media \(max-width: 900px\)/);
  assert.match(publicStyles, /@media \(max-width: 560px\)/);
  assert.match(publicStyles, /@media \(prefers-reduced-motion: reduce\)/);
  assert.match(publicStyles, /@media \(forced-colors: active\)/);
});

test("campos claros vencem o contrato global escuro inclusive no foco e autofill", () => {
  assert.match(publicStyles, /#root \.login\.login-gateway--public \.login-gateway__field[\s\S]*?background-color:\s*transparent !important;[\s\S]*?color-scheme:\s*light;/);
  assert.match(publicStyles, /input:-webkit-autofill[\s\S]*?-webkit-text-fill-color:\s*#1b2440 !important;[\s\S]*?-webkit-box-shadow:\s*0 0 0 1000px #fff inset !important;/);
  assert.match(publicStyles, /#root \.login\.login-gateway--dark[\s\S]*?color-scheme:\s*dark;/);
});
