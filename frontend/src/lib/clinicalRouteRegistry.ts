import type { NomeIcone } from "../components/Icone";
import { matchPath } from "react-router-dom";
import { heartTeamEnabled, whatsappAssistantEnabled } from "./aiFeatureFlags";

export type FunctionalSpace = "consultorio" | "hospital" | "ensino" | "pesquisa" | "gestao";
export type RouteSpace = FunctionalSpace | "home";
export type RouteGroup =
  | "documentos"
  | "pacientes"
  | "prescricao"
  | "agenda"
  | "mail"
  | "assistente"
  | "integracoes"
  | "conhecimento"
  | "ferramentas"
  | "emergencia"
  | "rede"
  | "telediagnostico"
  | "conta"
  | "admin"
  | "geral";
export type RouteLayout = "standard" | "reading" | "data" | "focus";
export type RouteKind = "page" | "detail" | "alias" | "immersive";
export type RouteGate = "admin" | "heart-team" | "whatsapp" | "admin-ai" | "no-product-access";

export type ClinicalRouteDefinition = {
  path: string;
  name: string;
  shortName?: string;
  space: RouteSpace;
  group: RouteGroup;
  icon: NomeIcone;
  layout: RouteLayout;
  intelligence: boolean;
  kind?: RouteKind;
  gate?: RouteGate;
  parent?: string;
  redirectTo?: string;
  catalog?: boolean;
  featured?: boolean;
};

export type ClinicalSpaceDefinition = {
  id: FunctionalSpace;
  label: string;
  eyebrow: string;
  description: string;
  icon: NomeIcone;
  accent: string;
  accentRgb: string;
  roomImage: string;
};

export const CLINICAL_SPACES: Record<FunctionalSpace, ClinicalSpaceDefinition> = {
  consultorio: {
    id: "consultorio",
    label: "Consultório",
    eyebrow: "Prática clínica",
    description: "Consulta, decisão, prescrição e continuidade do cuidado.",
    icon: "conta",
    accent: "#2bd8e1",
    accentRgb: "43, 216, 225",
    roomImage: "/spaces/corvia-room-consultorio-1280.webp",
  },
  hospital: {
    id: "hospital",
    label: "Hospital",
    eyebrow: "Cuidado agudo",
    description: "Round, terapia intensiva, emergência e segurança assistencial.",
    icon: "emergencia",
    accent: "#4b82ff",
    accentRgb: "75, 130, 255",
    roomImage: "/spaces/corvia-room-hospital-1280.webp",
  },
  ensino: {
    id: "ensino",
    label: "Ensino",
    eyebrow: "Aprendizagem contínua",
    description: "Trilhas, casos, apresentações e formação cardiológica.",
    icon: "curso",
    accent: "#a06df2",
    accentRgb: "160, 109, 242",
    roomImage: "/spaces/corvia-room-ensino-1280.webp",
  },
  pesquisa: {
    id: "pesquisa",
    label: "Pesquisa",
    eyebrow: "Ciência & evidência",
    description: "Estudos, diretrizes, evidências e produção científica.",
    icon: "evidencia",
    accent: "#f04f8b",
    accentRgb: "240, 79, 139",
    roomImage: "/spaces/corvia-room-pesquisa-1280.webp",
  },
  gestao: {
    id: "gestao",
    label: "Gestão",
    eyebrow: "Operação integrada",
    description: "Indicadores, comunicação, integrações, conta e administração.",
    icon: "gestao",
    accent: "#37c7c0",
    accentRgb: "55, 199, 192",
    roomImage: "/spaces/corvia-room-gestao-1280.webp",
  },
};

function route(definition: ClinicalRouteDefinition): ClinicalRouteDefinition {
  return Object.freeze({ kind: "page", catalog: false, ...definition });
}

/**
 * Fonte única para os 75 padrões autenticados declarados em App.tsx.
 *
 * O roteador continua responsável por lazy loading e gates de renderização.
 * Esta tabela governa identidade, navegação, layout e descoberta. Detalhes,
 * aliases e experiências imersivas permanecem registrados para impedir que
 * uma rota existente desapareça silenciosamente de uma das superfícies.
 */
