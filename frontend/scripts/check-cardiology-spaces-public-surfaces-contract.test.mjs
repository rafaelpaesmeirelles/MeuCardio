import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const read = (path) => readFileSync(new URL(`../${path}`, import.meta.url), "utf8");
const app = read("src/App.tsx");
const frame = read("src/components/PublicCardiologyFrame.tsx");
const legalFrame = read("src/components/LegalDocumentFrame.tsx");
const styles = read("src/styles/cardiology-spaces-public.css");
const atelierStyles = read("src/styles/corvia-atelier-public.css");
const entrar = read("src/pages/Entrar.tsx");
const auth = read("src/lib/auth.tsx");
const vite = read("vite.config.ts");

const publicPages = {
  produto: read("src/pages/Produto.tsx"),
  solicitar: read("src/pages/SolicitarAcesso.tsx"),
  esqueci: read("src/pages/EsqueciSenha.tsx"),
  redefinir: read("src/pages/RedefinirSenha.tsx"),
  validar: read("src/pages/ValidarDocumento.tsx"),
  privacidade: read("src/pages/PoliticaPrivacidade.tsx"),
  termos: read("src/pages/TermosUso.tsx"),
  excluir: read("src/pages/ExcluirConta.tsx"),
  mail: read("src/pages/CorviaMail.tsx"),
};

test("every anonymous surface remains explicitly routed", () => {
  for (const route of [
    "/produto",
    "/solicitar-acesso",
    "/esqueci-senha",
    "/redefinir-senha",
    "/corvia-mail",
    "/privacidade",
    "/termos",
    "/excluir-conta",
    "/validar",
    "/validar/:codigo",
  ]) {
    assert.ok(app.includes(`path=\"${route}\"`), `${route} precisa permanecer roteada`);
  }
});

test("public pages share one semantic Cardiology Spaces frame", () => {
  for (const page of ["solicitar", "esqueci", "redefinir", "validar"]) {
    assert.match(publicPages[page], /import PublicCardiologyFrame/);
    assert.match(publicPages[page], /<PublicCardiologyFrame/);
  }
  for (const page of ["privacidade", "termos", "excluir"]) {
    assert.match(publicPages[page], /import LegalDocumentFrame/);
    assert.match(publicPages[page], /<LegalDocumentFrame/);
  }
  assert.match(publicPages.produto, /import \{ PublicCorviaBrand \}/);
  assert.match(frame, /corvia-atelier-public/);
  assert.match(frame, /src="\/atelier\/corvia-logo-atelier\.svg"/);
  assert.doesNotMatch(frame, /public-space__stars|UniverseStars|<canvas/);
  assert.match(frame, /className="public-space__skip" href="#conteudo-principal"/);
  assert.match(frame, /<main className="public-space__workspace" id="conteudo-principal" tabIndex=\{-1\}>/);
  assert.match(frame, /<section className="public-space__context" aria-labelledby="public-space-title">/);
  assert.match(frame, /<section className="public-space__surface">/);
  assert.match(publicPages.produto, /className="public-space__skip" href="#conteudo-principal"/);
  assert.match(publicPages.produto, /<main id="conteudo-principal" tabIndex=\{-1\}>/);
});

test("login Atelier styling stays isolated from the shared public forms", () => {
  assert.match(entrar, /corvia-atelier-login\.css/);
  assert.doesNotMatch(entrar, /PublicCardiologyFrame|PublicCorviaBrand|public-space__/);
});

test("the anonymous Mail gateway changes presentation only", () => {
  const anonymousStart = publicPages.mail.indexOf("if (!usuario)");
  const authenticatedStart = publicPages.mail.indexOf('<div className="pagina"', anonymousStart);
  assert.ok(anonymousStart >= 0 && authenticatedStart > anonymousStart, "os ramos anônimo e autenticado precisam continuar separados");
  const anonymousBranch = publicPages.mail.slice(anonymousStart, authenticatedStart);
  const authenticatedBranch = publicPages.mail.slice(authenticatedStart);
  assert.match(anonymousBranch, /<PublicCardiologyFrame/);
  assert.match(anonymousBranch, /to="\/entrar"/);
  assert.match(anonymousBranch, /to="\/solicitar-acesso"/);
  assert.doesNotMatch(authenticatedBranch, /PublicCardiologyFrame|public-mail-card/);
  for (const preservedContract of [
    'api.get<ContaEmail>("/email/conta")',
    'navigate("/caixa-de-email"',
    '<AbaEntrar />',
    '<AbaEsqueciSenha />',
    '<AbaAssinar />',
  ]) {
    assert.ok(publicPages.mail.includes(preservedContract), `CorVIA Mail precisa preservar ${preservedContract}`);
  }
});

