import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const read = (path) => readFileSync(new URL(`../${path}`, import.meta.url), "utf8");
const shell = read("src/components/Shell.tsx");
const frame = read("src/components/CardiologySpacesAppFrame.tsx");
const registry = read("src/lib/clinicalRouteRegistry.ts");
const home = read("src/pages/CardiologySpacesHome.tsx");
const chat = read("src/components/ChatFlutuante.tsx");
const clinicalUpdates = read("src/components/ClinicalUpdates.tsx");
const agenda = read("src/pages/Agenda.tsx");
const exams = read("src/pages/Exames.tsx");
const checklist = read("src/pages/ChecklistModelo.tsx");
const evidence = read("src/pages/Evidencia.tsx");
const disease = read("src/pages/GuiaDoenca.tsx");
const triage = read("src/pages/TriagemSintomas.tsx");
const emergency = read("src/pages/Emergencia.tsx");
const styles = read("src/styles/cardiology-spaces-app-frame.css");
const atelierStyles = read("src/styles/corvia-atelier.css");
const homeStyles = read("src/styles/cardiology-spaces-home.css");
const agendaStyles = read("src/styles/clinical-agenda-final-polish.css");
const examStyles = read("src/styles/clinical-exams-v2.css");
const rc2 = read("../.github/workflows/rc2-acceptance.yml");
const visualQa = read("../.github/workflows/visual-qa.yml");
const film = read("src/components/CorviaPresentationFilm.tsx");

test("the checklist catalog wraps complete canonical labels without masking overflow", () => {
  const content = read("src/styles/corvia-atelier-content.css");
  const page = read("src/pages/Checklists.tsx");
  const rule = content.match(/html\[data-corvia-design="atelier"\] #root \.cv-app \.cv-content \.cos-content > div:has\(#buscar-checklist\) \.painel__funcao\s*\{([^}]+)\}/)?.[1];
  assert.ok(rule, "wrap protection must be restricted to the checklist catalog");
  assert.match(rule, /min-width:\s*0;/);
  assert.match(rule, /overflow-wrap:\s*anywhere;/);
  assert.doesNotMatch(rule, /overflow(?:-x)?:\s*(?:hidden|clip)|text-overflow|line-clamp|white-space:\s*nowrap/);
  assert.match(page, /<strong>\{modelo\.condicao\}<\/strong>/);
  assert.match(page, /<span>\{modelo\.resumo \|\|/);
  assert.match(page, /onClick=\{\(\) => iniciar\(modelo\.slug\)\}/);
  assert.match(page, /to=\{`\/checklists\/\$\{modelo\.slug\}`\}/);
  assert.match(page, /to=\{`\/biblioteca\/\$\{modelo\.documento_origem\}`\}/);
});

test("the launch film is optional, accessible and excluded from the initial PWA cache", () => {
  assert.match(film, /open && <dialog/);
  assert.match(film, /controls playsInline preload="none"/);
  assert.match(film, /<track kind="captions"/);
  assert.match(film, /onCancel=\{\(\) => setOpen\(false\)\}/);
  assert.match(film, /trigger\.current\?\.focus/);
  assert.match(film, /download="CorVIA-Cardiology-Spaces\.mp4"/);
  assert.doesNotMatch(film, /autoPlay|\.play\(|onboarding-concluido|api\.post/);
  assert.match(read("vite.config.ts"), /"media\/\*\*"/);
});

test("the tour cannot ship a film button without its MP4, poster and Portuguese captions", () => {
  const filmRoot = film.match(/const FILM_ROOT = "([^"]+)"/)?.[1];
  assert.match(filmRoot, /^\/media\/corvia-apresentacao-\d{8}$/);
  const binary = (extension) => readFileSync(new URL(`../public${filmRoot}.${extension}`, import.meta.url));
  const mp4 = binary("mp4");
  assert.ok(mp4.length > 1024 * 1024, "MP4 must contain the rendered presentation, not a placeholder");
  assert.ok(mp4.length < 95 * 1024 * 1024, "MP4 must remain portable and distributable without Git LFS");
  assert.equal(mp4.toString("ascii", 4, 8), "ftyp");
  const poster = binary("jpg");
  assert.equal(poster.subarray(0, 3).toString("hex"), "ffd8ff");
  const captions = binary("vtt").toString("utf8");
  assert.match(captions, /^WEBVTT/);
  assert.match(captions, /Texto na tela/);
  assert.match(captions, /01:12\.000/);
});

test("the operational flag restores the complete legacy shell", () => {
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

test("the frame remains reachable in short and landscape viewports", () => {
  assert.match(styles, /\.cv-app\s*\{[\s\S]*?height:\s*100dvh;[\s\S]*?min-height:\s*0;/);
  assert.doesNotMatch(styles, /\.cv-app\s*\{[^}]*min-height:\s*(?:620|700)px;/);
  assert.match(styles, /@media \(min-width: 901px\) and \(max-height: 699px\)/);
  assert.match(styles, /@media \(max-width: 900px\) and \(max-height: 619px\)/);
  assert.match(styles, /\.cv-content\s*\{[^}]*overflow-y:\s*auto;/);
  assert.match(atelierStyles, /\.atelier-app\s*\{[^}]*min-height:100dvh!important;[^}]*height:auto!important/);
  assert.match(atelierStyles, /\.atelier-app \.cv-content\s*\{[^}]*max-height:none!important;[^}]*overflow:visible!important/);
  assert.match(atelierStyles, /\.atelier-app>\.cv-shell\s*\{[^}]*position:relative!important;[^}]*inset:auto!important/);
  assert.match(atelierStyles, /\.atelier-app \.cv-workspace\s*\{[^}]*position:relative!important;[^}]*inset:auto!important;[^}]*width:100%!important/,
    "the retired sidebar must not leave absolute left/top offsets in the task workspace");
});

