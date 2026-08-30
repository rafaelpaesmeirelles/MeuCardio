import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import Icone, { type NomeIcone } from "../components/Icone";
import { CoracaoHolografico } from "../components/PreHomeBrand";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";
import "../styles/cardiology-spaces.css";

type Mode = "complete" | "essential";
type SpaceId = "consultorio" | "hospital" | "ensino" | "pesquisa" | "gestao";
type Tone = "cyan" | "blue" | "violet" | "rose" | "teal";
type Action = { to: string; label: string; icon: NomeIcone; adminOnly?: boolean };
type Space = {
  id: SpaceId;
  label: string;
  icon: NomeIcone;
  tone: Tone;
  description: string;
  now: Action[];
  next: Action[];
  references: Action[];
};
type Appointment = { id: number; patient_name: string | null; starts_at: string; appointment_type: string; status: string };

const MODE_KEY = "corvia:cardiology-spaces:mode";

const SPACES: Space[] = [
  {
    id: "consultorio", label: "Consultório", icon: "conta", tone: "cyan",
    description: "Tudo preparado para sua rotina no consultório.",
    now: [
      { to: "/agenda", label: "Abrir agenda", icon: "agenda" },
      { to: "/receituario", label: "Prescrever", icon: "prescricao" },
      { to: "/prontuario", label: "Prontuário", icon: "pacientes" },
    ],
    next: [
      { to: "/documentos", label: "Solicitar exames", icon: "clinica" },
      { to: "/exames", label: "Revisar exames", icon: "ecg" },
      { to: "/avaliacao-preoperatoria", label: "Avaliação pré-operatória", icon: "check" },
    ],
    references: [
      { to: "/medicamentos", label: "Medicamentos", icon: "medicamento" },
      { to: "/calculadoras", label: "Calculadoras", icon: "calculadora" },
      { to: "/diretrizes", label: "Diretrizes", icon: "conhecimento" },
      { to: "/interacoes", label: "Interações", icon: "check" },
    ],
  },
  {
    id: "hospital", label: "Hospital", icon: "emergencia", tone: "blue",
    description: "Tudo preparado para sua rotina hospitalar.",
    now: [
      { to: "/round", label: "Abrir round", icon: "pacientes" },
      { to: "/round", label: "Registrar evolução", icon: "documento" },
      { to: "/receituario", label: "Prescrever", icon: "prescricao" },
    ],
    next: [
      { to: "/exames", label: "Revisar exames", icon: "ecg" },
      { to: "/documentos", label: "Documentos para assinar", icon: "documento" },
      { to: "/checklists", label: "Checklists", icon: "check" },
    ],
    references: [
      { to: "/cardiologia-intensiva", label: "Cardiologia Intensiva", icon: "clinica" },
      { to: "/emergencia", label: "Emergências", icon: "emergencia" },
      { to: "/calculadoras", label: "Calculadoras", icon: "calculadora" },
      { to: "/diretrizes", label: "Diretrizes", icon: "conhecimento" },
    ],
  },
  {
    id: "ensino", label: "Ensino", icon: "curso", tone: "violet",
    description: "Conhecimento organizado para aprender e ensinar.",
    now: [
      { to: "/cursos", label: "Abrir cursos", icon: "curso" },
      { to: "/apresentacao", label: "Apresentar", icon: "documento" },
      { to: "/trilhas", label: "Continuar trilha", icon: "seta" },
    ],
    next: [
      { to: "/casos-clinicos", label: "Casos clínicos", icon: "doencas" },
      { to: "/galeria", label: "Atlas & Galeria", icon: "galeria" },
      { to: "/material-paciente", label: "Material educativo", icon: "documento" },
    ],
    references: [
      { to: "/biblioteca", label: "Biblioteca", icon: "conhecimento" },
      { to: "/evidencias", label: "Evidências", icon: "evidencia" },
      { to: "/diretrizes", label: "Diretrizes", icon: "conhecimento" },
      { to: "/trilhas/timeline", label: "Timeline", icon: "seta" },
    ],
  },
  {
    id: "pesquisa", label: "Pesquisa", icon: "evidencia", tone: "rose",
    description: "Evidência, literatura e investigação em um só espaço.",
    now: [
      { to: "/estudos", label: "Estudos clínicos", icon: "evidencia" },
      { to: "/evidencias", label: "Revisar evidências", icon: "conhecimento" },
      { to: "/documentos-cientificos-ia", label: "Documento científico IA", icon: "assistente" },
    ],
    next: [
      { to: "/biblioteca", label: "Biblioteca científica", icon: "conhecimento" },
      { to: "/busca", label: "Busca avançada", icon: "busca" },
      { to: "/diretrizes", label: "Atualizar diretrizes", icon: "evidencia" },
    ],
    references: [
      { to: "/casos-clinicos", label: "Casos clínicos", icon: "doencas" },
      { to: "/galeria", label: "Atlas & Galeria", icon: "galeria" },
      { to: "/exportar", label: "Exportar conteúdo", icon: "documento" },
      { to: "/favoritos", label: "Notas & Favoritos", icon: "favorito" },
    ],
  },
  {
    id: "gestao", label: "Gestão", icon: "gestao", tone: "teal",
    description: "Visão operacional, conexões e gestão da prática.",
    now: [
      { to: "/indicadores", label: "Ver indicadores", icon: "indicadores" },
      { to: "/agenda", label: "Organizar agenda", icon: "agenda" },
      { to: "/admin", label: "Painel administrativo", icon: "gestao", adminOnly: true },
    ],
    next: [
      { to: "/usuarios-online", label: "Rede profissional", icon: "pacientes" },
      { to: "/sincronizacao", label: "Contas conectadas", icon: "sincronizar" },
      { to: "/corvia-mail", label: "CorVIA Mail", icon: "mail" },
    ],
    references: [
      { to: "/minha-conta", label: "Minha conta", icon: "conta" },
      { to: "/privacidade", label: "Privacidade", icon: "check" },
      { to: "/termos", label: "Termos de uso", icon: "documento" },
      { to: "/tour", label: "Suporte & Ajuda", icon: "curso" },
    ],
  },
];