test("form and validation transport contracts were not rewritten", () => {
  assert.match(publicPages.solicitar, /\/auth\/solicitar-acesso-com-recuperacao/);
  assert.match(publicPages.esqueci, /\/auth\/esqueci-senha/);
  assert.match(publicPages.redefinir, /\/auth\/redefinir-senha/);
  assert.match(publicPages.validar, /\/api\/documentos-publicos\/validar\//);
  assert.match(publicPages.redefinir, /alvo === "email" \? "\/corvia-mail" : "\/entrar"/);
  assert.match(publicPages.validar, /resposta\.status === 404/);
  assert.match(publicPages.validar, /resposta\.status >= 500/);
  assert.match(publicPages.validar, /temporariamente indisponível/);
  assert.match(auth, /res\.status === 401 \|\| res\.status === 403/);
  assert.match(auth, /res\.status >= 500/);
  assert.match(auth, /Não foi possível conectar ao CorVIA/);
});

test("the product presentation exposes five distinct optimized spaces", () => {
  for (const space of ["consultorio", "hospital", "ensino", "pesquisa", "gestao"]) {
    assert.match(publicPages.produto, new RegExp(`/atelier/atelier-${space}\\.webp`));
    assert.match(publicPages.produto, new RegExp(`id: \"${space}\"`));
  }
  assert.match(publicPages.produto, /Completo/);
  assert.match(publicPages.produto, /Essencial/);
  assert.match(publicPages.produto, /Ciência & Ensino/);
});

test("architectural scenes receive a same-origin bounded offline runtime cache", () => {
  assert.match(vite, /url\.origin === self\.location\.origin/);
  const literal = vite.match(/&&\s*(\/\^[^\n]+?\/)\.test\(url\.pathname\)/)?.[1];
  assert.ok(literal, "a regra de cache de cenas precisa ser identificável");
  const scenePattern = new RegExp(literal.slice(1, -1));
  for (const path of ["/atelier/atelier-entrance.webp", "/atelier/atelier-hospital-small.webp", "/spaces/corvia-room-hospital.jpg"]) {
    assert.ok(scenePattern.test(path), path + " precisa funcionar no cache de cenas");
  }
  for (const path of ["/api/agenda/appointments", "/api/documentos", "/atelier/unsafe.html"]) {
    assert.ok(!scenePattern.test(path), path + " não pode entrar no cache público de cenas");
  }
  assert.match(vite, /handler: "StaleWhileRevalidate"/);
  assert.match(vite, /cacheName: "corvia-space-scenes-v1"/);
  assert.match(vite, /maxEntries: 30/);
  assert.match(vite, /cacheableResponse: \{ statuses: \[200\] \}/);
});

test("public CSS keeps geometry, accessibility and responsive constraints", () => {
  assert.match(styles, /\.public-space__surface\s*\{[^}]*border-radius:\s*12px;/s);
  assert.match(styles, /\.public-mail-card__brand\s*\{[^}]*border-radius:\s*12px;/s);
  assert.match(styles, /\.public-space__footer a\s*\{[^}]*min-width:\s*44px;[^}]*min-height:\s*44px;/s);
  assert.match(styles, /\.public-space \.campo-senha__alternar\s*\{[^}]*width:\s*44px;[^}]*height:\s*44px;/s);
  assert.match(styles, /@media \(max-width: 900px\)/);
  assert.match(styles, /@media \(max-width: 560px\)/);
  assert.match(styles, /@media \(max-height: 700px\) and \(min-width: 901px\)/);
  assert.match(styles, /@media \(prefers-reduced-motion: reduce\)/);
  assert.doesNotMatch(styles, /clip-path/);
  assert.match(frame, /import "\.\.\/styles\/corvia-atelier-public\.css"/);
  assert.match(atelierStyles, /\.corvia-atelier-public/);
  assert.match(atelierStyles, /focus-visible/);
  assert.match(atelierStyles, /prefers-reduced-motion/);
});

test("legal documents preserve the authenticated layout", () => {
  assert.match(legalFrame, /const \{ usuario \} = useAuth\(\)/);
  assert.match(legalFrame, /if \(usuario\)/);
  assert.match(legalFrame, /className="legal-page"/);
  assert.match(legalFrame, /<PublicCardiologyFrame/);
});