export const CLINICAL_ROUTES = [
  route({ path: "/", name: "Home Cardiology Spaces", shortName: "Início", space: "home", group: "geral", icon: "hoje", layout: "focus", intelligence: false }),

  // Consultório
  route({ path: "/doencas", name: "Guia de Doenças", space: "consultorio", group: "conhecimento", icon: "doencas", layout: "data", intelligence: true, catalog: true }),
  route({ path: "/doencas/:slug", name: "Doença", space: "consultorio", group: "conhecimento", icon: "doencas", layout: "reading", intelligence: true, kind: "detail", parent: "/doencas" }),
  route({ path: "/triagem-sintomas", name: "Triagem de sintomas", shortName: "Triagem", space: "consultorio", group: "ferramentas", icon: "triagem", layout: "focus", intelligence: false, catalog: true }),
  route({ path: "/calculadoras", name: "Calculadoras", space: "consultorio", group: "ferramentas", icon: "calculadora", layout: "data", intelligence: true, catalog: true }),
  route({ path: "/calculadoras/:slug", name: "Calculadora", space: "consultorio", group: "ferramentas", icon: "calculadora", layout: "focus", intelligence: false, kind: "detail", parent: "/calculadoras" }),
  route({ path: "/medicamentos", name: "Medicamentos", space: "consultorio", group: "conhecimento", icon: "medicamento", layout: "data", intelligence: true, catalog: true }),
  route({ path: "/interacoes", name: "Interações medicamentosas", shortName: "Interações", space: "consultorio", group: "conhecimento", icon: "medicamento", layout: "focus", intelligence: false, catalog: true }),
  route({ path: "/condicoes", name: "Condições especiais", space: "consultorio", group: "ferramentas", icon: "check", layout: "standard", intelligence: true, catalog: true }),
  route({ path: "/exames", name: "Exames", space: "consultorio", group: "conhecimento", icon: "clinica", layout: "data", intelligence: true, catalog: true }),
  route({ path: "/exames/:slug", name: "Exame", space: "consultorio", group: "conhecimento", icon: "clinica", layout: "reading", intelligence: true, kind: "detail", parent: "/exames" }),
  route({ path: "/assistente", name: "Apoio CorVIA", shortName: "Apoio", space: "consultorio", group: "assistente", icon: "assistente", layout: "focus", intelligence: false, catalog: true, featured: true }),
  route({ path: "/prontuario", name: "Prontuário", space: "consultorio", group: "pacientes", icon: "pacientes", layout: "focus", intelligence: false, catalog: true }),
  route({ path: "/agenda", name: "Agenda", space: "consultorio", group: "agenda", icon: "agenda", layout: "focus", intelligence: false, catalog: true }),
  route({ path: "/documentos", name: "Documentos & Solicitações", shortName: "Documentos", space: "consultorio", group: "documentos", icon: "documento", layout: "focus", intelligence: false, catalog: true }),
  route({ path: "/avaliacao-preoperatoria", name: "Avaliação pré-operatória", shortName: "Pré-operatório", space: "consultorio", group: "documentos", icon: "clinica", layout: "focus", intelligence: false, catalog: true }),
  route({ path: "/receituario", name: "Prescrição", space: "consultorio", group: "prescricao", icon: "prescricao", layout: "focus", intelligence: false, catalog: true }),

  // Hospital
  route({ path: "/cardiologia-intensiva", name: "Cardiologia Intensiva & UCO", shortName: "Cardio Intensiva", space: "hospital", group: "ferramentas", icon: "emergencia", layout: "data", intelligence: false, catalog: true }),
  route({ path: "/emergencia", name: "Emergência cardiovascular", shortName: "Emergência", space: "hospital", group: "emergencia", icon: "emergencia", layout: "focus", intelligence: false, catalog: true, featured: true }),
  route({ path: "/checklists", name: "Checklists", space: "hospital", group: "ferramentas", icon: "check", layout: "data", intelligence: true, catalog: true }),
  route({ path: "/checklists/alta/:id", name: "Checklist de alta aplicado", shortName: "Checklist de alta", space: "hospital", group: "ferramentas", icon: "check", layout: "focus", intelligence: false, kind: "detail", parent: "/checklists" }),
  route({ path: "/checklists/:slug", name: "Modelo de checklist", shortName: "Checklist", space: "hospital", group: "ferramentas", icon: "check", layout: "reading", intelligence: true, kind: "detail", parent: "/checklists" }),
  route({ path: "/heart-team", name: "Heart Team Virtual", shortName: "Heart Team", space: "hospital", group: "assistente", icon: "round", layout: "focus", intelligence: false, gate: "heart-team", catalog: true, featured: true }),
  route({ path: "/heart-team/:caseId", name: "Caso do Heart Team", shortName: "Caso Heart Team", space: "hospital", group: "assistente", icon: "round", layout: "focus", intelligence: false, kind: "detail", parent: "/heart-team", gate: "heart-team" }),
  route({ path: "/exames-ia", name: "IA para Exames", space: "hospital", group: "ferramentas", icon: "ecg", layout: "focus", intelligence: false, catalog: true, featured: true }),
  route({ path: "/ecg-ia", name: "ECG IA", space: "hospital", group: "ferramentas", icon: "ecg", layout: "focus", intelligence: false, kind: "alias", parent: "/exames-ia" }),
  route({ path: "/round", name: "Round hospitalar", shortName: "Round", space: "hospital", group: "pacientes", icon: "round", layout: "focus", intelligence: false, catalog: true }),

  // Ensino
  route({ path: "/apresentacao", name: "Modo Apresentação", shortName: "Apresentação", space: "ensino", group: "ferramentas", icon: "documento", layout: "focus", intelligence: false, catalog: true }),
  route({ path: "/trilhas", name: "Trilhas", space: "ensino", group: "conhecimento", icon: "seta", layout: "data", intelligence: true, catalog: true }),
  route({ path: "/trilhas/timeline", name: "Timeline do conhecimento", shortName: "Timeline", space: "ensino", group: "conhecimento", icon: "relogio", layout: "reading", intelligence: true, catalog: true, parent: "/trilhas" }),
  route({ path: "/trilhas/:slug", name: "Trilha", space: "ensino", group: "conhecimento", icon: "seta", layout: "reading", intelligence: true, kind: "detail", parent: "/trilhas" }),
  route({ path: "/material-paciente", name: "Material para paciente", shortName: "Material educativo", space: "ensino", group: "ferramentas", icon: "documento", layout: "data", intelligence: true, catalog: true }),
  route({ path: "/material-paciente/:slug", name: "Material para paciente", space: "ensino", group: "ferramentas", icon: "documento", layout: "reading", intelligence: true, kind: "detail", parent: "/material-paciente" }),
  route({ path: "/galeria", name: "Atlas & Galeria", shortName: "Atlas", space: "ensino", group: "ferramentas", icon: "galeria", layout: "data", intelligence: true, catalog: true }),
  route({ path: "/galeria/:slug", name: "Achado de imagem", shortName: "Imagem", space: "ensino", group: "ferramentas", icon: "galeria", layout: "reading", intelligence: true, kind: "detail", parent: "/galeria" }),
  route({ path: "/casos-clinicos", name: "Casos clínicos", shortName: "Casos", space: "ensino", group: "conhecimento", icon: "doencas", layout: "data", intelligence: true, catalog: true }),
  route({ path: "/casos-clinicos/:slug", name: "Caso clínico", space: "ensino", group: "conhecimento", icon: "doencas", layout: "focus", intelligence: false, kind: "detail", parent: "/casos-clinicos" }),

  // Pesquisa
  route({ path: "/biblioteca", name: "Biblioteca científica", shortName: "Biblioteca", space: "pesquisa", group: "conhecimento", icon: "conhecimento", layout: "data", intelligence: true, catalog: true }),
  route({ path: "/biblioteca/:slug", name: "Documento científico", shortName: "Documento", space: "pesquisa", group: "conhecimento", icon: "conhecimento", layout: "reading", intelligence: true, kind: "detail", parent: "/biblioteca" }),
  route({ path: "/documentos-cientificos-ia", name: "Documento científico IA", shortName: "Documento IA", space: "pesquisa", group: "conhecimento", icon: "assistente", layout: "focus", intelligence: false, catalog: true, featured: true }),
  route({ path: "/diretrizes", name: "Diretrizes & Guidelines", shortName: "Diretrizes", space: "pesquisa", group: "conhecimento", icon: "conhecimento", layout: "data", intelligence: true, catalog: true }),
  route({ path: "/busca", name: "Tudo com Tudo / Busca avançada", shortName: "Tudo com Tudo", space: "pesquisa", group: "ferramentas", icon: "busca", layout: "data", intelligence: false, catalog: true, featured: true }),
  route({ path: "/fluxogramas", name: "Fluxogramas clínicos", shortName: "Fluxogramas", space: "pesquisa", group: "ferramentas", icon: "seta", layout: "reading", intelligence: true, catalog: true }),
  route({ path: "/evidencias", name: "Evidências", space: "pesquisa", group: "conhecimento", icon: "evidencia", layout: "data", intelligence: true, catalog: true }),
  route({ path: "/evidencias/:slug", name: "Evidência", space: "pesquisa", group: "conhecimento", icon: "evidencia", layout: "reading", intelligence: true, kind: "detail", parent: "/evidencias" }),
  route({ path: "/estudos", name: "Estudos clínicos", shortName: "Estudos", space: "pesquisa", group: "conhecimento", icon: "evidencia", layout: "data", intelligence: true, catalog: true }),
  route({ path: "/estudos/:slug", name: "Estudo clínico", shortName: "Estudo", space: "pesquisa", group: "conhecimento", icon: "evidencia", layout: "reading", intelligence: true, kind: "detail", parent: "/estudos" }),
  route({ path: "/exportar", name: "Exportar conteúdo", shortName: "Exportar", space: "pesquisa", group: "ferramentas", icon: "documento", layout: "focus", intelligence: false, catalog: true }),
  route({ path: "/favoritos", name: "Notas & Favoritos", shortName: "Favoritos", space: "pesquisa", group: "conhecimento", icon: "favorito", layout: "data", intelligence: true, catalog: true }),

  // Gestão
  route({ path: "/indicadores", name: "Indicadores & Métricas", shortName: "Indicadores", space: "gestao", group: "conta", icon: "indicadores", layout: "data", intelligence: false, catalog: true }),
  route({ path: "/whatsapp-assistant", name: "Assistente pelo WhatsApp", shortName: "WhatsApp", space: "gestao", group: "integracoes", icon: "comunicacao", layout: "focus", intelligence: false, gate: "whatsapp", catalog: true, featured: true }),
  route({ path: "/minha-conta", name: "Minha conta", space: "gestao", group: "conta", icon: "conta", layout: "standard", intelligence: false, catalog: true }),
  route({ path: "/sincronizacao", name: "Contas conectadas", shortName: "Integrações", space: "gestao", group: "integracoes", icon: "sincronizar", layout: "data", intelligence: false, catalog: true }),
  route({ path: "/verificacao-identidade", name: "Verificação de identidade", shortName: "Identidade", space: "gestao", group: "conta", icon: "check", layout: "focus", intelligence: false, parent: "/minha-conta" }),
  route({ path: "/telediagnostico", name: "Telediagnóstico & Consultoria", shortName: "Telediagnóstico", space: "gestao", group: "telediagnostico", icon: "evidencia", layout: "data", intelligence: false, catalog: true }),
  route({ path: "/caixa-de-email", name: "Caixa de e-mail", shortName: "Caixa de e-mail", space: "gestao", group: "mail", icon: "mail", layout: "focus", intelligence: false, parent: "/corvia-mail" }),
  route({ path: "/corvia-mail", name: "CorVIA Mail", space: "gestao", group: "mail", icon: "mail", layout: "focus", intelligence: false, catalog: true }),
  route({ path: "/usuarios-online", name: "Rede profissional", shortName: "Rede", space: "gestao", group: "rede", icon: "pacientes", layout: "data", intelligence: false, catalog: true }),
  route({ path: "/privacidade", name: "Segurança & Privacidade", shortName: "Privacidade", space: "gestao", group: "geral", icon: "check", layout: "reading", intelligence: false, catalog: true }),
  route({ path: "/excluir-conta", name: "Excluir conta e dados", shortName: "Excluir conta", space: "gestao", group: "conta", icon: "conta", layout: "standard", intelligence: false, catalog: true }),
  route({ path: "/termos", name: "Termos de uso", shortName: "Termos", space: "gestao", group: "geral", icon: "documento", layout: "reading", intelligence: false, catalog: true }),

  // Administração
  route({ path: "/admin", name: "Painel administrativo", shortName: "Administração", space: "gestao", group: "admin", icon: "gestao", layout: "data", intelligence: false, gate: "admin", catalog: true }),
  route({ path: "/admin/usuarios", name: "Usuários & Permissões", shortName: "Usuários", space: "gestao", group: "admin", icon: "pacientes", layout: "data", intelligence: false, gate: "admin", catalog: true }),
  route({ path: "/admin/usuarios/:id/gerenciar", name: "Gerenciar conta", space: "gestao", group: "admin", icon: "configuracao", layout: "standard", intelligence: false, kind: "detail", parent: "/admin/usuarios", gate: "admin" }),
  route({ path: "/admin/usuarios/:id", name: "Ficha do usuário", shortName: "Ficha", space: "gestao", group: "admin", icon: "pacientes", layout: "data", intelligence: false, kind: "detail", parent: "/admin/usuarios", gate: "admin" }),
  route({ path: "/fila-telediagnostico", name: "Fila de telediagnóstico", shortName: "Fila de tele", space: "gestao", group: "telediagnostico", icon: "evidencia", layout: "data", intelligence: false, gate: "admin", catalog: true }),
  route({ path: "/receitas-para-assinatura", name: "Receitas para assinatura", shortName: "Receitas pendentes", space: "gestao", group: "admin", icon: "prescricao", layout: "focus", intelligence: false, gate: "admin", catalog: true }),
  route({ path: "/admin/operacoes-ia", name: "Operações de IA", shortName: "Operações IA", space: "gestao", group: "admin", icon: "indicadores", layout: "data", intelligence: false, gate: "admin-ai", catalog: true }),

  // Aliases preservados
  route({ path: "/cursos", name: "Cursos — alias de Trilhas", shortName: "Trilhas", space: "ensino", group: "conhecimento", icon: "curso", layout: "data", intelligence: true, kind: "alias", parent: "/trilhas", redirectTo: "/trilhas" }),
  route({ path: "/cursos/:slug", name: "Curso — alias de Trilhas", shortName: "Trilha", space: "ensino", group: "conhecimento", icon: "curso", layout: "data", intelligence: true, kind: "alias", parent: "/trilhas", redirectTo: "/trilhas" }),
  route({ path: "/assinatura", name: "Assinatura — alias do Tour", shortName: "Assinatura", space: "gestao", group: "conta", icon: "check", layout: "focus", intelligence: false, kind: "alias", parent: "/tour", redirectTo: "/tour?origem=assinatura&modo=quick" }),
  route({ path: "/admin/usuarios-online", name: "Usuários online — alias", shortName: "Rede", space: "gestao", group: "admin", icon: "pacientes", layout: "data", intelligence: false, kind: "alias", parent: "/usuarios-online", gate: "admin", redirectTo: "/usuarios-online" }),

  // Experiências autenticadas fora do shell
  route({ path: "/tour", name: "Tour CorVIA", shortName: "Tour", space: "home", group: "geral", icon: "curso", layout: "focus", intelligence: false, kind: "immersive" }),
  route({ path: "/tour/cardiology-spaces", name: "Onboarding Cardiology Spaces", shortName: "Onboarding", space: "home", group: "geral", icon: "hoje", layout: "focus", intelligence: false, kind: "immersive", parent: "/tour" }),
  route({ path: "/em-breve", name: "Em breve", space: "home", group: "geral", icon: "relogio", layout: "focus", intelligence: false, kind: "immersive", gate: "no-product-access" }),
] as const satisfies readonly ClinicalRouteDefinition[];

