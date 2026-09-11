import ClinicalChangeApprovalNotice from "../components/ClinicalChangeApprovalNotice";
import { useCallback, useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import AtelierHomeView from "../components/AtelierHomeView";
import { CLINICAL_SPACES, type FunctionalSpace } from "../lib/clinicalRouteRegistry";
import { atelierCatalogRoutesFor as catalogRoutesFor, atelierContextFromSearch, readAtelierContext, writeAtelierContext } from "../lib/atelierNavigation";
import { emptyShelfPreferences, migrateShelfPreferences, previewShelfImport, saveShelfProfile, shelfOrganizationLabel, shelfPreferenceStore, shelfProfileItems, shelfReserveFor, SHELF_PREFERENCES_PREFIX, type ShelfPreferences } from "../lib/atelierShelfPreferences";
import CardiologySpaceScene from "../components/CardiologySpaceScene";
import Icone, { type NomeIcone } from "../components/Icone";
import MapaDeslocamento, { type RotaDeslocamento } from "../components/MapaDeslocamento";
import { CoracaoHolografico } from "../components/PreHomeBrand";
import GalaxyThemeToggle from "../components/GalaxyThemeToggle";
import UniverseStars from "../components/UniverseStars";
import ScientificIntelligenceMonitor from "../components/ScientificIntelligenceMonitor";
import { mobilitySchedule, scheduleDateTime } from "../lib/mobilitySchedule";
import { coordinateValid, geometryAvailable, mobilityResultError as mobilityRouteError } from "../lib/mobilityGeometry";
import { api, assetUrl, type Usuario } from "../lib/api";
import { heartTeamEnabled, whatsappAssistantEnabled } from "../lib/aiFeatureFlags";
import { useAuth } from "../lib/auth";
import { chamamentoComArtigo, nomeComTratamento } from "../lib/clinicalIdentity";
import { withoutReservedSmokeTestRecord, withoutReservedSmokeTestRecords } from "../lib/reservedSmokeAgenda";
import "../styles/cardiology-spaces-home.css";
import "../styles/corvia-internal-final-approved-20260904.css";
import "../styles/cardiology-spaces-catalog-theme.css";

type Mode = "complete" | "essential" | "scientific";
type ClinicalSpaceId = "consultorio" | "hospital" | "ensino" | "pesquisa" | "gestao";
type ScientificSpaceId = "descobrir" | "evidencias" | "aprender" | "ensinar" | "produzir";
type SpaceId = ClinicalSpaceId | ScientificSpaceId;
type Tone = "cyan" | "blue" | "violet" | "rose" | "teal";
type ShelfId = "now" | "next" | "references" | "essential";
type Action = { to: string; label: string; icon: NomeIcone; adminOnly?: boolean; featured?: boolean };
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
  active?: boolean;
};
type MobilityTarget = {
  target_key: string;
  target_type?: string;
  appointment_id?: number | null;
  routine_id?: number | null;
  commitment_id?: string | null;
  starts_at?: string;
  ends_at?: string | null;
  service_name?: string | null;
  title?: string | null;
  source?: string;
  arrival_buffer_minutes?: number;
  location?: CalendarLocation | null;
};
type MobilityRoute = RotaDeslocamento;
type MobilityResult = {
  status?: string;
  provider?: string;
  updated_at?: string;
  routes?: MobilityRoute[];
  tips?: string[];
  destination?: MobilityTarget | null;
  origin_location?: CalendarLocation | null;
};
type MapConfiguration = { provider: string; configured: boolean; api_key: string | null };
type MobilityPreference = {
  enabled: boolean;
  traffic_configured?: boolean;
  day_start_origin_mode: "current_location" | "saved_location";
  day_start_location_id: number | null;
  day_start_location?: CalendarLocation | null;
  day_end_destination_location_id: number | null;
  day_end_destination_location?: CalendarLocation | null;
};
type MobilityDayContext = {
  stage: "before_first" | "active_day" | "at_last" | "no_commitments";
  first_target: MobilityTarget | null;
  last_target: MobilityTarget | null;
  start_location: CalendarLocation | null;
  end_location: CalendarLocation | null;
};
type ShelfDefinition = {
  id: ShelfId;
  capacity: number;
  defaultActionIds: string[];
};
type ShelfProfile = Partial<Record<ShelfId, string[]>>;

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
    id: "descobrir", label: "Descobrir", icon: "descobrir", tone: "cyan",
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
    id: "evidencias", label: "Evidências", icon: "validar-evidencia", tone: "blue",
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
    id: "aprender", label: "Aprender", icon: "aprender", tone: "violet",
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
    id: "ensinar", label: "Ensinar", icon: "ensinar", tone: "rose",
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
    id: "produzir", label: "Produzir", icon: "produzir", tone: "teal",
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
    ["/heart-team", "Heart Team Virtual", "round"],
    ["/doencas", "Guia de Doenças", "doencas"], ["/medicamentos", "Medicamentos", "medicamento"],
    ["/exames", "Exames", "clinica"], ["/calculadoras", "Calculadoras", "calculadora"],
    ["/emergencia", "Emergências", "emergencia"], ["/cardiologia-intensiva", "Cardiologia Intensiva & UCO", "clinica"],
    ["/checklists", "Checklists", "check"], ["/triagem-sintomas", "Triagem de sintomas", "triagem"],
    ["/interacoes", "Interações medicamentosas", "medicamento"], ["/condicoes", "Condições especiais", "check"],
    ["/fluxogramas", "Fluxogramas clínicos", "seta"], ["/avaliacao-preoperatoria", "Avaliação pré-operatória", "clinica"],
  ].map(([to, label, icon]) => ({ to, label, icon: icon as NomeIcone, featured: ["/heart-team", "/whatsapp-assistant", "/intelligence"].includes(to) })) },
  { title: "Assistência", actions: [
    ["/whatsapp-assistant", "Assistente WhatsApp", "comunicacao"],
    ["/exames-ia", "IA para Exames", "ecg"], ["/prontuario", "Prontuário", "pacientes"],
    ["/round", "Round hospitalar", "round"], ["/receituario", "Prescrição", "prescricao"],
    ["/documentos", "Documentos & Solicitações", "documento"], ["/agenda", "Agenda", "agenda"],
    ["/corvia-mail", "CorVIA Mail", "mail"], ["/caixa-de-email", "Caixa de e-mail unificada", "mail"],
    ["/assistente", "Apoio CorVIA", "assistente"], ["/telediagnostico", "Telediagnóstico & Consultoria", "evidencia"],
    ["/material-paciente", "Material para paciente", "documento"],
  ].map(([to, label, icon]) => ({ to, label, icon: icon as NomeIcone, featured: ["/heart-team", "/whatsapp-assistant", "/intelligence"].includes(to) })) },
  { title: "Ciência & Ensino", actions: [
    ["/intelligence", "CorVIA Intelligence", "sincronizar"],
    ["/evidencias", "Estudos & Evidências", "evidencia"], ["/estudos", "Estudos clínicos", "evidencia"],
    ["/documentos-cientificos-ia", "Documentos científicos IA", "assistente"], ["/trilhas/timeline", "Timeline do conhecimento", "seta"],
    ["/trilhas", "Trilhas", "seta"], ["/casos-clinicos", "Casos clínicos", "doencas"],
    ["/diretrizes", "Diretrizes & Guidelines", "conhecimento"], ["/biblioteca", "Biblioteca científica", "conhecimento"],
    ["/galeria", "Atlas & Galeria", "galeria"], ["/apresentacao", "Modo apresentação", "documento"],
    ["/exportar", "Exportar conteúdo", "documento"],
  ].map(([to, label, icon]) => ({ to, label, icon: icon as NomeIcone, featured: ["/heart-team", "/whatsapp-assistant", "/intelligence"].includes(to) })) },
  { title: "Produtividade & Rede", actions: [
    ["/indicadores", "Indicadores & Métricas", "indicadores"], ["/favoritos", "Notas & Favoritos", "favorito"],
    ["/busca", "Busca avançada", "busca"], ["/busca?modo=tudo-com-tudo", "Tudo com Tudo", "sincronizar"],
    ["/usuarios-online", "Rede profissional", "pacientes"], ["/sincronizacao", "Contas conectadas", "sincronizar"],
  ].map(([to, label, icon]) => ({ to, label, icon: icon as NomeIcone, featured: ["/heart-team", "/whatsapp-assistant", "/intelligence"].includes(to) })) },
  { title: "Conta & Administração", actions: [
    { to: "/minha-conta", label: "Minha Conta", icon: "conta" },
    { to: "/privacidade", label: "Segurança & Privacidade", icon: "check" },
    { to: "/termos", label: "Termos de uso", icon: "documento" },
    { to: "/tour", label: "Suporte & Ajuda", icon: "curso" },
    { to: "/verificacao-identidade", label: "Verificação de identidade", icon: "check" },
    { to: "/excluir-conta", label: "Excluir conta e dados", icon: "conta" },
    { to: "/admin", label: "Painel administrativo", icon: "gestao", adminOnly: true },
    { to: "/admin/usuarios", label: "Usuários & Permissões", icon: "pacientes", adminOnly: true },
    { to: "/admin/mudancas-clinicas", label: "Mudanças de Conduta Baseadas em Novas Evidências para Aprovação", icon: "evidencia", adminOnly: true },
    { to: "/fila-telediagnostico", label: "Fila de telediagnóstico", icon: "evidencia", adminOnly: true },
    { to: "/receitas-para-assinatura", label: "Receitas para assinatura", icon: "prescricao", adminOnly: true },
  ] },
  ...((heartTeamEnabled() || whatsappAssistantEnabled()) ? [{ title: "Operações de IA", actions: [
    { to: "/admin/operacoes-ia", label: "Operações e custos de IA", icon: "indicadores" as NomeIcone, adminOnly: true },
  ] }] : []),
];