const CATALOG: Array<{ title: string; actions: Action[] }> = [
  { title: "Clínica & Decisão", actions: [
    ["/doencas", "Guia de Doenças", "doencas"], ["/medicamentos", "Medicamentos", "medicamento"],
    ["/exames", "Exames", "clinica"], ["/calculadoras", "Calculadoras", "calculadora"],
    ["/emergencia", "Emergências", "emergencia"], ["/cardiologia-intensiva", "Cardiologia Intensiva & UCO", "clinica"],
    ["/checklists", "Checklists", "check"], ["/triagem-sintomas", "Triagem de sintomas", "triagem"],
    ["/interacoes", "Interações medicamentosas", "medicamento"], ["/condicoes", "Condições especiais", "check"],
    ["/fluxogramas", "Fluxogramas clínicos", "seta"], ["/avaliacao-preoperatoria", "Avaliação pré-operatória", "clinica"],
  ].map(([to, label, icon]) => ({ to, label, icon: icon as NomeIcone })) },
  { title: "Assistência", actions: [
    ["/exames-ia", "IA para Exames", "ecg"], ["/prontuario", "Prontuário", "pacientes"],
    ["/round", "Round hospitalar", "round"], ["/receituario", "Prescrição", "prescricao"],
    ["/documentos", "Documentos & Solicitações", "documento"], ["/agenda", "Agenda", "agenda"],
    ["/corvia-mail", "CorVIA Mail", "mail"], ["/assistente", "Assistente Clínica", "assistente"],
    ["/telediagnostico", "Telediagnóstico & Consultoria", "evidencia"], ["/material-paciente", "Material para paciente", "documento"],
  ].map(([to, label, icon]) => ({ to, label, icon: icon as NomeIcone })) },
  { title: "Ensino & Pesquisa", actions: [
    ["/evidencias", "Estudos & Evidências", "evidencia"], ["/estudos", "Estudos clínicos", "evidencia"],
    ["/documentos-cientificos-ia", "Documentos científicos IA", "assistente"], ["/trilhas/timeline", "Timeline do conhecimento", "seta"],
    ["/trilhas", "Trilhas", "seta"], ["/casos-clinicos", "Casos clínicos", "doencas"],
    ["/diretrizes", "Diretrizes & Guidelines", "conhecimento"], ["/cursos", "Cursos & Atualizações", "curso"],
    ["/biblioteca", "Biblioteca científica", "conhecimento"], ["/galeria", "Atlas & Galeria", "galeria"],
  ].map(([to, label, icon]) => ({ to, label, icon: icon as NomeIcone })) },
  { title: "Produtividade & Rede", actions: [
    ["/indicadores", "Indicadores & Métricas", "indicadores"], ["/apresentacao", "Modo apresentação", "documento"],
    ["/exportar", "Exportar conteúdo", "documento"], ["/favoritos", "Notas & Favoritos", "favorito"],
    ["/busca", "Busca avançada", "busca"], ["/busca?modo=tudo-com-tudo", "Tudo com Tudo", "sincronizar"],
    ["/usuarios-online", "Rede profissional", "pacientes"], ["/sincronizacao", "Contas conectadas", "sincronizar"],
  ].map(([to, label, icon]) => ({ to, label, icon: icon as NomeIcone })) },
  { title: "Conta & Administração", actions: [
    { to: "/minha-conta", label: "Minha Conta", icon: "conta" },
    { to: "/privacidade", label: "Segurança & Privacidade", icon: "check" },
    { to: "/termos", label: "Termos de uso", icon: "documento" },
    { to: "/tour", label: "Suporte & Ajuda", icon: "curso" },
    { to: "/admin", label: "Painel administrativo", icon: "gestao", adminOnly: true },
    { to: "/admin/usuarios", label: "Usuários & Permissões", icon: "pacientes", adminOnly: true },
    { to: "/fila-telediagnostico", label: "Fila de telediagnóstico", icon: "evidencia", adminOnly: true },
    { to: "/receitas-para-assinatura", label: "Receitas para assinatura", icon: "prescricao", adminOnly: true },
  ] },
];

