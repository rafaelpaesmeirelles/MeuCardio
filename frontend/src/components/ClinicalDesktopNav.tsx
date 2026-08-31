import { useEffect, useRef } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { assetUrl } from "../lib/api";
import usePrescriptionQueueBadge from "../hooks/usePrescriptionQueueBadge";
import Icone, { type NomeIcone } from "./Icone";
import { IconeHoje } from "./IdentidadeClinica";
import { heartTeamEnabled, whatsappAssistantEnabled } from "../lib/aiFeatureFlags";
import { nomeComTratamento } from "../lib/clinicalIdentity";

type NavItem = { to: string; label: string; icon: NomeIcone; adminOnly?: boolean; badge?: number; featured?: boolean };
type NavSection = { title: string; items: NavItem[] };
type SpaceKey = "consultorio" | "hospital" | "ensino" | "pesquisa" | "gestao";

const CLINICA_DECISAO: NavItem[] = [
  { to: "/doencas", label: "Guia de Doenças", icon: "doencas" },
  { to: "/medicamentos", label: "Medicamentos", icon: "medicamento" },
  { to: "/exames", label: "Exames", icon: "clinica" },
  { to: "/calculadoras", label: "Calculadoras", icon: "calculadora" },
  { to: "/emergencia", label: "Emergências", icon: "emergencia" },
  { to: "/cardiologia-intensiva", label: "Cardiologia Intensiva & UCO", icon: "clinica" },
  { to: "/checklists", label: "Checklists", icon: "check" },
  { to: "/triagem-sintomas", label: "Triagem de sintomas", icon: "triagem" },
  { to: "/interacoes", label: "Interações medicamentosas", icon: "medicamento" },
  { to: "/condicoes", label: "Condições especiais", icon: "check" },
  { to: "/fluxogramas", label: "Fluxogramas clínicos", icon: "seta" },
  { to: "/avaliacao-preoperatoria", label: "Avaliação pré-operatória", icon: "clinica" },
];

const ESTUDO_EDUCACAO: NavItem[] = [
  { to: "/evidencias", label: "Estudos & Evidências", icon: "evidencia" },
  { to: "/estudos", label: "Estudos clínicos", icon: "evidencia" },
  { to: "/documentos-cientificos-ia", label: "Documento científico IA", icon: "assistente" },
  { to: "/trilhas/timeline", label: "Timeline do conhecimento", icon: "seta" },
  { to: "/trilhas", label: "Trilhas", icon: "seta" },
  { to: "/casos-clinicos", label: "Casos clínicos", icon: "doencas" },
  { to: "/diretrizes", label: "Diretrizes & Guidelines", icon: "conhecimento" },
  { to: "/material-paciente", label: "Material para paciente", icon: "documento" },
  { to: "/biblioteca", label: "Biblioteca científica", icon: "conhecimento" },
  { to: "/galeria", label: "Atlas & Galeria", icon: "galeria" },
  { to: "/apresentacao", label: "Modo apresentação", icon: "documento" },
  { to: "/exportar", label: "Exportar conteúdo", icon: "documento" },
];

const TRABALHO_ASSISTENCIA: NavItem[] = [
  { to: "/exames-ia", label: "IA para Exames", icon: "ecg", featured: true },
  ...(heartTeamEnabled() ? [{ to: "/heart-team", label: "Heart Team Virtual", icon: "assistente" as NomeIcone, featured: true }] : []),
  ...(whatsappAssistantEnabled() ? [{ to: "/whatsapp-assistant", label: "Assistente pelo WhatsApp", icon: "comunicacao" as NomeIcone, featured: true }] : []),
  { to: "/prontuario", label: "Prontuário", icon: "pacientes" },
  { to: "/round", label: "Round hospitalar", icon: "pacientes" },
  { to: "/receituario", label: "Prescrição", icon: "prescricao" },
  { to: "/documentos", label: "Documentos & Solicitações", icon: "documento" },
  { to: "/agenda", label: "Agenda", icon: "agenda" },
  { to: "/corvia-mail", label: "CorVIA Mail", icon: "mail" },
  { to: "/assistente", label: "Apoio CorVIA", icon: "assistente" },
  { to: "/telediagnostico", label: "Telediagnóstico & Consultoria", icon: "evidencia" },
];

