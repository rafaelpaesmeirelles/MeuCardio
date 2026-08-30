import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const baseUrl = process.env.BASE_URL ?? "http://127.0.0.1:8080";
const email = process.env.E2E_EMAIL ?? "transactional-e2e@teste.local";
const password = process.env.E2E_PASSWORD ?? "transactional-e2e-seguro-123";
const artifactDir = process.env.ARTIFACT_DIR ?? path.resolve("transactional-e2e");
const marker = `E2E-${Date.now()}`;
fs.mkdirSync(path.join(artifactDir, "screenshots"), { recursive: true });

const report = { marker, startedAt: new Date().toISOString(), steps: [], pageErrors: [], serverErrors: [], failures: [] };
const record = (name, detail = {}) => report.steps.push({ name, ok: true, ...detail });

function required(result, name) {
  if (!result.ok) throw new Error(`${name}: HTTP ${result.status} — ${JSON.stringify(result.data)}`);
  return result.data;
}

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, locale: "pt-BR", colorScheme: "dark" });
const page = await context.newPage();
page.on("pageerror", (error) => report.pageErrors.push(String(error)));
page.on("response", (response) => {
  if (response.url().startsWith(baseUrl) && response.status() >= 500) {
    report.serverErrors.push(`${response.status()} ${response.request().method()} ${response.url()}`);
  }
});

async function api(url, options = {}) {
  return page.evaluate(async ({ url, options }) => {
    const response = await fetch(url, {
      method: options.method ?? "GET",
      credentials: "include",
      headers: options.body === undefined ? undefined : { "Content-Type": "application/json" },
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
    });
    const text = await response.text();
    let data = text;
    try { data = text ? JSON.parse(text) : null; } catch { /* textual error body */ }
    return { ok: response.ok, status: response.status, data };
  }, { url: `${baseUrl}${url}`, options });
}

async function pdf(url, options = {}) {
  return page.evaluate(async ({ url, options }) => {
    const response = await fetch(url, {
      method: options.method ?? "GET",
      credentials: "include",
      headers: options.body === undefined ? undefined : { "Content-Type": "application/json" },
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
    });
    const bytes = new Uint8Array(await response.arrayBuffer());
    return {
      ok: response.ok,
      status: response.status,
      contentType: response.headers.get("content-type"),
      signature: new TextDecoder().decode(bytes.slice(0, 5)),
      byteLength: bytes.byteLength,
    };
  }, { url: `${baseUrl}${url}`, options });
}

async function publicContracts() {
  const titles = new Map([
    ["/entrar", "Entrar — CorVIA Clinical OS"],
    ["/solicitar-acesso", "Solicitar acesso — CorVIA Clinical OS"],
    ["/termos", "Termos de Uso — CorVIA Clinical OS"],
    ["/validar", "Validar documento clínico — CorVIA Clinical OS"],
  ]);
  for (const [route, expected] of titles) {
    await page.goto(`${baseUrl}${route}`, { waitUntil: "networkidle" });
    assert.equal(await page.title(), expected, `título de ${route}`);
  }
  await page.goto(`${baseUrl}/solicitar-acesso`, { waitUntil: "networkidle" });
  const scroll = await page.locator(".prehome-card--register").evaluate((element) => {
    const style = getComputedStyle(element);
    return { overflowY: style.overflowY, clientHeight: element.clientHeight, scrollHeight: element.scrollHeight };
  });
  assert.ok(scroll.overflowY === "visible" || scroll.scrollHeight <= scroll.clientHeight + 1, `cadastro tem rolagem aninhada: ${JSON.stringify(scroll)}`);
  record("public-contracts", { routes: titles.size, signupScroll: scroll });
}

async function login() {
  await page.goto(`${baseUrl}/entrar`, { waitUntil: "networkidle" });
  await page.locator("#email").fill(email);
  await page.locator("#senha").fill(password);
  await page.locator('button[type="submit"]').click();
  await page.waitForURL((url) => !url.pathname.includes("/entrar"), { timeout: 20_000 });
  required(await api("/api/auth/me"), "sessão autenticada");
  record("login");
}