const ESSENTIAL_DEFAULTS: Record<ClinicalSpaceId, string[]> = {
  consultorio: ["/agenda", "/receituario", "/prontuario", "/documentos", "/exames", "/calculadoras"],
  hospital: ["/exames", "/documentos", "/checklists", "/calculadoras"],
  ensino: ["/trilhas", "/casos-clinicos", "/apresentacao", "/galeria", "/diretrizes", "/biblioteca"],
  pesquisa: ["/estudos", "/evidencias", "/documentos-cientificos-ia", "/biblioteca", "/diretrizes", "/exportar"],
  gestao: ["/indicadores", "/agenda", "/usuarios-online", "/sincronizacao", "/corvia-mail", "/minha-conta"],
};

const SHELF_CAPACITIES: Record<ShelfId, number> = { now: 4, next: 4, references: 4, essential: 4 };
const ATELIER_DEFAULTS: Record<ClinicalSpaceId, string[]> = {
  consultorio: ["/agenda", "/prontuario", "/receituario", "/exames-ia", "/documentos", "/exames", "/medicamentos", "/calculadoras", "/doencas", "/interacoes", "/avaliacao-preoperatoria", "/diretrizes"],
  hospital: ["/round", "/receituario", "/exames-ia", "/emergencia", "/cardiologia-intensiva", "/checklists", "/documentos", "/calculadoras", "/exames", "/medicamentos", "/interacoes", "/diretrizes"],
  ensino: ["/trilhas", "/casos-clinicos", "/apresentacao", "/galeria", "/material-paciente", "/biblioteca", "/doencas", "/trilhas/timeline", "/evidencias", "/diretrizes", "/favoritos", "/exportar"],
  pesquisa: ["/busca?modo=tudo-com-tudo", "/biblioteca", "/evidencias", "/estudos", "/diretrizes", "/documentos-cientificos-ia", "/favoritos", "/exportar", "/casos-clinicos", "/galeria", "/trilhas/timeline", "/intelligence"],
  gestao: ["/indicadores", "/agenda", "/corvia-mail", "/usuarios-online", "/sincronizacao", "/minha-conta", "/telediagnostico", "/documentos", "/favoritos", "/privacidade", "/termos", "/assistente"],
};
const ATELIER_SCIENCE: Record<ClinicalSpaceId, string[]> = {
  consultorio: ["/doencas", "/diretrizes", "/evidencias", "/biblioteca", "/busca?modo=tudo-com-tudo", "/estudos", "/casos-clinicos", "/favoritos"],
  hospital: ["/cardiologia-intensiva", "/diretrizes", "/evidencias", "/estudos", "/biblioteca", "/casos-clinicos", "/checklists", "/busca?modo=tudo-com-tudo"],
  ensino: ["/trilhas", "/casos-clinicos", "/galeria", "/apresentacao", "/material-paciente", "/biblioteca", "/trilhas/timeline", "/favoritos"],
  pesquisa: ["/busca?modo=tudo-com-tudo", "/biblioteca", "/evidencias", "/estudos", "/diretrizes", "/documentos-cientificos-ia", "/favoritos", "/exportar"],
  gestao: ["/indicadores", "/estudos", "/evidencias", "/diretrizes", "/biblioteca", "/documentos-cientificos-ia", "/exportar", "/favoritos"],
};

function normalizeActionSegment(value: string) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("pt-BR")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

function homeActionId(action: Action) {
  return `${encodeURIComponent(action.to)}::${normalizeActionSegment(action.label)}`;
}

const REGISTRY_ACTIONS: Action[] = (Object.keys(CLINICAL_SPACES) as FunctionalSpace[]).flatMap((space) => catalogRoutesFor(space, true).map((route) => ({ to: route.path, label: route.shortName || route.name, icon: route.icon, adminOnly: route.gate === "admin" || route.gate === "admin-ai", featured: route.featured })));
const HOME_ACTIONS = [...CATALOG.flatMap((section) => section.actions), ...REGISTRY_ACTIONS, ...SPACES.flatMap((space) => [
  ...space.now,
  ...space.next,
  ...space.references,
]), ...SCIENTIFIC_SPACES.flatMap((space) => [
  ...space.now,
  ...space.next,
  ...space.references,
])].reduce<Action[]>((actions, action) => {
  if (!actions.some((candidate) => homeActionId(candidate) === homeActionId(action))) actions.push(action);
  return actions;
}, []);

const HOME_ACTIONS_BY_ID = new Map(HOME_ACTIONS.map((action) => [homeActionId(action), action]));

function actionForLegacyPath(path: string) {
  return CATALOG.flatMap((section) => section.actions).find((action) => action.to === path)
    || HOME_ACTIONS.find((action) => action.to === path);
}

function shelfProfileKey(mode: Mode, spaceId: SpaceId) {
  return `${mode}:${spaceId}`;
}

function shelfLabel(_mode: Mode, shelfId: ShelfId) {
  return `Prateleira ${shelfId === "now" ? 1 : shelfId === "references" ? 3 : 2}`;
}

function shelfDefinitions(mode: Mode, space: Space): ShelfDefinition[] {
  const id = space.id as ClinicalSpaceId;
  const paths = mode === "scientific" ? ATELIER_SCIENCE[id] : ATELIER_DEFAULTS[id];
  const actions = (paths || ATELIER_DEFAULTS.consultorio).map(actionForLegacyPath).filter((action): action is Action => Boolean(action));
  const ids: ShelfId[] = mode === "complete" ? ["now", "next", "references"] : ["now", mode === "essential" ? "essential" : "next"];
  return ids.map((shelf, index) => ({ id: shelf, capacity: 4, defaultActionIds: actions.slice(index * 4, index * 4 + 4).map(homeActionId) }));
}

function resolveShelfActionIds(
  selectedIds: string[] | undefined,
  definition: ShelfDefinition,
  candidates: Action[],
) {
  const allowedIds = new Set(candidates.map(homeActionId));
  const result: string[] = [];
  // Ausência de preferência usa exatamente o desenho aprovado da prateleira.
  // Uma lista salva (inclusive vazia) é a escolha explícita do usuário: a
  // capacidade é um teto, nunca um motivo para reinserir itens removidos ou
  // completar a prateleira com funções arbitrárias do catálogo.
  const requestedIds = selectedIds === undefined ? definition.defaultActionIds : selectedIds;
  for (const actionId of requestedIds) {
    if (!allowedIds.has(actionId) || result.includes(actionId)) continue;
    result.push(actionId);
    if (result.length === definition.capacity) break;
  }
  return result;
}

const SPACE_TONES: Record<ClinicalSpaceId, Tone> = {
  consultorio: "cyan", hospital: "blue", ensino: "violet", pesquisa: "rose", gestao: "teal",
};

function Brand() {
  return <span className="spaces-brand atelier-brand"><img src="/atelier/corvia-logo-atelier.svg" alt="CorVIA Cardiology Spaces" /></span>;
}

function UserIdentity({ usuario, chevron = false }: { usuario: Usuario | null; chevron?: boolean }) {
  const [photoFailed, setPhotoFailed] = useState(false);
  const displayName = nomeComTratamento(usuario, true);
  const initials = (usuario?.full_name || "Assinante")
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();

  useEffect(() => setPhotoFailed(false), [usuario?.photo_url]);

  return (
    <>
      <span className="spaces-user__avatar" aria-hidden="true">
        {usuario?.photo_url && !photoFailed
          ? <img src={assetUrl(usuario.photo_url)} alt="" onError={() => setPhotoFailed(true)} />
          : <span>{initials}</span>}
      </span>
      <span className="spaces-user__name">{displayName}</span>
      {chevron ? <Icone nome="chevron" /> : null}
    </>
  );
}