export type ClinicalRoute = (typeof CLINICAL_ROUTES)[number];

function specificity(routeDefinition: ClinicalRouteDefinition) {
  return routeDefinition.path.split("/").filter(Boolean).reduce((score, segment) => score + (segment.startsWith(":") ? 1 : 4), 0);
}

const ROUTES_BY_SPECIFICITY = [...CLINICAL_ROUTES].sort((a, b) => specificity(b) - specificity(a));

export function matchesClinicalRoute(pathname: string, definition: ClinicalRouteDefinition) {
  return Boolean(matchPath({ path: definition.path, caseSensitive: false, end: true }, pathname));
}

export function findClinicalRoute(pathname: string) {
  return ROUTES_BY_SPECIFICITY.find((definition) => matchesClinicalRoute(pathname, definition));
}

export function resolveClinicalRoute(pathname: string): ClinicalRouteDefinition {
  return findClinicalRoute(pathname) ?? {
    path: pathname,
    name: "CorVIA",
    space: "consultorio",
    group: "geral",
    icon: "clinica",
    layout: "standard",
    intelligence: false,
    kind: "page",
    catalog: false,
  };
}

/** Visibilidade de navegação; autorização real permanece no roteador e backend. */
export function routeAvailable(definition: ClinicalRouteDefinition, isAdmin: boolean) {
  if (definition.gate === "admin") return isAdmin;
  if (definition.gate === "admin-ai") return isAdmin && (heartTeamEnabled() || whatsappAssistantEnabled());
  if (definition.gate === "heart-team") return heartTeamEnabled();
  if (definition.gate === "whatsapp") return whatsappAssistantEnabled();
  return definition.gate !== "no-product-access";
}