async function prescriptionFlow() {
  const created = required(await api("/api/receituario", { method: "POST", body: {
    destinatario: { nome: `Paciente Sintético ${marker}` },
    itens: [{ descricao: "Dipirona 500 mg — teste sintético", quantidade: "10 comprimidos", posologia: "1 comprimido se necessário" }],
    observacoes: "Dado sintético descartável para teste automatizado.",
  } }), "criar prescrição");
  assert.ok(created.prescricao_id);
  assert.equal(created.documentos.length, 1);
  const documentId = created.documentos[0].id;
  const reviewed = required(await api(`/api/receituario/documentos/${documentId}/revisar`, { method: "POST", body: { confirmar: true } }), "revisar prescrição");
  assert.equal(reviewed.status, "revisado");
  const providers = required(await api("/api/assinatura/provedores"), "listar provedores de assinatura");
  assert.ok(providers.some((provider) => provider.codigo === "MANUAL" && provider.disponivel));
  const emitted = await pdf(`/api/receituario/documentos/${documentId}/emitir`, { method: "POST", body: { metodo: "MANUAL" } });
  assert.equal(emitted.ok, true, `emitir receita: ${JSON.stringify(emitted)}`);
  assert.equal(emitted.signature, "%PDF-");
  assert.ok(emitted.byteLength > 1_000);
  const reread = required(await api(`/api/receituario/${created.prescricao_id}`), "reler prescrição");
  assert.equal(reread.destinatario.nome, `Paciente Sintético ${marker}`);
  assert.equal(reread.documentos[0].status, "emitido");
  await page.goto(`${baseUrl}/receituario`, { waitUntil: "networkidle" });
  await page.getByRole("tab", { name: "Histórico", exact: true }).click();
  await page.getByText(`Paciente Sintético ${marker}`, { exact: false }).first().waitFor({ state: "visible" });
  await page.screenshot({ path: path.join(artifactDir, "screenshots", "receituario.png"), fullPage: false });
  record("prescription", { prescriptionId: created.prescricao_id, documentId, pdfBytes: emitted.byteLength });
}

async function documentFlow() {
  const created = required(await api("/api/document-templates/gerar-livre", { method: "POST", body: {
    titulo: `Documento Sintético ${marker}`,
    corpo: "Conteúdo exclusivamente sintético para prova transacional automatizada.",
    patient_name: `Paciente Sintético ${marker}`,
  } }), "criar documento");
  const emitted = await pdf(`/api/document-templates/gerados/${created.id}/pdf?metodo=MANUAL`);
  assert.equal(emitted.ok, true, `emitir documento: ${JSON.stringify(emitted)}`);
  assert.equal(emitted.signature, "%PDF-");
  assert.ok(emitted.byteLength > 1_000);
  const list = required(await api(`/api/document-templates/gerados?nome=${encodeURIComponent(marker)}&page_size=100`), "listar documentos");
  assert.ok(list.items.some((item) => item.id === created.id && item.patient_name.includes(marker)));
  await page.goto(`${baseUrl}/documentos`, { waitUntil: "networkidle" });
  assert.ok((await page.locator("body").innerText()).includes(`Documento Sintético ${marker}`));
  await page.screenshot({ path: path.join(artifactDir, "screenshots", "documentos.png"), fullPage: false });
  record("document", { documentId: created.id, pdfBytes: emitted.byteLength });
}

async function emailSignatureFlow() {
  const saved = required(await api("/api/email/assinatura", { method: "PUT", body: {
    ativa: true, incluir_telefone: false, incluir_endereco: false, assinar_digitalmente: false,
  } }), "salvar assinatura de e-mail");
  assert.equal(saved.ativa, true);
  assert.equal(saved.assinar_digitalmente, false);
  const reread = required(await api("/api/email/assinatura"), "reler assinatura de e-mail");
  assert.equal(reread.ativa, true);
  assert.ok(reread.pre_visualizacao?.nome);
  await page.goto(`${baseUrl}/minha-conta`, { waitUntil: "networkidle" });
  const checkbox = page.locator('label:has-text("Incluir assinatura nos e-mails") input[type="checkbox"]');
  await checkbox.waitFor({ state: "visible" });
  assert.equal(await checkbox.isChecked(), true);
  record("email-signature", { visualSignature: true, smimeRequested: false, outboundEmailSent: false });
}

async function integrationFlow() {
  const created = required(await api("/api/agenda/integrations", { method: "POST", body: {
    provider: "feegow",
    display_name: `Integração sintética ${marker}`,
    sync_strategy: "bidirectional",
    configuration: {}, credentials: {}, enabled: true, write_enabled: false,
    consent_accepted: true, consent_version: "transactional-e2e-v1",
  } }), "criar integração segura");
  const diagnosis = required(await api(`/api/agenda/integrations/${created.id}/diagnose`, { method: "POST" }), "diagnosticar integração");
  assert.equal(diagnosis.ok, false);
  assert.equal(diagnosis.code, "homologation_required");
  const integrations = required(await api("/api/agenda/integrations"), "reler integrações");
  assert.ok(integrations.some((item) => item.id === created.id && item.display_name.includes(marker)));
  await page.goto(`${baseUrl}/agenda`, { waitUntil: "networkidle" });
  assert.ok((await page.locator("body").innerText()).includes(`Integração sintética ${marker}`));
  await page.screenshot({ path: path.join(artifactDir, "screenshots", "agenda.png"), fullPage: false });
  record("integration-adapter", { integrationId: created.id, code: diagnosis.code, externalNetworkCall: false });
}

