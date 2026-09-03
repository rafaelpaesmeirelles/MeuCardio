import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const read = (path) => readFileSync(new URL(`../${path}`, import.meta.url), "utf8");
const entrar = read("src/pages/Entrar.tsx");
const styles = read("src/styles/cardiology-spaces-login.css");
const finalStyles = read("src/styles/cardiology-spaces-login-approved-final.css");
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
  assert.match(finalStyles, /@media \(max-width: 900px\)[\s\S]*?\.login-gateway--public \.login-gateway__theme-choice-options\s*\{[\s\S]*?grid-template-columns:\s*repeat\(2,/);
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
  assert.match(finalStyles, /@media \(min-width: 901px\)/);
  assert.match(finalStyles, /@media \(max-width: 900px\)/);
  assert.match(finalStyles, /@media \(prefers-reduced-motion: reduce\)/);
  assert.doesNotMatch(`${entrar}\n${publicStyles}\n${finalStyles}`, /telesc[oó]pio|observat[oó]rio|montanha|planeta|lua cheia/i);
});

test("campos claros vencem o contrato global escuro inclusive no foco e autofill", () => {
  assert.match(publicStyles, /#root \.login\.login-gateway--public \.login-gateway__field[\s\S]*?background-color:\s*transparent !important;[\s\S]*?color-scheme:\s*light;/);
  assert.match(publicStyles, /input:-webkit-autofill[\s\S]*?-webkit-text-fill-color:\s*#1b2440 !important;[\s\S]*?-webkit-box-shadow:\s*0 0 0 1000px #fff inset !important;/);
  assert.match(publicStyles, /#root \.login\.login-gateway--dark[\s\S]*?color-scheme:\s*dark;/);
});

test("layout final aprovado: copy, galaxia horaria, ECG, marca, login horizontal e associação", () => {
  assert.match(entrar, /Um universo de espaços\. <strong>Uma só cardiologia\.<\/strong>/);
  assert.match(entrar, /Consultório, Hospital, Ensino, Pesquisa e Gestão orbitando juntos no seu Universo Profissional\./);
  assert.match(entrar, /cardiology-spaces-login-approved-final\.css/);

  assert.doesNotMatch(entrar, /login-gateway__routes|login-gateway__ring/,
    "círculos e traços curvos antigos não podem voltar ao coração central");
  assert.doesNotMatch(entrar, /MarcaAndroid|MarcaWindows|Baixar app|Aplicativo para Windows|\/downloads\/corvia-cardiology-spaces-/,
    "o login público não deve mais divulgar instaladores nativos");

  assert.match(entrar, /className="login-gateway__join" to="\/solicitar-acesso"/);
  assert.match(entrar, /<strong>Novo no CorVIA\?<\/strong><small>Solicite seu Acesso<\/small>/);

  assert.match(finalStyles, /--corvia-petroleum:\s*#0f727a/);
  assert.match(finalStyles, /\.login-gateway--public \.login-gateway__brand \.corvia-via\s*\{[^}]*color:\s*var\(--corvia-petroleum\) !important/s,
    "VIA deve permanecer azul-petróleo");

  assert.match(finalStyles, /animation:\s*login-gateway-galaxy-clockwise 48s linear infinite !important/,
    "a galáxia precisa girar lenta e continuamente em sentido horário");
  assert.match(finalStyles, /@keyframes login-gateway-galaxy-clockwise\s*\{[\s\S]*?rotate\(-12deg\)[\s\S]*?rotate\(348deg\)/,
    "a rotação precisa completar exatamente 360 graus, sem vai-e-volta");

  assert.match(finalStyles, /\.login-gateway--public \.login-gateway__pulse\s*\{[^}]*z-index:\s*7[^}]*bottom:\s*16%/s,
    "o ECG deve cruzar visualmente a ponta inferior do coração");
  assert.match(finalStyles, /animation:\s*login-gateway-ecg-flow 4\.8s linear infinite !important/,
    "o traçado do ECG precisa permanecer em movimento");

  assert.match(finalStyles, /@media \(min-width: 901px\)[\s\S]*?grid-template-areas:\s*"identity form theme join"/,
    "o desktop precisa usar a barra inferior horizontal fina aprovada");
  assert.match(finalStyles, /@media \(min-width: 901px\)[\s\S]*?\.login-gateway--public \.login-gateway__brand img\s*\{[^}]*width:\s*70px[^}]*height:\s*70px/s,
    "a marca CorVIA deve ficar discretamente maior no desktop");

  assert.match(finalStyles, /@media \(max-width: 900px\)[\s\S]*?\.login-gateway--public \.login-gateway__milky-way\s*\{[^}]*width:\s*min\(720px, 154vw\)/s,
    "mobile e desktop devem reutilizar o mesmo modelo de galáxia espiral");
});
