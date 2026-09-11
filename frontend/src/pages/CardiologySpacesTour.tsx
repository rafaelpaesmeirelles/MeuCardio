import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type TouchEvent as ReactTouchEvent,
} from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import Icone, { type NomeIcone } from "../components/Icone";
import CorviaPresentationFilm from "../components/CorviaPresentationFilm";
import { api, ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";
import { nomeComTratamento } from "../lib/clinicalIdentity";
import "../styles/corvia-atelier-tour.css";

const TOUR_KEY = "corvia:cardiology-spaces:tour:v4";
const INVESTOR_TOUR_SESSION_KEY = "corvia:cardiology-spaces:investor-tour-session:v1";

type ExperienceMode = "complete" | "essential" | "scientific";
type ClinicalSpaceId = "consultorio" | "hospital" | "ensino" | "pesquisa" | "gestao";
type ScientificSpaceId = "descobrir" | "evidencias" | "aprender" | "ensinar" | "produzir";
type ChapterId = "experience" | "spaces" | "layers" | "day" | "relations" | "science" | "essential";
type TourSpace = { id: ClinicalSpaceId; label: string; eyebrow: string; icon: NomeIcone; detail: string };
type Chapter = { id: ChapterId; name: string; eyebrow: string; title: string; text: string; detail: string };
type Action = { label: string; icon: NomeIcone };

const CLINICAL_SPACES: TourSpace[] = [
  { id: "consultorio", label: "Consultório", eyebrow: "Prática clínica", icon: "clinica", detail: "Agenda, prontuário e ferramentas de atendimento reunidos no contexto ambulatorial." },
  { id: "hospital", label: "Hospital", eyebrow: "Cuidado hospitalar", icon: "emergencia", detail: "Round, evolução e referências para acompanhar a rotina hospitalar." },
  { id: "ensino", label: "Ensino", eyebrow: "Formação contínua", icon: "curso", detail: "Trilhas, casos e materiais para continuar aprendendo e compartilhar conhecimento." },
  { id: "pesquisa", label: "Pesquisa", eyebrow: "Ciência e evidência", icon: "evidencia", detail: "Busca, biblioteca e conexões entre fontes para aprofundar uma pergunta científica." },
  { id: "gestao", label: "Gestão", eyebrow: "Organização da prática", icon: "gestao", detail: "Agenda, indicadores e documentos para organizar o trabalho e suas pendências." },
];

const SCIENTIFIC_SPACES: Array<{ id: ScientificSpaceId; label: string; detail: string; icon: NomeIcone; space: ClinicalSpaceId }> = [
  { id: "descobrir", label: "Descobrir", detail: "Explore assuntos e relações no conhecimento cardiovascular.", icon: "busca", space: "pesquisa" },
  { id: "evidencias", label: "Evidências", detail: "Aprofunde a leitura e consulte as fontes de cada conteúdo.", icon: "evidencia", space: "pesquisa" },
  { id: "aprender", label: "Aprender", detail: "Continue suas trilhas e acompanhe seu aprendizado no ambiente de Ensino.", icon: "conhecimento", space: "ensino" },
  { id: "ensinar", label: "Ensinar", detail: "Organize casos, aulas e materiais para compartilhar conhecimento.", icon: "curso", space: "ensino" },
  { id: "produzir", label: "Produzir", detail: "Reúna referências e desenvolva seus materiais científicos.", icon: "documento", space: "pesquisa" },
];

const ACTIONS_BY_SPACE: Record<ClinicalSpaceId, Action[]> = {
  consultorio: [
    { label: "Agenda", icon: "agenda" }, { label: "Prontuário", icon: "pacientes" },
    { label: "Prescrição", icon: "prescricao" }, { label: "Revisar exames", icon: "ecg" },
    { label: "Medicamentos", icon: "medicamento" }, { label: "Calculadoras", icon: "calculadora" },
  ],
  hospital: [
    { label: "Round hospitalar", icon: "round" }, { label: "Evolução", icon: "documento" },
    { label: "Prescrição", icon: "prescricao" }, { label: "Revisar exames", icon: "ecg" },
    { label: "Checklists", icon: "check" }, { label: "Diretrizes", icon: "conhecimento" },
  ],
  ensino: [
    { label: "Trilhas", icon: "curso" }, { label: "Casos clínicos", icon: "pacientes" },
    { label: "Biblioteca", icon: "conhecimento" }, { label: "Timeline", icon: "sincronizar" },
    { label: "Material ao paciente", icon: "documento" }, { label: "Galeria", icon: "camera" },
  ],
  pesquisa: [
    { label: "Tudo com Tudo", icon: "sincronizar" }, { label: "Evidências", icon: "evidencia" },
    { label: "Estudos", icon: "busca" }, { label: "Biblioteca", icon: "conhecimento" },
    { label: "Favoritos", icon: "favorito" }, { label: "Documento científico IA", icon: "documento" },
  ],
  gestao: [
    { label: "Indicadores", icon: "indicadores" }, { label: "Agenda", icon: "agenda" },
    { label: "Pendências", icon: "notificacao" }, { label: "Documentos", icon: "documento" },
    { label: "Minha conta", icon: "conta" }, { label: "Sincronização", icon: "sincronizar" },
  ],
};

const CHAPTERS: Chapter[] = [
  { id: "experience", name: "Organização", eyebrow: "01 · ESCOLHA A EXPERIÊNCIA", title: "Uma organização para cada momento.", text: "Completo, Essencial e Ciência & Ensino são perspectivas do mesmo CorVIA. A escolha fica no contexto do seu espaço e acompanha a forma como você quer trabalhar.", detail: "Experimente as opções. Esta seleção vale apenas para o tour." },
  { id: "spaces", name: "Cinco espaços", eyebrow: "02 · CINCO AMBIENTES", title: "O seu trabalho tem lugar aqui.", text: "Consultório, Hospital, Ensino, Pesquisa e Gestão aproximam as ferramentas de cada parte da sua rotina.", detail: "Selecione um espaço para conhecer seu ambiente." },
  { id: "layers", name: "Ferramentas", eyebrow: "03 · FERRAMENTAS NO CONTEXTO", title: "O que você precisa, ao alcance.", text: "As ferramentas se organizam por espaço. Você mantém acesso ao sistema completo e encontra um ponto de partida coerente com o seu trabalho.", detail: "Explore os exemplos. Os serviços são acessados depois de entrar no sistema." },
  { id: "day", name: "Meu dia", eyebrow: "04 · MEU DIA ENTRE ESPAÇOS", title: "Continuidade ao longo do dia.", text: "A agenda ajuda a organizar compromissos e locais. Os espaços mantêm próximos os recursos de atendimento, trabalho hospitalar e estudo.", detail: "Este percurso ilustra os contextos; não representa uma agenda de paciente." },
  { id: "relations", name: "Tudo com Tudo", eyebrow: "05 · TUDO COM TUDO", title: "Uma pergunta abre novas conexões.", text: "Doenças, exames, medicamentos, diretrizes e estudos podem ser explorados em conjunto, com acesso aos conteúdos e às suas referências.", detail: "Selecione uma categoria para conhecer seu papel na pesquisa." },
  { id: "science", name: "Ciência & Ensino", eyebrow: "06 · CIÊNCIA & ENSINO", title: "Conhecimento que acompanha a prática.", text: "Da descoberta ao estudo e à produção, uma organização dedicada à sua jornada científica. Suas trilhas e seu progresso continuam no ambiente real de aprendizado.", detail: "Conheça as cinco jornadas de Ciência & Ensino." },
  { id: "essential", name: "Seu espaço", eyebrow: "07 · O SEU CORVIA", title: "Uma rotina com a sua organização.", text: "Os essenciais aproximam as ferramentas que você mais utiliza. A personalização muda a ordem e o destaque, mantendo os demais recursos disponíveis.", detail: "Experimente até cinco favoritos. As preferências reais não são alteradas neste tour." },
];

const RELATIONS: Array<{ label: string; icon: NomeIcone; detail: string }> = [
  { label: "Doença", icon: "doencas", detail: "Contexto clínico e temas relacionados." },
  { label: "Exame", icon: "ecg", detail: "Conteúdos sobre achados e interpretação." },
  { label: "Medicamento", icon: "medicamento", detail: "Informações farmacológicas e referências." },
  { label: "Diretriz", icon: "conhecimento", detail: "Recomendações com acesso às fontes." },
  { label: "Evidência", icon: "evidencia", detail: "Estudos e publicações para leitura crítica." },
  { label: "Calculadora", icon: "calculadora", detail: "Ferramentas de cálculo e estratificação." },
  { label: "Caso", icon: "pacientes", detail: "Aprendizado em contexto clínico." },
  { label: "Documento", icon: "documento", detail: "Materiais e documentos associados ao tema." },
];

const ESSENTIALS: Action[] = [
  { label: "Prescrever", icon: "prescricao" }, { label: "Solicitar exames", icon: "clinica" },
  { label: "Prontuário", icon: "pacientes" }, { label: "Calculadoras", icon: "calculadora" },
  { label: "Diretrizes", icon: "conhecimento" }, { label: "Interações", icon: "medicamento" },
];

const MODE_COPY: Record<ExperienceMode, { label: string; detail: string; items: string[] }> = {
  complete: { label: "Completo", detail: "Uma visão ampla das ferramentas do seu espaço.", items: ["Ferramentas do espaço", "Referências", "Todos os recursos"] },
  essential: { label: "Essencial", detail: "Seus atalhos mais utilizados ganham destaque.", items: ["Meus essenciais", "Personalização", "Todos os recursos"] },
  scientific: { label: "Ciência & Ensino", detail: "Uma organização dedicada a explorar, aprender e produzir.", items: ["Descoberta e evidências", "Trilhas de aprendizado", "Produção científica"] },
};

const INTERIOR_ALT: Record<ClinicalSpaceId | "entrance", string> = {
  entrance: "Recepção CorVIA, com materiais claros e iluminação acolhedora.",
  consultorio: "Consultório com mesa de atendimento e acabamento em madeira clara.",
  hospital: "Ambiente hospitalar claro, com espaços de cuidado e trabalho.",
  ensino: "Ambiente de ensino com mesas de estudo e biblioteca.",
  pesquisa: "Ambiente de pesquisa com mesas de trabalho e referências.",
  gestao: "Ambiente de gestão com mesa de reunião e organização do trabalho.",
};

function Interior({ space, eager = false }: { space: ClinicalSpaceId | "entrance"; eager?: boolean }) {
  return <img className="cst-at__interior" src={`/atelier/atelier-${space}.webp`} srcSet={`/atelier/atelier-${space}-small.webp 640w, /atelier/atelier-${space}.webp 1536w`} sizes="(max-width: 900px) 100vw, 55vw" alt={INTERIOR_ALT[space]} loading={eager ? "eager" : "lazy"} decoding="async" />;
}

function SpacePicker({ selected, onSelect }: { selected: ClinicalSpaceId; onSelect: (space: ClinicalSpaceId) => void }) {
  return <div className="cst-at__space-picker" role="group" aria-label="Espaço apresentado no tour">
    {CLINICAL_SPACES.map((space) => <button key={space.id} type="button" aria-pressed={selected === space.id} onClick={() => onSelect(space.id)}><Icone nome={space.icon} /><span>{space.label}</span></button>)}
  </div>;
}

function ExperienceVisual({ mode, onMode }: { mode: ExperienceMode; onMode: (mode: ExperienceMode) => void }) {
  const active = MODE_COPY[mode];
  return <div className="cst-at__panel">
    <figure className="cst-at__photo"><Interior space={mode === "scientific" ? "pesquisa" : "consultorio"} /><figcaption>Um espaço. Diferentes formas de organizar.</figcaption></figure>
    <div className="cst-at__panel-body">
      <label className="cst-at__context-select"><span>Organização no tour</span><select value={mode} onChange={(event) => onMode(event.target.value as ExperienceMode)}>{(Object.keys(MODE_COPY) as ExperienceMode[]).map((item) => <option key={item} value={item}>{MODE_COPY[item].label}</option>)}</select></label>
      <div className="cst-at__selection-copy" aria-live="polite"><h2>{active.label}</h2><p>{active.detail}</p></div>
      <ul className="cst-at__features">{active.items.map((item) => <li key={item}><Icone nome="check" /><span>{item}</span></li>)}</ul>
    </div>
  </div>;
}

function SpacesVisual({ selected, onSelect, tools = false }: { selected: ClinicalSpaceId; onSelect: (space: ClinicalSpaceId) => void; tools?: boolean }) {
  const active = CLINICAL_SPACES.find((space) => space.id === selected) ?? CLINICAL_SPACES[0];
  return <div className="cst-at__space-explorer">
    <SpacePicker selected={selected} onSelect={onSelect} />
    <div className="cst-at__panel">
      <figure className="cst-at__photo"><Interior space={selected} /><figcaption><small>{active.eyebrow}</small><strong>{active.label}</strong></figcaption></figure>
      <div className="cst-at__panel-body">
        {tools ? <><p className="cst-at__eyebrow">Exemplos de ferramentas</p><ul className="cst-at__actions" aria-label={`Ferramentas de ${active.label}`}>{ACTIONS_BY_SPACE[selected].map((action) => <li key={action.label}><Icone nome={action.icon} /><span>{action.label}</span></li>)}</ul></> : <p className="cst-at__space-detail" aria-live="polite">{active.detail}</p>}
      </div>
    </div>
  </div>;
}

function DayVisual() {
  return <div className="cst-at__panel">
    <figure className="cst-at__photo"><Interior space="hospital" /><figcaption>O dia se organiza ao redor da sua prática.</figcaption></figure>
    <div className="cst-at__panel-body">
      <ol className="cst-at__day">
        <li><span><Icone nome="round" /></span><div><h2>Hospital</h2><p>Round, evolução e acompanhamento hospitalar.</p></div></li>
        <li><span><Icone nome="clinica" /></span><div><h2>Consultório</h2><p>Agenda, atendimento e documentação clínica.</p></div></li>
        <li><span><Icone nome="curso" /></span><div><h2>Ensino</h2><p>Retome uma trilha ou aprofunde um assunto.</p></div></li>
      </ol>
      <div className="cst-at__note"><Icone nome="rota" /><div><strong>DESLOCAMENTO</strong><p>Consulte os horários e locais dos seus compromissos na agenda real.</p></div></div>
    </div>
  </div>;
}

function RelationsVisual({ selected, onSelect }: { selected: number; onSelect: (index: number) => void }) {
  const active = RELATIONS[selected];
  return <div className="cst-at__panel cst-at__relations">
    <div className="cst-at__panel-heading"><Icone nome="sincronizar" /><div><p className="cst-at__eyebrow">Conhecimento conectado</p><h2>Tudo com Tudo</h2></div></div>
    <div className="cst-at__relation-grid" role="group" aria-label="Categorias de conhecimento">{RELATIONS.map((relation, index) => <button key={relation.label} type="button" aria-pressed={selected === index} onClick={() => onSelect(index)}><Icone nome={relation.icon} /><span>{relation.label}</span></button>)}</div>
    <div className="cst-at__relation-detail" aria-live="polite"><Icone nome={active.icon} /><div><h3>{active.label}</h3><p>{active.detail}</p></div></div>
    <p className="cst-at__caption">Apresentação das categorias. Nenhuma pesquisa clínica é realizada neste tour.</p>
  </div>;
}

function ScienceVisual({ selected, onSelect }: { selected: ScientificSpaceId; onSelect: (space: ScientificSpaceId) => void }) {
  const active = SCIENTIFIC_SPACES.find((space) => space.id === selected) ?? SCIENTIFIC_SPACES[0];
  return <div className="cst-at__panel">
    <figure className="cst-at__photo"><Interior space={active.space} /><figcaption>Ciência &amp; Ensino</figcaption></figure>
    <div className="cst-at__panel-body">
      <div className="cst-at__space-picker cst-at__science-picker" role="group" aria-label="Jornadas de Ciência e Ensino">{SCIENTIFIC_SPACES.map((space) => <button key={space.id} type="button" aria-pressed={selected === space.id} onClick={() => onSelect(space.id)}><Icone nome={space.icon} /><span>{space.label}</span></button>)}</div>
      <div className="cst-at__selection-copy" aria-live="polite"><h2>{active.label}</h2><p>{active.detail}</p></div>
    </div>
  </div>;
}

function EssentialVisual({ selected, onToggle, callName }: { selected: string[]; onToggle: (label: string) => void; callName: string }) {
  return <div className="cst-at__panel cst-at__essentials">
    <div className="cst-at__panel-heading"><Icone nome="conta" /><div><p className="cst-at__eyebrow">Sua organização</p><h2>{callName}</h2></div></div>
    <header className="cst-at__essential-heading"><div><p className="cst-at__eyebrow">Exemplo · Consultório</p><h3>Meus essenciais</h3></div><span aria-live="polite">{selected.length} de 5 selecionados</span></header>
    <div className="cst-at__essential-grid" role="group" aria-label="Favoritos demonstrativos">{ESSENTIALS.map((action) => {
      const active = selected.includes(action.label);
      return <button key={action.label} type="button" aria-pressed={active} disabled={!active && selected.length >= 5} onClick={() => onToggle(action.label)}><Icone nome={action.icon} /><span>{action.label}</span><Icone nome={active ? "check" : "adicionar"} /></button>;
    })}</div>
    <p className="cst-at__caption">Escolha até cinco. Para substituir um favorito quando atingir o limite, desmarque uma opção. Esta prévia não altera seu perfil.</p>
  </div>;
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
  const stage = useRef<HTMLDivElement>(null);
  const quickTour = params.get("modo") === "quick";
  const chapters = useMemo(
    () => quickTour ? CHAPTERS.filter((chapter) => ["spaces", "layers", "day"].includes(chapter.id)) : CHAPTERS,
    [quickTour],
  );
  const total = chapters.length + 2;
  const assinaturaSemAcesso = params.get("origem") === "assinatura" && !usuario?.product_access;
  const requested = params.get("retorno") || (assinaturaSemAcesso ? "/em-breve" : "/");
  const destination = useMemo(() => {
    try {
      const resolved = new URL(requested, window.location.origin);
      if (resolved.origin !== window.location.origin) return "/";
      return `${resolved.pathname}${resolved.search}${resolved.hash}`;
    } catch { return "/"; }
  }, [requested]);
  const manual = !usuario?.onboarding_pendente && !usuario?.investidor;
  const callName = nomeComTratamento(usuario, true);
  const welcome = step === 0;
  const final = step === total - 1;
  const current = !welcome && !final ? chapters[step - 1] : null;
  const stepNames = ["Boas-vindas", ...chapters.map((chapter) => chapter.name), "Entrar no CorVIA"];
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
      // Successful server-side completion must not become a failure when
      // browser preferences are blocked. These markers are only conveniences.
      try { localStorage.setItem(TOUR_KEY, "seen"); } catch { /* session remains usable */ }
      if (usuario?.investidor) {
        try { sessionStorage.setItem(INVESTOR_TOUR_SESSION_KEY, "seen"); } catch { /* read-only tour can be replayed */ }
      }
      if (usuario?.onboarding_pendente) window.location.replace(destination);
      else leave();
    } catch (error) {
      setFinishError(error instanceof ApiError ? "Não foi possível concluir o tour. Tente novamente." : "Ocorreu uma falha ao abrir o Cardiology Spaces.");
      setFinishing(false);
    }
  }

  useEffect(() => {
    stage.current?.scrollTo({ top: 0 });
    stage.current?.querySelector<HTMLElement>("h1")?.focus({ preventScroll: true });
  }, [step]);

  useEffect(() => {
    function keyboard(event: KeyboardEvent) {
      if (finishing) return;
      const target = event.target as HTMLElement | null;
      if (target?.closest("input, textarea, select, button, a, video, dialog, [contenteditable='true']")) return;
      if (event.key === "ArrowRight" || event.key === "PageDown") { event.preventDefault(); next(); }
      if (event.key === "ArrowLeft" || event.key === "PageUp") { event.preventDefault(); back(); }
      if (event.key === "Home") { event.preventDefault(); goTo(0); }
      if (event.key === "End") { event.preventDefault(); goTo(total - 1); }
      if (event.key === "Escape" && manual) leave();
    }
    window.addEventListener("keydown", keyboard);
    return () => window.removeEventListener("keydown", keyboard);
  }, [back, finishing, goTo, leave, manual, next, total]);

  function handleTouchStart(event: ReactTouchEvent<HTMLElement>) {
    const target = event.target as HTMLElement | null;
    if (finishing || target?.closest("button, a, input, select, textarea, video, dialog, [contenteditable='true']")) {
      touchStart.current = null;
      return;
    }
    const touch = event.touches[0];
    touchStart.current = touch ? { x: touch.clientX, y: touch.clientY } : null;
  }

  function handleTouchEnd(event: ReactTouchEvent<HTMLElement>) {
    const start = touchStart.current;
    const touch = event.changedTouches[0];
    touchStart.current = null;
    if (finishing || !start || !touch) return;
    const dx = touch.clientX - start.x;
    const dy = touch.clientY - start.y;
    if (Math.abs(dx) < 58 || Math.abs(dx) < Math.abs(dy) * 1.15) return;
    if (dx < 0) next(); else back();
  }

  function toggleEssential(label: string) {
    setEssentials((items) => items.includes(label) ? items.filter((item) => item !== label) : [...items, label].slice(0, 5));
  }

  function chapterVisual() {
    if (current?.id === "experience") return <ExperienceVisual mode={mode} onMode={setMode} />;
    if (current?.id === "spaces" || current?.id === "layers") return <SpacesVisual selected={selectedSpace} onSelect={setSelectedSpace} tools={current.id === "layers"} />;
    if (current?.id === "day") return <DayVisual />;
    if (current?.id === "relations") return <RelationsVisual selected={selectedRelation} onSelect={setSelectedRelation} />;
    if (current?.id === "science") return <ScienceVisual selected={selectedScientific} onSelect={setSelectedScientific} />;
    return <EssentialVisual selected={essentials} onToggle={toggleEssential} callName={callName} />;
  }

  return <main className="cst cst--atelier" data-step={current?.id ?? (welcome ? "welcome" : "final")} onTouchStart={handleTouchStart} onTouchEnd={handleTouchEnd}>
    <header className="cst-at__header">
      <span className="cst-at__brand"><img src="/atelier/corvia-logo-atelier.svg" alt="CorVIA Cardiology Spaces" width="900" height="240" /></span>
      <span className="cst-at__header-description">Conheça seus espaços</span>
      {manual ? <button className="cst-at__exit" type="button" onClick={leave} disabled={finishing}>Sair do tour</button> : <span className="cst-at__profile">{usuario?.investidor ? "Perfil Investidor" : "Seu primeiro acesso"}</span>}
    </header>
    <div className="cst-at__progress" role="progressbar" aria-label="Progresso do tour" aria-valuenow={step + 1} aria-valuemin={1} aria-valuemax={total}><span style={{ width: `${((step + 1) / total) * 100}%` }} /></div>
    <div className="cst-at__stage" ref={stage}>
      {(welcome || final) && <section className="cst-at__chapter cst-at__welcome" aria-labelledby="cst-title">
        <article className="cst-at__copy">
          <p className="cst-at__eyebrow">{welcome ? "Cardiology Spaces · CorVIA" : "Agora começa a rotina real"}</p>
          <h1 id="cst-title" tabIndex={-1}>{welcome ? <>Bem-vindo, {callName}.<br /><em>Cinco espaços.<br />Uma só cardiologia.</em></> : <>Seu próximo espaço<br /><em>começa com você.</em></>}</h1>
          <p>{welcome ? "Ambientes que acompanham sua prática, seu conhecimento e a organização do seu dia." : usuario?.investidor ? "A demonstração abre em modo somente leitura. O tour será exibido novamente em uma nova sessão do perfil Investidor." : "Você pode rever este percurso a qualquer momento pelo menu do Cardiology Spaces."}</p>
          <button className="cst-at__primary" type="button" onClick={welcome ? next : () => void finish()} disabled={finishing}>{welcome ? "Conhecer os espaços" : finishing ? "Abrindo…" : "Entrar no Cardiology Spaces"}<Icone nome="seta" /></button>
          {(welcome || final) && <CorviaPresentationFilm />}
          {welcome && <small>Avance pelas etapas ou use o seletor de capítulos. Você também pode navegar pelas setas do teclado ou deslizar a tela.</small>}
          {final && finishError && <p className="cst-at__error" role="alert">{finishError}</p>}
        </article>
        <figure className="cst-at__welcome-image"><Interior space={welcome ? "entrance" : selectedSpace} eager /></figure>
      </section>}
      {current && <section className="cst-at__chapter" aria-labelledby={`cst-title-${current.id}`}>
        <article className="cst-at__copy">
          <p className="cst-at__eyebrow">{quickTour ? current.eyebrow.replace(/^\d+ · /, "") : current.eyebrow}</p>
          <h1 id={`cst-title-${current.id}`} tabIndex={-1}>{current.title}</h1>
          <p>{current.text}</p>
          <small>{current.detail}</small>
        </article>
        <div className="cst-at__visual">{chapterVisual()}</div>
      </section>}
    </div>
    <footer className="cst-at__controls" aria-label="Navegação do tour">
      <button className="cst-at__previous" type="button" onClick={back} disabled={step === 0 || finishing}><span aria-hidden="true">←</span> Voltar</button>
      <label className="cst-at__chapter-select"><span className="cst-at__sr-only">Capítulo do tour</span><select value={step} onChange={(event) => goTo(Number(event.target.value))} disabled={finishing}>{stepNames.map((name, index) => <option key={name} value={index}>{index + 1} de {total} · {name}</option>)}</select></label>
      <button className="cst-at__next" type="button" onClick={next} disabled={final || finishing}>Próximo <span aria-hidden="true">→</span></button>
    </footer>
    <span className="cst-at__sr-only" aria-live="polite">Etapa {step + 1} de {total}: {stepNames[step]}</span>
  </main>;
}