async function clinicalLegibility() {
  const drugs = required(await api("/api/drugs"), "listar medicamentos");
  assert.ok(drugs.length > 0, "catálogo sintético/isolado precisa conter medicamentos");
  await page.goto(`${baseUrl}/medicamentos?slug=${encodeURIComponent(drugs[0].slug)}`, { waitUntil: "networkidle" });
  await page.locator(".mc-command").waitFor({ state: "visible" });
  const medication = await page.evaluate(() => {
    const copy = document.querySelector(".mc-command__primary-block .clinical-richtext p, .mc-command__primary-block strong");
    const tab = document.querySelector(".mc-command__tabs button");
    const copyStyle = copy ? getComputedStyle(copy) : null;
    const tabRect = tab?.getBoundingClientRect();
    return { copyFont: copyStyle ? parseFloat(copyStyle.fontSize) : 0, tabHeight: tabRect?.height ?? 0 };
  });
  assert.ok(medication.copyFont >= 16, `texto de medicamento abaixo de 16px: ${medication.copyFont}`);
  assert.ok(medication.tabHeight >= 44, `aba de medicamento abaixo de 44px: ${medication.tabHeight}`);
  await page.goto(`${baseUrl}/emergencia`, { waitUntil: "networkidle" });
  const emergency = await page.locator(".emerg").evaluate((element) => {
    const rect = element.getBoundingClientRect();
    return { left: rect.left, right: rect.right, viewport: innerWidth };
  });
  assert.ok(emergency.right <= emergency.viewport + 1, `emergência ultrapassa viewport: ${JSON.stringify(emergency)}`);
  record("clinical-legibility", { medication, emergency });
}

async function navigationAndFavorites() {
  const drugs = required(await api("/api/drugs"), "listar medicamentos para favoritos");
  assert.ok(drugs.length > 0);
  const drug = required(await api(`/api/drug-insights/${encodeURIComponent(drugs[0].slug)}`), "abrir medicamento favorito");
  assert.ok(Number.isInteger(drug.id), "detalhe do medicamento precisa expor id canônico");
  await api(`/api/favorites/medicamento/${drug.id}`, { method: "DELETE" });

  await page.goto(`${baseUrl}/medicamentos?slug=${encodeURIComponent(drug.slug)}`, { waitUntil: "networkidle" });
  const command = page.locator(".cos-command-mini input");
  await command.fill("prescrever");
  await command.press("Enter");
  await page.waitForURL((url) => url.pathname === "/receituario");
  await page.goto(`${baseUrl}/medicamentos?slug=${encodeURIComponent(drug.slug)}`, { waitUntil: "networkidle" });
  await page.locator(".cos-command-mini input").fill("calcular risco");
  await page.locator(".cos-command-mini input").press("Enter");
  await page.waitForURL((url) => url.pathname === "/calculadoras");
  await page.locator(".ccc-nav__context").getByText("Decisão clínica", { exact: true }).waitFor({ state: "visible" });

  await page.goto(`${baseUrl}/medicamentos?slug=${encodeURIComponent(drug.slug)}`, { waitUntil: "networkidle" });
  const favoriteButton = page.getByRole("button", { name: "☆ Favoritar", exact: true });
  await favoriteButton.waitFor({ state: "visible" });
  await favoriteButton.click();
  await page.getByRole("button", { name: "★ Favoritado", exact: true }).waitFor({ state: "visible" });
  const favorites = required(await api("/api/favorites"), "reler favorito");
  assert.ok(favorites.some((item) => item.item_type === "medicamento" && item.item_id === drug.id));

  await page.goto(`${baseUrl}/favoritos`, { waitUntil: "networkidle" });
  await page.getByText(drug.generic_name, { exact: true }).waitFor({ state: "visible" });
  assert.equal(await page.getByRole("button", { name: `Todos · ${favorites.length}`, exact: true }).count(), 1);
  const medicationCount = favorites.filter((item) => item.item_type === "medicamento").length;
  assert.equal(await page.getByRole("button", { name: `Medicamento · ${medicationCount}`, exact: true }).count(), 1);

  await page.goto(`${baseUrl}/medicamentos?slug=${encodeURIComponent(drug.slug)}`, { waitUntil: "networkidle" });
  const nav = await page.locator(".ccc-nav__scroll").evaluate((element) => ({ clientHeight: element.clientHeight, scrollHeight: element.scrollHeight }));
  assert.ok(nav.scrollHeight <= nav.clientHeight + 1, `navegação contextual ainda exige rolagem: ${JSON.stringify(nav)}`);
  assert.ok(await page.locator(".ccc-nav__context").isVisible());
  assert.equal(await page.locator(".ccc-nav__section[open]").count(), 1);

  await api(`/api/favorites/medicamento/${drug.id}`, { method: "DELETE" });
  record("navigation-favorites", { drugId: drug.id, nav });
}

try {
  await publicContracts();
  await login();
  await prescriptionFlow();
  await documentFlow();
  await emailSignatureFlow();
  await integrationFlow();
  await clinicalLegibility();
  await navigationAndFavorites();
} catch (error) {
  report.failures.push(error?.stack ?? String(error));
} finally {
  report.finishedAt = new Date().toISOString();
  if (report.pageErrors.length) report.failures.push(`page errors: ${report.pageErrors.join(" | ")}`);
  if (report.serverErrors.length) report.failures.push(`server errors: ${report.serverErrors.join(" | ")}`);
  fs.writeFileSync(path.join(artifactDir, "report.json"), JSON.stringify(report, null, 2));
  await context.close();
  await browser.close();
}

console.log(JSON.stringify(report, null, 2));
if (report.failures.length) process.exitCode = 1;
