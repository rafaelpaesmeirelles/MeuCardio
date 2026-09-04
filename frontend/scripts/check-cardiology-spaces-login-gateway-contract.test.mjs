import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const read = (path) => readFileSync(new URL(`../${path}`, import.meta.url), "utf8");
const entrar = read("src/pages/Entrar.tsx");
const styles = read("src/styles/cardiology-spaces-login.css");
const finalStyles = read("src/styles/cardiology-spaces-login-approved-final.css");
const approvedStyles = read("src/styles/corvia-approved-fidelity-20260904.css");
const assetFixStyles = read("src/styles/corvia-approved-fidelity-asset-fix-20260904.css");
const heartAsset = read("src/assets/approvedHeartData.ts");
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
  assert.match(entrar, /Preferência visual desta sessão/);
});

test("seletor compacto do topo mantém semântica nativa e estado anunciado", () => {
  assert.match(entrar, /login-gateway__theme-choice login-gateway__theme-choice--top/);
  assert.match(entrar, /<legend>Escolha a aparência<\/legend>/);
  assert.match(entrar, /type="radio"\s*name="tema-publico"/s);
  assert.match(entrar, /checked=\{temaPublico === opcao\.id\}/);
  assert.match(entrar, /onChange=\{\(\) => selecionarTemaPublico\(opcao\.id\)\}/);
  assert.match(approvedStyles, /\.login-gateway--public \.login-gateway__theme-choice--top label\.is-selected/);
  assert.match(approvedStyles, /@media \(max-width: 900px\)/);
});

test("as duas aparências preservam o mesmo login, links e garantias", () => {
  assert.match(entrar, /login-gateway--\$\{temaPublico\}/);
  assert.equal((entrar.match(/<form className="login-gateway__form"/g) || []).length, 1);
  assert.match(entrar, /id="email"[\s\S]*?autoComplete="username"/);
  assert.match(entrar, /id="senha"[\s\S]*?autoComplete="current-password"/);
  assert.match(entrar, /to="\/esqueci-senha"/);
  assert.match(entrar, /to="\/solicitar-acesso"/);
  assert.match(entrar, /Ambiente Protegido/);
  assert.match(entrar, /Sistema seguro/);
});

test("claro e escuro compartilham a geometria e mudam somente a cromia", () => {
  assert.match(approvedStyles, /\.login-gateway--public\s*\{/);
  assert.match(approvedStyles, /\.login-gateway--light\s*\{/);
  assert.match(assetFixStyles, /@media \(max-width: 900px\)/);
  assert.match(assetFixStyles, /@media \(prefers-reduced-motion: reduce\)/);
  assert.doesNotMatch(`${entrar}\n${approvedStyles}\n${assetFixStyles}`, /telesc[oó]pio|observat[oó]rio|montanha|planeta|lua cheia/i);
});

test("campos claros continuam vencendo o contrato global de formulário", () => {
  assert.match(publicStyles, /#root \.login\.login-gateway--public \.login-gateway__field[\s\S]*?background-color:\s*transparent !important;[\s\S]*?color-scheme:\s*light;/);
  assert.match(publicStyles, /input:-webkit-autofill[\s\S]*?-webkit-text-fill-color:\s*#1b2440 !important;[\s\S]*?-webkit-box-shadow:\s*0 0 0 1000px #fff inset !important;/);
  assert.match(publicStyles, /#root \.login\.login-gateway--dark[\s\S]*?color-scheme:\s*dark;/);
});

test("layout final aprovado: copy, galaxia real horaria, ECG, coração, login fino e associação", () => {
  assert.match(entrar, /Um universo de espaços\. <strong>Uma só cardiologia\.<\/strong>/);
  assert.match(entrar, /Consultório, Hospital, Ensino, Pesquisa e Gestão orbitando juntos no seu Universo Profissional\./);
  assert.match(entrar, /corvia-approved-fidelity-asset-fix-20260904\.css/);

  assert.doesNotMatch(entrar, /login-gateway__routes|login-gateway__ring/,
    "círculos e traços curvos antigos não podem voltar ao coração central");
  assert.doesNotMatch(entrar, /MarcaAndroid|MarcaWindows|Baixar app|Aplicativo para Windows|\/downloads\/corvia-cardiology-spaces-/,
    "o login público não deve divulgar instaladores nativos");
  assert.doesNotMatch(entrar, /token\/SSO|Entrar com token|\bSSO\b/i,
    "o login final aprovado não possui acesso por token/SSO");

  assert.match(entrar, /className="login-gateway__join" to="\/solicitar-acesso"/);
  assert.match(entrar, /<strong>Novo no CorVIA\?<\/strong><small>Solicite seu Acesso<\/small>/);

  assert.match(entrar, /className="login-gateway__galaxy-image"/);
  assert.match(entrar, /src="\/spaces\/corvia-galaxy-cameo\.webp"/);
  assert.doesNotMatch(entrar, /login-gateway__galaxy-video|galaxy-loop-v2\.mp4/);
  assert.match(read("src/styles/corvia-login-final-approved-20260904.css"), /animation:\s*corvia-final-galaxy-clockwise 120s linear infinite !important/,
    "as quatro variantes precisam girar lentamente em sentido horário");
  assert.match(read("src/styles/corvia-login-final-approved-20260904.css"), /@keyframes corvia-final-galaxy-clockwise[\s\S]*?rotate\(0\)[\s\S]*?rotate\(360deg\)/,
    "a rotação precisa completar exatamente 360 graus, sem vai-e-volta");
  assert.match(assetFixStyles, /mask:\s*none !important/,
    "a galáxia real não pode voltar a ser recortada em oval");

  assert.match(entrar, /approvedHeartDataUri/);
  assert.match(entrar, /login-gateway__approved-heart/);
  assert.match(heartAsset, /data:image\/webp;base64,/,
    "o coração aprovado precisa estar incorporado como asset transparente real");

  assert.match(approvedStyles, /\.login-gateway--public \.login-gateway__pulse\s*\{[\s\S]*?z-index:\s*7 !important[\s\S]*?bottom:\s*16px !important/,
    "o ECG deve cruzar visualmente a ponta inferior do coração");
  assert.match(finalStyles, /animation:\s*login-gateway-ecg-flow 4\.8s linear infinite !important/,
    "o traçado do ECG precisa permanecer em movimento");
  assert.match(read("src/styles/corvia-login-final-approved-20260904.css"), /login-gateway__pulse \{ display:block !important/,
    "o traçado do ECG precisa permanecer em movimento");

  assert.match(read("src/styles/corvia-login-final-approved-20260904.css"), /grid-template-areas:\s*"head join" "form join" !important/,
    "o desktop precisa usar a barra inferior horizontal fina aprovada");
  assert.match(assetFixStyles, /min-height:\s*104px !important/,
    "a caixa de acesso desktop deve permanecer fina");

  for (const space of ["ensino", "hospital", "pesquisa", "consultorio", "gestao"]) {
    assert.match(approvedStyles, new RegExp(`login-gateway__space--${space}`), `o espaço ${space} precisa manter posição explícita`);
  }

  assert.match(approvedStyles, /@media \(max-width: 900px\)[\s\S]*?\.login-gateway--public \.login-gateway__console\s*\{[\s\S]*?grid-template-areas:\s*"head" "form" "join"/,
    "o mobile deve preservar login compacto abaixo da composição cósmica");
});