const FERRAMENTAS_PRODUTIVIDADE: NavItem[] = [
  { to: "/busca?modo=tudo-com-tudo", label: "Tudo com Tudo", icon: "sincronizar", featured: true },
  { to: "/calculadoras", label: "Calculadoras avançadas", icon: "calculadora" },
  { to: "/indicadores", label: "Indicadores & Métricas", icon: "indicadores" },
  { to: "/favoritos", label: "Notas & Favoritos", icon: "favorito" },
  { to: "/busca", label: "Busca avançada", icon: "busca" },
];

const REDE_CONECTIVIDADE: NavItem[] = [
  { to: "/usuarios-online", label: "Rede profissional", icon: "pacientes" },
  { to: "/sincronizacao", label: "Contas conectadas", icon: "sincronizar" },
  { to: "/telediagnostico", label: "Colaboração / Consultoria", icon: "evidencia" },
];

const ADMINISTRACAO: NavItem[] = [
  { to: "/admin", label: "Painel administrativo", icon: "gestao", adminOnly: true },
  ...((heartTeamEnabled() || whatsappAssistantEnabled()) ? [{ to: "/admin/operacoes-ia", label: "Operações de IA", icon: "indicadores" as NomeIcone, adminOnly: true }] : []),
  { to: "/admin/usuarios", label: "Usuários & Permissões", icon: "pacientes", adminOnly: true },
  { to: "/fila-telediagnostico", label: "Fila de telediagnóstico", icon: "evidencia", adminOnly: true },
  { to: "/receitas-para-assinatura", label: "Receitas para assinatura", icon: "prescricao", adminOnly: true },
  { to: "/minha-conta", label: "Minha Conta", icon: "conta" },
  { to: "/privacidade", label: "Segurança & Privacidade", icon: "check" },
  { to: "/excluir-conta", label: "Excluir conta e dados", icon: "conta" },
  { to: "/termos", label: "Termos de uso", icon: "documento" },
  { to: "/tour", label: "Suporte & Ajuda", icon: "curso" },
];

const SPACE_META: Record<SpaceKey, { label: string; icon: NomeIcone; actions: NavItem[] }> = {
  consultorio: {
    label: "Consultório", icon: "conta",
    actions: [
      { to: "/agenda", label: "Agenda", icon: "agenda" },
      { to: "/receituario", label: "Prescrever", icon: "prescricao" },
      { to: "/prontuario", label: "Prontuário", icon: "pacientes" },
      { to: "/exames", label: "Exames", icon: "clinica" },
      { to: "/medicamentos", label: "Medicamentos", icon: "medicamento" },
      { to: "/calculadoras", label: "Calculadoras", icon: "calculadora" },
      { to: "/doencas", label: "Guia de Doenças", icon: "doencas" },
    ],
  },
  hospital: {
    label: "Hospital", icon: "emergencia",
    actions: [
      { to: "/round", label: "Round", icon: "pacientes" },
      ...(heartTeamEnabled() ? [{ to: "/heart-team", label: "Heart Team", icon: "assistente" as NomeIcone }] : []),
      { to: "/cardiologia-intensiva", label: "Cardio Intensiva", icon: "clinica" },
      { to: "/emergencia", label: "Emergências", icon: "emergencia" },
      { to: "/exames-ia", label: "IA para Exames", icon: "ecg" },
      { to: "/checklists", label: "Checklists", icon: "check" },
      { to: "/documentos", label: "Documentos", icon: "documento" },
      { to: "/calculadoras", label: "Calculadoras", icon: "calculadora" },
    ],
  },
  ensino: {
    label: "Ensino", icon: "curso",
    actions: [
      { to: "/trilhas", label: "Trilhas", icon: "seta" },
      { to: "/casos-clinicos", label: "Casos clínicos", icon: "doencas" },
      { to: "/apresentacao", label: "Apresentação", icon: "documento" },
      { to: "/galeria", label: "Atlas & Galeria", icon: "galeria" },
      { to: "/material-paciente", label: "Material educativo", icon: "documento" },
      { to: "/diretrizes", label: "Diretrizes", icon: "conhecimento" },
      { to: "/trilhas/timeline", label: "Timeline", icon: "relogio" },
    ],
  },
  pesquisa: {
    label: "Pesquisa", icon: "evidencia",
    actions: [
      { to: "/busca?modo=tudo-com-tudo", label: "Tudo com Tudo", icon: "sincronizar" },
      { to: "/evidencias", label: "Evidências", icon: "evidencia" },
      { to: "/estudos", label: "Estudos", icon: "documento" },
      { to: "/diretrizes", label: "Diretrizes", icon: "conhecimento" },
      { to: "/biblioteca", label: "Biblioteca", icon: "conhecimento" },
      { to: "/documentos-cientificos-ia", label: "Documento IA", icon: "assistente" },
      { to: "/exportar", label: "Exportar", icon: "documento" },
    ],
  },
  gestao: {
    label: "Gestão", icon: "gestao",
    actions: [
      { to: "/indicadores", label: "Indicadores", icon: "indicadores" },
      { to: "/corvia-mail", label: "CorVIA Mail", icon: "mail" },
      { to: "/usuarios-online", label: "Rede profissional", icon: "pacientes" },
      { to: "/sincronizacao", label: "Contas conectadas", icon: "sincronizar" },
      { to: "/minha-conta", label: "Minha conta", icon: "conta" },
      { to: "/admin", label: "Administração", icon: "gestao", adminOnly: true },
    ],
  },
};