function CommutePreview({ target, route, minutes, busy, onOpen, origin, configuration, provider, updatedAt, error }: {
  target: MobilityTarget | null; route?: MobilityRoute; minutes: number | null; busy: boolean; onOpen: () => void;
  origin: { latitude: number; longitude: number } | null; configuration: MapConfiguration | null;
  provider?: string; updatedAt?: string; error: string | null;
}) {
  const destination = target?.location?.name || target?.service_name || "Próximo destino";
  const hasRoute = geometryAvailable(route);
  const hasEstimate = Boolean(route && minutes != null);
  const schedule = mobilitySchedule(target, route?.duration_seconds);
  const location = target?.location;
  const previewRef = useRef<HTMLElement>(null);
  const [mapVisible, setMapVisible] = useState(false);
  useEffect(() => {
    if (!hasRoute || mapVisible || !previewRef.current) return;
    if (typeof IntersectionObserver === "undefined") { setMapVisible(true); return; }
    const observer = new IntersectionObserver((entries) => {
      if (entries.some((entry) => entry.isIntersecting)) { setMapVisible(true); observer.disconnect(); }
    });
    observer.observe(previewRef.current);
    return () => observer.disconnect();
  }, [hasRoute, mapVisible]);
  return <article ref={previewRef} className="spaces-stellar-route atelier-commute" data-state={busy ? "loading" : hasRoute ? "ready" : "pending"} aria-busy={busy}>
    <button type="button" className="atelier-commute__open" onClick={onOpen} disabled={busy} aria-label={`Abrir deslocamento para ${destination}`}>
      <span className="spaces-stellar-route__heading"><span><Icone nome="rota" /></span><span><strong>Seu próximo percurso</strong><small>{destination}</small></span><Icone nome="seta" /></span>
    </button>
    {schedule && <div className="spaces-stellar-route__schedule"><span>{schedule.returning ? "Retorno" : "Compromisso"} · {scheduleDateTime(schedule.start)}</span>{schedule.departure && <span>Saída planejada · {scheduleDateTime(schedule.departure)}</span>}</div>}
    {hasRoute && location && coordinateValid(location.latitude, location.longitude) ? <div className="atelier-commute__map">
      {mapVisible && <MapaDeslocamento compact rotas={route ? [route] : []} origem={origin} destino={{ name: destination, latitude: location.latitude!, longitude: location.longitude! }} provider={provider || configuration?.provider} googleMapsApiKey={configuration?.api_key} updatedAt={updatedAt} />}
    </div> : <div className="atelier-mobility-empty" role="status"><Icone nome="pin" /><strong>{busy ? "Preparando seu percurso…" : hasEstimate ? "Estimativa disponível" : target ? "Seu destino está preparado" : "Seu dia, em movimento"}</strong><span>{error || (hasEstimate ? "O provedor ainda não entregou o desenho do caminho." : target ? "Calcule para visualizar o caminho e comparar o trânsito." : "Vincule um local à agenda para planejar seu deslocamento.")}</span></div>}
    {hasEstimate && <div className="spaces-stellar-route__metrics"><strong>{minutes} min</strong><span>{distanceLabel(route?.distance_meters)}</span><span>{trafficShortLabel(route?.congestion)}</span></div>}
    {error && hasRoute && <p className="atelier-commute__notice" role="status">{error}</p>}
    <button type="button" className="atelier-commute__action" onClick={onOpen} disabled={busy}>{busy ? "Calculando…" : hasRoute ? "Explorar percurso" : hasEstimate ? "Revisar deslocamento" : "Calcular meu percurso"}<Icone nome="seta" /></button>
  </article>;
}

function ActionLink({ action, compact = false }: { action: Action; compact?: boolean }) {
  return <Link className={`spaces-action${compact ? " spaces-action--compact" : ""}${action.featured ? " spaces-action--featured" : ""}`} data-feature={action.to === "/exames-ia" ? "exam-ai" : undefined} to={action.to}><Icone nome={action.icon} /><span>{action.label}{action.featured && <small className="spaces-action__highlight">Destaque</small>}</span></Link>;
}

function useDialogFocus(open: boolean) {
  const dialogRef = useRef<HTMLElement>(null);
  const returnFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!open) return;
    returnFocusRef.current = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const dialog = dialogRef.current;
    const focusable = () => Array.from(dialog?.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
    ) ?? []).filter((element) => element.offsetParent !== null);
    requestAnimationFrame(() => focusable()[0]?.focus());
    const trap = (event: KeyboardEvent) => {
      if (event.key !== "Tab") return;
      const items = focusable();
      if (!items.length) return;
      const first = items[0];
      const last = items[items.length - 1];
      if (!dialog?.contains(document.activeElement)) {
        event.preventDefault();
        (event.shiftKey ? last : first).focus();
      } else if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };
    document.addEventListener("keydown", trap);
    return () => {
      document.removeEventListener("keydown", trap);
      requestAnimationFrame(() => returnFocusRef.current?.focus());
    };
  }, [open]);

  return dialogRef;
}

function sameLocalDay(value: string, reference = new Date()) {
  const date = new Date(value);
  return !Number.isNaN(date.getTime()) && date.getFullYear() === reference.getFullYear() && date.getMonth() === reference.getMonth() && date.getDate() === reference.getDate();
}

function localDateKey(date = new Date()) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function time(value?: string | null) {
  if (!value) return "";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "" : date.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
}

function routineToAgendaItem(routine: WorkRoutine): AgendaItem | null {
  if (routine.active === false) return null;
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

function trafficLabel(value?: string) {
  if (!value) return "trânsito a calcular";
  if (/severe|heavy|high|intens|congestion|traffic[_ -]?jam/i.test(value)) return "trânsito intenso";
  if (/moderate|moderad|medium|m[eé]di|regular|slow/i.test(value)) return "trânsito moderado";
  if (/light|low|livre|flu[ií]d|leve|normal/i.test(value)) return "trânsito fluido";
  return "trânsito não classificado";
}

function trafficShortLabel(value?: string) {
  if (!value) return "Trânsito a calcular";
  if (/severe|heavy|high|intens|congestion|traffic[_ -]?jam/i.test(value)) return "Intenso";
  if (/moderate|moderad|medium|m[eé]di|regular|slow/i.test(value)) return "Moderado";
  if (/light|low|livre|flu[ií]d|leve|normal/i.test(value)) return "Fluido";
  return "Não classificado";
}

function trafficLevel(value?: string) {
  if (/severe|heavy|high|intens|congestion|traffic[_ -]?jam/i.test(value || "")) return "heavy";
  if (/moderate|moderad|medium|m[eé]di|regular|slow/i.test(value || "")) return "moderate";
  if (/light|low|livre|flu[ií]d|leve|normal/i.test(value || "")) return "light";
  return value ? "unknown" : "pending";
}

function currentPosition(): Promise<GeolocationPosition> {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("Geolocalização não disponível neste dispositivo."));
      return;
    }
    navigator.geolocation.getCurrentPosition(resolve, reject, { enableHighAccuracy: false, timeout: 8000, maximumAge: 120000 });
  });
}

function geolocationErrorMessage(error: unknown) {
  const code = typeof error === "object" && error !== null && "code" in error
    ? Number((error as { code?: number }).code)
    : 0;
  if (code === 1) return "A localização foi negada no navegador. Autorize-a para traçar a rota a partir da sua posição atual.";
  if (code === 2) return "O dispositivo não conseguiu determinar sua localização atual.";
  if (code === 3) return "A localização demorou para responder. Tente novamente ou abra o destino no mapa.";
  return error instanceof Error ? error.message : "Não foi possível obter sua localização atual.";
}

function sanitizeMobilityResult(result: MobilityResult, target: MobilityTarget) {
  const destination = withoutReservedSmokeTestRecord(result.destination);
  if (!destination || destination.target_key !== target.target_key) return null;
  return { ...result, destination, routes: Array.isArray(result.routes) ? result.routes : [] };
}


