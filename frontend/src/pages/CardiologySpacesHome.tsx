import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import CardiologySpaceScene from "../components/CardiologySpaceScene";
import Icone, { type NomeIcone } from "../components/Icone";
import { CoracaoHolografico } from "../components/PreHomeBrand";
import { api } from "../lib/api";
import { heartTeamEnabled, whatsappAssistantEnabled } from "../lib/aiFeatureFlags";
import { useAuth } from "../lib/auth";
import { nomeComTratamento } from "../lib/clinicalIdentity";
import "../styles/cardiology-spaces.css";
import "../styles/cardiology-spaces-v2.css";

type Mode = "complete" | "essential" | "scientific";
type ClinicalSpaceId = "consultorio" | "hospital" | "ensino" | "pesquisa" | "gestao";
type ScientificSpaceId = "descobrir" | "evidencias" | "aprender" | "ensinar" | "produzir";
type SpaceId = ClinicalSpaceId | ScientificSpaceId;
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
type CalendarLocation = {
  id?: number;
  name?: string;
  latitude?: number | null;
  longitude?: number | null;
  address?: Record<string, string | null | undefined> | null;
};
type AgendaItem = {
  id: string | number;
  calendar_kind?: string;
  title?: string | null;
  patient_name?: string | null;
  starts_at: string;
  ends_at?: string | null;
  appointment_type?: string | null;
  status?: string | null;
  location?: CalendarLocation | null;
};
type WorkRoutine = {
  id: string | number;
  weekday: number;
  start_time: string;
  end_time?: string | null;
  label?: string | null;
  routine_type?: string | null;
  location?: CalendarLocation | null;
};
type MobilityTarget = {
  target_key: string;
  starts_at?: string;
  service_name?: string | null;
  title?: string | null;
  arrival_buffer_minutes?: number;
  location?: CalendarLocation | null;
};
type MobilityRoute = {
  duration_seconds: number;
  distance_meters: number;
  congestion?: string;
  summary?: string;
  recommended?: boolean;
};
type MobilityResult = {
  status?: string;
  provider?: string;
  routes?: MobilityRoute[];
  tips?: string[];
  destination?: MobilityTarget | null;
};

const MODE_KEY = "corvia:cardiology-spaces:mode";
const TOUR_KEY = "corvia:cardiology-spaces:tour:v3";
const INVESTOR_TOUR_SESSION_KEY = "corvia:cardiology-spaces:investor-tour-session:v1";

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
      ...(heartTeamEnabled() ? [{ to: "/heart-team", label: "Heart Team Virtual", icon: "round" as NomeIcone }] : []),
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
      { to: "/trilhas", label: "Continuar trilha", icon: "seta" },
      { to: "/apresentacao", label: "Modo apresentação", icon: "documento" },
      { to: "/casos-clinicos", label: "Casos clínicos", icon: "doencas" },
    ],
    next: [
      { to: "/galeria", label: "Atlas & Galeria", icon: "galeria" },
      { to: "/material-paciente", label: "Material educativo", icon: "documento" },
      { to: "/trilhas/timeline", label: "Timeline", icon: "relogio" },
    ],
    references: [
      { to: "/biblioteca", label: "Biblioteca", icon: "conhecimento" },
      { to: "/evidencias", label: "Evidências", icon: "evidencia" },
      { to: "/diretrizes", label: "Diretrizes", icon: "conhecimento" },
      { to: "/doencas", label: "Guia de Doenças", icon: "doencas" },
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
      ...(whatsappAssistantEnabled() ? [{ to: "/whatsapp-assistant", label: "Assistente no WhatsApp", icon: "comunicacao" as NomeIcone }] : []),
    ],
    references: [
      { to: "/minha-conta", label: "Minha conta", icon: "conta" },
      { to: "/privacidade", label: "Privacidade", icon: "check" },
      { to: "/termos", label: "Termos de uso", icon: "documento" },
      { to: "/assistente", label: "Apoio CorVIA", icon: "assistente" },
    ],
  },
];