const PATH_TO_SPACE: Array<[string, SpaceKey]> = [
  ["/documentos-cientificos-ia", "pesquisa"], ["/evidencias", "pesquisa"], ["/estudos", "pesquisa"], ["/diretrizes", "pesquisa"], ["/biblioteca", "pesquisa"], ["/busca", "pesquisa"], ["/fluxogramas", "pesquisa"], ["/exportar", "pesquisa"], ["/favoritos", "pesquisa"],
  ["/casos-clinicos", "ensino"], ["/trilhas", "ensino"], ["/material-paciente", "ensino"], ["/galeria", "ensino"], ["/apresentacao", "ensino"],
  ["/heart-team", "hospital"], ["/round", "hospital"], ["/cardiologia-intensiva", "hospital"], ["/checklists", "hospital"], ["/emergencia", "hospital"], ["/exames-ia", "hospital"], ["/ecg-ia", "hospital"],
  ["/corvia-mail", "gestao"], ["/caixa-de-email", "gestao"], ["/whatsapp-assistant", "gestao"], ["/usuarios-online", "gestao"], ["/telediagnostico", "gestao"], ["/fila-telediagnostico", "gestao"], ["/sincronizacao", "gestao"], ["/minha-conta", "gestao"], ["/verificacao-identidade", "gestao"], ["/excluir-conta", "gestao"], ["/indicadores", "gestao"], ["/receitas-para-assinatura", "gestao"], ["/admin", "gestao"], ["/privacidade", "gestao"], ["/termos", "gestao"],
];

function spaceFor(pathname: string): SpaceKey {
  return PATH_TO_SPACE.find(([prefix]) => pathname === prefix || pathname.startsWith(`${prefix}/`))?.[1] ?? "consultorio";
}

function Item({ item, compact = false }: { item: NavItem; compact?: boolean }) {
  return (
    <NavLink to={item.to} className={({ isActive }) => `ccc-nav__item${isActive ? " is-active" : ""}${item.featured ? " is-featured" : ""}${compact ? " ccc-nav__item--context" : ""}`}>
      <Icone nome={item.icon} /><span>{item.label}</span>
      {!!item.badge && <span className="cos-account-menu__badge" aria-label={`${item.badge} pendentes`}>{item.badge}</span>}
    </NavLink>
  );
}

function CatalogSection({ section, isAdmin }: { section: NavSection; isAdmin: boolean }) {
  const items = section.items.filter((item) => !item.adminOnly || isAdmin);
  if (!items.length) return null;
  return <section className="ccc-nav__catalog-section"><h3>{section.title}</h3><div>{items.map((item) => <Item key={`${section.title}-${item.label}-${item.to}`} item={item} />)}</div></section>;
}

