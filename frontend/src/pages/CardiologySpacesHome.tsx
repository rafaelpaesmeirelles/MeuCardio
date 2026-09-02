import { useCallback, useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import CardiologySpaceScene from "../components/CardiologySpaceScene";
import Icone, { type NomeIcone } from "../components/Icone";
import MapaDeslocamento, { type RotaDeslocamento } from "../components/MapaDeslocamento";
import { CoracaoHolografico } from "../components/PreHomeBrand";
import { api, assetUrl, type Usuario } from "../lib/api";
import { heartTeamEnabled, whatsappAssistantEnabled } from "../lib/aiFeatureFlags";
import { useAuth } from "../lib/auth";
import { nomeComTratamento } from "../lib/clinicalIdentity";
import { withoutReservedSmokeTestRecord, withoutReservedSmokeTestRecords } from "../lib/reservedSmokeAgenda";
import "../styles/cardiology-spaces-home.css";

type Mode = "complete" | "essential" | "scientific";
type ClinicalSpaceId = "consultorio" | "hospital" | "ensino" | "pesquisa" | "gestao";
type ScientificSpaceId = "descobrir" | "evidencias" | "aprender" | "ensinar" | "produzir";
type SpaceId = ClinicalSpaceId | ScientificSpaceId;
type Tone = "cyan" | "blue" | "violet" | "rose" | "teal";
type ShelfId = "now" | "next" | "references" | "essential";
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
type MiniRoutePoint = { x: number; y: number };
type MiniRouteGeometry = {
  path: string;
  start: MiniRoutePoint;
  end: MiniRoutePoint;
  ship: MiniRoutePoint & { angle: number };
  ringedPlanet: MiniRoutePoint;
  violetPlanet: MiniRoutePoint;
  asteroidField: MiniRoutePoint;
  trafficPaths: Array<{ path: string; speed: "normal" | "slow" | "traffic_jam" }>;
  actual: boolean;
};
type ShelfDefinition = {
  id: ShelfId;
  capacity: number;
  defaultActionIds: string[];
};
type ShelfProfile = Partial<Record<ShelfId, string[]>>;
type ShelfPreferences = {
  schemaVersion: 1;
  updatedAt: string;
  profiles: Record<string, ShelfProfile>;
};

const MODE_KEY = "corvia:cardiology-spaces:mode";
const TOUR_KEY = "corvia:cardiology-spaces:tour:v3";
const INVESTOR_TOUR_SESSION_KEY = "corvia:cardiology-spaces:investor-tour-session:v1";
const SHELF_PREFERENCES_PREFIX = "corvia:cardiology-spaces:shelves:v1";

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
  hospital: ["/exames", "/documentos", "/checklists", "/calculadoras"],
  ensino: ["/trilhas", "/casos-clinicos", "/apresentacao", "/galeria", "/diretrizes", "/biblioteca"],
  pesquisa: ["/estudos", "/evidencias", "/documentos-cientificos-ia", "/biblioteca", "/diretrizes", "/exportar"],
  gestao: ["/indicadores", "/agenda", "/usuarios-online", "/sincronizacao", "/corvia-mail", "/minha-conta"],
};