test("the mandatory RC2 gate recognizes native Cardiology Spaces pages", () => {
  assert.match(frame, /className={`cv-app atelier-app cv-app--\$\{space\}/);
  assert.match(
    rc2,
    /document\.querySelector\('[^']*\.cv-app[^']*\.atelier-home[^']*'\)/,
    "RC2 must recognize both the native task frame and the Atelier overview",
  );
});

test("the mandatory visual gate follows the approved AppFrame geometry", () => {
  assert.doesNotMatch(
    visualQa,
    /button\[aria-label\^="Abrir o CorvIA Chat"\]|section\[aria-label="CorvIA Chat"\]/,
    "the subscriber chat is a preserved function, not a legacy emergency FAB",
  );
  assert.match(visualQa, /const emergencyUnderChrome = emergency/);
  assert.match(visualQa, /overlaps\(emergency, sidebar\) \|\| overlaps\(emergency, topbar\)/);
  assert.doesNotMatch(visualQa, /emergencyRect\.left < 200|emergencyRect\.top < 50/);
});

test("account access is a native disclosure and the skip target keeps focus visible", () => {
  assert.match(frame, /aria-controls="cv-account-panel"/);
  assert.match(frame, /aria-label=\{`\$\{accountOpen \? "Fechar" : "Abrir"\} menu da conta de/);
  assert.doesNotMatch(frame, /role="menu(?:item)?"|aria-haspopup="menu"/);
  assert.match(styles, /\.cv-content:focus\s*\{[^}]*outline:\s*2px solid var\(--cv-accent\)/);
  assert.doesNotMatch(styles, /\.cv-content:focus\s*\{\s*outline:\s*0/);
});

test("emergency protocols open the first clinical step with stable accordion semantics", () => {
  assert.match(emergency, /setSecaoAberta\(blocos\.findIndex\(\(secao\) => Boolean\(secao\.titulo\)\)\)/);
  assert.match(emergency, /aria-controls=\{`emerg-step-panel-\$\{i\}`\}/);
  assert.match(emergency, /hidden=\{s\.titulo \? secaoAberta !== i : undefined\}/);
  assert.doesNotMatch(emergency, /\{\(secaoAberta === i \|\| !s\.titulo\) && <div/);
});

test("emergency stacks above chat and unread state refreshes when the app resumes", () => {
  assert.match(styles, /\.cv-app \.corvia-chat-launch \{ right: 18px; bottom: 78px; \}/);
  assert.match(styles, /\.cv-app \.cv-emergency-fab \{ right: 44px; bottom: 132px; \}/);
  assert.match(styles, /\.cv-app \.corvia-chat-launch \{ right: 14px; bottom: 82px; \}/);
  assert.match(styles, /\.cv-app \.cv-emergency-fab \{ right: 35px; bottom: 136px; \}/);
  assert.match(chat, /api\.get<\{ total: number \}>\("\/chat\/nao-lidas"\)/);
  assert.match(chat, /window\.addEventListener\("focus", aoRetomar\)/);
  assert.match(chat, /document\.addEventListener\("visibilitychange", aoMudarVisibilidade\)/);
  assert.match(chat, /className="corvia-chat-launch__badge" aria-live="polite"/);
});

test("agenda deletion uses the numeric series id and preserves cancellation history", () => {
  assert.match(agenda, /api\.delete\(`\/agenda\/commitment-series\/\$\{id\}`\)/);
  assert.match(agenda, /removerSerie\(ajustando\.series_id/);
  assert.doesNotMatch(agenda, /api\.delete\(`\/agenda\/commitment-series\/\$\{ajustando\.id\}`\)/);
  assert.match(styles, /\.cv-app \.cv-workspace:has\(\.agenda-modal\) \{ z-index: 1301; \}/);
});

test("clinical updates remain separate from canonical text across clinical detail pages", () => {
  assert.match(clinicalUpdates, /Atualizações científicas vigentes/);
  assert.match(clinicalUpdates, /rel="noopener noreferrer"/);
  for (const page of [disease, evidence, checklist, triage]) {
    assert.match(page, /<ClinicalUpdates updates=/);
  }
});

test("tasks use a compact header with focus and catalog, not a repeated architectural scene", () => {
  assert.match(frame, /<header className="atelier-taskbar">/);
  assert.match(frame, /className="atelier-taskbar__return"/);
  assert.match(frame, /aria-pressed=\{focusMode\} onClick=\{\(\) => setFocusMode\(\(active\) => !active\)\}/);
  assert.match(frame, /onClick=\{\(event\) => openDrawer\(event\.currentTarget\)\}[^\n]*Trocar função/);
  assert.match(frame, /route\.intelligence && contextOpen && !focusMode/);
  assert.doesNotMatch(frame, /className="cv-function-deck"|className="cv-space-horizon"|<ClinicalFunctionFigure/);
  assert.match(atelierStyles, /\.atelier-app--focus \.cv-topbar\{display:none!important/);
  assert.match(atelierStyles, /\.atelier-app--focus \.atelier-taskbar\{position:sticky;top:0/);
});

test("IA para Exames remains prominent in the catalog and native route", () => {
  assert.match(frame, /data-feature=\{route\.path === "\/exames-ia" \? "exam-ai" : undefined\}/);
  assert.match(registry, /hospital: \["\/round", "\/exames-ia", "\/cardiologia-intensiva"/);
  assert.match(styles, /\.cv-drawer \.cv-nav-link\[data-feature="exam-ai"\]:not\(\.is-current\)/);
  assert.match(home, /data-feature=\{action\.to === "\/exames-ia" \? "exam-ai" : undefined\}/);
  assert.match(homeStyles, /\.spaces-catalog \.spaces-action\[data-feature="exam-ai"\]/);
  assert.doesNotMatch(styles, /data-feature="exam-ai"[^}]*?(?:width|height|padding|grid-template|transform)\s*:/);
});

test("Exames exposes the highlighted IA action with a symmetric mobile layout", () => {
  assert.match(exams, /to: "\/exames-ia", label: "IA para Exames", icon: "ecg", tone: "primary"/);
  assert.match(examStyles, /\.cc-exams-page \.cv-page-hero__actions>\.cv-action\[href="\/exames-ia"\]\{grid-column:1\/-1\}/);
});

test("agenda patient names use the canonical clinical-flow link before opening the chart", () => {
  assert.match(agenda, /className="agenda-evento__paciente"/);
  assert.match(agenda, /\/agenda-clinica\/hoje\?dia=/);
  assert.match(agenda, /`\/agenda-clinica\/\$\{appointmentId\}\/vincular`/);
  assert.match(agenda, /navigate\(`\/prontuario\?paciente=\$\{perfil\.id\}`\)/);
  assert.doesNotMatch(agenda, /patient_id[^\n]*\/prontuario/);
  assert.match(agendaStyles, /\.agenda-evento__paciente:focus-visible/);
});
