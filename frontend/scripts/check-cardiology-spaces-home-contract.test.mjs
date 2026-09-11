import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { validateMobileSpaces } from "./mobile-spaces-geometry.mjs";

const read = (path) => readFileSync(new URL(`../${path}`, import.meta.url), "utf8");
const home = read("src/pages/CardiologySpacesHome.tsx");
const shelfPreferences = read("src/lib/atelierShelfPreferences.ts");
const view = read("src/components/AtelierHomeView.tsx");
const atelierStyles = read("src/styles/corvia-atelier.css");
const app = read("src/App.tsx");
const styles = read("src/styles/cardiology-spaces-home.css");
const tour = read("src/pages/CardiologySpacesTour.tsx");
const tourAlias = read("src/pages/Tour.tsx");
const shell = read("src/components/Shell.tsx");
const featureFlags = read("src/lib/cardiologySpacesFeature.ts");
const accountSync = read("src/pages/Sincronizacao.tsx");
const agenda = read("src/pages/Agenda.tsx");
const myAccount = read("src/pages/MinhaConta.tsx");
const clinicalIdentity = read("src/lib/clinicalIdentity.ts");
const catalog = home.slice(home.indexOf("const CATALOG"), home.indexOf("const ESSENTIAL_DEFAULTS"));
// Only route tuples or explicit actions, not arrays used by featured.includes(to).
const catalogPaths = [...catalog.matchAll(/\["(\/[^"\s]+)",\s*"[^"/][^"]*",\s*"[^"]+"\]|\bto:\s*"(\/[^"\s]+)"/g)].map((match) => match[1] || match[2]);
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
  "admin/atividade", // subpágina acessível pela central administrativa
]);