const ESSENTIAL_DEFAULTS = ["/agenda", "/receituario", "/prontuario", "/documentos", "/exames", "/calculadoras"];

function firstName(name?: string) {
  const parts = (name || "").trim().split(/\s+/).filter(Boolean).filter((part) => !/^(dr|dra|prof|profa)\.?$/i.test(part));
  return parts[0] || "Médico(a)";
}

function time(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "" : date.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
}

function Brand() {
  return (
    <span className="spaces-brand" aria-label="CorVIA Cardiology Spaces">
      <img src="/corvia-mark-canonical.svg" alt="" />
      <span><strong><i>Cor</i><b>VIA</b></strong><small>CARDIOLOGY SPACES</small></span>
    </span>
  );
}

function ActionLink({ action }: { action: Action }) {
  return <Link className="spaces-action" to={action.to}><Icone nome={action.icon} /><span>{action.label}</span></Link>;
}

export default function CardiologySpacesHome() {
  const { usuario } = useAuth();
  const storageKey = `corvia:cardiology-spaces:essentials:${usuario?.id || "user"}`;
  const [mode, setMode] = useState<Mode | null>(() => {
    const saved = sessionStorage.getItem(MODE_KEY);
    return saved === "complete" || saved === "essential" ? saved : null;
  });
  const [selectedSpace, setSelectedSpace] = useState<SpaceId>("consultorio");
  const [previewSpace, setPreviewSpace] = useState<SpaceId | null>(null);
  const [catalogOpen, setCatalogOpen] = useState(false);
  const [personalizerOpen, setPersonalizerOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [essentialPaths, setEssentialPaths] = useState<string[]>(() => {
    try {
      const saved = JSON.parse(localStorage.getItem(storageKey) || "[]") as string[];
      return saved.length ? saved.slice(0, 8) : ESSENTIAL_DEFAULTS;
    } catch { return ESSENTIAL_DEFAULTS; }
  });

  useEffect(() => {
    document.body.classList.add("cardiology-spaces-active");
    return () => document.body.classList.remove("cardiology-spaces-active");
  }, []);

  useEffect(() => {
    api.get<Appointment[]>("/agenda/appointments").then((items) => setAppointments(Array.isArray(items) ? items : [])).catch(() => setAppointments([]));
  }, []);

  useEffect(() => {
    if (!catalogOpen && !personalizerOpen) return;
    const close = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      setCatalogOpen(false);
      setPersonalizerOpen(false);
    };
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, [catalogOpen, personalizerOpen]);

  const activeSpace = SPACES.find((space) => space.id === (previewSpace || selectedSpace)) || SPACES[0];
  const visibleCatalog = useMemo(() => CATALOG.map((section) => ({
    ...section,
    actions: section.actions.filter((action) => (!action.adminOnly || usuario?.role === "admin") && (!query || action.label.toLocaleLowerCase("pt-BR").includes(query.toLocaleLowerCase("pt-BR")))),
  })).filter((section) => section.actions.length), [query, usuario?.role]);
  const allActions = useMemo(() => CATALOG.flatMap((section) => section.actions).filter((action) => !action.adminOnly || usuario?.role === "admin"), [usuario?.role]);
  const essentials = essentialPaths.map((path) => allActions.find((action) => action.to === path)).filter((action): action is Action => Boolean(action));
  const day = appointments.filter((item) => !/cancel/i.test(item.status || "")).slice(0, 3);

  function chooseMode(nextMode: Mode) {
    sessionStorage.setItem(MODE_KEY, nextMode);
    setMode(nextMode);
    setSelectedSpace("consultorio");
    setPreviewSpace(null);
  }

  function toggleEssential(path: string) {
    setEssentialPaths((current) => {
      const next = current.includes(path) ? current.filter((item) => item !== path) : [...current, path].slice(0, 8);
      localStorage.setItem(storageKey, JSON.stringify(next));
      return next;
    });
  }

  if (!mode) {
    return (
      <main className="spaces-choice">
        <div className="spaces-choice__heart" aria-hidden="true"><CoracaoHolografico /></div>
        <header><Brand /><span className="spaces-user"><Icone nome="conta" /> Dr. {firstName(usuario?.full_name)}</span></header>
        <section className="spaces-choice__content">
          <p className="spaces-eyebrow">SEU JEITO DE TRABALHAR</p>
          <h1>Como você quer trabalhar hoje?</h1>
          <p>Escolha a profundidade da experiência. Em ambos os modos, você começa no Consultório e mantém acesso a todas as funções.</p>
          <div className="spaces-choice__cards">
            <button type="button" onClick={() => chooseMode("complete")}>
              <span className="spaces-choice__icon"><Icone nome="gestao" /></span>
              <strong>Completo</strong><small>Todos os ambientes, três camadas funcionais e visão integral do CorVIA.</small>
              <em>Entrar no sistema completo <Icone nome="seta" /></em>
            </button>
            <button type="button" onClick={() => chooseMode("essential")}>
              <span className="spaces-choice__icon"><Icone nome="configuracao" /></span>
              <strong>Essencial</strong><small>Sua rotina em foco, com atalhos personalizáveis e navegação imediata.</small>
              <em>Entrar no sistema essencial <Icone nome="seta" /></em>
            </button>
          </div>
        </section>
        <footer>O ambiente muda. <strong>O médico continua no centro.</strong></footer>
      </main>
    );
  }

  return (
    <main className={`spaces-home spaces-home--${activeSpace.tone}`}>
      <header className="spaces-home__topbar">
        <Brand />
        <nav aria-label="Modo de trabalho">
          <button className={mode === "complete" ? "is-active" : ""} onClick={() => chooseMode("complete")}>Completo</button>
          <button className={mode === "essential" ? "is-active" : ""} onClick={() => chooseMode("essential")}>Essencial</button>
        </nav>
        <Link to="/minha-conta" className="spaces-user"><Icone nome="conta" /> Dr. {firstName(usuario?.full_name)} <Icone nome="chevron" /></Link>
      </header>

      <aside className="spaces-rail" aria-label="Meus espaços">
        <span>MEUS<br />ESPAÇOS</span>
        {SPACES.map((space) => <button key={space.id} className={selectedSpace === space.id ? "is-active" : ""} onClick={() => { setSelectedSpace(space.id); setPreviewSpace(null); }} aria-label={space.label}><Icone nome={space.icon} /><i data-tone={space.tone} /></button>)}
        <button onClick={() => setPersonalizerOpen(true)} aria-label="Personalizar essencial"><Icone nome="configuracao" /></button>
      </aside>

      <section className="spaces-workspace">
        <h1>Onde você está trabalhando agora?</h1>
        <div className="spaces-doors" onMouseLeave={() => setPreviewSpace(null)}>
          {SPACES.map((space) => {
            const active = activeSpace.id === space.id;
            return (
              <button key={space.id} type="button" className={`spaces-door spaces-door--${space.tone}${active ? " is-active" : ""}`} onMouseEnter={() => setPreviewSpace(space.id)} onFocus={() => setPreviewSpace(space.id)} onBlur={() => setPreviewSpace(null)} onClick={() => { setSelectedSpace(space.id); setPreviewSpace(null); }} aria-pressed={selectedSpace === space.id}>
                <span><Icone nome={space.icon} />{space.label}</span><i aria-hidden="true"><b /><b /><b /></i>
              </button>
            );
          })}
        </div>

        <div className="spaces-title"><span>Meu espaço</span> <strong>{activeSpace.label}</strong><small>{activeSpace.description}</small></div>

        <div className="spaces-layers" aria-live="polite">
          <section className="spaces-layer spaces-layer--now">
            <header><span>AGORA</span><strong>{activeSpace.label === "Hospital" ? "Round hospitalar · 3 prioridades" : `Rotina de ${activeSpace.label.toLocaleLowerCase("pt-BR")}`}</strong></header>
            <div>{activeSpace.now.filter((action) => !action.adminOnly || usuario?.role === "admin").map((action) => <ActionLink key={`${activeSpace.id}-now-${action.label}`} action={action} />)}</div>
          </section>
          {mode === "complete" ? <>
            <section className="spaces-layer spaces-layer--next"><header><span>EM SEGUIDA</span></header><div>{activeSpace.next.map((action) => <ActionLink key={`${activeSpace.id}-next-${action.label}`} action={action} />)}</div></section>
            <section className="spaces-layer spaces-layer--refs"><header><span>REFERÊNCIAS DO ESPAÇO</span></header><div>{activeSpace.references.map((action) => <ActionLink key={`${activeSpace.id}-ref-${action.label}`} action={action} />)}</div></section>
          </> : <>
            <section className="spaces-layer spaces-layer--essential"><header><span>MEUS ESSENCIAIS</span></header><div>{essentials.slice(0, 6).map((action) => <ActionLink key={`essential-${action.to}`} action={action} />)}</div></section>
            <button type="button" className="spaces-personalize" onClick={() => setPersonalizerOpen(true)}><Icone nome="configuracao" /> Personalizar essencial</button>
          </>}
        </div>
        <div className="spaces-doctor"><Icone nome="conta" /><span>Dr. {firstName(usuario?.full_name)}</span><small>Meu espaço ativo</small></div>
      </section>

      <aside className="spaces-day">
        <h2>Meu dia entre espaços</h2>
        {(day.length ? day : [
          { id: 1, appointment_type: "Consultório", starts_at: new Date().toISOString(), patient_name: null, status: "" },
          { id: 2, appointment_type: "Hospital", starts_at: "", patient_name: null, status: "" },
          { id: 3, appointment_type: "Estudo", starts_at: "", patient_name: null, status: "" },
        ]).map((item, index) => <Link to="/agenda" key={item.id} className={`spaces-day__item spaces-day__item--${index}`}><i /><span><strong>{item.appointment_type || "Compromisso"}</strong><small>{item.starts_at ? time(item.starts_at) : index === 1 ? "13:00" : "20:00"}</small></span></Link>)}
        <Link to="/agenda" className="spaces-day__travel"><Icone nome="rota" /><span><strong>Deslocamento</strong><small>Ver rota do dia</small></span></Link>
      </aside>

      <nav className="spaces-dock" aria-label="Ações globais">
        <Link to="/receituario"><Icone nome="prescricao" /><span>Prescrever</span></Link>
        <Link to="/documentos"><Icone nome="clinica" /><span>Solicitar exames</span></Link>
        <Link to="/prontuario"><Icone nome="pacientes" /><span>Prontuário</span></Link>
        <Link to="/documentos"><Icone nome="documento" /><span>Documentos</span></Link>
        <Link to="/busca?modo=tudo-com-tudo"><Icone nome="sincronizar" /><span>Tudo com Tudo</span></Link>
        <button type="button" onClick={() => setCatalogOpen(true)}><Icone nome="mais" /><span>Todas as funções</span></button>
      </nav>
      <p className="spaces-motto">O ambiente <strong>muda.</strong> O médico <strong>continua no centro.</strong></p>

      {catalogOpen && <div className="spaces-overlay" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setCatalogOpen(false); }}><aside className="spaces-catalog" role="dialog" aria-modal="true" aria-label="Todas as funções"><header><div><Brand /><h2>Todas as funções</h2></div><button type="button" onClick={() => setCatalogOpen(false)} aria-label="Fechar"><Icone nome="fechar" /></button></header><label><Icone nome="busca" /><input autoFocus value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar função" /></label><div>{visibleCatalog.map((section) => <section key={section.title}><h3>{section.title}</h3><div>{section.actions.map((action) => <ActionLink key={`${section.title}-${action.to}-${action.label}`} action={action} />)}</div></section>)}</div></aside></div>}

      {personalizerOpen && <div className="spaces-overlay" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setPersonalizerOpen(false); }}><aside className="spaces-personalizer" role="dialog" aria-modal="true" aria-label="Personalizar essencial"><header><div><p>SEU ESPAÇO</p><h2>Personalizar essencial</h2><small>Escolha até 8 funções. O acesso completo permanece disponível.</small></div><button type="button" onClick={() => setPersonalizerOpen(false)} aria-label="Fechar"><Icone nome="fechar" /></button></header><div className="spaces-personalizer__count"><span>{essentialPaths.length}/8 selecionadas</span><button onClick={() => { setEssentialPaths(ESSENTIAL_DEFAULTS); localStorage.setItem(storageKey, JSON.stringify(ESSENTIAL_DEFAULTS)); }}>Restaurar padrão</button></div><div className="spaces-personalizer__grid">{allActions.map((action) => { const checked = essentialPaths.includes(action.to); return <button type="button" key={`pick-${action.to}-${action.label}`} className={checked ? "is-selected" : ""} onClick={() => toggleEssential(action.to)} disabled={!checked && essentialPaths.length >= 8}><Icone nome={action.icon} /><span>{action.label}</span><i><Icone nome={checked ? "check" : "adicionar"} /></i></button>; })}</div><footer><button type="button" onClick={() => setPersonalizerOpen(false)}>Salvar meus essenciais</button></footer></aside></div>}
    </main>
  );
}
