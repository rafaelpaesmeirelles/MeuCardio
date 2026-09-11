import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const read = (path) => readFileSync(new URL(`../${path}`, import.meta.url), "utf8");
const entrar = read("src/pages/Entrar.tsx");
const styles = read("src/styles/corvia-atelier-login.css");

test("gateway oferece exatamente claro e escuro, com claro padrão e preferência explícita preservada", () => {
  assert.deepEqual([...entrar.matchAll(/id: "(light|dark)"/g)].map((match) => match[1]), ["light", "dark"]);
  assert.match(entrar, /sessionStorage\.getItem\(CORVIA_LOGIN_THEME_KEY\) === "dark" \? "dark" : "light"/);
  assert.match(entrar, /catch\s*\{\s*return "light"/);
  assert.doesNotMatch(entrar, /id: "(?:complete|essential|scientific)"/);
});

test("tema é preferência visual e não modifica permissões ou modo autenticado", () => {
  assert.match(entrar, /sessionStorage\.setItem\(CORVIA_LOGIN_THEME_KEY, temaPublico\)/);
  assert.match(entrar, /sessionStorage\.removeItem\("corvia:cardiology-spaces:mode"\)/);
  assert.match(entrar, /Preferência visual desta sessão/);
  assert.doesNotMatch(entrar, /plano\s*=|permiss(?:ao|ão)\s*=|autoriz(?:acao|ação)\s*=/i);
  assert.doesNotMatch(entrar, /(?:localStorage|sessionStorage)\.setItem\([^\n]*(?:senha|password)/i);
});

test("seletor nativo anuncia o estado e conserva alvos de toque de 44px em todos os breakpoints", () => {
  assert.match(entrar, /<fieldset className="login-gateway__theme-choice login-gateway__theme-choice--top" aria-describedby="login-theme-note">/);
  assert.match(entrar, /<legend>Escolha a aparência<\/legend>/);
  assert.match(entrar, /type="radio"\s*name="tema-publico"/s);
  assert.match(entrar, /checked=\{temaPublico === opcao\.id\}/);
  assert.match(entrar, /onChange=\{\(\) => selecionarTemaPublico\(opcao\.id\)\}/);
  const labels = [...styles.matchAll(/#corvia-login \.login-gateway__theme-choice label\s*\{([^}]+)\}/g)];
  assert.ok(labels.length >= 1);
  for (const [, body] of labels) {
    for (const dimension of ["width", "height"]) {
      const value = body.match(new RegExp(`(?:^|;)\\s*${dimension}:\\s*(\\d+)px`));
      if (value) assert.ok(Number(value[1]) >= 44, `${dimension} do tema não pode ficar abaixo de 44px`);
    }
  }
  assert.match(styles, /label:has\(input:focus-visible\)[^{]*\{[^}]*outline:/);
});

test("as duas aparências usam o mesmo formulário real, autocomplete e links de recuperação", () => {
  assert.match(entrar, /login-gateway--\$\{temaPublico\}/);
  assert.equal((entrar.match(/<form\b/g) || []).length, 1);
  assert.match(entrar, /<form className="login-gateway__form" onSubmit=\{enviar\} aria-busy=\{enviando\}>/);
  assert.match(entrar, /htmlFor="email"/);
  assert.match(entrar, /id="email" type="email" inputMode="email" autoCapitalize="none" autoComplete="username"[^\n]+required/);
  assert.match(entrar, /htmlFor="senha"/);
  assert.match(entrar, /id="senha" type=\{mostrarSenha \? "text" : "password"\} autoComplete="current-password"[^\n]+required/);
  assert.match(entrar, /aria-label=\{mostrarSenha \? "Ocultar senha" : "Mostrar senha"\} aria-pressed=\{mostrarSenha\}/);
  for (const route of ["esqueci-senha", "solicitar-acesso", "privacidade", "termos"]) assert.ok(entrar.includes(`to="/${route}"`));
});

test("envio mantém autenticação canônica, remember-me, proteção contra duplo envio e erro anunciado", () => {
  assert.match(entrar, /const \{ entrar \} = useAuth\(\)/);
  assert.match(entrar, /if \(enviando \|\| !email\.trim\(\) \|\| !senha\) return/);
  assert.match(entrar, /await entrar\(email\.trim\(\)\.toLowerCase\(\), senha, permanecerConectado\)/);
  assert.match(entrar, /checked=\{permanecerConectado\} onChange=\{\(event\) => setPermanecerConectado\(event\.target\.checked\)\}/);
  assert.match(entrar, /finally\s*\{\s*setEnviando\(false\)/);
  assert.match(entrar, /type="submit" disabled=\{enviando\}/);
  assert.match(entrar, /aria-invalid=\{Boolean\(erro\)\} aria-describedby=\{erro \? "login-erro" : undefined\}/);
  assert.match(entrar, /id="login-erro"[^>]+role="alert"/);
  assert.doesNotMatch(entrar, /fetch\(|api\.(?:post|get)|token\/SSO|Entrar com token|\bSSO\b/);
});

test("arquitetura é separada do formulário e não reintroduz cenografia cósmica ou instaladores", () => {
  assert.match(entrar, /corvia-atelier-login\.css/);
  assert.match(entrar, /id="corvia-login"/);
  assert.match(entrar, /className="atelier-login__story"/);
  assert.match(entrar, /className="atelier-login__access" aria-labelledby="login-acesso-titulo"/);
  for (const space of ["consultorio", "hospital", "ensino", "pesquisa", "gestao"]) assert.ok(entrar.includes(`id: "${space}"`));
  assert.match(entrar, /src="\/atelier\/atelier-entrance\.webp" width="1536" height="1024" alt="[^"]+" fetchPriority="high"/);
  const bytes = readFileSync(new URL("../public/atelier/atelier-entrance.webp", import.meta.url));
  assert.equal(bytes.toString("ascii", 0, 4), "RIFF");
  assert.equal(bytes.toString("ascii", 8, 12), "WEBP");
  assert.doesNotMatch(entrar, /LoginGalaxy|UniverseStars|CoracaoHolografico|<canvas|MarcaAndroid|MarcaWindows|Baixar app|\/downloads\//);
  assert.doesNotMatch(styles, /\.atelier-login__access\s*\{[^}]*url\(/);
});

test("geometria é compartilhada pelos temas, responsiva e oferece foco e movimento reduzido", () => {
  assert.match(styles, /#corvia-login\.corvia-atelier-login\s*\{/);
  assert.match(styles, /\[data-login-theme="dark"\]\s*\{[^}]*color-scheme:\s*dark/s);
  assert.match(styles, /color-scheme:\s*light/);
  assert.match(styles, /@media \(max-width: 760px\)/);
  assert.match(styles, /\.atelier-login__layout\s*\{[^}]*flex-direction:\s*column/);
  assert.match(styles, /prefers-reduced-motion:\s*reduce/);
  assert.match(entrar, /href="#login-acesso-titulo"/);
  assert.match(entrar, /id="login-acesso-titulo" tabIndex=\{-1\}/);
  assert.match(styles, /\.atelier-login__skip:focus\s*\{\s*transform:\s*none/);
});

test("aviso de segurança reserva duas linhas nas colunas estreitas sem alterar o desktop amplo", () => {
  const base = styles.match(/#corvia-login \.atelier-login__security\s*\{([^}]+)\}/)?.[1];
  assert.ok(base);
  assert.match(base, /line-height:\s*1\.5\s*;/);
  assert.doesNotMatch(base, /(?:^|;)\s*(?:min-height|height|max-height):/);
  const narrowStart = styles.indexOf("@media (max-width: 1150px)");
  const mobileStart = styles.indexOf("@media (max-width: 760px)", narrowStart);
  assert.ok(narrowStart >= 0 && mobileStart > narrowStart);
  const narrow = styles.slice(narrowStart, mobileStart);
  assert.match(narrow, /#corvia-login \.atelier-login__security\s*\{\s*min-height:\s*3em\s*;\s*\}/);
  assert.doesNotMatch(narrow, /\.atelier-login__security[^}]*\b(?:overflow:\s*hidden|display:\s*none|visibility:\s*hidden)/);
  assert.match(entrar, /temaPublico === "light" \? "Sistema seguro" : "Ambiente Protegido"/);
});