export function catalogRoutesFor(space: FunctionalSpace, isAdmin: boolean) {
  return CLINICAL_ROUTES.filter((definition) => definition.catalog && definition.space === space && routeAvailable(definition, isAdmin));
}

export const SPACE_QUICK_ROUTES: Record<FunctionalSpace, readonly string[]> = {
  consultorio: ["/agenda", "/receituario", "/prontuario", "/exames", "/medicamentos", "/calculadoras", "/doencas"],
  hospital: ["/round", "/cardiologia-intensiva", "/emergencia", "/exames-ia", "/checklists", "/documentos", "/calculadoras", "/heart-team"],
  ensino: ["/trilhas", "/casos-clinicos", "/apresentacao", "/galeria", "/material-paciente", "/diretrizes", "/trilhas/timeline"],
  pesquisa: ["/busca", "/evidencias", "/estudos", "/diretrizes", "/biblioteca", "/documentos-cientificos-ia", "/exportar"],
  gestao: ["/indicadores", "/corvia-mail", "/usuarios-online", "/sincronizacao", "/minha-conta", "/admin"],
};

export function quickRoutesFor(space: FunctionalSpace, isAdmin: boolean) {
  return SPACE_QUICK_ROUTES[space]
    .map((path) => CLINICAL_ROUTES.find((definition) => definition.path === path))
    .filter((definition): definition is ClinicalRoute => Boolean(definition && routeAvailable(definition, isAdmin)));
}

export function parentRouteFor(definition: ClinicalRouteDefinition) {
  return definition.parent ? CLINICAL_ROUTES.find((candidate) => candidate.path === definition.parent) : undefined;
}