const SCIENTIFIC_SPACES: Space[] = [
  {
    id: "descobrir", label: "Descobrir", icon: "busca", tone: "cyan",
    description: "Todo o conhecimento cardiovascular conectado em uma única entrada.",
    now: [
      { to: "/busca?modo=tudo-com-tudo", label: "Explorar Tudo com Tudo", icon: "sincronizar" },
      { to: "/biblioteca", label: "Abrir biblioteca", icon: "conhecimento" },
      { to: "/busca", label: "Busca avançada", icon: "busca" },
    ],
    next: [
      { to: "/doencas", label: "Guia de doenças", icon: "doencas" },
      { to: "/medicamentos", label: "Medicamentos", icon: "medicamento" },
      { to: "/exames", label: "Exames cardiovasculares", icon: "ecg" },
    ],
    references: [
      { to: "/calculadoras", label: "Calculadoras", icon: "calculadora" },
      { to: "/fluxogramas", label: "Fluxogramas", icon: "seta" },
      { to: "/diretrizes", label: "Diretrizes", icon: "conhecimento" },
      { to: "/favoritos", label: "Notas & favoritos", icon: "favorito" },
    ],
  },
  {
    id: "evidencias", label: "Evidências", icon: "evidencia", tone: "blue",
    description: "Diretrizes, estudos e evidências organizados para decisões fundamentadas.",
    now: [
      { to: "/evidencias", label: "Revisar evidências", icon: "evidencia" },
      { to: "/estudos", label: "Estudos clínicos", icon: "documento" },
      { to: "/diretrizes", label: "Diretrizes & guidelines", icon: "conhecimento" },
    ],
    next: [
      { to: "/documentos-cientificos-ia", label: "Documento científico IA", icon: "assistente" },
      { to: "/biblioteca", label: "Literatura científica", icon: "conhecimento" },
      { to: "/busca", label: "Pesquisar no acervo", icon: "busca" },
    ],
    references: [
      { to: "/trilhas/timeline", label: "Timeline do conhecimento", icon: "seta" },
      { to: "/casos-clinicos", label: "Casos clínicos", icon: "doencas" },
      { to: "/calculadoras", label: "Calculadoras", icon: "calculadora" },
      { to: "/exportar", label: "Exportar conteúdo", icon: "documento" },
    ],
  },
  {
    id: "aprender", label: "Aprender", icon: "curso", tone: "violet",
    description: "Aprendizagem contínua por trilhas, casos e conteúdo multimodal.",
    now: [
      { to: "/trilhas", label: "Minhas trilhas", icon: "seta" },
      { to: "/casos-clinicos", label: "Resolver casos clínicos", icon: "doencas" },
      { to: "/doencas", label: "Revisar doenças", icon: "doencas" },
    ],
    next: [
      { to: "/exames", label: "Interpretar exames", icon: "ecg" },
      { to: "/calculadoras", label: "Praticar calculadoras", icon: "calculadora" },
      { to: "/galeria", label: "Atlas & galeria", icon: "galeria" },
    ],
    references: [
      { to: "/diretrizes", label: "Diretrizes", icon: "conhecimento" },
      { to: "/evidencias", label: "Evidências", icon: "evidencia" },
      { to: "/biblioteca", label: "Biblioteca", icon: "conhecimento" },
      { to: "/trilhas/timeline", label: "Timeline", icon: "relogio" },
    ],
  },
  {
    id: "ensinar", label: "Ensinar", icon: "curso", tone: "rose",
    description: "Ferramentas para transformar conhecimento em aulas e educação em saúde.",
    now: [
      { to: "/apresentacao", label: "Modo apresentação", icon: "documento" },
      { to: "/material-paciente", label: "Material ao paciente", icon: "comunicacao" },
      { to: "/casos-clinicos", label: "Ensinar com casos", icon: "doencas" },
    ],
    next: [
      { to: "/exportar", label: "Exportar aula e conteúdo", icon: "documento" },
      { to: "/documentos-cientificos-ia", label: "Preparar documento IA", icon: "assistente" },
      { to: "/galeria", label: "Selecionar imagens", icon: "galeria" },
    ],
    references: [
      { to: "/biblioteca", label: "Biblioteca", icon: "conhecimento" },
      { to: "/diretrizes", label: "Diretrizes", icon: "evidencia" },
      { to: "/trilhas", label: "Trilhas educacionais", icon: "seta" },
      { to: "/favoritos", label: "Notas & favoritos", icon: "favorito" },
    ],
  },
  {
    id: "produzir", label: "Produzir", icon: "documento", tone: "teal",
    description: "Crie, apresente e exporte conteúdo científico com rastreabilidade.",
    now: [
      { to: "/documentos-cientificos-ia", label: "Criar documento científico", icon: "assistente" },
      { to: "/apresentacao", label: "Criar apresentação", icon: "documento" },
      { to: "/exportar", label: "Exportar conteúdo", icon: "seta" },
    ],
    next: [
      { to: "/biblioteca", label: "Consultar fontes", icon: "conhecimento" },
      { to: "/busca?modo=tudo-com-tudo", label: "Conectar referências", icon: "sincronizar" },
      { to: "/evidencias", label: "Validar evidências", icon: "evidencia" },
    ],
    references: [
      { to: "/estudos", label: "Estudos clínicos", icon: "documento" },
      { to: "/diretrizes", label: "Diretrizes", icon: "conhecimento" },
      { to: "/material-paciente", label: "Material ao paciente", icon: "comunicacao" },
      { to: "/favoritos", label: "Notas & favoritos", icon: "favorito" },
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
    ["/corvia-mail", "CorVIA Mail", "mail"], ["/caixa-de-email", "Caixa de e-mail unificada", "mail"],
    ["/assistente", "Apoio CorVIA", "assistente"], ["/telediagnostico", "Telediagnóstico & Consultoria", "evidencia"],
    ["/material-paciente", "Material para paciente", "documento"],
  ].map(([to, label, icon]) => ({ to, label, icon: icon as NomeIcone })) },
  { title: "Ciência & Ensino", actions: [
    ["/evidencias", "Estudos & Evidências", "evidencia"], ["/estudos", "Estudos clínicos", "evidencia"],
    ["/documentos-cientificos-ia", "Documentos científicos IA", "assistente"], ["/trilhas/timeline", "Timeline do conhecimento", "seta"],
    ["/trilhas", "Trilhas", "seta"], ["/casos-clinicos", "Casos clínicos", "doencas"],
    ["/diretrizes", "Diretrizes & Guidelines", "conhecimento"], ["/biblioteca", "Biblioteca científica", "conhecimento"],
    ["/galeria", "Atlas & Galeria", "galeria"], ["/apresentacao", "Modo apresentação", "documento"],
    ["/exportar", "Exportar conteúdo", "documento"],
  ].map(([to, label, icon]) => ({ to, label, icon: icon as NomeIcone })) },
  { title: "Produtividade & Rede", actions: [
    ["/indicadores", "Indicadores & Métricas", "indicadores"], ["/favoritos", "Notas & Favoritos", "favorito"],
    ["/busca", "Busca avançada", "busca"], ["/busca?modo=tudo-com-tudo", "Tudo com Tudo", "sincronizar"],
    ["/usuarios-online", "Rede profissional", "pacientes"], ["/sincronizacao", "Contas conectadas", "sincronizar"],
  ].map(([to, label, icon]) => ({ to, label, icon: icon as NomeIcone })) },
  { title: "Conta & Administração", actions: [
    { to: "/minha-conta", label: "Minha Conta", icon: "conta" },
    { to: "/privacidade", label: "Segurança & Privacidade", icon: "check" },
    { to: "/termos", label: "Termos de uso", icon: "documento" },
    { to: "/tour", label: "Suporte & Ajuda", icon: "curso" },
    { to: "/verificacao-identidade", label: "Verificação de identidade", icon: "check" },
    { to: "/excluir-conta", label: "Excluir conta e dados", icon: "conta" },
    { to: "/admin", label: "Painel administrativo", icon: "gestao", adminOnly: true },
    { to: "/admin/usuarios", label: "Usuários & Permissões", icon: "pacientes", adminOnly: true },
    { to: "/fila-telediagnostico", label: "Fila de telediagnóstico", icon: "evidencia", adminOnly: true },
    { to: "/receitas-para-assinatura", label: "Receitas para assinatura", icon: "prescricao", adminOnly: true },
  ] },
  ...((heartTeamEnabled() || whatsappAssistantEnabled()) ? [{ title: "Inteligência integrada", actions: [
    ...(heartTeamEnabled() ? [{ to: "/heart-team", label: "Heart Team Virtual", icon: "round" as NomeIcone }] : []),
    ...(whatsappAssistantEnabled() ? [{ to: "/whatsapp-assistant", label: "Assistente Pessoal no WhatsApp", icon: "comunicacao" as NomeIcone }] : []),
    { to: "/admin/operacoes-ia", label: "Operações e custos de IA", icon: "indicadores" as NomeIcone, adminOnly: true },
  ] }] : []),
];