test("Atelier exposes all five architectural spaces independently of work mode", () => {
  for (const label of ["Consultório", "Hospital", "Ensino", "Pesquisa", "Gestão"]) assert.ok(home.includes(label));
  assert.match(home, /const availableSpaces = SPACES;/);
  assert.match(home, /<AtelierHomeView spaces=\{availableSpaces\}/);
  assert.match(view, /props\.spaces\.map/);
  assert.match(view, /\/atelier\/atelier-\$\{space\.id\}-small\.webp/);
  assert.match(view, /srcSet=\{/);
  assert.match(view, /<section className="atelier-arrival"/);
  assert.match(view, /className="atelier-space"/);
  assert.doesNotMatch(view, /CoracaoHolografico|UniverseStars|GalaxyThemeToggle|<canvas|spaces-choice__cards/);
});

test("space selection is keyboard-native and entering keeps the canonical query context", () => {
  assert.match(view, /<button[^>]*type="button"[^>]*onClick=\{\(\) => props\.onSelect\(space\.id\)\}/);
  assert.match(view, /aria-pressed=\{space\.id === props\.active\.id\}/);
  assert.match(view, /onClick=\{props\.onEnter\}/);
  assert.match(home, /onSelect=\{\(id\) => \{ setSelectedSpace\(id as SpaceId\)/);
  assert.match(home, /onEnter=\{\(\) => \{[\s\S]{0,300}setSearchParams\(\{ espaco: activeSpace\.id, modo: mode \}\)/);
  assert.match(home, /onBack=\{resetMode\}/);
  assert.match(home, /function resetMode\(\) \{ setSearchParams\(\{\}\)/);
  assert.match(view, /role="search" onSubmit=\{props\.onSearch\}/);
});

test("user-preferred treatment and name replace generic professional labels", () => {
  assert.match(home, /import \{ chamamentoComArtigo, nomeComTratamento \} from "\.\.\/lib\/clinicalIdentity"/);
  assert.match(home, /const chamamentoNaFrase = chamamentoComArtigo\(usuario, \{ curto: true \}\)/);
  assert.match(home, /const chamamentoNoInicio = chamamentoComArtigo\(usuario, \{ curto: true, inicioDeFrase: true \}\)/);
  assert.match(home, /`Onde \$\{chamamentoNaFrase\} vai trabalhar agora\?`/);
  assert.match(home, /`Como \$\{chamamentoNaFrase\} quer explorar o conhecimento agora\?`/);
  assert.match(home, /identity=\{<UserIdentity usuario=\{usuario\} \/>\}/);
  assert.match(home, /nomeComTratamento\(usuario, true\)/);
  assert.match(view, /<summary[^\n]+>\{props\.identity\}<\/summary>/);
  assert.doesNotMatch(home, /O Médico <strong>continua no centro/);

  assert.match(clinicalIdentity, /\["sra", "dra", "profa", "profa dra", "ma"\]/);
  assert.match(clinicalIdentity, /\["sr", "dr", "prof", "prof dr", "me"\]/);
  assert.match(clinicalIdentity, /usuario\?\.gender \|\| usuario\?\.genero \|\| usuario\?\.sex \|\| usuario\?\.sexo/);
  assert.match(clinicalIdentity, /const identidade = nomeComTratamento\(usuario, curto\)/);
  assert.match(clinicalIdentity, /fallback = "você"/);
});

test("responsive Atelier preserves five touch targets and the real day disclosure", () => {
  assert.match(atelierStyles, /\.atelier-mobile-spaces\{[^}]*grid-template-columns:repeat\(5,minmax\(0,1fr\)\)/);
  assert.match(atelierStyles, /\.atelier-mobile-spaces button\{[^}]*min-height:44px/);
  assert.match(atelierStyles, /\.atelier-portal\.is-selected\{[^}]*display:block/);
  assert.match(home, /<details className="atelier-day">/);
  assert.match(atelierStyles, /@media\s*\(prefers-reduced-motion:reduce\)/);
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
  assert.match(home, /function CommutePreview/);
  assert.match(home, /const hasRoute = geometryAvailable\(route\)/);
  assert.match(home, /<article ref=\{previewRef\} className="spaces-stellar-route atelier-commute"/);
  assert.match(home, /<MapaDeslocamento compact/);
  assert.doesNotMatch(home, /buildMiniRouteGeometry|decodeMiniRoutePolyline|ringedPlanet|spaces-orbit__path/);
  const map = read("src/components/MapaDeslocamento.tsx");
  assert.match(map, /"google_routes"/);
  assert.match(map, /decodeRoutePolyline/);
  assert.match(map, /route\?\.traffic_segments/);
  assert.match(map, /controlSize: 44/);
  assert.match(map, /ResizeObserver/);
  assert.match(map, /MAPS_AUTH_ERROR/);
  assert.match(read("src/lib/mobilityGeometry.ts"), /case "geometry_unavailable"/);
  assert.match(home, /moderate\|moderad\|medium/);
  assert.match(home, /leve\|normal/);
  assert.match(styles, /spaces-stellar-route__traffic--traffic_jam/);
});

test("shelf profiles retain persistence, ordering and cancellation in the Atelier layout", () => {
  assert.match(home, /const ESSENTIAL_DEFAULTS: Record<ClinicalSpaceId, string\[\]>/);
  assert.match(shelfPreferences, /SHELF_PREFERENCES_PREFIX = "corvia:cardiology-spaces:shelves:v1"/);
  assert.match(home, /type ShelfId = "now" \| "next" \| "references" \| "essential"/);
  assert.match(home, /SHELF_CAPACITIES: Record<ShelfId, number> = \{ now: 4, next: 4, references: 4, essential: 4 \}/);
  assert.match(home, /shelfProfileKey\(activeMode, activeSpace\.id\)/);
  assert.match(shelfPreferences, /schemaVersion: 1/);
  assert.match(home, /window\.addEventListener\("storage", syncPreferences\)/);
  assert.match(home, /Salvar personalização/);
  assert.match(home, /Cancelar/);
  assert.match(home, /Restaurar esta prateleira/);
  assert.match(home, /moveShelfAction\(actionId, -1\)/);
  assert.match(home, /moveShelfAction\(actionId, 1\)/);
  assert.match(home, /selectedIds === undefined \? definition\.defaultActionIds : selectedIds/);
  assert.doesNotMatch(home, /\.\.\.definition\.defaultActionIds, \.\.\.allowedIds/);
  assert.match(shelfPreferences, /hasOwnProperty\.call\(next\.profiles\[key\] \|\| \{\}, "essential"\)/);
  assert.doesNotMatch(home, /localStorage\.removeItem\(legacyKey\)/);
  assert.doesNotMatch(shelfPreferences, /removeItem\(/);
  assert.match(home, /className="atelier-previous-organizations"/);
  assert.match(home, /className="atelier-shelves"/);
  assert.match(atelierStyles, /\.atelier-shelf\{/);
  assert.match(atelierStyles, /\.spaces-personalizer__tabs/);
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

  assert.match(read("src/pages/Admin.tsx"), /<Link to="\/admin\/atividade"/, "a subpágina de atividade precisa continuar acessível pela central administrativa");

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


const geometryBox = (left, right, top=0, bottom=44) => ({left,right,top,bottom,width:right-left,height:bottom-top,visible:true});
function mobileGeometrySample() {
  const box=geometryBox;
  return {
    width:320,height:900,documentWidth:320,arrival:true,modeValue:"complete",
    header:box(0,320,0,160),brand:box(16,134,0,44),wordmark:box(16,134,4,40),
    brandAlt:"CorVIA Cardiology Spaces",brandLoaded:true,
    identity:box(144,304,0,88),avatar:box(144,188,0,44),
    identityName:{...box(196,304,0,84),text:"Profa. Dra. Alexandriana",scrollWidth:108,clientWidth:108,textRects:[{left:198,right:300,top:3,bottom:80}]},
    search:box(16,250,104,150),input:box(50,190,104,150),catalog:box(260,304,104,150),organization:box(16,180,760,804),
    spaceButtons:[0,1,2,3,4].map(index => ({box:box(16+index*58,70+index*58,290,334),text:[],selected:index===0})),
    cards:[0,1,2,3,4].map(index => ({box:{...box(16,304,360,660),visible:index===0},text:index===0 ? [{left:40,right:240,top:620,bottom:648}] : [],selected:index===0,image:{loaded:true,alt:"Interior do espaço"}})),
    actions:[],
  };
}

test("mobile geometry rejects hidden wordmarks and clipped architecture even when body overflow is masked", () => {
  const sample=mobileGeometrySample();
  assert.deepEqual(validateMobileSpaces(sample), []);
  assert.ok(validateMobileSpaces({...sample,wordmark:{...sample.wordmark,visible:false}}).includes("wordmark: not visible"));
  assert.ok(validateMobileSpaces({...sample,brandLoaded:false}).includes("wordmark: missing accessible or loaded branding"));
  assert.ok(validateMobileSpaces({...sample,header:{...sample.header,top:-58,bottom:102}}).includes("header: outside vertical viewport"));
  assert.ok(validateMobileSpaces({...sample,cards:[{...sample.cards[0],box:geometryBox(16,380,360,660)},...sample.cards.slice(1)]}).includes("card 0: outside viewport"));
  assert.ok(validateMobileSpaces({...sample,cards:[{...sample.cards[0],text:[{left:90,right:330,top:620,bottom:648}]},...sample.cards.slice(1)]}).includes("card 0: clipped text"));
  assert.ok(validateMobileSpaces({...sample,catalog:geometryBox(110,154)}).includes("brand/catalog: overlap"));
  assert.ok(validateMobileSpaces({...sample,organization:geometryBox(16,180,760,800)}).includes("organization: touch target below 44px"));
  assert.ok(validateMobileSpaces({...sample,spaceButtons:sample.spaceButtons.slice(1)}).includes("arrival: expected five mobile spaces"));
  assert.ok(validateMobileSpaces({...sample,spaceButtons:sample.spaceButtons.map(item=>({...item,selected:false}))}).includes("arrival: expected one selected mobile space"));
  assert.ok(validateMobileSpaces({...sample,spaceButtons:[{...sample.spaceButtons[0],text:[{left:16,right:90,top:300,bottom:322}]},...sample.spaceButtons.slice(1)]}).includes("space button 0: clipped text"));
  assert.ok(validateMobileSpaces({...sample,cards:[{...sample.cards[0],image:{loaded:false,alt:"Interior"}},...sample.cards.slice(1)]}).includes("card 0: missing loaded accessible interior"));
  const interior={...sample,arrival:false,cards:[],spaceButtons:[],actions:Array.from({length:12},(_,index)=>({box:geometryBox(16,304,350+index*110,450+index*110),text:[],href:"/agenda"}))};
  assert.deepEqual(validateMobileSpaces(interior),[]);
  assert.ok(validateMobileSpaces({...interior,actions:interior.actions.slice(1)}).includes("interior: expected 12 actions"));
  assert.deepEqual(validateMobileSpaces({...interior,modeValue:"essential",actions:interior.actions.slice(0,8)}),[]);
  assert.deepEqual(validateMobileSpaces({...interior,modeValue:"scientific",actions:interior.actions.slice(0,8)}),[]);
  assert.ok(validateMobileSpaces({...interior,actions:[{...interior.actions[0],href:"//example.org"},...interior.actions.slice(1)]}).includes("action 0: missing same-origin route"));
});

test("mobile identity gate rejects missing, truncated and overlapping professional names", () => {
  const sample=mobileGeometrySample();
  const name=sample.identityName;
  assert.deepEqual(validateMobileSpaces(sample,name.text),[]);
  assert.ok(validateMobileSpaces({...sample,identityName:{...name,visible:false}},name.text).includes("identityName: not visible"));
  assert.ok(validateMobileSpaces({...sample,identityName:{...name,text:"D."}},name.text).includes("identity name: unexpected text"));
  assert.ok(validateMobileSpaces({...sample,identityName:{...name,scrollWidth:180}},name.text).includes("identity name: clipped text"));
  assert.ok(validateMobileSpaces({...sample,identityName:{...name,textRects:[{left:204,right:340,top:3,bottom:80}]}},name.text).includes("identity name: clipped text"));
  assert.ok(validateMobileSpaces({...sample,identityName:{...name,...geometryBox(160,304,20,52)}},name.text).includes("identity name/avatar: overlap"));
});