function iniciais(nome?: string) {
  return (nome || "R").trim().split(/\s+/).slice(0, 2).map((parte) => parte[0]?.toUpperCase()).join("");
}

export default function ClinicalDesktopNav() {
  const { usuario } = useAuth();
  const { pathname } = useLocation();
  const catalogRef = useRef<HTMLDetailsElement>(null);
  const pendentesAssinatura = usePrescriptionQueueBadge(usuario?.role === "admin");
  const currentSpace = spaceFor(pathname);
  const meta = SPACE_META[currentSpace];
  const contextual = meta.actions.filter((item) => !item.adminOnly || usuario?.role === "admin");
  const administracao = ADMINISTRACAO.map((item) => item.to === "/receitas-para-assinatura" ? { ...item, badge: pendentesAssinatura } : item);
  const sections: NavSection[] = [
    { title: "Clínica & Decisão", items: CLINICA_DECISAO },
    { title: "Ciência & Ensino", items: ESTUDO_EDUCACAO },
    { title: "Trabalho & Assistência", items: TRABALHO_ASSISTENCIA },
    { title: "Produtividade", items: FERRAMENTAS_PRODUTIVIDADE },
    { title: "Rede & Conectividade", items: REDE_CONECTIVIDADE },
    { title: "Administração & Conta", items: administracao },
  ];

  useEffect(() => {
    if (catalogRef.current) catalogRef.current.open = false;
  }, [pathname]);

  return (
    <aside className={`ccc-nav ccc-nav--reference ccc-nav--space-${currentSpace}`} aria-label={`Ferramentas do espaço ${meta.label}`}>
      <NavLink to="/" className="ccc-nav__brand" aria-label="CorVIA — Início">
        <span className="ccc-nav__brand-mark"><img src="/corvia-mark-canonical.svg" alt="" /></span>
        <span className="ccc-nav__brand-copy"><strong>Cor<span className="corvia-via">VIA</span></strong><small>Cardiology Spaces</small></span>
      </NavLink>

      <div className="ccc-nav__space-head"><span><Icone nome={meta.icon} /></span><div><small>NO ESPAÇO</small><strong>{meta.label}</strong></div></div>

      <nav className="ccc-nav__scroll ccc-nav__scroll--context">
        <NavLink to="/" end className={({ isActive }) => `ccc-nav__item ccc-nav__home${isActive ? " is-active" : ""}`}><IconeHoje /><span>Página inicial</span></NavLink>
        <div className="ccc-nav__context-actions">{contextual.map((item) => <Item compact key={`${currentSpace}-${item.to}`} item={item} />)}</div>

        <details ref={catalogRef} className="ccc-nav__catalog">
          <summary><Icone nome="mais" /><span>Todas as funções</span><Icone nome="chevron" /></summary>
          <div className="ccc-nav__catalog-panel" role="dialog" aria-label="Todas as funções do CorVIA">
            <header><div><small>CATÁLOGO COMPLETO</small><strong>Todas as funções</strong><span>O espaço muda; todas as ferramentas continuam acessíveis.</span></div></header>
            <div className="ccc-nav__catalog-grid">{sections.map((section) => <CatalogSection key={section.title} section={section} isAdmin={usuario?.role === "admin"} />)}</div>
          </div>
        </details>
      </nav>

      <NavLink to="/minha-conta" className="ccc-nav__footer ccc-nav__plan" aria-label="Abrir perfil e conta">
        {usuario?.photo_url ? <img className="ccc-nav__plan-photo" src={assetUrl(usuario.photo_url)} alt="" /> : <span className="ccc-nav__plan-avatar">{iniciais(usuario?.full_name)}</span>}
        <span className="ccc-nav__plan-copy"><strong>{usuario ? nomeComTratamento(usuario) : "Minha conta"}</strong><small>{usuario?.role === "admin" ? "Administrador" : "Profissional"}</small></span>
      </NavLink>
    </aside>
  );
}