const ESSENTIAL_DEFAULTS: Record<ClinicalSpaceId, string[]> = {
  consultorio: ["/agenda", "/receituario", "/prontuario", "/documentos", "/exames", "/calculadoras"],
  hospital: ["/round", "/exames", "/documentos", "/checklists", "/emergencia", "/calculadoras"],
  ensino: ["/trilhas", "/casos-clinicos", "/apresentacao", "/galeria", "/diretrizes", "/biblioteca"],
  pesquisa: ["/estudos", "/evidencias", "/documentos-cientificos-ia", "/biblioteca", "/diretrizes", "/exportar"],
  gestao: ["/indicadores", "/agenda", "/usuarios-online", "/sincronizacao", "/corvia-mail", "/minha-conta"],
};

const SPACE_TONES: Record<ClinicalSpaceId, Tone> = {
  consultorio: "cyan", hospital: "blue", ensino: "violet", pesquisa: "rose", gestao: "teal",
};

function Brand() {
  return (
    <span className="spaces-brand" aria-label="CorVIA Cardiology Spaces">
      <img src="/corvia-mark-canonical.svg" alt="" />
      <span><strong><i>Cor</i><b>VIA</b></strong><small>CARDIOLOGY SPACES</small></span>
    </span>
  );
}

function ActionLink({ action, compact = false }: { action: Action; compact?: boolean }) {
  return <Link className={`spaces-action${compact ? " spaces-action--compact" : ""}`} to={action.to}><Icone nome={action.icon} /><span>{action.label}</span></Link>;
}

function sameLocalDay(value: string, reference = new Date()) {
  const date = new Date(value);
  return !Number.isNaN(date.getTime()) && date.getFullYear() === reference.getFullYear() && date.getMonth() === reference.getMonth() && date.getDate() === reference.getDate();
}

function time(value?: string | null) {
  if (!value) return "";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "" : date.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
}

function routineToAgendaItem(routine: WorkRoutine): AgendaItem | null {
  const today = new Date();
  const pythonWeekday = (today.getDay() + 6) % 7;
  if (routine.weekday !== pythonWeekday || !routine.start_time) return null;
  const [hour = "0", minute = "0", second = "0"] = routine.start_time.split(":");
  const start = new Date(today);
  start.setHours(Number(hour), Number(minute), Number(second), 0);
  const end = routine.end_time ? new Date(today) : null;
  if (end && routine.end_time) {
    const [eh = "0", em = "0", es = "0"] = routine.end_time.split(":");
    end.setHours(Number(eh), Number(em), Number(es), 0);
  }
  return {
    id: `routine-${routine.id}`,
    calendar_kind: "routine",
    title: routine.label || "Rotina profissional",
    appointment_type: routine.routine_type || "Rotina",
    starts_at: start.toISOString(),
    ends_at: end?.toISOString(),
    status: "confirmado",
    location: routine.location,
  };
}

