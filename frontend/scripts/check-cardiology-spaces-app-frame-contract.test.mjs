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
const homeStyles = read("src/styles/cardiology-spaces-home.css");
const agendaStyles = read("src/styles/clinical-agenda-final-polish.css");
const examStyles = read("src/styles/clinical-exams-v2.css");
const rc2 = read("../.github/workflows/rc2-acceptance.yml");
const visualQa = read("../.github/workflows/visual-qa.yml");

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
});

test("the mandatory RC2 gate recognizes native Cardiology Spaces pages", () => {
  assert.match(frame, /className={`cv-app cv-app--\$\{space\}/);
  assert.match(
    rc2,
    /document\.querySelector\('\.cv-app, \.clinical-os, \.spaces-home'\)/,
    "RC2 must accept the native .cv-app root used by the five approved pages",
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

test("IA para Exames is prominent without changing deck or dock geometry", () => {
  assert.match(frame, /data-feature=\{route\.path === "\/exames-ia" \? "exam-ai" : undefined\}/);
  assert.match(registry, /hospital: \["\/round", "\/exames-ia", "\/cardiologia-intensiva"/);
  assert.match(styles, /\.cv-function-deck \.cv-nav-link\[data-feature="exam-ai"\]:not\(\.is-current\)/);
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
