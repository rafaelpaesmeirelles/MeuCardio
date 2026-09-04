import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type PointerEvent as ReactPointerEvent,
  type TouchEvent as ReactTouchEvent,
} from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import CardiologySpaceScene, { type CardiologySpaceSceneId } from "../components/CardiologySpaceScene";
import Icone, { type NomeIcone } from "../components/Icone";
import { CoracaoHolografico } from "../components/PreHomeBrand";
import { api, ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";
import { nomeComTratamento } from "../lib/clinicalIdentity";
import "../styles/cardiology-spaces-tour.css";

const TOUR_KEY = "corvia:cardiology-spaces:tour:v4";
const INVESTOR_TOUR_SESSION_KEY = "corvia:cardiology-spaces:investor-tour-session:v1";

type ExperienceMode = "complete" | "essential" | "scientific";
type ClinicalSpaceId = "consultorio" | "hospital" | "ensino" | "pesquisa" | "gestao";
type ScientificSpaceId = "descobrir" | "evidencias" | "aprender" | "ensinar" | "produzir";
type ChapterId = "experience" | "spaces" | "layers" | "day" | "relations" | "science" | "essential";

type TourSpace = { id: ClinicalSpaceId; label: string; eyebrow: string; icon: NomeIcone; tone: string };
type Chapter = { id: ChapterId; eyebrow: string; title: string; text: string; detail: string; icon: NomeIcone };
type Action = { label: string; icon: NomeIcone };

const CLINICAL_SPACES: TourSpace[] = [
  { id: "consultorio", label: "Consultório", eyebrow: "Prática clínica", icon: "clinica", tone: "#22d7e6" },
  { id: "hospital", label: "Hospital", eyebrow: "Decisão aguda", icon: "emergencia", tone: "#4d82ff" },
  { id: "ensino", label: "Ensino", eyebrow: "Formação", icon: "curso", tone: "#9b6cf7" },
  { id: "pesquisa", label: "Pesquisa", eyebrow: "Ciência e evidência", icon: "evidencia", tone: "#ec5d92" },
  { id: "gestao", label: "Gestão", eyebrow: "Operação integrada", icon: "gestao", tone: "#36c8c4" },
];

const SCIENTIFIC_SPACES: Array<{ id: ScientificSpaceId; label: string; detail: string; icon: NomeIcone; scene: CardiologySpaceSceneId }> = [
  { id: "descobrir", label: "Descobrir", detail: "Encontre relações antes de procurar uma tela.", icon: "busca", scene: "descobrir" },
  { id: "evidencias", label: "Evidências", detail: "Valide decisões com fontes rastreáveis.", icon: "evidencia", scene: "evidencias" },
  { id: "aprender", label: "Aprender", detail: "Transforme conhecimento em jornada clínica.", icon: "conhecimento", scene: "aprender" },
  { id: "ensinar", label: "Ensinar", detail: "Organize casos, aulas e raciocínio.", icon: "curso", scene: "ensinar" },
  { id: "produzir", label: "Produzir", detail: "Converta contexto em material científico.", icon: "documento", scene: "produzir" },
];

const ACTIONS_BY_SPACE: Record<ClinicalSpaceId, { now: Action[]; next: Action[]; references: Action[] }> = {
  consultorio: {
    now: [{ label: "Abrir agenda", icon: "agenda" }, { label: "Prescrever", icon: "prescricao" }, { label: "Prontuário", icon: "pacientes" }],
    next: [{ label: "Solicitar exames", icon: "clinica" }, { label: "Revisar exames", icon: "ecg" }, { label: "Avaliação pré-operatória", icon: "check" }],
    references: [{ label: "Medicamentos", icon: "medicamento" }, { label: "Calculadoras", icon: "calculadora" }, { label: "Diretrizes", icon: "conhecimento" }],
  },
  hospital: {
    now: [{ label: "Abrir round", icon: "round" }, { label: "Registrar evolução", icon: "documento" }, { label: "Prescrever", icon: "prescricao" }],
    next: [{ label: "Revisar exames", icon: "ecg" }, { label: "Documentos", icon: "documento" }, { label: "Checklists", icon: "check" }],
    references: [{ label: "Emergências", icon: "emergencia" }, { label: "Diretrizes", icon: "conhecimento" }, { label: "Interações", icon: "medicamento" }],
  },
  ensino: {
    now: [{ label: "Continuar trilha", icon: "curso" }, { label: "Revisar caso", icon: "clinica" }, { label: "Abrir biblioteca", icon: "conhecimento" }],
    next: [{ label: "Casos clínicos", icon: "pacientes" }, { label: "Timeline", icon: "sincronizar" }, { label: "Material ao paciente", icon: "documento" }],
    references: [{ label: "Diretrizes", icon: "conhecimento" }, { label: "Exames", icon: "ecg" }, { label: "Galeria", icon: "camera" }],
  },
  pesquisa: {
    now: [{ label: "Explorar evidências", icon: "evidencia" }, { label: "Buscar estudos", icon: "busca" }, { label: "Documento IA", icon: "assistente" }],
    next: [{ label: "Biblioteca", icon: "conhecimento" }, { label: "Favoritos", icon: "favorito" }, { label: "Exportar", icon: "documento" }],
    references: [{ label: "Diretrizes", icon: "conhecimento" }, { label: "Medicamentos", icon: "medicamento" }, { label: "Calculadoras", icon: "calculadora" }],
  },
  gestao: {
    now: [{ label: "Ver indicadores", icon: "indicadores" }, { label: "Organizar agenda", icon: "agenda" }, { label: "Pendências", icon: "notificacao" }],
    next: [{ label: "Documentos", icon: "documento" }, { label: "Usuários", icon: "pacientes" }, { label: "Sincronização", icon: "sincronizar" }],
    references: [{ label: "Relatórios", icon: "indicadores" }, { label: "Minha conta", icon: "conta" }, { label: "Suporte", icon: "assistente" }],
  },
};

const CHAPTERS: Chapter[] = [
  { id: "experience", eyebrow: "01 · ESCOLHA A EXPERIÊNCIA", title: "O CorVIA muda de profundidade sem perder continuidade.", text: "Completo, Essencial e Ciência & Ensino não são produtos separados. São três perspectivas do mesmo sistema, ajustadas ao momento do Médico.", detail: "Experimente os três modos dentro do próprio tour.", icon: "configuracao" },
  { id: "spaces", eyebrow: "02 · CINCO AMBIENTES", title: "Entre no lugar em que o trabalho realmente acontece.", text: "Consultório, Hospital, Ensino, Pesquisa e Gestão possuem atmosfera, prioridade e repertório próprios. Selecione cada portal para sentir a transição.", detail: "As cenas são as mesmas da Home Cardiology Spaces aprovada.", icon: "clinica" },
  { id: "layers", eyebrow: "03 · PRIORIDADE EM CAMADAS", title: "Agora, em seguida e referências se reorganizam com o contexto.", text: "O sistema não despeja funções sobre o Médico. Ele aproxima o que importa agora e mantém o restante ao alcance, sem esconder o CorVIA.", detail: "Troque o espaço para ver as prateleiras se recombinarem.", icon: "agenda" },
  { id: "day", eyebrow: "04 · MEU DIA ENTRE ESPAÇOS", title: "A rotina deixa de ser uma lista e vira uma jornada contínua.", text: "Compromissos, locais e deslocamentos formam um único trilho. A rota orbital preserva a identidade CorVIA; a navegação real orienta o trajeto.", detail: "Dados demonstrativos e seguros são usados nesta experiência.", icon: "rota" },
  { id: "relations", eyebrow: "05 · TUDO COM TUDO", title: "Conhecimento conectado aparece ao redor da sua pergunta.", text: "Doenças, exames, medicamentos, diretrizes, evidências, casos e documentos deixam de ser ilhas e passam a formar contexto.", detail: "Toque nos nós para explorar o raciocínio conectado.", icon: "sincronizar" },
  { id: "science", eyebrow: "06 · CIÊNCIA & ENSINO", title: "Descobrir, validar, aprender, ensinar e produzir na mesma órbita.", text: "O conhecimento cardiovascular mantém profundidade científica, mas ganha uma jornada clara entre descoberta, evidência e produção.", detail: "Selecione uma jornada para transformar o ambiente.", icon: "conhecimento" },
  { id: "essential", eyebrow: "07 · O SEU CORVIA", title: "Essencial é pessoal — e continua ligado ao sistema completo.", text: "Cada espaço pode destacar as ferramentas que mais importam para a sua rotina. Personalizar muda a proximidade, nunca a disponibilidade.", detail: "Ative e desative os exemplos para sentir a personalização.", icon: "conta" },
];

const RELATIONS: Array<{ label: string; icon: NomeIcone; detail: string }> = [
  { label: "Doença", icon: "doencas", detail: "Contexto clínico e diferenciais" },
  { label: "Exame", icon: "ecg", detail: "Achados e interpretação" },
  { label: "Medicamento", icon: "medicamento", detail: "Dose, evidência e segurança" },
  { label: "Diretriz", icon: "conhecimento", detail: "Recomendação rastreável" },
  { label: "Evidência", icon: "evidencia", detail: "Estudos que sustentam a decisão" },
  { label: "Calculadora", icon: "calculadora", detail: "Estratificação aplicada" },
  { label: "Caso", icon: "pacientes", detail: "Aprendizado contextual" },
  { label: "Documento", icon: "documento", detail: "Da decisão à execução" },
];

const ESSENTIALS: Action[] = [
  { label: "Prescrever", icon: "prescricao" }, { label: "Solicitar exames", icon: "clinica" },
  { label: "Prontuário", icon: "pacientes" }, { label: "Calculadoras", icon: "calculadora" },
  { label: "Diretrizes", icon: "conhecimento" }, { label: "Interações", icon: "medicamento" },
];

const MODE_COPY: Record<ExperienceMode, { label: string; detail: string; accent: string }> = {
  complete: { label: "Completo", detail: "Agora · Em seguida · Referências", accent: "#22d7e6" },
  essential: { label: "Essencial", detail: "Agora · Meus essenciais", accent: "#4d82ff" },
  scientific: { label: "Ciência & Ensino", detail: "Descobrir · Validar · Produzir", accent: "#9b6cf7" },
};

function Brand() {
  return <span className="cst__brand"><img src="/corvia-mark-canonical.svg" alt="" /><span><strong>Cor<b>VIA</b></strong><small>CARDIOLOGY SPACES</small></span></span>;
}

function SpaceField({ compact = false }: { compact?: boolean }) {
  return <div className={`cst-space-field${compact ? " is-compact" : ""}`} aria-hidden="true">
    <div className="cst-space-field__heart"><CoracaoHolografico /></div>
    {CLINICAL_SPACES.map((space, index) => <span key={space.id} className={`cst-space-field__node is-${space.id}`} style={{ "--space-tone": space.tone, "--space-index": index } as CSSProperties}><Icone nome={space.icon} /><b>{space.label}</b></span>)}
    <svg viewBox="0 0 680 390" preserveAspectRatio="none"><path d="M340 194C253 52 107 66 67 153"/><path d="M340 194C170 164 89 244 62 312"/><path d="M340 194C340 92 340 54 340 38"/><path d="M340 194C427 52 573 66 613 153"/><path d="M340 194C510 164 591 244 618 312"/></svg>
  </div>;
}

function ExperienceVisual({ mode, onMode }: { mode: ExperienceMode; onMode: (mode: ExperienceMode) => void }) {
  const selected = MODE_COPY[mode];
  return <div className="cst-experience" style={{ "--experience-accent": selected.accent } as CSSProperties}>
    <div className="cst-experience__top"><span>Como você quer trabalhar agora?</span><div role="tablist" aria-label="Experiências do CorVIA">{(Object.keys(MODE_COPY) as ExperienceMode[]).map((item) => <button key={item} type="button" role="tab" aria-selected={mode === item} className={mode === item ? "is-active" : ""} onClick={() => onMode(item)}>{MODE_COPY[item].label}</button>)}</div></div>
    <div className="cst-experience__stage"><div className="cst-experience__mode-mark"><Icone nome={mode === "scientific" ? "conhecimento" : mode === "essential" ? "favorito" : "sincronizar"}/></div><p>{selected.label}</p><strong>{mode === "scientific" ? "O conhecimento vira jornada." : mode === "essential" ? "Sua rotina ganha foco." : "Todos os contextos permanecem visíveis."}</strong><span>{selected.detail}</span><div className="cst-experience__shelves"><i/><i/><i className={mode === "essential" ? "is-hidden" : ""}/></div></div>
  </div>;
}

function SpacesVisual({ selected, onSelect }: { selected: ClinicalSpaceId; onSelect: (space: ClinicalSpaceId) => void }) {
  return <div className="cst-portals" role="group" aria-label="Ambientes Cardiology Spaces">{CLINICAL_SPACES.map((space) => <button type="button" key={space.id} className={selected === space.id ? "is-active" : ""} style={{ "--space-tone": space.tone } as CSSProperties} aria-pressed={selected === space.id} onClick={() => onSelect(space.id)}><span className="cst-portals__label"><Icone nome={space.icon}/>{space.label}</span><span className="cst-portals__scene"><CardiologySpaceScene space={space.id}/></span><small>{space.eyebrow}</small></button>)}</div>;
}

function Shelf({ title, actions, active = false }: { title: string; actions: Action[]; active?: boolean }) {
  return <div className={`cst-shelf${active ? " is-active" : ""}`}><span>{title}</span>{actions.map((action) => <b key={action.label}><Icone nome={action.icon}/>{action.label}</b>)}</div>;
}

function LayersVisual({ selected, onSelect }: { selected: ClinicalSpaceId; onSelect: (space: ClinicalSpaceId) => void }) {
  const active = CLINICAL_SPACES.find((space) => space.id === selected) ?? CLINICAL_SPACES[0];
  const actions = ACTIONS_BY_SPACE[selected];
  return <div className="cst-layers-live" style={{ "--space-tone": active.tone } as CSSProperties}>
    <div className="cst-layers-live__backdrop"><CardiologySpaceScene space={selected}/></div>
    <div className="cst-layers-live__spaces" role="tablist" aria-label="Alterar ambiente das prateleiras">{CLINICAL_SPACES.map((space) => <button key={space.id} role="tab" aria-selected={space.id === selected} type="button" onClick={() => onSelect(space.id)}><Icone nome={space.icon}/><span>{space.label}</span></button>)}</div>
    <div className="cst-layers-live__title"><span>Meu espaço</span><strong>{active.label}</strong><small>{active.eyebrow}</small></div>
    <div className="cst-layers-live__stack"><Shelf title="AGORA" actions={actions.now} active/><Shelf title="EM SEGUIDA" actions={actions.next}/><Shelf title="REFERÊNCIAS" actions={actions.references}/></div>
  </div>;
}

function DayVisual() {
  return <div className="cst-day-live">
    <div className="cst-day-live__timeline"><header><Icone nome="relogio"/><span><small>SEU DIA ENTRE ESPAÇOS</small><strong>Uma jornada. Vários contextos.</strong></span></header><div className="cst-day-live__event is-blue"><i/><span><b>Hospital</b><small>07:00–13:00 · Round e enfermaria</small></span><em>AGORA</em></div><div className="cst-day-live__event is-cyan"><i/><span><b>Consultório</b><small>15:00–18:00 · Atendimento</small></span><em>EM SEGUIDA</em></div><div className="cst-day-live__event is-violet"><i/><span><b>Estudo</b><small>20:00 · Trilha de insuficiência cardíaca</small></span></div></div>
    <div className="cst-day-live__route"><div className="cst-day-live__route-head"><Icone nome="rota"/><span><small>DESLOCAMENTO</small><strong>Hospital → Consultório</strong></span><b>18 min</b></div><div className="cst-day-live__universe"><span className="origin"><i/><small>AGORA</small></span><span className="destination"><i/><small>DESTINO</small></span><svg viewBox="0 0 520 180" preserveAspectRatio="none"><path className="glow" d="M55 145C152 15 364 7 470 128"/><path className="route" d="M55 145C152 15 364 7 470 128"/></svg><i className="cst-day-live__ship"/><i className="cst-day-live__planet one"/><i className="cst-day-live__planet two"/><i className="cst-day-live__planet three"/></div><div className="cst-day-live__metrics"><span><b>12 km</b><small>distância</small></span><span><b>13:42</b><small>saída sugerida</small></span><span><b>Moderado</b><small>trânsito</small></span></div></div>
  </div>;
}

function RelationsVisual({ selected, onSelect }: { selected: number; onSelect: (index: number) => void }) {
  return <div className="cst-relations-live"><svg viewBox="0 0 720 520" preserveAspectRatio="none" aria-hidden="true">{RELATIONS.map((_, index) => { const angle = (index / RELATIONS.length) * Math.PI * 2 - Math.PI / 2; const x = 360 + Math.cos(angle) * 250; const y = 260 + Math.sin(angle) * 178; return <path key={index} className={selected === index ? "is-active" : ""} d={`M360 260 Q${(360 + x) / 2 + Math.sin(angle) * 42} ${(260 + y) / 2 - Math.cos(angle) * 42} ${x} ${y}`}/>; })}</svg><div className="cst-relations-live__core"><Icone nome="sincronizar"/><b>Tudo com Tudo</b><small>Relações, evidências e funções</small></div>{RELATIONS.map((relation, index) => <button key={relation.label} type="button" className={selected === index ? "is-active" : ""} style={{ "--relation-index": index } as CSSProperties} aria-pressed={selected === index} onClick={() => onSelect(index)}><Icone nome={relation.icon}/><span><b>{relation.label}</b><small>{selected === index ? relation.detail : "Explorar relação"}</small></span></button>)}</div>;
}

function ScienceVisual({ selected, onSelect }: { selected: ScientificSpaceId; onSelect: (space: ScientificSpaceId) => void }) {
  const active = SCIENTIFIC_SPACES.find((space) => space.id === selected) ?? SCIENTIFIC_SPACES[0];
  return <div className="cst-science-live"><div className="cst-science-live__search"><Icone nome="busca"/><span>Tudo com Tudo — conhecimento cardiovascular conectado</span><b>↗</b></div><div className="cst-science-live__portals" role="tablist" aria-label="Jornadas de Ciência e Ensino">{SCIENTIFIC_SPACES.map((space) => <button key={space.id} type="button" role="tab" aria-selected={space.id === selected} className={space.id === selected ? "is-active" : ""} onClick={() => onSelect(space.id)}><span><Icone nome={space.icon}/>{space.label}</span><i><CardiologySpaceScene space={space.scene}/></i></button>)}</div><div className="cst-science-live__journey"><span><small>MINHA JORNADA</small><b>{active.label}</b></span><strong>{active.detail}</strong><div><em>Explorar</em><em>Aprofundar</em><em>Conectar</em></div></div></div>;
}

function EssentialVisual({ selected, onToggle, callName }: { selected: string[]; onToggle: (label: string) => void; callName: string }) {
  return <div className="cst-essential-live"><div className="cst-essential-live__identity"><span><Icone nome="conta"/></span><b>{callName}</b><small>Meu espaço ativo</small></div><header><span><small>MEUS ESSENCIAIS</small><strong>Consultório</strong></span><em>{selected.length} selecionados</em></header><div className="cst-essential-live__grid">{ESSENTIALS.map((action) => <button key={action.label} type="button" className={selected.includes(action.label) ? "is-active" : ""} aria-pressed={selected.includes(action.label)} onClick={() => onToggle(action.label)}><span><Icone nome={action.icon}/></span><b>{action.label}</b><i><Icone nome={selected.includes(action.label) ? "check" : "adicionar"}/></i></button>)}</div><div className="cst-essential-live__continuity"><Icone nome="sincronizar"/><span><b>O ambiente muda.</b><small>O Médico continua no centro.</small></span></div></div>;
}

function ImmersiveVisual({ chapter, mode, setMode, selectedSpace, setSelectedSpace, selectedRelation, setSelectedRelation, selectedScientific, setSelectedScientific, essentials, toggleEssential, callName }: { chapter: ChapterId; mode: ExperienceMode; setMode: (mode: ExperienceMode) => void; selectedSpace: ClinicalSpaceId; setSelectedSpace: (space: ClinicalSpaceId) => void; selectedRelation: number; setSelectedRelation: (index: number) => void; selectedScientific: ScientificSpaceId; setSelectedScientific: (space: ScientificSpaceId) => void; essentials: string[]; toggleEssential: (label: string) => void; callName: string }) {
  if (chapter === "experience") return <ExperienceVisual mode={mode} onMode={setMode}/>;
  if (chapter === "spaces") return <SpacesVisual selected={selectedSpace} onSelect={setSelectedSpace}/>;
  if (chapter === "layers") return <LayersVisual selected={selectedSpace} onSelect={setSelectedSpace}/>;
  if (chapter === "day") return <DayVisual/>;
  if (chapter === "relations") return <RelationsVisual selected={selectedRelation} onSelect={setSelectedRelation}/>;
  if (chapter === "science") return <ScienceVisual selected={selectedScientific} onSelect={setSelectedScientific}/>;
  return <EssentialVisual selected={essentials} onToggle={toggleEssential} callName={callName}/>;
}

export default function CardiologySpacesTour() {
  const { usuario } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const [step, setStep] = useState(0);
  const [finishing, setFinishing] = useState(false);
  const [finishError, setFinishError] = useState("");
  const [mode, setMode] = useState<ExperienceMode>("complete");
  const [selectedSpace, setSelectedSpace] = useState<ClinicalSpaceId>("consultorio");
  const [selectedRelation, setSelectedRelation] = useState(3);
  const [selectedScientific, setSelectedScientific] = useState<ScientificSpaceId>("descobrir");
  const [essentials, setEssentials] = useState(["Prescrever", "Solicitar exames", "Prontuário"]);
  const touchStart = useRef<{ x: number; y: number } | null>(null);
  const quickTour = params.get("modo") === "quick";
  const chapters = useMemo(
    () => quickTour ? CHAPTERS.filter((chapter) => ["spaces", "layers", "day"].includes(chapter.id)) : CHAPTERS,
    [quickTour],
  );
  const total = chapters.length + 2;
  const assinaturaSemAcesso = params.get("origem") === "assinatura" && !usuario?.product_access;
  const requested = params.get("retorno") || (assinaturaSemAcesso ? "/em-breve" : "/");
  const destination = useMemo(() => { try { const resolved = new URL(requested, window.location.origin); if (resolved.origin !== window.location.origin) return "/"; return `${resolved.pathname}${resolved.search}${resolved.hash}`; } catch { return "/"; } }, [requested]);
  const manual = !usuario?.onboarding_pendente && !usuario?.investidor;
  const callName = nomeComTratamento(usuario, true);
  const welcome = step === 0;
  const final = step === total - 1;
  const current = !welcome && !final ? chapters[step - 1] : null;
  const goTo = useCallback((nextStep: number) => setStep(Math.max(0, Math.min(nextStep, total - 1))), [total]);
  const next = useCallback(() => setStep((currentStep) => Math.min(currentStep + 1, total - 1)), [total]);
  const back = useCallback(() => setStep((currentStep) => Math.max(currentStep - 1, 0)), []);
  const leave = useCallback(() => navigate(destination, { replace: true }), [destination, navigate]);

  async function finish() {
    if (finishing) return;
    setFinishing(true);
    setFinishError("");
    try {
      if (usuario?.onboarding_pendente) await api.post("/auth/me/onboarding-concluido", {});
      localStorage.setItem(TOUR_KEY, "seen");
      if (usuario?.investidor) sessionStorage.setItem(INVESTOR_TOUR_SESSION_KEY, "seen");
      if (usuario?.onboarding_pendente) window.location.replace(destination);
      else leave();
    } catch (error) {
      setFinishError(error instanceof ApiError ? "Não foi possível concluir o tour. Tente novamente." : "Ocorreu uma falha ao abrir o Cardiology Spaces.");
      setFinishing(false);
    }
  }

  useEffect(() => {
    function keyboard(event: KeyboardEvent) {
      const target = event.target as HTMLElement | null;
      if (target?.matches("input, textarea, select, button, a, [contenteditable='true']")) return;
      if (event.key === "ArrowRight" || event.key === "PageDown") { event.preventDefault(); next(); }
      if (event.key === "ArrowLeft" || event.key === "PageUp") { event.preventDefault(); back(); }
      if (event.key === "Home") { event.preventDefault(); goTo(0); }
      if (event.key === "End") { event.preventDefault(); goTo(total - 1); }
      if (event.key === "Escape" && manual) leave();
    }
    window.addEventListener("keydown", keyboard);
    return () => window.removeEventListener("keydown", keyboard);
  }, [back, goTo, leave, manual, next, total]);

  function handlePointerMove(event: ReactPointerEvent<HTMLElement>) {
    if (event.pointerType === "touch") return;
    const rect = event.currentTarget.getBoundingClientRect();
    event.currentTarget.style.setProperty("--pointer-x", ((((event.clientX - rect.left) / rect.width) - .5) * 2).toFixed(3));
    event.currentTarget.style.setProperty("--pointer-y", ((((event.clientY - rect.top) / rect.height) - .5) * 2).toFixed(3));
  }
  function handleTouchStart(event: ReactTouchEvent<HTMLElement>) {
    const target = event.target as HTMLElement | null;
    if (target?.closest("button, a, input, select, textarea, [role='tablist'], .cst-portals, .cst-science-live__portals, .cst-essential-live__grid")) {
      touchStart.current = null;
      return;
    }
    const touch = event.touches[0];
    touchStart.current = touch ? { x: touch.clientX, y: touch.clientY } : null;
  }
  function handleTouchEnd(event: ReactTouchEvent<HTMLElement>) { const start = touchStart.current; const touch = event.changedTouches[0]; touchStart.current = null; if (!start || !touch) return; const dx = touch.clientX - start.x; const dy = touch.clientY - start.y; if (Math.abs(dx) < 58 || Math.abs(dx) < Math.abs(dy) * 1.15) return; if (dx < 0) next(); else back(); }
  function toggleEssential(label: string) { setEssentials((items) => items.includes(label) ? items.filter((item) => item !== label) : [...items, label].slice(0, 5)); }

  return <main className="cst" data-step={current?.id ?? (welcome ? "welcome" : "final")} onPointerMove={handlePointerMove} onTouchStart={handleTouchStart} onTouchEnd={handleTouchEnd}>
    <div className="cst__cosmos" aria-hidden="true"><i className="cst__nebula cst__nebula--one"/><i className="cst__nebula cst__nebula--two"/><div className="cst__stars">{Array.from({ length: 42 }).map((_, index) => <i key={index} style={{ "--star-index": index } as CSSProperties}/>)}</div><div className="cst__horizon"/></div>
    <header className="cst__header"><Brand/><span className="cst__chapter-name"><i/> TOUR IMERSIVO · {welcome ? "BOAS-VINDAS" : final ? "CONTINUIDADE" : current?.eyebrow.split(" · ")[1]}</span>{manual ? <button type="button" onClick={leave}>Sair</button> : <em>{usuario?.investidor ? "MODO INVESTIDOR" : "NOVO USUÁRIO"}</em>}</header>
    <div className="cst__progress" aria-hidden="true"><i style={{ width: `${((step + 1) / total) * 100}%` }}/></div>
    <div className="cst__stage" key={current?.id ?? (welcome ? "welcome" : "final")}>
      {welcome && <section className="cst__welcome" aria-labelledby="cst-welcome-title"><div className="cst__welcome-field"><SpaceField/></div><div className="cst__welcome-copy"><p>O MÉDICO CONTINUA NO CENTRO</p><h1 id="cst-welcome-title">Bem-vindo, {callName}.<br/><strong>Entre no universo Cardiology Spaces.</strong></h1><span>O ambiente muda, o conhecimento se conecta e o CorVIA acompanha a sua jornada sem romper o contexto.</span><button type="button" onClick={next}>Iniciar experiência <Icone nome="seta"/></button><small>Use as setas, deslize a tela ou explore os elementos destacados.</small></div></section>}
      {current && <section className="cst__step" aria-labelledby={`cst-title-${current.id}`}><div className="cst__visual-shell"><div className="cst__visual"><ImmersiveVisual chapter={current.id} mode={mode} setMode={setMode} selectedSpace={selectedSpace} setSelectedSpace={setSelectedSpace} selectedRelation={selectedRelation} setSelectedRelation={setSelectedRelation} selectedScientific={selectedScientific} setSelectedScientific={setSelectedScientific} essentials={essentials} toggleEssential={toggleEssential} callName={callName}/></div><span className="cst__interaction-hint"><i/> {current.id === "day" ? "DEMONSTRAÇÃO ANIMADA" : "INTERATIVO · TOQUE PARA EXPLORAR"}</span></div><article><div className="cst__step-index"><span><Icone nome={current.icon}/></span><small>{String(step).padStart(2, "0")} / {String(chapters.length).padStart(2, "0")}</small></div><p>{quickTour ? current.eyebrow.replace(/^\d+ · /, "") : current.eyebrow}</p><h1 id={`cst-title-${current.id}`}>{current.title}</h1><div>{current.text}</div><small>{current.detail}</small></article></section>}
      {final && <section className="cst__final" aria-labelledby="cst-final-title"><div className="cst__final-field"><SpaceField compact/></div><div className="cst__final-copy"><img src="/corvia-mark-canonical.svg" alt=""/><p>AGORA COMEÇA A ROTINA REAL</p><h1 id="cst-final-title">Escolha o seu espaço.<br/><strong>O CorVIA continua com você.</strong></h1><span>{usuario?.investidor ? "A demonstração abre em modo somente leitura. Este tour será exibido novamente em uma nova sessão do perfil Investidor." : "Você pode rever esta experiência a qualquer momento pelo menu do Cardiology Spaces."}</span><button type="button" onClick={() => void finish()} disabled={finishing}>{finishing ? "Abrindo…" : "Entrar no Cardiology Spaces"} <Icone nome="seta"/></button>{finishError && <p className="cst__finish-error" role="alert">{finishError}</p>}</div></section>}
    </div>
    <footer className="cst__controls" aria-label="Navegação do tour"><button type="button" onClick={back} disabled={step === 0}><span>←</span> Voltar</button><div className="cst__dots" role="progressbar" aria-label="Progresso do tour" aria-valuenow={step + 1} aria-valuemin={1} aria-valuemax={total}>{Array.from({ length: total }).map((_, index) => <button key={index} type="button" aria-label={`Ir para a etapa ${index + 1}`} aria-current={index === step ? "step" : undefined} className={`${index === step ? "is-active" : ""}${index < step ? " is-done" : ""}`} onClick={() => goTo(index)}/>)}</div><button type="button" onClick={next} disabled={step === total - 1}>Próximo <span>→</span></button></footer>
    <span className="sr-only" aria-live="polite">Etapa {step + 1} de {total}: {welcome ? "Boas-vindas" : final ? "Conclusão" : current?.title}</span>
  </main>;
}
