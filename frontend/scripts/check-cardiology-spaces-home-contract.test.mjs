import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const home = readFileSync(new URL("../src/pages/CardiologySpacesHome.tsx", import.meta.url), "utf8");
const app = readFileSync(new URL("../src/App.tsx", import.meta.url), "utf8");
const catalog = home.slice(home.indexOf("const CATALOG"), home.indexOf("const ESSENTIAL_DEFAULTS"));
const catalogPaths = [...catalog.matchAll(/(?:\["|to:\s*")((?:\/)[^"\s]+)"/g)].map((match) => match[1]);
const primaryRoutes = [
  "/doencas", "/medicamentos", "/exames", "/calculadoras", "/emergencia", "/cardiologia-intensiva",
  "/checklists", "/triagem-sintomas", "/interacoes", "/condicoes", "/fluxogramas", "/avaliacao-preoperatoria",
  "/exames-ia", "/prontuario", "/round", "/receituario", "/documentos", "/agenda", "/deslocamento", "/corvia-mail",
  "/caixa-de-email", "/assistente", "/validar", "/telediagnostico", "/material-paciente", "/evidencias",
  "/estudos", "/documentos-cientificos-ia", "/trilhas/timeline", "/trilhas", "/casos-clinicos", "/diretrizes",
  "/biblioteca", "/galeria", "/indicadores", "/apresentacao", "/exportar", "/favoritos", "/busca",
  "/busca?modo=tudo-com-tudo", "/usuarios-online", "/sincronizacao", "/minha-conta", "/privacidade", "/termos",
  "/tour", "/tour/cardiology-spaces", "/verificacao-identidade", "/excluir-conta", "/admin", "/admin/usuarios",
  "/fila-telediagnostico", "/receitas-para-assinatura", "/heart-team", "/whatsapp-assistant", "/admin/operacoes-ia",
];

test("empty or unavailable agenda never fabricates appointments or times", () => {
  assert.doesNotMatch(home, /appointment_type:\s*"Consultório"/);
  assert.doesNotMatch(home, /appointment_type:\s*"Hospital"/);
  assert.doesNotMatch(home, /appointment_type:\s*"Estudo"/);
  assert.doesNotMatch(home, /"13:00"|"20:00"/);
  assert.match(home, /appointmentsState === "error" \? "Agenda indisponível agora"/);
  assert.match(home, /setAppointmentsState\("ready"\)/);
  for (const path of ["/agenda", "/documentos", "/favoritos"]) assert.match(home, new RegExp(`to: "${path}"`));
});

test("Todas as funções contains every primary user-facing entry point exactly once", () => {
  assert.deepEqual([...new Set(catalogPaths)], catalogPaths, "o catálogo não pode duplicar destinos");
  assert.deepEqual(new Set(catalogPaths), new Set(primaryRoutes));
  for (const route of catalogPaths) {
    const path = route.split("?")[0];
    const relative = path.slice(1).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    assert.match(app, new RegExp(`<Route path="\\/?${relative}"`), `${route} precisa existir em App.tsx`);
  }
});

test("detail, contextual, alias and authentication routes stay outside the function catalog", () => {
  for (const excluded of ["/:slug", "/:id", "/heart-team/:caseId", "/admin/usuarios/:id", "/ecg-ia", "/assinatura", "/entrar", "/redefinir-senha", "/em-breve"]) {
    assert.ok(!catalogPaths.includes(excluded), `${excluded} não é um ponto de entrada primário`);
  }
});

test("home day card uses the canonical mobility itinerary and opens the orbital map", () => {
  assert.match(home, /\/agenda\/mobility\/day-context/);
  assert.match(home, /to="\/deslocamento"/);
  assert.match(app, /path="deslocamento" element=\{<SpaceTravelMap \/>\}/);
  assert.doesNotMatch(catalog, /"\/cursos"/);
});