function inferClinicalSpace(item: AgendaItem): ClinicalSpaceId {
  const haystack = `${item.title || ""} ${item.appointment_type || ""} ${item.location?.name || ""}`.toLocaleLowerCase("pt-BR");
  if (/hospital|round|enferm|uti|uco|intern/.test(haystack)) return "hospital";
  if (/aula|ensino|precept|estudo|trilha/.test(haystack)) return "ensino";
  if (/pesquisa|artigo|cient[ií]fic|congresso/.test(haystack)) return "pesquisa";
  if (/gest[aã]o|administr|reuni[aã]o|financeiro/.test(haystack)) return "gestao";
  return "consultorio";
}

function distanceLabel(meters?: number) {
  if (!meters || meters <= 0) return "";
  return meters >= 1000 ? `${(meters / 1000).toFixed(meters >= 10000 ? 0 : 1)} km` : `${Math.round(meters)} m`;
}

function currentPosition(): Promise<GeolocationPosition> {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("Geolocalização não disponível neste dispositivo."));
      return;
    }
    navigator.geolocation.getCurrentPosition(resolve, reject, { enableHighAccuracy: true, timeout: 12000, maximumAge: 60000 });
  });
}

export default function CardiologySpacesHome() {
  const { usuario } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState<Mode | null>(() => {
    const saved = sessionStorage.getItem(MODE_KEY);
    return saved === "complete" || saved === "essential" || saved === "scientific" ? saved : null;
  });
  const [selectedSpace, setSelectedSpace] = useState<SpaceId>(() => sessionStorage.getItem(MODE_KEY) === "scientific" ? "descobrir" : "consultorio");
  const [previewSpace, setPreviewSpace] = useState<SpaceId | null>(null);
  const [catalogOpen, setCatalogOpen] = useState(false);
  const [personalizerOpen, setPersonalizerOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [essentialRevision, setEssentialRevision] = useState(0);
  const [dayItems, setDayItems] = useState<AgendaItem[]>([]);
  const [dayState, setDayState] = useState<"loading" | "ready" | "error">("loading");
  const [mobilityTarget, setMobilityTarget] = useState<MobilityTarget | null>(null);
  const [mobilityResult, setMobilityResult] = useState<MobilityResult | null>(null);
  const [travelOpen, setTravelOpen] = useState(false);
  const [travelBusy, setTravelBusy] = useState(false);
  const [travelError, setTravelError] = useState<string | null>(null);

  useEffect(() => {
    document.body.classList.add("cardiology-spaces-active");
    return () => document.body.classList.remove("cardiology-spaces-active");
  }, []);

  useEffect(() => {
    let active = true;
    setDayState("loading");
    Promise.allSettled([
      api.get<AgendaItem[]>("/agenda/appointments"),
      api.get<AgendaItem[]>("/agenda/commitments"),
      api.get<WorkRoutine[]>("/agenda/work-routines"),
    ]).then((results) => {
      if (!active) return;
      const [appointmentsResult, commitmentsResult, routinesResult] = results;
      const appointments = appointmentsResult.status === "fulfilled" && Array.isArray(appointmentsResult.value) ? appointmentsResult.value : [];
      const commitments = commitmentsResult.status === "fulfilled" && Array.isArray(commitmentsResult.value) ? commitmentsResult.value : [];
      const routines = routinesResult.status === "fulfilled" && Array.isArray(routinesResult.value) ? routinesResult.value : [];
      const routineItems = routines.map(routineToAgendaItem).filter((item): item is AgendaItem => Boolean(item));
      const merged = [...appointments, ...commitments, ...routineItems]
        .filter((item) => item?.starts_at && sameLocalDay(item.starts_at) && !/cancel|faltou/i.test(item.status || ""))
        .sort((a, b) => new Date(a.starts_at).getTime() - new Date(b.starts_at).getTime());
      const seen = new Set<string>();
      const unique = merged.filter((item) => {
        const key = `${item.starts_at}|${item.title || item.patient_name || item.appointment_type || "compromisso"}`;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      });
      setDayItems(unique.slice(0, 5));
      setDayState(results.every((result) => result.status === "rejected") ? "error" : "ready");
    }).catch(() => {
      if (!active) return;
      setDayItems([]);
      setDayState("error");
    });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!mode || mode === "scientific" || usuario?.investidor) return;
    let active = true;
    api.post<MobilityTarget | null>("/agenda/mobility/prepare-next-target", {})
      .then((target) => { if (active) setMobilityTarget(target || null); })
      .catch(() => { if (active) setMobilityTarget(null); });
    return () => { active = false; };
  }, [mode, usuario?.investidor]);

  useEffect(() => {
    if (!catalogOpen && !personalizerOpen && !travelOpen) return;
    const close = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      setCatalogOpen(false);
      setPersonalizerOpen(false);
      setTravelOpen(false);
    };
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, [catalogOpen, personalizerOpen, travelOpen]);

  const availableSpaces = mode === "scientific" ? SCIENTIFIC_SPACES : SPACES;
  const activeSpace = availableSpaces.find((space) => space.id === (previewSpace || selectedSpace)) || availableSpaces[0];
  const visibleCatalog = useMemo(() => CATALOG.map((section) => ({
    ...section,
    actions: section.actions.filter((action) => (!action.adminOnly || usuario?.role === "admin") && (!query || action.label.toLocaleLowerCase("pt-BR").includes(query.toLocaleLowerCase("pt-BR")))),
  })).filter((section) => section.actions.length), [query, usuario?.role]);
  const allActions = useMemo(() => CATALOG.flatMap((section) => section.actions).filter((action) => !action.adminOnly || usuario?.role === "admin"), [usuario?.role]);

  const essentialPaths = useMemo(() => {
    if (mode !== "essential" || !SPACES.some((space) => space.id === activeSpace.id)) return [];
    const spaceId = activeSpace.id as ClinicalSpaceId;
    const key = `corvia:cardiology-spaces:essentials:${usuario?.id || "user"}:${spaceId}`;
    try {
      const saved = JSON.parse(localStorage.getItem(key) || "[]") as string[];
      return saved.length ? saved.slice(0, 8) : ESSENTIAL_DEFAULTS[spaceId];
    } catch {
      return ESSENTIAL_DEFAULTS[spaceId];
    }
  }, [activeSpace.id, essentialRevision, mode, usuario?.id]);

  const essentials = essentialPaths.map((path) => allActions.find((action) => action.to === path)).filter((action): action is Action => Boolean(action));
  const contextActions = useMemo(() => {
    const candidates = [...activeSpace.now, ...activeSpace.next, ...activeSpace.references].filter((action) => !action.adminOnly || usuario?.role === "admin");
    const seen = new Set<string>();
    return candidates.filter((action) => {
      if (seen.has(action.to)) return false;
      seen.add(action.to);
      return true;
    }).slice(0, 5);
  }, [activeSpace, usuario?.role]);

  const chamamento = usuario?.professional_title?.trim() || nomeComTratamento(usuario, true);
  const question = mode === "scientific" ? `Como ${chamamento} quer explorar o conhecimento agora?` : `Onde ${chamamento} vai trabalhar agora?`;
  const travelTarget = mobilityResult?.destination || mobilityTarget;
  const bestRoute = mobilityResult?.routes?.[0];
  const travelMinutes = bestRoute?.duration_seconds ? Math.max(1, Math.round(bestRoute.duration_seconds / 60)) : null;

  const chooseMode = useCallback((nextMode: Mode) => {
    sessionStorage.setItem(MODE_KEY, nextMode);
    setMode(nextMode);
    setSelectedSpace(nextMode === "scientific" ? "descobrir" : "consultorio");
    setPreviewSpace(null);
    const investorNeedsTour = usuario?.investidor && !sessionStorage.getItem(INVESTOR_TOUR_SESSION_KEY);
    if (usuario?.onboarding_pendente || investorNeedsTour) {
      navigate("/tour/cardiology-spaces?retorno=/");
    }
  }, [navigate, usuario?.investidor, usuario?.onboarding_pendente]);

  function resetMode() {
    sessionStorage.removeItem(MODE_KEY);
    setMode(null);
    setSelectedSpace("consultorio");
    setPreviewSpace(null);
  }

  function toggleEssential(path: string) {
    if (mode !== "essential" || !SPACES.some((space) => space.id === selectedSpace)) return;
    const spaceId = selectedSpace as ClinicalSpaceId;
    const key = `corvia:cardiology-spaces:essentials:${usuario?.id || "user"}:${spaceId}`;
    let current = ESSENTIAL_DEFAULTS[spaceId];
    try {
      const saved = JSON.parse(localStorage.getItem(key) || "[]") as string[];
      if (saved.length) current = saved.slice(0, 8);
    } catch { /* usa padrão */ }
    const next = current.includes(path) ? current.filter((item) => item !== path) : [...current, path].slice(0, 8);
    localStorage.setItem(key, JSON.stringify(next));
    setEssentialRevision((value) => value + 1);
  }

  function restoreEssentialDefaults() {
    if (!SPACES.some((space) => space.id === selectedSpace)) return;
    const spaceId = selectedSpace as ClinicalSpaceId;
    localStorage.setItem(`corvia:cardiology-spaces:essentials:${usuario?.id || "user"}:${spaceId}`, JSON.stringify(ESSENTIAL_DEFAULTS[spaceId]));
    setEssentialRevision((value) => value + 1);
  }

  async function startTravel() {
    setTravelOpen(true);
    setTravelBusy(true);
    setTravelError(null);
    setMobilityResult(null);
    try {
      if (usuario?.investidor) {
        setTravelError("No Modo Investidor, o deslocamento é demonstrativo e não usa localização real.");
        return;
      }
      let target = mobilityTarget;
      if (!target) {
        target = await api.post<MobilityTarget | null>("/agenda/mobility/prepare-next-target", {});
        setMobilityTarget(target || null);
      }
      if (!target?.target_key) {
        setTravelError("Não há um próximo compromisso presencial com local cadastrado para traçar a rota.");
        return;
      }
      const position = await currentPosition();
      const result = await api.post<MobilityResult>("/agenda/mobility/commute-target", {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
        target_key: target.target_key,
      });
      setMobilityResult(result);
      if (!result.routes?.length && result.status !== "live") {
        setTravelError(result.status === "not_configured" ? "O destino está pronto, mas o provedor de trânsito ainda não está configurado." : "A rota não pôde ser calculada agora. O destino pode ser aberto no mapa.");
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "Não foi possível calcular o deslocamento.";
      setTravelError(message);
    } finally {
      setTravelBusy(false);
    }
  }

  function openExternalMap() {
    const location = travelTarget?.location;
    if (location?.latitude == null || location?.longitude == null) {
      setTravelError("Este destino ainda não possui coordenadas para abrir a navegação.");
      return;
    }
    const url = `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(`${location.latitude},${location.longitude}`)}&travelmode=driving`;
    window.open(url, "_blank", "noopener,noreferrer");
  }

  if (!mode) {
    return (
      <main className="spaces-choice">
        <div className="spaces-choice__heart" aria-hidden="true"><CoracaoHolografico /></div>
        <header><Brand /><span className="spaces-user"><Icone nome="conta" /> {nomeComTratamento(usuario, true)}</span></header>
        <section className="spaces-choice__content">
          <p className="spaces-eyebrow">CARDIOLOGY SPACES</p>
          <h1>Como {chamamento} quer trabalhar hoje?</h1>
          <p>Escolha a experiência. O coração CorVIA permanece como eixo visual e todas as funções continuam acessíveis pelo catálogo completo.</p>
          <div className="spaces-choice__cards">
            <button type="button" onClick={() => chooseMode("complete")}>
              <span className="spaces-choice__icon"><Icone nome="gestao" /></span>
              <strong>Completo</strong><small>Todos os ambientes e as três camadas funcionais: Agora, Em seguida e Referências.</small>
              <em>Entrar no sistema completo <Icone nome="seta" /></em>
            </button>
            <button type="button" onClick={() => chooseMode("essential")}>
              <span className="spaces-choice__icon"><Icone nome="configuracao" /></span>
              <strong>Essencial</strong><small>A mesma potência, com a rotina em foco e essenciais personalizados por espaço.</small>
              <em>Entrar no sistema essencial <Icone nome="seta" /></em>
            </button>
            <button type="button" className="spaces-choice__science" onClick={() => chooseMode("scientific")}>
              <span className="spaces-choice__icon"><Icone nome="conhecimento" /></span>
              <strong>Ciência & Ensino</strong><small>Descobrir, validar evidências, aprender, ensinar e produzir no mesmo universo visual.</small>
              <em>Entrar no ambiente científico <Icone nome="seta" /></em>
            </button>
          </div>
        </section>
        <footer>O ambiente muda. <strong>O médico continua no centro.</strong></footer>
      </main>
    );
  }

  return (
    <main className={`spaces-home spaces-home--${activeSpace.tone}${mode === "scientific" ? " spaces-home--scientific" : ""}`}>
      <div className="spaces-home__heart" aria-hidden="true"><CoracaoHolografico /></div>
      <header className="spaces-home__topbar">
        <button type="button" className="spaces-brand-button" onClick={resetMode} aria-label="Voltar à escolha de experiência"><Brand /></button>
        <nav aria-label="Modo de trabalho">
          <button className={mode === "complete" ? "is-active" : ""} onClick={() => chooseMode("complete")}>Completo</button>
          <button className={mode === "essential" ? "is-active" : ""} onClick={() => chooseMode("essential")}>Essencial</button>
          <button className={mode === "scientific" ? "is-active" : ""} onClick={() => chooseMode("scientific")}>Ciência & Ensino</button>
        </nav>
        <Link to="/minha-conta" className="spaces-user"><Icone nome="conta" /> {nomeComTratamento(usuario, true)} <Icone nome="chevron" /></Link>
      </header>

      <aside className="spaces-context-rail" aria-label={`Ferramentas do espaço ${activeSpace.label}`}>
        <span><small>NO ESPAÇO</small><strong>{activeSpace.label}</strong></span>
        {contextActions.map((action) => <ActionLink key={`rail-${activeSpace.id}-${action.to}`} action={action} compact />)}
        <button type="button" className="spaces-context-rail__all" onClick={() => setCatalogOpen(true)}><Icone nome="mais" /><span>Todas as funções</span></button>
        {mode === "essential" && <button type="button" className="spaces-context-rail__personalize" onClick={() => { setPreviewSpace(null); setPersonalizerOpen(true); }}><Icone nome="configuracao" /><span>Personalizar</span></button>}
      </aside>

      <section className="spaces-workspace">
        <header className="spaces-workspace__greeting">
          <h1>{question}</h1>
          <span>{mode === "scientific" ? "Escolha uma jornada científica. O conhecimento continua conectado." : "Escolha o ambiente. A interface reorganiza as prioridades sem esconder o CorVIA."}</span>
        </header>

        <div className="spaces-doors" onMouseLeave={() => setPreviewSpace(null)}>
          {availableSpaces.map((space) => {
            const active = activeSpace.id === space.id;
            return (
              <button key={space.id} type="button" className={`spaces-door spaces-door--${space.tone}${active ? " is-active" : ""}`} onMouseEnter={() => setPreviewSpace(space.id)} onFocus={() => setPreviewSpace(space.id)} onBlur={() => setPreviewSpace(null)} onClick={() => { setSelectedSpace(space.id); setPreviewSpace(null); }} aria-pressed={selectedSpace === space.id}>
                <span><Icone nome={space.icon} />{space.label}</span>
                <i aria-hidden="true"><CardiologySpaceScene space={space.id} /></i>
              </button>
            );
          })}
        </div>

        <div className="spaces-title"><span>{mode === "scientific" ? "Minha jornada" : "Meu espaço"}</span> <strong>{activeSpace.label}</strong><small>{activeSpace.description}</small></div>

        <div className="spaces-layers" aria-live="polite">
          <section className="spaces-layer spaces-layer--now">
            <header><span>AGORA</span><strong>{activeSpace.label === "Hospital" ? "Round hospitalar · prioridades" : mode === "scientific" ? `Jornada para ${activeSpace.label.toLocaleLowerCase("pt-BR")}` : `Rotina de ${activeSpace.label.toLocaleLowerCase("pt-BR")}`}</strong></header>
            <div>{activeSpace.now.filter((action) => !action.adminOnly || usuario?.role === "admin").map((action) => <ActionLink key={`${activeSpace.id}-now-${action.label}`} action={action} />)}</div>
          </section>
          {mode !== "essential" ? <>
            <section className="spaces-layer spaces-layer--next"><header><span>{mode === "scientific" ? "APROFUNDAR" : "EM SEGUIDA"}</span></header><div>{activeSpace.next.map((action) => <ActionLink key={`${activeSpace.id}-next-${action.label}`} action={action} />)}</div></section>
            <section className="spaces-layer spaces-layer--refs"><header><span>{mode === "scientific" ? "CONEXÕES DO CONHECIMENTO" : "REFERÊNCIAS DO ESPAÇO"}</span></header><div>{activeSpace.references.map((action) => <ActionLink key={`${activeSpace.id}-ref-${action.label}`} action={action} />)}</div></section>
          </> : <>
            <section className="spaces-layer spaces-layer--essential"><header><span>MEUS ESSENCIAIS</span></header><div>{essentials.slice(0, 6).map((action) => <ActionLink key={`essential-${activeSpace.id}-${action.to}`} action={action} />)}</div></section>
            <button type="button" className="spaces-personalize" onClick={() => { setPreviewSpace(null); setPersonalizerOpen(true); }}><Icone nome="configuracao" /> Personalizar essencial</button>
          </>}
        </div>
        <div className="spaces-doctor"><Icone nome="conta" /><span>{nomeComTratamento(usuario, true)}</span><small>{mode === "scientific" ? "Minha jornada ativa" : "Meu espaço ativo"}</small></div>
      </section>

      <aside className="spaces-day">
        <h2>{mode === "scientific" ? "Minha jornada científica" : "Meu dia entre espaços"}</h2>
        {mode === "scientific" ? <>
          <Link to="/busca?modo=tudo-com-tudo" className="spaces-day__item spaces-day__item--cyan"><i /><span><strong>Tudo com Tudo</strong><small>Explorar relações</small></span></Link>
          <Link to="/trilhas" className="spaces-day__item spaces-day__item--violet"><i /><span><strong>Trilhas</strong><small>Continuar aprendizagem</small></span></Link>
          <Link to="/favoritos" className="spaces-day__item spaces-day__item--rose"><i /><span><strong>Favoritos</strong><small>Retomar leituras</small></span></Link>
          <Link to="/trilhas/timeline" className="spaces-day__travel"><Icone nome="relogio" /><span><strong>Minha timeline</strong><small>Ver evolução do conhecimento</small></span></Link>
        </> : dayItems.length ? <>
          {dayItems.slice(0, 4).map((item) => {
            const itemSpace = inferClinicalSpace(item);
            const label = item.title || item.patient_name || item.appointment_type || "Compromisso";
            return <Link to="/agenda" key={`${item.calendar_kind || "item"}-${item.id}`} className={`spaces-day__item spaces-day__item--${SPACE_TONES[itemSpace]}`}><i /><span><strong>{label}</strong><small>{time(item.starts_at)}{item.location?.name ? ` · ${item.location.name}` : ""}</small></span></Link>;
          })}
          <button type="button" className="spaces-day__travel" onClick={() => void startTravel()}><Icone nome="rota" /><span><strong>Deslocamento</strong><small>{travelMinutes ? `${travelMinutes} min · ${distanceLabel(bestRoute?.distance_meters)}` : mobilityTarget?.location?.name ? `Traçar rota para ${mobilityTarget.location.name}` : "Traçar a próxima viagem"}</small></span></button>
        </> : <div className={`spaces-day__empty is-${dayState}`} role="status"><strong>{dayState === "loading" ? "Sincronizando seu dia…" : dayState === "error" ? "Agenda indisponível agora" : "Nenhum compromisso hoje"}</strong><small>{dayState === "error" ? "Abra a Agenda para consultar as fontes conectadas." : "Atendimentos, compromissos e rotinas aparecerão aqui."}</small><ActionLink action={{ to: "/agenda", label: "Abrir agenda completa", icon: "agenda" }} /></div>}
      </aside>

      <nav className="spaces-dock" aria-label="Ações globais">
        {mode === "scientific" ? <>
          <Link to="/busca?modo=tudo-com-tudo"><Icone nome="sincronizar" /><span>Tudo com Tudo</span></Link>
          <Link to="/biblioteca"><Icone nome="conhecimento" /><span>Biblioteca</span></Link>
          <Link to="/evidencias"><Icone nome="evidencia" /><span>Evidências</span></Link>
          <Link to="/trilhas"><Icone nome="seta" /><span>Trilhas</span></Link>
          <Link to="/documentos-cientificos-ia"><Icone nome="assistente" /><span>Documento IA</span></Link>
          <Link to="/apresentacao"><Icone nome="documento" /><span>Apresentar</span></Link>
        </> : <>
          <Link to="/receituario"><Icone nome="prescricao" /><span>Prescrever</span></Link>
          <Link to="/documentos"><Icone nome="clinica" /><span>Solicitar exames</span></Link>
          <Link to="/prontuario"><Icone nome="pacientes" /><span>Prontuário</span></Link>
          <Link to="/documentos"><Icone nome="documento" /><span>Documentos</span></Link>
          <Link to="/busca?modo=tudo-com-tudo"><Icone nome="sincronizar" /><span>Tudo com Tudo</span></Link>
          <Link to="/assistente"><Icone nome="assistente" /><span>Apoio CorVIA</span></Link>
        </>}
      </nav>
      <p className="spaces-motto">{mode === "scientific" ? <>O conhecimento <strong>se conecta.</strong> {nomeComTratamento(usuario, true)} <strong>conduz a jornada.</strong></> : <>O ambiente <strong>muda.</strong> O médico <strong>continua no centro.</strong></>}</p>

      {catalogOpen && <div className="spaces-overlay" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setCatalogOpen(false); }}><aside className="spaces-catalog" role="dialog" aria-modal="true" aria-label="Todas as funções"><header><div><Brand /><h2>Todas as funções</h2></div><button type="button" onClick={() => setCatalogOpen(false)} aria-label="Fechar"><Icone nome="fechar" /></button></header><label><Icone nome="busca" /><input autoFocus value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar função" /></label><div>{visibleCatalog.map((section) => <section key={section.title}><h3>{section.title}</h3><div>{section.actions.map((action) => <ActionLink key={`${section.title}-${action.to}-${action.label}`} action={action} />)}</div></section>)}</div></aside></div>}

      {personalizerOpen && mode === "essential" && <div className="spaces-overlay" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setPersonalizerOpen(false); }}><aside className="spaces-personalizer" role="dialog" aria-modal="true" aria-label="Personalizar essencial"><header><div><p>SEU ESPAÇO {activeSpace.label.toLocaleUpperCase("pt-BR")}</p><h2>Personalizar essencial</h2><small>Escolha até 8 funções para este espaço. O catálogo completo permanece disponível.</small></div><button type="button" onClick={() => setPersonalizerOpen(false)} aria-label="Fechar"><Icone nome="fechar" /></button></header><div className="spaces-personalizer__count"><span>{essentialPaths.length}/8 selecionadas</span><button type="button" onClick={restoreEssentialDefaults}>Restaurar padrão</button></div><div className="spaces-personalizer__grid">{allActions.map((action) => { const checked = essentialPaths.includes(action.to); return <button type="button" key={`pick-${action.to}-${action.label}`} className={checked ? "is-selected" : ""} onClick={() => toggleEssential(action.to)} disabled={!checked && essentialPaths.length >= 8}><Icone nome={action.icon} /><span>{action.label}</span><i><Icone nome={checked ? "check" : "adicionar"} /></i></button>; })}</div><footer><button type="button" onClick={() => setPersonalizerOpen(false)}>Salvar meus essenciais</button></footer></aside></div>}

      {travelOpen && <div className="spaces-overlay spaces-travel-overlay" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setTravelOpen(false); }}><section className="spaces-travel" role="dialog" aria-modal="true" aria-label="Deslocamento entre espaços"><header><div><p>DESLOCAMENTO CORVIA</p><h2>Viagem entre espaços</h2><small>Seu próximo destino transformado em uma rota orbital. A localização atual é usada somente para esta consulta.</small></div><button type="button" onClick={() => setTravelOpen(false)} aria-label="Fechar"><Icone nome="fechar" /></button></header><div className="spaces-orbit" aria-hidden="true"><span className="spaces-orbit__planet spaces-orbit__planet--origin"><i /><b>AGORA</b></span><span className="spaces-orbit__path"><i /></span><span className="spaces-orbit__planet spaces-orbit__planet--destination"><i /><b>{travelTarget?.location?.name || travelTarget?.title || "DESTINO"}</b></span></div><div className="spaces-travel__status">{travelBusy ? <><strong>Calculando trajetória…</strong><small>Consultando o próximo compromisso e o trânsito atual.</small></> : bestRoute ? <><strong>{travelMinutes} min <em>·</em> {distanceLabel(bestRoute.distance_meters)}</strong><small>{bestRoute.summary || "Rota recomendada"}{bestRoute.congestion ? ` · trânsito ${bestRoute.congestion}` : ""}{mobilityResult?.provider ? ` · ${mobilityResult.provider}` : ""}</small></> : <><strong>{travelTarget?.location?.name || "Próximo destino"}</strong><small>{travelError || "Pronto para traçar sua próxima rota."}</small></>}</div>{mobilityResult?.tips?.length ? <ul>{mobilityResult.tips.slice(0, 3).map((tip) => <li key={tip}>{tip}</li>)}</ul> : null}<footer><button type="button" className="spaces-travel__recalculate" onClick={() => void startTravel()} disabled={travelBusy}><Icone nome="rota" /> {travelBusy ? "Calculando…" : "Recalcular rota"}</button><button type="button" className="spaces-travel__maps" onClick={openExternalMap}><Icone nome="rota" /> Abrir navegação no mapa</button></footer></section></div>}
    </main>
  );
}

export { TOUR_KEY, INVESTOR_TOUR_SESSION_KEY };