export default function CardiologySpacesHome() {
  const { usuario } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [mode, setMode] = useState<Mode>(() => atelierContextFromSearch(searchParams, readAtelierContext(usuario?.id)).mode);
  const [selectedSpace, setSelectedSpace] = useState<SpaceId>(() => atelierContextFromSearch(searchParams, readAtelierContext(usuario?.id)).space);
  const interior = SPACES.some((space) => space.id === searchParams.get("espaco"));
  const [storageNotice, setStorageNotice] = useState("");
  const [personalizerQuery, setPersonalizerQuery] = useState("");
  useEffect(() => {
    const selected = SPACES.find((space) => space.id === searchParams.get("espaco"));
    const context = atelierContextFromSearch(searchParams, readAtelierContext(usuario?.id));
    if (selected) setSelectedSpace(context.space);
    const requestedMode = searchParams.get("modo");
    const validMode = requestedMode === "complete" || requestedMode === "essential" || requestedMode === "scientific";
    if (validMode) setMode(context.mode);
    if (selected || validMode) writeAtelierContext(usuario?.id, context);
  }, [searchParams, usuario?.id]);
  const [previewSpace, setPreviewSpace] = useState<SpaceId | null>(null);
  const [catalogOpen, setCatalogOpen] = useState(false);
  const [personalizerOpen, setPersonalizerOpen] = useState(false);
  const [personalizerShelf, setPersonalizerShelf] = useState<ShelfId>("now");
  const [shelfPreferences, setShelfPreferences] = useState<ShelfPreferences>(emptyShelfPreferences);
  const [shelfDraft, setShelfDraft] = useState<ShelfProfile>({});
  const [shelfReserve, setShelfReserve] = useState<string[]>([]);
  const [previousOrganization, setPreviousOrganization] = useState("");
  const [importNotice, setImportNotice] = useState("");
  const [query, setQuery] = useState("");
  const [globalQuery, setGlobalQuery] = useState("");
  const [dayItems, setDayItems] = useState<AgendaItem[]>([]);
  const [dayState, setDayState] = useState<"loading" | "ready" | "error">("loading");
  const [mobilityTarget, setMobilityTarget] = useState<MobilityTarget | null>(null);
  const [mobilityResult, setMobilityResult] = useState<MobilityResult | null>(null);
  const [mobilityPreference, setMobilityPreference] = useState<MobilityPreference | null>(null);
  const [mobilityDayContext, setMobilityDayContext] = useState<MobilityDayContext | null>(null);
  const [mapConfiguration, setMapConfiguration] = useState<MapConfiguration | null>(null);
  const [travelOrigin, setTravelOrigin] = useState<{ latitude: number; longitude: number } | null>(null);
  const [travelOpen, setTravelOpen] = useState(false);
  const [travelBusy, setTravelBusy] = useState(false);
  const [travelError, setTravelError] = useState<string | null>(null);
  const travelRequestGeneration = useRef(0);
  const travelResultIdentity = useRef<string | null>(null);
  const catalogRef = useDialogFocus(catalogOpen);
  const personalizerRef = useDialogFocus(personalizerOpen);
  const travelRef = useDialogFocus(travelOpen);
  const globalSearchRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    document.body.classList.add("cardiology-spaces-active");
    return () => document.body.classList.remove("cardiology-spaces-active");
  }, []);

  useEffect(() => {
    if (!usuario?.id) {
      setShelfPreferences(emptyShelfPreferences());
      return;
    }
    const preferenceKey = `${SHELF_PREFERENCES_PREFIX}:${usuario.id}`;
    const loaded = shelfPreferenceStore.read(usuario.id);
    const legacyEssentials: Record<string, string[]> = {};
    for (const space of SPACES) {
      try {
        const raw = localStorage.getItem(`corvia:cardiology-spaces:essentials:${usuario.id}:${space.id}`);
        const paths: unknown = raw === null ? null : JSON.parse(raw);
        if (Array.isArray(paths)) legacyEssentials[space.id] = paths.filter((path): path is string => typeof path === "string");
      } catch { /* A fonte antiga permanece intacta; nunca apagar nem truncar. */ }
    }
    const preferences = migrateShelfPreferences(loaded, legacyEssentials, (path) => {
      const action = actionForLegacyPath(path);
      return action ? homeActionId(action) : `${encodeURIComponent(path)}::funcao-anterior`;
    });
    if (JSON.stringify(preferences) !== JSON.stringify(loaded) && !shelfPreferenceStore.write(usuario.id, preferences)) setStorageNotice("Sua organização e o histórico serão mantidos nesta sessão; o navegador não permitiu gravá-los.");
    setShelfPreferences(preferences);
    const syncPreferences = (event: StorageEvent) => {
      if (event.key === preferenceKey) setShelfPreferences(shelfPreferenceStore.sync(usuario.id, event.newValue));
    };
    window.addEventListener("storage", syncPreferences);
    return () => window.removeEventListener("storage", syncPreferences);
  }, [usuario?.id]);

  useEffect(() => {
    const focusEverything = (event: KeyboardEvent) => {
      if (!(event.metaKey || event.ctrlKey) || event.key.toLocaleLowerCase("pt-BR") !== "k") return;
      event.preventDefault();
      const modal = Array.from(document.querySelectorAll<HTMLElement>('[aria-modal="true"]')).reverse().find((element) => element.offsetParent !== null && getComputedStyle(element).visibility !== "hidden");
      if (modal) {
        (modal.querySelector<HTMLElement>('input:not([disabled]), button:not([disabled])'))?.focus();
        return;
      }
      globalSearchRef.current?.focus();
    };
    document.addEventListener("keydown", focusEverything);
    return () => document.removeEventListener("keydown", focusEverything);
  }, []);

  useEffect(() => {
    let active = true;
    setDayState("loading");
    const today = localDateKey();
    Promise.allSettled([
      api.get<AgendaItem[]>("/agenda/appointments"),
      api.get<AgendaItem[]>(`/agenda/commitments?start=${today}&end=${today}`),
      api.get<WorkRoutine[]>("/agenda/work-routines"),
    ]).then((results) => {
      if (!active) return;
      const [appointmentsResult, commitmentsResult, routinesResult] = results;
      const appointments = withoutReservedSmokeTestRecords<AgendaItem>(appointmentsResult.status === "fulfilled" && Array.isArray(appointmentsResult.value) ? appointmentsResult.value : []);
      const commitments = withoutReservedSmokeTestRecords<AgendaItem>(commitmentsResult.status === "fulfilled" && Array.isArray(commitmentsResult.value) ? commitmentsResult.value : []);
      const routines = withoutReservedSmokeTestRecords<WorkRoutine>(routinesResult.status === "fulfilled" && Array.isArray(routinesResult.value) ? routinesResult.value : []);
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
      .then((target) => { if (active) setMobilityTarget(withoutReservedSmokeTestRecord(target)); })
      .catch(() => { if (active) setMobilityTarget(null); });
    return () => { active = false; };
  }, [mode, usuario?.investidor]);

  useEffect(() => {
    if (!mode || mode === "scientific" || usuario?.investidor) {
      setMapConfiguration(null);
      setMobilityPreference(null);
      setMobilityDayContext(null);
      return;
    }
    let active = true;
    Promise.allSettled([
      api.get<MapConfiguration>("/agenda/mobility/map-config"),
      api.get<MobilityPreference>("/agenda/mobility/preferences"),
      api.get<MobilityDayContext>("/agenda/mobility/day-context"),
    ]).then(([mapResult, preferenceResult, contextResult]) => {
      if (!active) return;
      setMapConfiguration(mapResult.status === "fulfilled" ? mapResult.value : null);
      setMobilityPreference(preferenceResult.status === "fulfilled" ? preferenceResult.value : null);
      setMobilityDayContext(contextResult.status === "fulfilled" ? {
        ...contextResult.value,
        first_target: withoutReservedSmokeTestRecord(contextResult.value.first_target),
        last_target: withoutReservedSmokeTestRecord(contextResult.value.last_target),
      } : null);
    });
    return () => { active = false; };
  }, [mode, usuario?.investidor]);

  useEffect(() => {
    if (!catalogOpen && !personalizerOpen && !travelOpen) return;
    const close = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      setCatalogOpen(false);
      setPersonalizerOpen(false);
      setShelfDraft({});
      setShelfReserve([]);
      setImportNotice("");
      closeTravel();
    };
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, [catalogOpen, personalizerOpen, travelOpen]);

  const activeMode: Mode = mode || "complete";
  const availableSpaces = SPACES;
  const activeSpace = availableSpaces.find((space) => space.id === selectedSpace) || availableSpaces[0];
  const permittedPaths = useMemo(() => new Set((Object.keys(CLINICAL_SPACES) as FunctionalSpace[]).flatMap((space) => catalogRoutesFor(space, usuario?.role === "admin").map((route) => route.path))), [usuario?.role]);
  const candidateActions = useMemo(() => HOME_ACTIONS.filter((action) => (!action.adminOnly || usuario?.role === "admin") && permittedPaths.has(action.to.split("?")[0])), [usuario?.role, permittedPaths]);
  const visibleCatalog = useMemo(() => (Object.keys(CLINICAL_SPACES) as FunctionalSpace[]).map((space) => ({
    title: CLINICAL_SPACES[space].label,
    actions: catalogRoutesFor(space, usuario?.role === "admin").map((route) => ({ to: route.path, label: route.name, icon: route.icon, featured: route.featured })).filter((action) => normalizeActionSegment(action.label).includes(normalizeActionSegment(query))),
  })).filter((section) => section.actions.length), [query, usuario?.role]);
  const activeProfileKey = shelfProfileKey(activeMode, activeSpace.id);
  const activeShelfDefinitions = useMemo(
    () => shelfDefinitions(activeMode, activeSpace),
    [activeMode, activeSpace],
  );
  const resolvedShelfActions = useMemo(() => {
    const profile = shelfPreferences.profiles[activeProfileKey] || {};
    return activeShelfDefinitions.reduce<Partial<Record<ShelfId, Action[]>>>((resolved, definition) => {
      const actionIds = resolveShelfActionIds(profile[definition.id], definition, candidateActions);
      resolved[definition.id] = actionIds
        .map((actionId) => HOME_ACTIONS_BY_ID.get(actionId))
        .filter((action): action is Action => Boolean(action));
      return resolved;
    }, {});
  }, [activeProfileKey, activeShelfDefinitions, candidateActions, shelfPreferences]);
  const activePersonalizerDefinition = activeShelfDefinitions.find((definition) => definition.id === personalizerShelf)
    || activeShelfDefinitions[0];
  const activeDraftIds = shelfDraft[activePersonalizerDefinition.id] || [];
  const draftSelectedIds = new Set(shelfProfileItems(shelfDraft));
  const recoverableIds = [...new Set(shelfReserve)].filter((id) => !draftSelectedIds.has(id));
  const allowedPreferenceIds = useMemo(() => new Set(candidateActions.map(homeActionId)), [candidateActions]);
  const chamamentoNaFrase = chamamentoComArtigo(usuario, { curto: true });
  const chamamentoNoInicio = chamamentoComArtigo(usuario, { curto: true, inicioDeFrase: true });
  const question = mode === "scientific" ? `Como ${chamamentoNaFrase} quer explorar o conhecimento agora?` : `Onde ${chamamentoNaFrase} vai trabalhar agora?`;
  const returnHomeTarget = useMemo<MobilityTarget | null>(() => {
    if (mobilityDayContext?.stage !== "at_last" || !mobilityDayContext.last_target || mobilityDayContext.end_location?.id == null) return null;
    const lastTarget = mobilityDayContext.last_target;
    const endLocation = mobilityDayContext.end_location;
    return {
      target_key: `return:${lastTarget.target_key}:${endLocation.id}`,
      target_type: "day_return",
      appointment_id: null,
      routine_id: null,
      commitment_id: null,
      starts_at: lastTarget.ends_at || lastTarget.starts_at,
      ends_at: null,
      service_name: "Retorno",
      title: `Retorno para ${endLocation.name || "casa"}`,
      source: "return",
      arrival_buffer_minutes: 0,
      location: endLocation,
    };
  }, [mobilityDayContext]);
  const plannedMobilityTarget = mobilityDayContext?.stage === "at_last"
    ? returnHomeTarget
    : mobilityDayContext?.stage === "no_commitments"
      ? null
      : mobilityTarget;
  const returnHomeActive = plannedMobilityTarget?.source === "return";
  const resultMatchesTarget = Boolean(
    mobilityResult?.destination?.target_key
    && plannedMobilityTarget?.target_key
    && mobilityResult.destination.target_key === plannedMobilityTarget.target_key,
  );
  // Provider destination data may omit the agenda's date/buffer. Keep the
  // schedule tied to the selected commitment even after a route is calculated.
  const travelTarget = resultMatchesTarget && plannedMobilityTarget ? {
    ...plannedMobilityTarget,
    ...mobilityResult?.destination,
    starts_at: plannedMobilityTarget.starts_at || mobilityResult?.destination?.starts_at,
    arrival_buffer_minutes: plannedMobilityTarget.arrival_buffer_minutes ?? mobilityResult?.destination?.arrival_buffer_minutes,
  } : plannedMobilityTarget;
  const bestRoute = resultMatchesTarget ? mobilityResult?.routes?.[0] : undefined;
  const travelSeconds = bestRoute?.duration_seconds;
  const travelMinutes = typeof travelSeconds === "number" && Number.isFinite(travelSeconds) && travelSeconds >= 0
    ? Math.max(1, Math.ceil(travelSeconds / 60)) : null;
  const travelDestination = travelTarget?.location?.latitude != null && travelTarget.location.longitude != null ? {
    latitude: travelTarget.location.latitude,
    longitude: travelTarget.location.longitude,
    name: travelTarget.location.name || travelTarget.service_name || "Próximo destino",
  } : null;
  const resultOrigin = resultMatchesTarget && mobilityResult?.origin_location?.latitude != null && mobilityResult.origin_location.longitude != null ? {
    latitude: mobilityResult.origin_location.latitude,
    longitude: mobilityResult.origin_location.longitude,
  } : null;
  const usesSavedOrigin = Boolean(
    mobilityPreference?.enabled
    && mobilityPreference.day_start_origin_mode === "saved_location"
    && mobilityPreference.day_start_location_id
    && mobilityDayContext?.stage === "before_first",
  );
  const savedOrigin = mobilityDayContext?.start_location || mobilityPreference?.day_start_location || null;
  const savedOriginCoordinates = usesSavedOrigin && savedOrigin?.latitude != null && savedOrigin.longitude != null ? {
    latitude: savedOrigin.latitude,
    longitude: savedOrigin.longitude,
  } : null;
  const returnHomeOrigin = returnHomeActive
    && mobilityDayContext?.last_target?.location?.latitude != null
    && mobilityDayContext.last_target.location.longitude != null ? {
      latitude: mobilityDayContext.last_target.location.latitude,
      longitude: mobilityDayContext.last_target.location.longitude,
    } : null;
  const travelMapOrigin = resultOrigin || returnHomeOrigin || travelOrigin || savedOriginCoordinates;
  const travelIdentityFor = (target: MobilityTarget | null) => JSON.stringify([
    usuario?.id, target?.target_key, target?.location?.latitude, target?.location?.longitude,
    mobilityPreference?.enabled, mobilityPreference?.day_start_origin_mode,
    mobilityPreference?.day_start_location_id, mobilityPreference?.day_end_destination_location_id,
    mobilityDayContext?.stage, mobilityDayContext?.last_target?.target_key,
    savedOriginCoordinates, returnHomeOrigin,
  ]);
  const travelIdentity = travelIdentityFor(plannedMobilityTarget);
  const currentTravelIdentity = useRef(travelIdentity);
  currentTravelIdentity.current = travelIdentity;

  function closeTravel() {
    travelRequestGeneration.current += 1;
    setTravelBusy(false);
    setTravelOpen(false);
  }

  useEffect(() => () => { travelRequestGeneration.current += 1; }, []);

  useEffect(() => {
    travelRequestGeneration.current += 1;
    setTravelBusy(false);
    if (travelResultIdentity.current !== travelIdentity) {
      setMobilityResult(null);
      setTravelOrigin(null);
      setTravelError(null);
    }
  }, [travelIdentity]);

  useEffect(() => {
    if (!usesSavedOrigin || !plannedMobilityTarget?.target_key || !mobilityPreference?.day_start_location_id || resultMatchesTarget) return;
    let active = true;
    const generation = ++travelRequestGeneration.current;
    const isCurrent = () => active && generation === travelRequestGeneration.current && currentTravelIdentity.current === travelIdentity;
    api.post<MobilityResult>("/agenda/mobility/commute-target-from-location", {
      origin_location_id: mobilityPreference.day_start_location_id,
      target_key: plannedMobilityTarget.target_key,
    }).then((result) => {
      if (!isCurrent()) return;
      const safeResult = sanitizeMobilityResult(result, plannedMobilityTarget);
      if (safeResult) {
        travelResultIdentity.current = travelIdentity;
        setMobilityResult(safeResult);
        setTravelError(mobilityRouteError(safeResult));
      } else setTravelError(mobilityRouteError(result) || "O destino retornado não corresponde ao compromisso exibido. A rota foi descartada.");
    }).catch((error) => { if (isCurrent()) setTravelError(geolocationErrorMessage(error)); });
    return () => { active = false; };
  }, [mobilityPreference?.day_start_location_id, plannedMobilityTarget, resultMatchesTarget, usesSavedOrigin, travelIdentity]);

  useEffect(() => {
    if (!returnHomeActive
      || !plannedMobilityTarget?.target_key
      || !mobilityDayContext?.last_target?.target_key
      || !mobilityPreference?.enabled
      || !mobilityPreference.day_end_destination_location_id
      || resultMatchesTarget) return;
    let active = true;
    const generation = ++travelRequestGeneration.current;
    const isCurrent = () => active && generation === travelRequestGeneration.current && currentTravelIdentity.current === travelIdentity;
    api.post<MobilityResult>("/agenda/mobility/commute-return", {
      origin_target_key: mobilityDayContext.last_target.target_key,
      destination_location_id: mobilityPreference.day_end_destination_location_id,
    }).then((result) => {
      if (!isCurrent()) return;
      const safeResult = sanitizeMobilityResult(result, plannedMobilityTarget);
      if (safeResult) {
        travelResultIdentity.current = travelIdentity;
        setMobilityResult(safeResult);
        setTravelError(mobilityRouteError(safeResult));
      } else setTravelError(mobilityRouteError(result) || "O destino retornado não corresponde ao compromisso exibido. A rota foi descartada.");
    }).catch((error) => { if (isCurrent()) setTravelError(geolocationErrorMessage(error)); });
    return () => { active = false; };
  }, [mobilityDayContext?.last_target?.target_key, mobilityPreference?.day_end_destination_location_id, mobilityPreference?.enabled, plannedMobilityTarget, resultMatchesTarget, returnHomeActive, travelIdentity]);

  const chooseMode = useCallback((nextMode: Mode) => {
    if (!writeAtelierContext(usuario?.id, { space: selectedSpace as FunctionalSpace, mode: nextMode })) setStorageNotice("Sua organização será mantida apenas nesta sessão.");
    setMode(nextMode);
    if (interior) setSearchParams({ espaco: selectedSpace, modo: nextMode }, { replace: true });
    setPreviewSpace(null);
  }, [interior, selectedSpace, setSearchParams, usuario?.id]);

  function resetMode() { setSearchParams({}); setPreviewSpace(null); }

  function searchEverything(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const term = globalQuery.trim();
    navigate(`/busca?modo=tudo-com-tudo${term ? `&q=${encodeURIComponent(term)}` : ""}`);
  }

  function openShelfPersonalizer(shelfId?: ShelfId) {
    const requestedShelf = shelfId && activeShelfDefinitions.some((definition) => definition.id === shelfId)
      ? shelfId
      : activeShelfDefinitions[0].id;
    const nextDraft = activeShelfDefinitions.reduce<ShelfProfile>((draft, definition) => {
      draft[definition.id] = (resolvedShelfActions[definition.id] || []).map(homeActionId);
      return draft;
    }, {});
    setShelfDraft(nextDraft);
    setShelfReserve(shelfReserveFor(shelfPreferences, activeProfileKey, nextDraft));
    setPreviousOrganization("");
    setImportNotice("");
    setPersonalizerQuery("");
    setPersonalizerShelf(requestedShelf);
    setPreviewSpace(null);
    setPersonalizerOpen(true);
  }

  function cancelShelfPersonalizer() {
    setPersonalizerOpen(false);
    setShelfDraft({});
    setShelfReserve([]);
    setImportNotice("");
  }

  function toggleShelfAction(actionId: string) {
    const definition = activePersonalizerDefinition;
    setShelfDraft((currentDraft) => {
      const current = currentDraft[definition.id] || [];
      const next = current.includes(actionId)
        ? current.filter((candidateId) => candidateId !== actionId)
        : current.length < definition.capacity
          ? [...current, actionId]
          : current;
      const cleaned = { ...currentDraft };
      if (next.includes(actionId)) {
        for (const shelf of activeShelfDefinitions) {
          if (shelf.id !== definition.id) cleaned[shelf.id] = (cleaned[shelf.id] || []).filter((id) => id !== actionId);
        }
      }
      return { ...cleaned, [definition.id]: next };
    });
  }

  function moveShelfAction(actionId: string, direction: -1 | 1) {
    const shelfId = activePersonalizerDefinition.id;
    setShelfDraft((currentDraft) => {
      const current = [...(currentDraft[shelfId] || [])];
      const currentIndex = current.indexOf(actionId);
      const targetIndex = currentIndex + direction;
      if (currentIndex < 0 || targetIndex < 0 || targetIndex >= current.length) return currentDraft;
      [current[currentIndex], current[targetIndex]] = [current[targetIndex], current[currentIndex]];
      return { ...currentDraft, [shelfId]: current };
    });
  }

  function transferShelfAction(actionId: string, target: ShelfId) {
    const destination = activeShelfDefinitions.find((definition) => definition.id === target);
    if (!destination) return;
    setShelfDraft((draft) => {
      if ((draft[target] || []).length >= destination.capacity) return draft;
      const next = { ...draft };
      for (const definition of activeShelfDefinitions) next[definition.id] = (next[definition.id] || []).filter((id) => id !== actionId);
      next[target] = [...(next[target] || []), actionId];
      return next;
    });
  }

  function reorderShelfDrop(actionId: string, before: string) {
    setShelfDraft((draft) => {
      const current = [...(draft[personalizerShelf] || [])];
      if (!current.includes(actionId) || !current.includes(before) || actionId === before) return draft;
      const next = current.filter((id) => id !== actionId);
      next.splice(next.indexOf(before), 0, actionId);
      return { ...draft, [personalizerShelf]: next };
    });
  }

  function restoreShelfDefaults() {
    const definition = activePersonalizerDefinition;
    setShelfReserve((reserve) => [...new Set([...reserve, ...(shelfDraft[definition.id] || [])])]);
    setImportNotice("Padrão aplicado apenas ao rascunho. As funções substituídas continuam na reserva; salve para confirmar ou cancele.");
    setShelfDraft((currentDraft) => ({
      ...currentDraft,
      [definition.id]: resolveShelfActionIds(undefined, definition, candidateActions),
    }));
  }

  function importPreviousOrganization() {
    const source = shelfPreferences.archives.find((archive) => archive.id === previousOrganization);
    if (!source) return;
    const preview = previewShelfImport(source.profile, activeShelfDefinitions, allowedPreferenceIds, shelfDraft, shelfReserve);
    setShelfDraft(preview.profile);
    setShelfReserve(preview.reserve);
    setImportNotice(`Prévia de ${shelfOrganizationLabel(source.profileKey)}. A origem foi preservada; ${preview.reserve.length} função(ões) ficam na reserva. Salve para aplicar ou cancele.`);
  }

  function saveShelfPreferences() {
    const nextPreferences = saveShelfProfile(shelfPreferences, activeProfileKey, shelfDraft, activeShelfDefinitions, allowedPreferenceIds, shelfReserve);
    setShelfPreferences(nextPreferences);
    if (usuario?.id) {
      const persisted = shelfPreferenceStore.write(usuario.id, nextPreferences);
      setStorageNotice(persisted ? "Personalização salva. As organizações anteriores e a reserva foram preservadas." : "Preferência e histórico mantidos nesta sessão. O armazenamento do navegador está indisponível.");
    }
    setPersonalizerOpen(false);
    setShelfDraft({});
    setShelfReserve([]);
    setImportNotice("");
  }

  async function startTravel() {
    const generation = ++travelRequestGeneration.current;
    const isCurrent = () => generation === travelRequestGeneration.current && currentTravelIdentity.current === travelIdentity;
    setTravelOpen(true);
    setTravelBusy(true);
    setTravelError(null);
    try {
      if (usuario?.investidor) {
        setTravelError("No Modo Investidor, o deslocamento é demonstrativo e não usa localização real.");
        return;
      }
      let target = plannedMobilityTarget;
      if (mobilityDayContext?.stage === "at_last" && !target) {
        setTravelError("Configure Casa ou outro destino final na Agenda para calcular o retorno após o último compromisso.");
        return;
      }
      if (mobilityDayContext?.stage === "no_commitments") {
        setTravelError("Não há compromissos presenciais hoje para calcular um deslocamento.");
        return;
      }
      if (!target) {
        const preparedTarget = await api.post<MobilityTarget | null>("/agenda/mobility/prepare-next-target", {});
        if (!isCurrent()) return;
        target = withoutReservedSmokeTestRecord(preparedTarget);
      }
      if (!target?.target_key) {
        setTravelError("Não há um próximo compromisso presencial com local cadastrado para traçar a rota.");
        return;
      }
      if (!mobilityPreference) {
        setTravelError("Não foi possível confirmar sua preferência de mobilidade. Abra a Agenda e revise a autorização antes de usar sua localização.");
        return;
      }
      if (!mobilityPreference.enabled) {
        setTravelError("Ative o deslocamento inteligente na Agenda para calcular rotas e trânsito.");
        return;
      }
      let result: MobilityResult;
      if (returnHomeActive && mobilityDayContext?.last_target?.target_key && mobilityPreference?.day_end_destination_location_id) {
        setTravelOrigin(null);
        result = await api.post<MobilityResult>("/agenda/mobility/commute-return", {
          origin_target_key: mobilityDayContext.last_target.target_key,
          destination_location_id: mobilityPreference.day_end_destination_location_id,
        });
      } else if (usesSavedOrigin && mobilityPreference?.day_start_location_id) {
        setTravelOrigin(null);
        result = await api.post<MobilityResult>("/agenda/mobility/commute-target-from-location", {
          origin_location_id: mobilityPreference.day_start_location_id,
          target_key: target.target_key,
        });
      } else {
        const position = await currentPosition();
        if (!isCurrent()) return;
        const liveOrigin = { latitude: position.coords.latitude, longitude: position.coords.longitude };
        setTravelOrigin(liveOrigin);
        result = await api.post<MobilityResult>("/agenda/mobility/commute-target", {
          ...liveOrigin,
          target_key: target.target_key,
        });
      }
      if (!isCurrent()) return;
      const safeResult = sanitizeMobilityResult(result, target);
      if (!safeResult) {
        setTravelError(mobilityRouteError(result) || "O destino retornado não corresponde ao compromisso exibido. A rota anterior foi preservada.");
        return;
      }
      travelResultIdentity.current = travelIdentityFor(target);
      if (!plannedMobilityTarget) setMobilityTarget(target);
      setMobilityResult(safeResult);
      if (safeResult.origin_location?.latitude != null && safeResult.origin_location.longitude != null && !usesSavedOrigin) {
        setTravelOrigin({ latitude: safeResult.origin_location.latitude, longitude: safeResult.origin_location.longitude });
      }
      setTravelError(mobilityRouteError(safeResult));
    } catch (error) {
      if (isCurrent()) setTravelError(geolocationErrorMessage(error));
    } finally {
      if (isCurrent()) setTravelBusy(false);
    }
  }

  function openExternalMap() {
    const location = travelTarget?.location;
    if (location?.latitude == null || location?.longitude == null) {
      setTravelError("Este destino ainda não possui coordenadas para abrir a navegação.");
      return;
    }
    const destination = encodeURIComponent(`${location.latitude},${location.longitude}`);
    const baseUrl = `https://www.google.com/maps/dir/?api=1&destination=${destination}&travelmode=driving`;
    const url = travelMapOrigin
      ? `${baseUrl}&origin=${encodeURIComponent(`${travelMapOrigin.latitude},${travelMapOrigin.longitude}`)}`
      : baseUrl;
    window.open(url, "_blank", "noopener,noreferrer");
  }

  return (
    <main className={`atelier-home spaces-home--mode-${mode}`} data-space={activeSpace.id}>
      <AtelierHomeView spaces={availableSpaces} active={activeSpace} mode={mode} interior={interior}
        onSelect={(id) => { setSelectedSpace(id as SpaceId); setPreviewSpace(null); }}
        onEnter={() => {
          if (!writeAtelierContext(usuario?.id, { space: activeSpace.id as FunctionalSpace, mode })) setStorageNotice("Seu espaço será mantido apenas nesta sessão.");
          setSearchParams({ espaco: activeSpace.id, modo: mode });
        }} onBack={resetMode}
        onMode={chooseMode} onCatalog={() => setCatalogOpen(true)} onPersonalize={() => openShelfPersonalizer()}
        query={globalQuery} onQuery={setGlobalQuery} onSearch={searchEverything} searchRef={globalSearchRef}
        identity={<UserIdentity usuario={usuario} />}>
        <div className="atelier-shelves">
          {activeShelfDefinitions.filter((definition) => (resolvedShelfActions[definition.id] || []).length > 0).map((definition) => <section key={definition.id} className="atelier-shelf" aria-label={shelfLabel(mode, definition.id)}>
            {(resolvedShelfActions[definition.id] || []).map((action) => <ActionLink key={homeActionId(action)} action={{ ...action, featured: action.to === "/exames-ia" || action.featured }} />)}
          </section>)}
          {!activeShelfDefinitions.some((definition) => (resolvedShelfActions[definition.id] || []).length > 0) && <div className="atelier-empty"><p>Organize este espaço do seu jeito.</p><button type="button" onClick={() => openShelfPersonalizer()}>Adicionar funções</button></div>}
        </div>
        <div className="atelier-space__note"><span>Seu espaço. Seu jeito de trabalhar.</span><Link to="/assistente"><Icone nome="assistente" />Apoio CorVIA</Link></div>
        <details className="atelier-day"><summary><Icone nome="agenda" />{mode === "scientific" ? "Sua jornada científica" : "Seu dia e deslocamento"}<Icone nome="chevron" /></summary>
      <aside className="spaces-day">
        <ClinicalChangeApprovalNotice />
        <h2>{mode === "scientific" ? "Minha jornada científica" : "Meu dia entre espaços"}</h2>
        {mode === "scientific" ? <>
          <Link to="/busca?modo=tudo-com-tudo" className="spaces-day__item spaces-day__item--cyan"><i /><span><strong>Tudo com Tudo</strong><small>Explorar relações</small></span></Link>
          <Link to="/trilhas" className="spaces-day__item spaces-day__item--violet"><i /><span><strong>Trilhas</strong><small>Continuar aprendizagem</small></span></Link>
          <Link to="/favoritos" className="spaces-day__item spaces-day__item--rose"><i /><span><strong>Favoritos</strong><small>Retomar leituras</small></span></Link>
          <ScientificIntelligenceMonitor compact />
        </> : <>
          {dayItems.length ? dayItems.slice(0, 3).map((item) => {
            const itemSpace = inferClinicalSpace(item);
            const label = item.title || item.patient_name || item.appointment_type || "Compromisso";
            return <Link to="/agenda" key={`${item.calendar_kind || "item"}-${item.id}`} className={`spaces-day__item spaces-day__item--${SPACE_TONES[itemSpace]}`}><i /><span><strong>{label}</strong><small>{time(item.starts_at)}{item.location?.name ? ` · ${item.location.name}` : ""}</small></span></Link>;
          }) : <div className={`spaces-day__empty is-${dayState}`} role="status"><strong>{dayState === "loading" ? "Sincronizando seu dia…" : dayState === "error" ? "Agenda indisponível agora" : "Nenhum compromisso hoje"}</strong><small>{dayState === "error" ? "Abra a Agenda para consultar as fontes conectadas." : "Atendimentos, compromissos e rotinas aparecerão aqui."}</small><ActionLink action={{ to: "/agenda", label: "Abrir agenda completa", icon: "agenda" }} /></div>}
          <CommutePreview
            target={travelTarget}
            route={bestRoute}
            minutes={travelMinutes}
            origin={travelMapOrigin}
            configuration={mapConfiguration}
            provider={resultMatchesTarget ? mobilityResult?.provider : undefined}
            updatedAt={resultMatchesTarget ? mobilityResult?.updated_at : undefined}
            error={travelError}
            busy={travelBusy}
            onOpen={() => {
              if (bestRoute) setTravelOpen(true);
              else void startTravel();
            }}
          />
        </>}
      </aside>


        </details>
      </AtelierHomeView>
      {storageNotice && <p className="atelier-storage-notice" role="status">{storageNotice}</p>}

      {catalogOpen && <div className="spaces-overlay" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setCatalogOpen(false); }}><aside ref={catalogRef} className="spaces-catalog" role="dialog" aria-modal="true" aria-label="Todas as funções"><header><div><Brand /><h2>Todas as funções, um único sistema.</h2></div><button type="button" onClick={() => setCatalogOpen(false)} aria-label="Fechar"><Icone nome="fechar" /></button></header><label><Icone nome="busca" /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar função" /></label><div>{visibleCatalog.map((section) => <section key={section.title}><h3>{section.title}</h3><div>{section.actions.map((action) => <ActionLink key={`${section.title}-${action.to}-${action.label}`} action={action} />)}</div></section>)}</div></aside></div>}

      {personalizerOpen && <div className="spaces-overlay" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) cancelShelfPersonalizer(); }}>
        <aside ref={personalizerRef} className="spaces-personalizer" role="dialog" aria-modal="true" aria-label="Personalizar prateleiras">
          <header>
            <div>
              <p>{mode === "scientific" ? "MINHA JORNADA" : "MEU ESPAÇO"} {activeSpace.label.toLocaleUpperCase("pt-BR")}</p>
              <h2>Personalizar prateleiras</h2>
              <small>Escolha e ordene as funções. A geometria do ambiente e o catálogo completo permanecem intactos.</small>
            </div>
            <button type="button" onClick={cancelShelfPersonalizer} aria-label="Fechar sem salvar"><Icone nome="fechar" /></button>
          </header>
          <nav className="spaces-personalizer__tabs" aria-label="Prateleiras disponíveis">
            {activeShelfDefinitions.map((definition) => <button type="button" key={`shelf-tab-${definition.id}`} className={personalizerShelf === definition.id ? "is-active" : ""} onClick={() => setPersonalizerShelf(definition.id)} aria-pressed={personalizerShelf === definition.id}>{shelfLabel(activeMode, definition.id)}</button>)}
          </nav>
          {(shelfPreferences.archives.length > 0 || recoverableIds.length > 0) && <details className="atelier-previous-organizations" style={{ margin: "12px 0", minWidth: 0 }}>
            <summary style={{ minHeight: 44, display: "flex", alignItems: "center", gap: 8, cursor: "pointer", fontSize: 16 }}><Icone nome="relogio" />Organizações anteriores e reserva</summary>
            <p style={{ lineHeight: 1.5 }}>Seu histórico foi guardado integralmente. Importar altera somente o rascunho; nada será aplicado antes de salvar.</p>
            {shelfPreferences.archives.length > 0 && <div style={{ display: "grid", gap: 8 }}>
              <label htmlFor="atelier-previous-organization">Organização anterior</label>
              <select id="atelier-previous-organization" value={previousOrganization} onChange={(event) => setPreviousOrganization(event.target.value)} style={{ minHeight: 44, width: "100%", minWidth: 0, fontSize: 16 }}>
                <option value="">Escolha uma organização para visualizar</option>
                {shelfPreferences.archives.map((archive, index) => <option key={archive.id} value={archive.id}>{shelfOrganizationLabel(archive.profileKey)} · versão {shelfPreferences.archives.length - index} · {shelfProfileItems(archive.profile).length} funções</option>)}
              </select>
              <button type="button" disabled={!previousOrganization} onClick={importPreviousOrganization} style={{ minHeight: 44, padding: "10px 12px", fontSize: 16 }}>Pré-visualizar nesta organização</button>
            </div>}
            {recoverableIds.length > 0 && <section aria-label="Funções preservadas na reserva" style={{ marginTop: 16 }}>
              <h3>Reserva · {recoverableIds.length}</h3><p>Adicione à prateleira atual quando houver espaço. Funções sem acesso continuam guardadas, sem liberar permissões.</p>
              <ul style={{ listStyle: "none", padding: 0, display: "grid", gap: 8 }}>{recoverableIds.map((id) => {
                const action = HOME_ACTIONS_BY_ID.get(id);
                const allowed = allowedPreferenceIds.has(id);
                return <li key={id} style={{ display: "flex", alignItems: "center", flexWrap: "wrap", gap: 8, minWidth: 0 }}><span style={{ flex: "1 1 160px", overflowWrap: "anywhere" }}>{action?.label || "Função anterior indisponível"}{!allowed && <small style={{ display: "block" }}>Indisponível para o acesso atual; preservada no histórico.</small>}</span><button type="button" disabled={!allowed || activeDraftIds.length >= activePersonalizerDefinition.capacity} onClick={() => toggleShelfAction(id)} style={{ minHeight: 44, padding: "10px 12px", fontSize: 16 }}>Adicionar à {shelfLabel(mode, activePersonalizerDefinition.id).toLocaleLowerCase("pt-BR")}</button></li>;
              })}</ul>
            </section>}
          </details>}
          {importNotice && <p role="status" style={{ lineHeight: 1.5 }}>{importNotice}</p>}
          <div className="spaces-personalizer__count">
            <span>{activeDraftIds.length}/{activePersonalizerDefinition.capacity} selecionadas · ordem de exibição</span>
            <button type="button" onClick={restoreShelfDefaults}>Restaurar esta prateleira</button>
          </div>
          <div className="spaces-personalizer__selected" aria-label="Funções selecionadas em ordem">
            {activeDraftIds.map((actionId, index) => {
              const action = HOME_ACTIONS_BY_ID.get(actionId);
              if (!action) return null;
              return <article key={`ordered-${actionId}`} draggable onDragStart={(event) => { event.dataTransfer.setData("text/plain", actionId); event.dataTransfer.effectAllowed = "move"; }} onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); reorderShelfDrop(event.dataTransfer.getData("text/plain"), actionId); }}>
                <Icone nome={action.icon} />
                <span><b>{index + 1}</b>{action.label}</span>
                <div>
                  <select aria-label={`Mover ${action.label} para outra prateleira`} value={personalizerShelf} onChange={(event) => transferShelfAction(actionId, event.target.value as ShelfId)}>{activeShelfDefinitions.map((definition) => <option key={definition.id} value={definition.id} disabled={definition.id !== personalizerShelf && (shelfDraft[definition.id] || []).length >= definition.capacity}>{shelfLabel(mode, definition.id)}</option>)}</select>
                  <button type="button" aria-label={`Remover ${action.label}`} onClick={() => toggleShelfAction(actionId)}><Icone nome="fechar" /></button>
                  <button type="button" onClick={() => moveShelfAction(actionId, -1)} disabled={index === 0} aria-label={`Mover ${action.label} para antes`}>↑</button>
                  <button type="button" onClick={() => moveShelfAction(actionId, 1)} disabled={index === activeDraftIds.length - 1} aria-label={`Mover ${action.label} para depois`}>↓</button>
                </div>
              </article>;
            })}
          </div>
          <label className="atelier-personalizer-search"><Icone nome="busca" /><input aria-label="Buscar função para adicionar" placeholder="Buscar em todas as funções" value={personalizerQuery} onChange={(event) => setPersonalizerQuery(event.target.value)} /></label>
          <div className="spaces-personalizer__grid">{candidateActions.filter((action, index, list) => list.findIndex((item) => item.to === action.to) === index && normalizeActionSegment(action.label).includes(normalizeActionSegment(personalizerQuery))).map((action) => {
            const actionId = homeActionId(action);
            const checked = activeDraftIds.includes(actionId);
            return <button type="button" key={`pick-${actionId}`} className={checked ? "is-selected" : ""} onClick={() => toggleShelfAction(actionId)} disabled={!checked && activeDraftIds.length >= activePersonalizerDefinition.capacity} aria-pressed={checked}><Icone nome={action.icon} /><span>{action.label}</span><i><Icone nome={checked ? "check" : "adicionar"} /></i></button>;
          })}</div>
          <footer><button type="button" className="is-secondary" onClick={cancelShelfPersonalizer}>Cancelar</button><button type="button" onClick={saveShelfPreferences}>Salvar personalização</button></footer>
        </aside>
      </div>}

      {travelOpen && <div className="spaces-overlay spaces-travel-overlay" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) closeTravel(); }}>
        <section ref={travelRef} className="spaces-travel" role="dialog" aria-modal="true" aria-label="Mapa do deslocamento entre espaços">
          <header>
            <div>
              <p>DESLOCAMENTO CORVIA</p>
              <h2>Mapa do deslocamento</h2>
              <small>Visualize o destino, a rota geográfica e o trânsito real. Sua localização atual é usada somente após sua ação e exclusivamente nesta consulta.</small>
            </div>
            <button type="button" onClick={closeTravel} aria-label="Fechar"><Icone nome="fechar" /></button>
          </header>

          {travelDestination ? <div className="spaces-travel__map">
            <MapaDeslocamento
              rotas={resultMatchesTarget ? mobilityResult?.routes || [] : []}
              origem={travelMapOrigin}
              destino={travelDestination}
              provider={(resultMatchesTarget ? mobilityResult?.provider : undefined) || mapConfiguration?.provider}
              updatedAt={resultMatchesTarget ? mobilityResult?.updated_at : undefined}
              googleMapsApiKey={mapConfiguration?.api_key}
            />
          </div> : <div className="atelier-mobility-empty"><Icone nome="pin" /><strong>Vamos preparar seu próximo percurso</strong><span>Vincule um endereço ao compromisso ou configure o destino de retorno na Agenda.</span><Link to="/agenda" onClick={closeTravel}>Abrir agenda</Link></div>}

          <div className="spaces-travel__status" role="status" aria-live="polite">
            {travelBusy ? <><strong>Calculando rota…</strong><small>Consultando sua posição autorizada e o trânsito atual.</small></> : bestRoute ? <><strong>{travelMinutes} min <em>·</em> {distanceLabel(bestRoute.distance_meters)}</strong><small>{bestRoute.summary || "Rota recomendada"}{bestRoute.congestion ? ` · ${trafficLabel(bestRoute.congestion)}` : ""}{mobilityResult?.provider ? ` · ${mobilityResult.provider}` : ""}</small></> : <><strong>{travelTarget?.location?.name || travelTarget?.service_name || "Próximo destino"}</strong><small>{travelError || "Destino preparado. Calcule a rota para incluir sua origem e o trânsito atual."}</small></>}
          </div>
          {bestRoute && travelError && <p className="atelier-commute__notice" role="status">{travelError}</p>}
          {resultMatchesTarget && mobilityResult?.tips?.length ? <ul>{mobilityResult.tips.slice(0, 3).map((tip) => <li key={tip}>{tip}</li>)}</ul> : null}
          <footer>
            <Link to="/agenda" onClick={closeTravel}>Revisar locais na Agenda</Link>
            <button type="button" className="spaces-travel__recalculate" onClick={() => void startTravel()} disabled={travelBusy}><Icone nome="rota" /> {travelBusy ? "Calculando…" : bestRoute ? "Recalcular rota" : "Calcular rota real"}</button>
            <button type="button" className="spaces-travel__maps" onClick={openExternalMap}><Icone nome="rota" /> Abrir navegação no mapa</button>
          </footer>
        </section>
      </div>}
    </main>
  );
}

export { TOUR_KEY, INVESTOR_TOUR_SESSION_KEY };