const SHELF_CAPACITIES: Record<ShelfId, number> = {
  now: 3,
  next: 3,
  references: 4,
  essential: 6,
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

const HOME_ACTIONS = [...CATALOG.flatMap((section) => section.actions), ...SPACES.flatMap((space) => [
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

function shelfLabel(mode: Mode, shelfId: ShelfId) {
  if (shelfId === "now") return "Agora";
  if (shelfId === "essential") return "Meus essenciais";
  if (shelfId === "next") return mode === "scientific" ? "Aprofundar" : "Em seguida";
  return mode === "scientific" ? "Conexões" : "Referências";
}

function shelfDefinitions(mode: Mode, space: Space): ShelfDefinition[] {
  const definition = (id: ShelfId, actions: Action[]): ShelfDefinition => ({
    id,
    capacity: SHELF_CAPACITIES[id],
    defaultActionIds: actions.map(homeActionId),
  });
  if (mode === "essential") {
    const spaceId = space.id as ClinicalSpaceId;
    const essentialActions = ESSENTIAL_DEFAULTS[spaceId]
      .map(actionForLegacyPath)
      .filter((action): action is Action => Boolean(action));
    return [definition("now", space.now), definition("essential", essentialActions)];
  }
  return [
    definition("now", space.now),
    definition("next", space.next),
    definition("references", space.references),
  ];
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

function emptyShelfPreferences(): ShelfPreferences {
  return { schemaVersion: 1, updatedAt: new Date(0).toISOString(), profiles: {} };
}

function parseShelfPreferences(raw: string | null): ShelfPreferences {
  if (!raw) return emptyShelfPreferences();
  try {
    const parsed = JSON.parse(raw) as Partial<ShelfPreferences>;
    if (parsed.schemaVersion !== 1 || !parsed.profiles || typeof parsed.profiles !== "object") return emptyShelfPreferences();
    const profiles: Record<string, ShelfProfile> = {};
    for (const [profileKey, profile] of Object.entries(parsed.profiles)) {
      if (!profile || typeof profile !== "object") continue;
      const safeProfile: ShelfProfile = {};
      for (const shelfId of ["now", "next", "references", "essential"] as ShelfId[]) {
        const actionIds = profile[shelfId];
        if (!Array.isArray(actionIds)) continue;
        safeProfile[shelfId] = [...new Set(actionIds.filter((actionId): actionId is string => typeof actionId === "string"))];
      }
      profiles[profileKey] = safeProfile;
    }
    return {
      schemaVersion: 1,
      updatedAt: typeof parsed.updatedAt === "string" ? parsed.updatedAt : new Date(0).toISOString(),
      profiles,
    };
  } catch {
    return emptyShelfPreferences();
  }
}

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

function decodeMiniRoutePolyline(value: string, precision = 5) {
  const coordinates: Array<[number, number]> = [];
  const factor = 10 ** precision;
  let index = 0;
  let latitude = 0;
  let longitude = 0;
  while (index < value.length) {
    let result = 0;
    let shift = 0;
    let byte = 0;
    do {
      byte = value.charCodeAt(index++) - 63;
      result |= (byte & 0x1f) << shift;
      shift += 5;
    } while (byte >= 0x20 && index <= value.length);
    latitude += result & 1 ? ~(result >> 1) : result >> 1;
    result = 0;
    shift = 0;
    do {
      byte = value.charCodeAt(index++) - 63;
      result |= (byte & 0x1f) << shift;
      shift += 5;
    } while (byte >= 0x20 && index <= value.length);
    longitude += result & 1 ? ~(result >> 1) : result >> 1;
    coordinates.push([latitude / factor, longitude / factor]);
  }
  return coordinates;
}

function miniRoutePath(points: MiniRoutePoint[]) {
  return points.map((point, index) => `${index ? "L" : "M"}${point.x.toFixed(1)} ${point.y.toFixed(1)}`).join(" ");
}

function buildMiniRouteGeometry(route?: MobilityRoute): MiniRouteGeometry {
  const fallback: MiniRouteGeometry = {
    path: "M16 70 C42 14 112 13 164 57",
    start: { x: 16, y: 70 },
    end: { x: 164, y: 57 },
    ship: { x: 91, y: 25, angle: 13 },
    ringedPlanet: { x: 59, y: 47 },
    violetPlanet: { x: 128, y: 25 },
    asteroidField: { x: 103, y: 66 },
    trafficPaths: [],
    actual: false,
  };
  if (!route?.geometry?.value) return fallback;

  const coordinates = decodeMiniRoutePolyline(route.geometry.value, route.geometry.precision);
  if (coordinates.length < 2) return fallback;
  const averageLatitude = coordinates.reduce((total, point) => total + point[0], 0) / coordinates.length;
  const longitudeFactor = Math.cos(averageLatitude * Math.PI / 180);
  const cartesian = coordinates.map(([latitude, longitude]) => ({ x: longitude * longitudeFactor, y: latitude }));
  const minX = Math.min(...cartesian.map((point) => point.x));
  const maxX = Math.max(...cartesian.map((point) => point.x));
  const minY = Math.min(...cartesian.map((point) => point.y));
  const maxY = Math.max(...cartesian.map((point) => point.y));
  const width = 180;
  const height = 92;
  const padding = 14;
  const scale = Math.min(
    (width - padding * 2) / Math.max(maxX - minX, 0.00001),
    (height - padding * 2) / Math.max(maxY - minY, 0.00001),
  );
  const contentWidth = (maxX - minX) * scale;
  const contentHeight = (maxY - minY) * scale;
  const offsetX = (width - contentWidth) / 2;
  const offsetY = (height - contentHeight) / 2;
  const projected = cartesian.map((point) => ({
    x: offsetX + (point.x - minX) * scale,
    y: height - (offsetY + (point.y - minY) * scale),
  }));
  const clamp = (value: number, minimum: number, maximum: number) => Math.max(minimum, Math.min(maximum, value));
  const pointAroundRoute = (ratio: number, offset: number) => {
    const index = Math.round((projected.length - 1) * ratio);
    const current = projected[index];
    const previous = projected[Math.max(0, index - 1)];
    const next = projected[Math.min(projected.length - 1, index + 1)];
    const dx = next.x - previous.x;
    const dy = next.y - previous.y;
    const length = Math.max(1, Math.hypot(dx, dy));
    return {
      x: clamp(current.x - (dy / length) * offset, 12, width - 12),
      y: clamp(current.y + (dx / length) * offset, 12, height - 12),
    };
  };
  const shipIndex = Math.round((projected.length - 1) * 0.52);
  const shipPrevious = projected[Math.max(0, shipIndex - 1)];
  const shipNext = projected[Math.min(projected.length - 1, shipIndex + 1)];
  const trafficPaths = (route.traffic_segments || []).flatMap((segment) => {
    const end = segment.end_index == null ? projected.length : segment.end_index + 1;
    const points = projected.slice(segment.start_index, end);
    if (points.length < 2) return [];
    const normalizedSpeed: "normal" | "slow" | "traffic_jam" = segment.speed === "traffic_jam" || segment.speed === "slow" ? segment.speed : "normal";
    return [{ path: miniRoutePath(points), speed: normalizedSpeed }];
  });

  return {
    path: miniRoutePath(projected),
    start: projected[0],
    end: projected[projected.length - 1],
    ship: {
      ...projected[shipIndex],
      angle: Math.atan2(shipNext.y - shipPrevious.y, shipNext.x - shipPrevious.x) * 180 / Math.PI + 90,
    },
    ringedPlanet: pointAroundRoute(0.31, 11),
    violetPlanet: pointAroundRoute(0.72, -10),
    asteroidField: pointAroundRoute(0.54, 12),
    trafficPaths,
    actual: true,
  };
}

function StellarRouteMiniMap({
  target,
  route,
  minutes,
  busy,
  onOpen,
}: {
  target: MobilityTarget | null;
  route?: MobilityRoute;
  minutes: number | null;
  busy: boolean;
  onOpen: () => void;
}) {
  const destination = target?.location?.name || target?.service_name || "Próximo destino";
  const hasRoute = Boolean(route && minutes);
  const level = trafficLevel(route?.congestion);
  const miniRoute = useMemo(() => buildMiniRouteGeometry(route), [route]);
  const accessibleStatus = busy
    ? `Calculando deslocamento para ${destination}`
    : hasRoute
      ? `Abrir deslocamento para ${destination}: ${minutes} minutos, ${distanceLabel(route?.distance_meters)}, ${trafficLabel(route?.congestion)}`
      : `Calcular deslocamento para ${destination}`;

  return (
    <button
      type="button"
      className="spaces-stellar-route"
      data-traffic={level}
      data-state={busy ? "loading" : hasRoute ? "ready" : "pending"}
      onClick={onOpen}
      aria-busy={busy}
      aria-label={accessibleStatus}
      disabled={busy}
    >
      <span className="spaces-stellar-route__heading">
        <span><Icone nome="rota" /></span>
        <span><strong>Deslocamento</strong><small>{destination}</small></span>
        <Icone nome="seta" />
      </span>
      <span className="spaces-stellar-route__map" aria-hidden="true">
        <i className="spaces-stellar-route__star spaces-stellar-route__star--one" />
        <i className="spaces-stellar-route__star spaces-stellar-route__star--two" />
        <i className="spaces-stellar-route__star spaces-stellar-route__star--three" />
        <svg viewBox="0 0 180 92" preserveAspectRatio="xMidYMid meet">
          <ellipse className="spaces-stellar-route__nebula" cx="94" cy="49" rx="71" ry="35" />
          <g className="spaces-stellar-route__celestial spaces-stellar-route__celestial--ringed" transform={`translate(${miniRoute.ringedPlanet.x} ${miniRoute.ringedPlanet.y}) rotate(-17)`}>
            <ellipse className="spaces-stellar-route__planet-ring spaces-stellar-route__planet-ring--back" cx="0" cy="0" rx="12" ry="3.6" />
            <circle className="spaces-stellar-route__planet spaces-stellar-route__planet--amber" cx="0" cy="0" r="6.3" />
            <ellipse className="spaces-stellar-route__planet-ring spaces-stellar-route__planet-ring--front" cx="0" cy="0" rx="12" ry="3.6" />
          </g>
          <g className="spaces-stellar-route__celestial spaces-stellar-route__celestial--violet" transform={`translate(${miniRoute.violetPlanet.x} ${miniRoute.violetPlanet.y})`}>
            <circle className="spaces-stellar-route__planet-glow" cx="0" cy="0" r="9" />
            <circle className="spaces-stellar-route__planet spaces-stellar-route__planet--violet" cx="0" cy="0" r="5.5" />
            <path className="spaces-stellar-route__planet-shade" d="M-4 -3 C-1 -5 4 -4 5 -1 C2 -2 -1 1 -4 -3Z" />
            <circle className="spaces-stellar-route__moon" cx="10" cy="-6" r="1.8" />
          </g>
          <g className="spaces-stellar-route__asteroids" transform={`translate(${miniRoute.asteroidField.x} ${miniRoute.asteroidField.y})`}>
            <circle cx="-8" cy="1" r="1.25" />
            <circle cx="-3" cy="-3" r="0.9" />
            <circle cx="3" cy="2" r="1.1" />
            <circle cx="9" cy="-2" r="0.7" />
          </g>
          <path className="spaces-stellar-route__orbit-glow" d={miniRoute.path} />
          <path className="spaces-stellar-route__orbit" d={miniRoute.path} data-geometry={miniRoute.actual ? "real" : "preview"} />
          {miniRoute.trafficPaths.length ? miniRoute.trafficPaths.map((segment, index) => <path key={`${segment.speed}-${index}`} className={`spaces-stellar-route__traffic spaces-stellar-route__traffic--${segment.speed}`} d={segment.path} />) : <path className="spaces-stellar-route__traffic" d={miniRoute.path} />}
          <circle className="spaces-stellar-route__origin" cx={miniRoute.start.x} cy={miniRoute.start.y} r="5" />
          <circle className="spaces-stellar-route__destination-glow" cx={miniRoute.end.x} cy={miniRoute.end.y} r="10" />
          <circle className="spaces-stellar-route__destination" cx={miniRoute.end.x} cy={miniRoute.end.y} r="5" />
          <g className="spaces-stellar-route__ship" transform={`translate(${miniRoute.ship.x} ${miniRoute.ship.y}) rotate(${miniRoute.ship.angle})`}><path d="M-5 4 0-7 5 4 0 2Z" /></g>
          <text className="spaces-stellar-route__label" x={miniRoute.start.x} y={Math.min(89, miniRoute.start.y + 13)} textAnchor={miniRoute.start.x < 30 ? "start" : "middle"}>AGORA</text>
          <text className="spaces-stellar-route__label" x={miniRoute.end.x} y={Math.min(89, miniRoute.end.y + 13)} textAnchor={miniRoute.end.x > 150 ? "end" : "middle"}>DESTINO</text>
        </svg>
      </span>
      <span className="spaces-stellar-route__metrics" role="status" aria-live="polite" aria-atomic="true">
        {busy ? <strong>Calculando trajetória…</strong> : hasRoute ? <>
          <strong>{minutes} min</strong>
          <span>{distanceLabel(route?.distance_meters)}</span>
          <span>{trafficShortLabel(route?.congestion)}</span>
        </> : <>
          <strong>Traçar rota</strong>
          <span>Sem cálculo</span>
          <span>{target ? "Destino pronto" : "Aguardando agenda"}</span>
        </>}
      </span>
    </button>
  );
}

function ActionLink({ action, compact = false }: { action: Action; compact?: boolean }) {
  return <Link className={`spaces-action${compact ? " spaces-action--compact" : ""}`} data-feature={action.to === "/exames-ia" ? "exam-ai" : undefined} to={action.to}><Icone nome={action.icon} /><span>{action.label}</span></Link>;
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
      if (event.shiftKey && document.activeElement === first) {
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

function mobilityRouteError(result: MobilityResult) {
  if (result.routes?.length) return null;
  if (result.status === "not_configured") return "O destino está pronto, mas o provedor de trânsito ainda não está configurado.";
  if (result.status === "origin_not_geocoded") return "Não foi possível localizar com segurança o ponto de partida salvo.";
  if (result.status === "destination_not_geocoded") return "Não foi possível localizar o endereço deste compromisso. Revise o local cadastrado na Agenda.";
  if (result.status === "destination_without_location") return "Este compromisso ainda não possui um local cadastrado para a rota.";
  if (result.status === "live") return "O provedor respondeu, mas não retornou uma rota utilizável. Tente novamente.";
  return "A rota não pôde ser calculada agora. O destino continua disponível no mapa.";
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
  const [personalizerShelf, setPersonalizerShelf] = useState<ShelfId>("now");
  const [shelfPreferences, setShelfPreferences] = useState<ShelfPreferences>(emptyShelfPreferences);
  const [shelfDraft, setShelfDraft] = useState<ShelfProfile>({});
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
    let preferences = emptyShelfPreferences();
    try {
      preferences = parseShelfPreferences(localStorage.getItem(preferenceKey));
      let migrated = false;
      for (const space of SPACES) {
        const profileKey = shelfProfileKey("essential", space.id);
        // A propriedade presente, inclusive [], é uma preferência nova e
        // explícita. Testar length reinjetava o legado após o usuário esvaziar
        // a prateleira.
        if (Object.prototype.hasOwnProperty.call(preferences.profiles[profileKey] || {}, "essential")) continue;
        const legacyKey = `corvia:cardiology-spaces:essentials:${usuario.id}:${space.id}`;
        let legacyPaths: unknown = [];
        try {
          legacyPaths = JSON.parse(localStorage.getItem(legacyKey) || "[]") as unknown;
        } catch {
          continue;
        }
        if (!Array.isArray(legacyPaths) || !legacyPaths.length) continue;
        const migratedActionIds = legacyPaths
          .filter((path): path is string => typeof path === "string")
          .map(actionForLegacyPath)
          .filter((action): action is Action => Boolean(action))
          .map(homeActionId)
          .slice(0, SHELF_CAPACITIES.essential);
        if (!migratedActionIds.length) continue;
        preferences.profiles[profileKey] = {
          ...preferences.profiles[profileKey],
          essential: migratedActionIds,
        };
        localStorage.removeItem(legacyKey);
        migrated = true;
      }
      if (migrated) {
        preferences.updatedAt = new Date().toISOString();
        localStorage.setItem(preferenceKey, JSON.stringify(preferences));
      }
    } catch {
      preferences = emptyShelfPreferences();
    }
    setShelfPreferences(preferences);
    const syncPreferences = (event: StorageEvent) => {
      if (event.key === preferenceKey) setShelfPreferences(parseShelfPreferences(event.newValue));
    };
    window.addEventListener("storage", syncPreferences);
    return () => window.removeEventListener("storage", syncPreferences);
  }, [usuario?.id]);

  useEffect(() => {
    const focusEverything = (event: KeyboardEvent) => {
      if (!(event.metaKey || event.ctrlKey) || event.key.toLocaleLowerCase("pt-BR") !== "k") return;
      event.preventDefault();
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
      setTravelOpen(false);
    };
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, [catalogOpen, personalizerOpen, travelOpen]);

  const activeMode: Mode = mode || "complete";
  const availableSpaces = activeMode === "scientific" ? SCIENTIFIC_SPACES : SPACES;
  const activeSpace = availableSpaces.find((space) => space.id === selectedSpace) || availableSpaces[0];
  const visibleCatalog = useMemo(() => CATALOG.map((section) => ({
    ...section,
    actions: section.actions.filter((action) => (!action.adminOnly || usuario?.role === "admin") && (!query || action.label.toLocaleLowerCase("pt-BR").includes(query.toLocaleLowerCase("pt-BR")))),
  })).filter((section) => section.actions.length), [query, usuario?.role]);
  const candidateActions = useMemo(
    () => HOME_ACTIONS.filter((action) => !action.adminOnly || usuario?.role === "admin"),
    [usuario?.role],
  );
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
  const chamamento = usuario?.professional_title?.trim() || nomeComTratamento(usuario, true);
  const tratamentoNormalizado = usuario?.professional_title?.trim().toLocaleLowerCase("pt-BR").replaceAll(".", "") || "";
  const artigoDoChamamento = /\b(?:dra|sra|profa)\b/.test(tratamentoNormalizado)
    ? "a"
    : /\b(?:dr|sr|prof)\b/.test(tratamentoNormalizado)
      ? "o"
      : "";
  const chamamentoComArtigo = [artigoDoChamamento, chamamento].filter(Boolean).join(" ");
  const question = mode === "scientific" ? `Como ${chamamentoComArtigo} quer explorar o conhecimento agora?` : `Onde ${chamamentoComArtigo} vai trabalhar agora?`;
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
  const travelTarget = resultMatchesTarget ? mobilityResult?.destination || plannedMobilityTarget : plannedMobilityTarget;
  const bestRoute = resultMatchesTarget ? mobilityResult?.routes?.[0] : undefined;
  const travelMinutes = bestRoute?.duration_seconds ? Math.max(1, Math.round(bestRoute.duration_seconds / 60)) : null;
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

  useEffect(() => {
    setMobilityResult((current) => current?.destination?.target_key === plannedMobilityTarget?.target_key ? current : null);
    setTravelOrigin(null);
    setTravelError(null);
  }, [plannedMobilityTarget?.target_key]);

  useEffect(() => {
    if (!usesSavedOrigin || !plannedMobilityTarget?.target_key || !mobilityPreference?.day_start_location_id || resultMatchesTarget) return;
    let active = true;
    api.post<MobilityResult>("/agenda/mobility/commute-target-from-location", {
      origin_location_id: mobilityPreference.day_start_location_id,
      target_key: plannedMobilityTarget.target_key,
    }).then((result) => {
      if (!active) return;
      const safeResult = sanitizeMobilityResult(result, plannedMobilityTarget);
      if (safeResult?.routes?.length) setMobilityResult(safeResult);
    }).catch(() => undefined);
    return () => { active = false; };
  }, [mobilityPreference?.day_start_location_id, plannedMobilityTarget, resultMatchesTarget, usesSavedOrigin]);

  useEffect(() => {
    if (!returnHomeActive
      || !plannedMobilityTarget?.target_key
      || !mobilityDayContext?.last_target?.target_key
      || !mobilityPreference?.enabled
      || !mobilityPreference.day_end_destination_location_id
      || resultMatchesTarget) return;
    let active = true;
    api.post<MobilityResult>("/agenda/mobility/commute-return", {
      origin_target_key: mobilityDayContext.last_target.target_key,
      destination_location_id: mobilityPreference.day_end_destination_location_id,
    }).then((result) => {
      if (!active) return;
      const safeResult = sanitizeMobilityResult(result, plannedMobilityTarget);
      if (safeResult) {
        setMobilityResult(safeResult);
        setTravelError(mobilityRouteError(safeResult));
      }
    }).catch(() => undefined);
    return () => { active = false; };
  }, [mobilityDayContext?.last_target?.target_key, mobilityPreference?.day_end_destination_location_id, mobilityPreference?.enabled, plannedMobilityTarget, resultMatchesTarget, returnHomeActive]);

  const chooseMode = useCallback((nextMode: Mode) => {
    sessionStorage.setItem(MODE_KEY, nextMode);
    setMode(nextMode);
    setSelectedSpace(nextMode === "scientific" ? "descobrir" : "consultorio");
    setPreviewSpace(null);
    const investorNeedsTour = usuario?.investidor && !sessionStorage.getItem(INVESTOR_TOUR_SESSION_KEY);
    if (usuario?.onboarding_pendente || investorNeedsTour) {
      navigate("/tour?retorno=/");
    }
  }, [navigate, usuario?.investidor, usuario?.onboarding_pendente]);

  function resetMode() {
    sessionStorage.removeItem(MODE_KEY);
    setMode(null);
    setSelectedSpace("consultorio");
    setPreviewSpace(null);
  }

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
    setPersonalizerShelf(requestedShelf);
    setPreviewSpace(null);
    setPersonalizerOpen(true);
  }

  function cancelShelfPersonalizer() {
    setPersonalizerOpen(false);
    setShelfDraft({});
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
      return { ...currentDraft, [definition.id]: next };
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

  function restoreShelfDefaults() {
    const definition = activePersonalizerDefinition;
    setShelfDraft((currentDraft) => ({
      ...currentDraft,
      [definition.id]: resolveShelfActionIds(undefined, definition, candidateActions),
    }));
  }

  function saveShelfPreferences() {
    const allowedIds = new Set(candidateActions.map(homeActionId));
    const savedProfile = activeShelfDefinitions.reduce<ShelfProfile>((profile, definition) => {
      profile[definition.id] = [...new Set((shelfDraft[definition.id] || [])
        .filter((actionId) => allowedIds.has(actionId)))]
        .slice(0, definition.capacity);
      return profile;
    }, {});
    const nextPreferences: ShelfPreferences = {
      schemaVersion: 1,
      updatedAt: new Date().toISOString(),
      profiles: { ...shelfPreferences.profiles, [activeProfileKey]: savedProfile },
    };
    setShelfPreferences(nextPreferences);
    if (usuario?.id) {
      try {
        localStorage.setItem(`${SHELF_PREFERENCES_PREFIX}:${usuario.id}`, JSON.stringify(nextPreferences));
      } catch {
        // A personalização continua válida na sessão mesmo se o armazenamento local estiver indisponível.
      }
    }
    setPersonalizerOpen(false);
    setShelfDraft({});
  }

  async function startTravel() {
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
        target = withoutReservedSmokeTestRecord(preparedTarget);
        setMobilityTarget(target);
      }
      if (!target?.target_key) {
        setTravelError("Não há um próximo compromisso presencial com local cadastrado para traçar a rota.");
        return;
      }
      if (mobilityPreference && !mobilityPreference.enabled) {
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
        const liveOrigin = { latitude: position.coords.latitude, longitude: position.coords.longitude };
        setTravelOrigin(liveOrigin);
        result = await api.post<MobilityResult>("/agenda/mobility/commute-target", {
          ...liveOrigin,
          target_key: target.target_key,
        });
      }
      const safeResult = sanitizeMobilityResult(result, target);
      if (!safeResult) {
        setTravelError("O destino retornado não corresponde ao compromisso exibido. A rota anterior foi preservada.");
        return;
      }
      setMobilityResult(safeResult);
      if (safeResult.origin_location?.latitude != null && safeResult.origin_location.longitude != null && !usesSavedOrigin) {
        setTravelOrigin({ latitude: safeResult.origin_location.latitude, longitude: safeResult.origin_location.longitude });
      }
      setTravelError(mobilityRouteError(safeResult));
    } catch (error) {
      setTravelError(geolocationErrorMessage(error));
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
    const destination = encodeURIComponent(`${location.latitude},${location.longitude}`);
    const baseUrl = `https://www.google.com/maps/dir/?api=1&destination=${destination}&travelmode=driving`;
    const url = travelMapOrigin
      ? `${baseUrl}&origin=${encodeURIComponent(`${travelMapOrigin.latitude},${travelMapOrigin.longitude}`)}`
      : baseUrl;
    window.open(url, "_blank", "noopener,noreferrer");
  }

  if (!mode) {
    return (
      <main className="spaces-choice">
        <div className="spaces-choice__heart" aria-hidden="true"><CoracaoHolografico /></div>
        <header><Brand /><span className="spaces-user"><UserIdentity usuario={usuario} /></span></header>
        <section className="spaces-choice__content">
          <p className="spaces-eyebrow">CARDIOLOGY SPACES</p>
          <h1>Como {chamamento} quer trabalhar hoje?</h1>
          <p>Escolha a experiência que acompanha o seu momento. O CorVIA reorganiza cada ambiente ao redor do que importa agora.</p>
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
        <footer>O ambiente muda. <strong>O Médico continua no centro.</strong></footer>
      </main>
    );
  }

  return (
    <main className={`spaces-home spaces-home--${activeSpace.tone} spaces-home--mode-${mode}${mode === "scientific" ? " spaces-home--scientific" : ""}`}>
      <div className="spaces-home__heart" aria-hidden="true"><CoracaoHolografico /></div>
      <header className="spaces-home__topbar">
        <button type="button" className="spaces-brand-button" onClick={resetMode} aria-label="Voltar à escolha de experiência"><Brand /></button>
        <form className="spaces-everything-search" role="search" onSubmit={searchEverything}>
          <Icone nome="busca" />
          <input ref={globalSearchRef} value={globalQuery} onChange={(event) => setGlobalQuery(event.target.value)} placeholder="Tudo com Tudo — relações, evidências e funções" aria-label="Buscar no Tudo com Tudo" />
          <kbd>⌘ K</kbd>
          <button type="submit" aria-label="Buscar no Tudo com Tudo"><Icone nome="seta" /></button>
        </form>
        <nav aria-label="Modo de trabalho">
          <button className={mode === "complete" ? "is-active" : ""} onClick={() => chooseMode("complete")}>Completo</button>
          <button className={mode === "essential" ? "is-active" : ""} onClick={() => chooseMode("essential")}>Essencial</button>
          <button className={mode === "scientific" ? "is-active" : ""} onClick={() => chooseMode("scientific")}>Ciência & Ensino</button>
        </nav>
        <Link to="/minha-conta" className="spaces-user"><UserIdentity usuario={usuario} chevron /></Link>
      </header>

      <aside className="spaces-context-rail" aria-label="Navegação entre espaços">
        <span><small>{mode === "scientific" ? "MINHAS" : "MEUS"}</small><strong>{mode === "scientific" ? "JORNADAS" : "ESPAÇOS"}</strong></span>
        <div className="spaces-context-rail__spaces">
          {availableSpaces.map((space) => (
            <button
              key={`rail-${space.id}`}
              type="button"
              className={`spaces-context-rail__space spaces-context-rail__space--${space.tone}${selectedSpace === space.id ? " is-active" : ""}`}
              onClick={() => { setSelectedSpace(space.id); setPreviewSpace(null); }}
              aria-label={`Abrir ${space.label}`}
              aria-pressed={selectedSpace === space.id}
            >
              <Icone nome={space.icon} /><span>{space.label}</span><i aria-hidden="true" />
            </button>
          ))}
        </div>
        <button type="button" className="spaces-context-rail__all" onClick={() => setCatalogOpen(true)}><Icone nome="mais" /><span>Todas as funções</span></button>
        <button type="button" className="spaces-context-rail__personalize" onClick={() => openShelfPersonalizer()}><Icone nome="configuracao" /><span>Personalizar prateleiras</span></button>
      </aside>

      <section className="spaces-workspace">
        <header className="spaces-workspace__greeting">
          <h1>{question}</h1>
          <span>{mode === "scientific" ? "Escolha uma jornada científica. O conhecimento continua conectado." : "Escolha o ambiente. A interface reorganiza as prioridades sem esconder o CorVIA."}</span>
        </header>

        <div className="spaces-doors" onMouseLeave={() => setPreviewSpace(null)}>
          {availableSpaces.map((space) => {
            const active = activeSpace.id === space.id;
            const preview = previewSpace === space.id && !active;
            return (
              <button key={space.id} type="button" className={`spaces-door spaces-door--${space.tone}${active ? " is-active" : ""}${preview ? " is-preview" : ""}`} data-state={active ? "active" : preview ? "preview" : "inactive"} onMouseEnter={() => setPreviewSpace(space.id)} onFocus={() => setPreviewSpace(space.id)} onBlur={() => setPreviewSpace(null)} onClick={() => { setSelectedSpace(space.id); setPreviewSpace(null); }} aria-label={`${space.label}. ${space.description}`} aria-pressed={selectedSpace === space.id}>
                <span><Icone nome={space.icon} />{space.label}</span>
                <i aria-hidden="true"><CardiologySpaceScene space={space.id} /></i>
              </button>
            );
          })}
        </div>

        <div className="spaces-title"><span>{mode === "scientific" ? "Minha jornada" : "Meu espaço"}</span> <strong>{activeSpace.label}</strong><small>{activeSpace.description}</small></div>

        <div className="spaces-layers" aria-live="polite">
          <section className="spaces-layer spaces-layer--now">
            <header><span>AGORA</span><strong>{activeSpace.label === "Hospital" ? "Round hospitalar · prioridades" : mode === "scientific" ? `Jornada para ${activeSpace.label.toLocaleLowerCase("pt-BR")}` : `Rotina de ${activeSpace.label.toLocaleLowerCase("pt-BR")}`}</strong><button type="button" className="spaces-layer__edit" onClick={() => openShelfPersonalizer("now")} aria-label="Personalizar prateleira Agora"><Icone nome="configuracao" /></button></header>
            <div>{(resolvedShelfActions.now || []).map((action) => <ActionLink key={`${activeSpace.id}-now-${homeActionId(action)}`} action={action} />)}</div>
          </section>
          {mode !== "essential" ? <>
            <section className="spaces-layer spaces-layer--next"><header><span>{mode === "scientific" ? "APROFUNDAR" : "EM SEGUIDA"}</span><button type="button" className="spaces-layer__edit" onClick={() => openShelfPersonalizer("next")} aria-label={`Personalizar prateleira ${mode === "scientific" ? "Aprofundar" : "Em seguida"}`}><Icone nome="configuracao" /></button></header><div>{(resolvedShelfActions.next || []).map((action) => <ActionLink key={`${activeSpace.id}-next-${homeActionId(action)}`} action={action} />)}</div></section>
            <section className="spaces-layer spaces-layer--refs"><header><span>{mode === "scientific" ? "CONEXÕES DO CONHECIMENTO" : "REFERÊNCIAS DO ESPAÇO"}</span><button type="button" className="spaces-layer__edit" onClick={() => openShelfPersonalizer("references")} aria-label={`Personalizar ${mode === "scientific" ? "conexões do conhecimento" : "referências do espaço"}`}><Icone nome="configuracao" /></button></header><div>{(resolvedShelfActions.references || []).map((action) => <ActionLink key={`${activeSpace.id}-ref-${homeActionId(action)}`} action={action} />)}</div></section>
          </> : <>
            <section className="spaces-layer spaces-layer--essential"><header><span>MEUS ESSENCIAIS</span><button type="button" className="spaces-layer__edit" onClick={() => openShelfPersonalizer("essential")} aria-label="Personalizar Meus essenciais"><Icone nome="configuracao" /></button></header><div>{(resolvedShelfActions.essential || []).map((action) => <ActionLink key={`essential-${activeSpace.id}-${homeActionId(action)}`} action={action} />)}</div></section>
            <button type="button" className="spaces-personalize" onClick={() => openShelfPersonalizer("essential")}><Icone nome="configuracao" /> Personalizar prateleiras</button>
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
        </> : <>
          {dayItems.length ? dayItems.slice(0, 3).map((item) => {
            const itemSpace = inferClinicalSpace(item);
            const label = item.title || item.patient_name || item.appointment_type || "Compromisso";
            return <Link to="/agenda" key={`${item.calendar_kind || "item"}-${item.id}`} className={`spaces-day__item spaces-day__item--${SPACE_TONES[itemSpace]}`}><i /><span><strong>{label}</strong><small>{time(item.starts_at)}{item.location?.name ? ` · ${item.location.name}` : ""}</small></span></Link>;
          }) : <div className={`spaces-day__empty is-${dayState}`} role="status"><strong>{dayState === "loading" ? "Sincronizando seu dia…" : dayState === "error" ? "Agenda indisponível agora" : "Nenhum compromisso hoje"}</strong><small>{dayState === "error" ? "Abra a Agenda para consultar as fontes conectadas." : "Atendimentos, compromissos e rotinas aparecerão aqui."}</small><ActionLink action={{ to: "/agenda", label: "Abrir agenda completa", icon: "agenda" }} /></div>}
          <StellarRouteMiniMap
            target={travelTarget}
            route={bestRoute}
            minutes={travelMinutes}
            busy={travelBusy}
            onOpen={() => {
              if (bestRoute) setTravelOpen(true);
              else void startTravel();
            }}
          />
        </>}
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
      <p className="spaces-motto">{mode === "scientific" ? <>O conhecimento <strong>se conecta.</strong> {nomeComTratamento(usuario, true)} <strong>conduz a jornada.</strong></> : <>O ambiente <strong>muda.</strong> O Médico <strong>continua no centro.</strong></>}</p>

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
          <div className="spaces-personalizer__count">
            <span>{activeDraftIds.length}/{activePersonalizerDefinition.capacity} selecionadas · ordem de exibição</span>
            <button type="button" onClick={restoreShelfDefaults}>Restaurar esta prateleira</button>
          </div>
          <div className="spaces-personalizer__selected" aria-label="Funções selecionadas em ordem">
            {activeDraftIds.map((actionId, index) => {
              const action = HOME_ACTIONS_BY_ID.get(actionId);
              if (!action) return null;
              return <article key={`ordered-${actionId}`}>
                <Icone nome={action.icon} />
                <span><b>{index + 1}</b>{action.label}</span>
                <div>
                  <button type="button" onClick={() => moveShelfAction(actionId, -1)} disabled={index === 0} aria-label={`Mover ${action.label} para antes`}>↑</button>
                  <button type="button" onClick={() => moveShelfAction(actionId, 1)} disabled={index === activeDraftIds.length - 1} aria-label={`Mover ${action.label} para depois`}>↓</button>
                </div>
              </article>;
            })}
          </div>
          <div className="spaces-personalizer__grid">{candidateActions.map((action) => {
            const actionId = homeActionId(action);
            const checked = activeDraftIds.includes(actionId);
            return <button type="button" key={`pick-${actionId}`} className={checked ? "is-selected" : ""} onClick={() => toggleShelfAction(actionId)} disabled={!checked && activeDraftIds.length >= activePersonalizerDefinition.capacity} aria-pressed={checked}><Icone nome={action.icon} /><span>{action.label}</span><i><Icone nome={checked ? "check" : "adicionar"} /></i></button>;
          })}</div>
          <footer><button type="button" className="is-secondary" onClick={cancelShelfPersonalizer}>Cancelar</button><button type="button" onClick={saveShelfPreferences}>Salvar personalização</button></footer>
        </aside>
      </div>}

      {travelOpen && <div className="spaces-overlay spaces-travel-overlay" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setTravelOpen(false); }}>
        <section ref={travelRef} className="spaces-travel" role="dialog" aria-modal="true" aria-label="Mapa do deslocamento entre espaços">
          <header>
            <div>
              <p>DESLOCAMENTO CORVIA</p>
              <h2>Mapa do deslocamento</h2>
              <small>Visualize o destino, a rota geográfica e o trânsito real. Sua localização atual é usada somente após sua ação e exclusivamente nesta consulta.</small>
            </div>
            <button type="button" onClick={() => setTravelOpen(false)} aria-label="Fechar"><Icone nome="fechar" /></button>
          </header>

          {travelDestination ? <div className="spaces-travel__map">
            <MapaDeslocamento
              rotas={resultMatchesTarget ? mobilityResult?.routes || [] : []}
              origem={travelMapOrigin}
              destino={travelDestination}
              provider={mapConfiguration?.provider || (resultMatchesTarget ? mobilityResult?.provider : undefined)}
              updatedAt={resultMatchesTarget ? mobilityResult?.updated_at : undefined}
              googleMapsApiKey={mapConfiguration?.api_key}
            />
          </div> : <div className="spaces-orbit" aria-hidden="true">
            <span className="spaces-orbit__planet spaces-orbit__planet--origin"><i /><b>AGORA</b></span>
            <span className="spaces-orbit__path"><i /></span>
            <span className="spaces-orbit__planet spaces-orbit__planet--destination"><i /><b>DESTINO</b></span>
          </div>}

          <div className="spaces-travel__status" role="status" aria-live="polite">
            {travelBusy ? <><strong>Calculando rota…</strong><small>Consultando sua posição autorizada e o trânsito atual.</small></> : bestRoute ? <><strong>{travelMinutes} min <em>·</em> {distanceLabel(bestRoute.distance_meters)}</strong><small>{bestRoute.summary || "Rota recomendada"}{bestRoute.congestion ? ` · ${trafficLabel(bestRoute.congestion)}` : ""}{mobilityResult?.provider ? ` · ${mobilityResult.provider}` : ""}</small></> : <><strong>{travelTarget?.location?.name || travelTarget?.service_name || "Próximo destino"}</strong><small>{travelError || "Destino preparado. Calcule a rota para incluir sua origem e o trânsito atual."}</small></>}
          </div>
          {resultMatchesTarget && mobilityResult?.tips?.length ? <ul>{mobilityResult.tips.slice(0, 3).map((tip) => <li key={tip}>{tip}</li>)}</ul> : null}
          <footer>
            <button type="button" className="spaces-travel__recalculate" onClick={() => void startTravel()} disabled={travelBusy}><Icone nome="rota" /> {travelBusy ? "Calculando…" : bestRoute ? "Recalcular rota" : "Calcular rota real"}</button>
            <button type="button" className="spaces-travel__maps" onClick={openExternalMap}><Icone nome="rota" /> Abrir navegação no mapa</button>
          </footer>
        </section>
      </div>}
    </main>
  );
}

export { TOUR_KEY, INVESTOR_TOUR_SESSION_KEY };
