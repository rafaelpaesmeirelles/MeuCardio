import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const read = (path) => readFileSync(new URL(`../${path}`, import.meta.url), "utf8");
const home = read("src/pages/CardiologySpacesHome.tsx");
const app = read("src/App.tsx");
const styles = read("src/styles/cardiology-spaces-home.css");
const tour = read("src/pages/CardiologySpacesTour.tsx");
const tourAlias = read("src/pages/Tour.tsx");
const shell = read("src/components/Shell.tsx");
const featureFlags = read("src/lib/cardiologySpacesFeature.ts");
const accountSync = read("src/pages/Sincronizacao.tsx");
const agenda = read("src/pages/Agenda.tsx");
const myAccount = read("src/pages/MinhaConta.tsx");
const catalog = home.slice(home.indexOf("const CATALOG"), home.indexOf("const ESSENTIAL_DEFAULTS"));
const catalogPaths = [...catalog.matchAll(/(?:\["|to:\s*")((?:\/)[^"\s]+)"/g)].map((match) => match[1]);
const catalogPrimaryPaths = new Set(catalogPaths.map((path) => path.split("?")[0]));
const shellStart = app.indexOf('<Route element={<Shell />}>');
const shellEnd = app.indexOf("</Route>", shellStart);
const shellRoutes = shellStart >= 0 && shellEnd > shellStart ? app.slice(shellStart, shellEnd) : "";
const shellRoutePaths = [...shellRoutes.matchAll(/<Route\s+path="([^"]+)"/g)].map((match) => match[1]);

const requiredCatalogRoutes = [
  "/doencas", "/medicamentos", "/exames", "/calculadoras", "/emergencia", "/cardiologia-intensiva",
  "/checklists", "/triagem-sintomas", "/interacoes", "/condicoes", "/fluxogramas", "/avaliacao-preoperatoria",
  "/exames-ia", "/prontuario", "/round", "/receituario", "/documentos", "/agenda", "/corvia-mail",
  "/caixa-de-email", "/assistente", "/telediagnostico", "/material-paciente", "/evidencias", "/estudos",
  "/documentos-cientificos-ia", "/trilhas/timeline", "/trilhas", "/casos-clinicos", "/diretrizes", "/biblioteca",
  "/galeria", "/apresentacao", "/exportar", "/favoritos", "/busca", "/busca?modo=tudo-com-tudo",
  "/usuarios-online", "/sincronizacao", "/minha-conta", "/privacidade", "/termos", "/tour",
  "/verificacao-identidade", "/excluir-conta", "/admin", "/admin/usuarios", "/fila-telediagnostico",
  "/receitas-para-assinatura", "/heart-team", "/whatsapp-assistant", "/admin/operacoes-ia",
];

const nonCatalogShellRoutes = new Set([
  "cursos", // alias histórico → Trilhas
  "ecg-ia", // alias histórico → IA para Exames
  "assinatura", // fluxo técnico → tour rápido de assinatura
  "admin/usuarios-online", // alias administrativo → Rede profissional
]);

test("approved image composition is encoded as a product contract", () => {
  assert.match(home, /spaces-choice__heart/);
  assert.match(home, /spaces-home__heart/);
  assert.match(home, /<CoracaoHolografico \/>/);
  assert.match(home, /Consultório/);
  assert.match(home, /Hospital/);
  assert.match(home, /Ensino/);
  assert.match(home, /Pesquisa/);
  assert.match(home, /Gestão/);
  assert.match(home, /spaces-context-rail/);
  assert.doesNotMatch(home, /aria-label="Meus espaços"/);
  assert.match(styles, /\.spaces-door\.is-active/);
  assert.match(styles, /\.spaces-layer--now/);
  assert.match(styles, /\.spaces-dock\{[^}]*repeat\(6,minmax\(0,1fr\)\)/);
  assert.match(styles, /\.spaces-home__heart/);
});

test("portal preview is local on mouse and keyboard and only click persists selection", () => {
  assert.match(home, /const \[previewSpace, setPreviewSpace\] = useState<SpaceId \| null>\(null\)/);
  assert.match(home, /availableSpaces\.find\(\(space\) => space\.id === selectedSpace\)/);
  assert.match(home, /const preview = previewSpace === space\.id && !active/);
  assert.match(home, /data-state=\{active \? "active" : preview \? "preview" : "inactive"\}/);
  assert.match(home, /onMouseEnter=\{\(\) => setPreviewSpace\(space\.id\)\}/);
  assert.match(home, /onFocus=\{\(\) => setPreviewSpace\(space\.id\)\}/);
  assert.match(home, /onBlur=\{\(\) => setPreviewSpace\(null\)\}/);
  assert.match(home, /className="spaces-doors" onMouseLeave=\{\(\) => setPreviewSpace\(null\)\}/);
  assert.match(home, /onClick=\{\(\) => \{ setSelectedSpace\(space\.id\); setPreviewSpace\(null\); \}\}/);
});

test("user-preferred treatment replaces generic voce in the work question", () => {
  assert.match(home, /const chamamento = usuario\?\.professional_title\?\.trim\(\) \|\| nomeComTratamento\(usuario, true\)/);
  assert.match(home, /dra\|sra\|profa/);
  assert.match(home, /dr\|sr\|prof/);
  assert.match(home, /const chamamentoComArtigo = \[artigoDoChamamento, chamamento\]\.filter\(Boolean\)\.join\(" "\)/);
  assert.match(home, /`Onde \$\{chamamentoComArtigo\} vai trabalhar agora\?`/);
  assert.match(home, /`Como \$\{chamamentoComArtigo\} quer explorar o conhecimento agora\?`/);
  assert.doesNotMatch(home, /Onde você vai trabalhar agora\?/);
});

test("compact desktop keeps Meu dia entre espacos in the approved right rail", () => {
  assert.match(styles, /@media \(min-width: 901px\) and \(max-width: 1199px\)[\s\S]*grid-template-columns: 88px minmax\(0, 1fr\) 176px/);
  assert.match(styles, /@media \(min-width: 901px\) and \(max-width: 1199px\)[\s\S]*--spaces-side-height: 519px/);
  assert.doesNotMatch(styles, /@media \(min-width: 901px\) and \(max-width: 1199px\)[\s\S]*?\.spaces-day \{[\s\S]*?flex-direction: row/);
});

test("Meu dia entre espaços merges all canonical agenda sources without invented appointments", () => {
  for (const endpoint of ["/agenda/appointments", "/agenda/commitments", "/agenda/work-routines"]) {
    assert.match(home, new RegExp(endpoint.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  }
  assert.match(home, /Promise\.allSettled/);
  assert.match(home, /sameLocalDay\(item\.starts_at\)/);
  assert.match(home, /routineToAgendaItem/);
  assert.match(home, /setDayState\(results\.every/);
  assert.doesNotMatch(home, /appointment_type:\s*"Consultório"/);
  assert.doesNotMatch(home, /appointment_type:\s*"Hospital"/);
  assert.doesNotMatch(home, /"13:00"|"20:00"/);
});

test("Deslocamento uses the canonical mobility target, live geolocation and a real map escape hatch", () => {
  assert.match(home, /"\/agenda\/mobility\/prepare-next-target"/);
  assert.match(home, /"\/agenda\/mobility\/commute-target"/);
  assert.match(home, /"\/agenda\/mobility\/map-config"/);
  assert.match(home, /navigator\.geolocation\.getCurrentPosition/);
  assert.match(home, /target_key: target\.target_key/);
  assert.match(home, /https:\/\/www\.google\.com\/maps\/dir\/\?api=1&destination=/);
  assert.match(home, /<MapaDeslocamento/);
  assert.match(home, /buildMiniRouteGeometry\(route\)/);
  assert.match(home, /route\.geometry\.value/);
  assert.match(home, /route\.traffic_segments/);
  assert.match(home, /data-geometry=\{miniRoute\.actual \? "real" : "preview"\}/);
  assert.match(home, /moderate\|moderad\|medium/);
  assert.match(home, /leve\|normal/);
  assert.match(home, /spaces-orbit/);
  assert.match(styles, /\.spaces-orbit/);
  assert.match(styles, /spaces-stellar-route__traffic--traffic_jam/);
  assert.match(styles, /@keyframes spaces-flight/);
});

test("all shelf profiles are personalized without changing the approved geometry", () => {
  assert.match(home, /const ESSENTIAL_DEFAULTS: Record<ClinicalSpaceId, string\[\]>/);
  assert.match(home, /SHELF_PREFERENCES_PREFIX = "corvia:cardiology-spaces:shelves:v1"/);
  assert.match(home, /type ShelfId = "now" \| "next" \| "references" \| "essential"/);
  assert.match(home, /now: 3,[\s\S]*next: 3,[\s\S]*references: 4,[\s\S]*essential: 6/);
  assert.match(home, /shelfProfileKey\(activeMode, activeSpace\.id\)/);
  assert.match(home, /schemaVersion: 1/);
  assert.match(home, /window\.addEventListener\("storage", syncPreferences\)/);
  assert.match(home, /Salvar personalização/);
  assert.match(home, /Cancelar/);
  assert.match(home, /Restaurar esta prateleira/);
  assert.match(home, /moveShelfAction\(actionId, -1\)/);
  assert.match(home, /moveShelfAction\(actionId, 1\)/);
  assert.match(home, /selectedIds === undefined \? definition\.defaultActionIds : selectedIds/);
  assert.doesNotMatch(home, /\.\.\.definition\.defaultActionIds, \.\.\.allowedIds/);
  assert.match(home, /hasOwnProperty\.call\(preferences\.profiles\[profileKey\] \|\| \{\}, "essential"\)/);
  assert.match(home, /localStorage\.removeItem\(legacyKey\)/);
  assert.match(styles, /\.spaces-layer__edit/);
  assert.match(styles, /\.spaces-layer__edit \{[\s\S]*right: 7%/);
  assert.match(styles, /\.spaces-layer__edit \{ top: 5px; right: 4\.5%/);
  assert.match(styles, /\.spaces-personalizer__tabs/);
});

test("catalog stays complete, unique and courses are retired safely", () => {
  assert.deepEqual([...new Set(catalogPaths)], catalogPaths, "o catálogo não pode duplicar destinos");
  for (const route of requiredCatalogRoutes) assert.ok(catalogPaths.includes(route), `${route} precisa permanecer no catálogo`);
  assert.ok(!catalogPaths.includes("/cursos"), "Cursos não pode continuar como opção do produto");
  assert.doesNotMatch(home, /to:\s*"\/cursos"|\["\/cursos"/);
  assert.match(app, /<Route path="cursos" element=\{<Navigate to="\/trilhas" replace \/>\}/);
  assert.match(app, /<Route path="cursos\/:slug" element=\{<Navigate to="\/trilhas" replace \/>\}/);

  for (const route of catalogPaths) {
    const path = route.split("?")[0];
    const relative = path.slice(1).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    assert.match(app, new RegExp(`<Route path="\\/?${relative}`), `${route} precisa existir em App.tsx`);
  }
});

test("every authenticated primary Shell route is catalogued or explicitly classified as alias/technical", () => {
  assert.ok(shellStart >= 0 && shellEnd > shellStart, "o bloco autenticado do Shell precisa ser localizável");
  assert.ok(shellRoutePaths.length > 30, "o inventário autenticado não pode encolher silenciosamente");

  const primaryRoutes = [...new Set(shellRoutePaths.filter((path) => !path.includes(":") && !nonCatalogShellRoutes.has(path)))];
  const missing = primaryRoutes.filter((path) => !catalogPrimaryPaths.has(`/${path}`));
  assert.deepEqual(missing, [], `funções autenticadas fora de Todas as funções: ${missing.join(", ")}`);

  for (const alias of nonCatalogShellRoutes) {
    assert.ok(shellRoutePaths.includes(alias), `alias/técnica classificada deixou de existir: ${alias}`);
    assert.ok(!catalogPrimaryPaths.has(`/${alias}`), `alias/técnica ${alias} não deve virar função duplicada no catálogo`);
  }
});

test("tour is immersive and automatically gated only for onboarding and investor sessions", () => {
  assert.match(tour, /corvia:cardiology-spaces:tour:v4/);
  assert.match(tour, /DESLOCAMENTO/);
  assert.match(tour, /TUDO COM TUDO/);
  assert.match(tour, /CIÊNCIA & ENSINO/);
  assert.match(tour, /usuario\?\.investidor/);
  assert.match(app, /usuario\.onboarding_pendente/);
  assert.match(app, /usuario\.investidor/);
  assert.match(app, /investor-tour-session:v1/);
  assert.match(app, /<Navigate to="\/tour\?retorno=\/" replace \/>/);
  assert.match(app, /path="\/tour" element=\{<CardiologySpacesTour \/>\}/);
  assert.match(app, /path="\/tour\/cardiology-spaces" element=\{<Tour \/>\}/);
  assert.match(tourAlias, /pathname: "\/tour", search: location\.search, hash: location\.hash/);
});

test("tour return target is resolved against and confined to the current origin", () => {
  assert.match(tour, /new URL\(requested, window\.location\.origin\)/);
  assert.match(tour, /resolved\.origin !== window\.location\.origin/);
  assert.doesNotMatch(tour, /requested\.startsWith\("\/"\).*requested\.startsWith\("\/\/"\)/);
});

test("detail and alias routes stay outside the function catalog", () => {
  for (const excluded of ["/:slug", "/:id", "/heart-team/:caseId", "/admin/usuarios/:id", "/ecg-ia", "/assinatura", "/entrar", "/redefinir-senha", "/em-breve", "/cursos"]) {
    assert.ok(!catalogPaths.includes(excluded), `${excluded} não é um ponto de entrada primário`);
  }
});

test("the operational feature flag restores the complete legacy shell", () => {
  assert.match(shell, /const spacesEnabled = cardiologySpacesEnabled\(\)/);
  assert.match(shell, /spacesEnabled \? \(\s*<CardiologySpacesAppFrame \/>/);
  for (const legacySurface of [
    "<ClinicalDesktopNav />",
    "<HomePendingActionsPortal />",
    "<ShellClinicalOSLaunch />",
    "<ClinicalMobileNav />",
  ]) {
    assert.ok(shell.includes(legacySurface), `rollback precisa restaurar ${legacySurface}`);
  }
});

test("new Google account connection stays hidden behind an opt-in flag", () => {
  assert.match(featureFlags, /VITE_GOOGLE_ACCOUNT_CONNECT_VISIBLE === "true"/);
  assert.match(accountSync, /GOOGLE_ACCOUNT_CONNECT_VISIBLE && \(/);
  assert.doesNotMatch(accountSync, /item\.provider !== "google_calendar" \|\| GOOGLE_ACCOUNT_CONNECT_VISIBLE/);
  assert.match(agenda, /PROVEDORES_DE_CONEXAO/);
  assert.match(agenda, /\["microsoft_365", "apple_icloud"\]/);
  assert.match(agenda, /GOOGLE_ACCOUNT_CONNECT_VISIBLE \|\| item\.provider !== "google_calendar"/);
  assert.match(agenda, /gridTemplateColumns: `repeat\(\$\{PROVEDORES_DE_CONEXAO\.length\}/);
  assert.match(myAccount, /GOOGLE_ACCOUNT_CONNECT_VISIBLE \? "Google, Microsoft e Apple" : "Microsoft e Apple"/);
});
