import { NavLink } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { assetUrl } from "../lib/api";
import usePrescriptionQueueBadge from "../hooks/usePrescriptionQueueBadge";
import Icone, { type NomeIcone } from "./Icone";
import { IconeHoje } from "./IdentidadeClinica";

type NavItem = { to: string; label: string; icon: NomeIcone; adminOnly?: boolean; badge?: number; featured?: boolean };
type NavSection = { title: string; items: NavItem[] };

const CLINICA_DECISAO: NavItem[] = [
  { to: "/doencas", label: "Condições", icon: "doencas" },
  { to: "/medicamentos", label: "Medicamentos", icon: "medicamento" },
  { to: "/exames", label: "Exames", icon: "clinica" },
  { to: "/calculadoras", label: "Calculadoras", icon: "calculadora" },
  { to: "/emergencia", label: "Emergências", icon: "emergencia" },
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
  { to: "/trilhas/timeline", label: "Timeline do conhecimento", icon: "seta" },
  { to: "/trilhas", label: "Trilhas", icon: "seta" },
  { to: "/casos-clinicos", label: "Casos clínicos", icon: "doencas" },
  { to: "/diretrizes", label: "Diretrizes & Guidelines", icon: "conhecimento" },
  { to: "/material-paciente", label: "Material para paciente", icon: "documento" },
  { to: "/cursos", label: "Cursos & Atualizações", icon: "curso" },
  { to: "/biblioteca", label: "Biblioteca científica", icon: "conhecimento" },
  { to: "/galeria", label: "Atlas & Galeria", icon: "galeria" },
];

const TRABALHO_ASSISTENCIA: NavItem[] = [
  { to: "/exames-ia", label: "IA para Exames", icon: "ecg", featured: true },
  { to: "/prontuario", label: "Prontuário", icon: "pacientes" },
  { to: "/round", label: "Round hospitalar", icon: "pacientes" },
  { to: "/receituario", label: "Prescrição", icon: "prescricao" },
  { to: "/documentos", label: "Documentos & Solicitações", icon: "documento" },
  { to: "/agenda", label: "Agenda", icon: "agenda" },
  { to: "/corvia-mail", label: "CorVIA Mail", icon: "mail" },
  { to: "/assistente", label: "Assistente Clínica", icon: "assistente" },
  { to: "/telediagnostico", label: "Telediagnóstico & Consultoria", icon: "evidencia" },
];

const FERRAMENTAS_PRODUTIVIDADE: NavItem[] = [
  { to: "/calculadoras", label: "Calculadoras avançadas", icon: "calculadora" },
  { to: "/indicadores", label: "Indicadores & Métricas", icon: "indicadores" },
  { to: "/apresentacao", label: "Modo apresentação", icon: "documento" },
  { to: "/exportar", label: "Exportar conteúdo (PDF)", icon: "documento" },
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
  { to: "/admin/usuarios", label: "Usuários & Permissões", icon: "pacientes", adminOnly: true },
  { to: "/fila-telediagnostico", label: "Fila de telediagnóstico", icon: "evidencia", adminOnly: true },
  { to: "/receitas-para-assinatura", label: "Receitas para assinatura", icon: "prescricao", adminOnly: true },
  { to: "/minha-conta", label: "Configurações / Minha Conta", icon: "conta" },
  { to: "/privacidade", label: "Segurança & Privacidade", icon: "check" },
  { to: "/tour?origem=assinatura&modo=quick", label: "Tour CorVIA", icon: "check" },
  { to: "/termos", label: "Termos de uso", icon: "documento" },
  { to: "/tour", label: "Suporte & Ajuda", icon: "curso" },
];

function Item({ item }: { item: NavItem }) {
  return (
    <NavLink to={item.to} className={({ isActive }) => `ccc-nav__item${isActive ? " is-active" : ""}${item.featured ? " is-featured" : ""}`}>
      <Icone nome={item.icon} /><span>{item.label}</span>
      {item.featured && <span className="ccc-nav__featured">Destaque</span>}
      {!!item.badge && <span className="cos-account-menu__badge" aria-label={`${item.badge} pendentes`}>{item.badge}</span>}
    </NavLink>
  );
}

function Section({ section, isAdmin }: { section: NavSection; isAdmin: boolean }) {
  const items = section.items.filter((item) => !item.adminOnly || isAdmin);
  if (!items.length) return null;
  return <div className="ccc-nav__section"><p>{section.title}</p>{items.map((item) => <Item key={`${section.title}-${item.label}-${item.to}`} item={item} />)}</div>;
}

function iniciais(nome?: string) {
  return (nome || "R").trim().split(/\s+/).slice(0, 2).map((parte) => parte[0]?.toUpperCase()).join("");
}

export default function ClinicalDesktopNav() {
  const { usuario } = useAuth();
  const pendentesAssinatura = usePrescriptionQueueBadge(usuario?.role === "admin");

  const administracao=ADMINISTRACAO
    .filter(item=>item.to!=="/receitas-para-assinatura"||pendentesAssinatura!==undefined)
    .map(item=>item.to==="/receitas-para-assinatura"?{...item,badge:pendentesAssinatura}:item);

  const sections: NavSection[] = [
    { title: "Clínica & Decisão", items: CLINICA_DECISAO },
    { title: "Estudos & Educação", items: ESTUDO_EDUCACAO },
    { title: "Trabalho & Assistência", items: TRABALHO_ASSISTENCIA },
    { title: "Ferramentas & Produtividade", items: FERRAMENTAS_PRODUTIVIDADE },
    { title: "Rede & Conectividade", items: REDE_CONECTIVIDADE },
    { title: "Administração", items: administracao },
  ];

  return (
    <aside className="ccc-nav ccc-nav--reference" aria-label="Navegação principal do CorVIA">
      <NavLink to="/" className="ccc-nav__brand" aria-label="CorVIA — Início">
        <span className="ccc-nav__brand-mark"><img src="/corvia-mark-canonical.svg" alt="" /></span>
        <span className="ccc-nav__brand-copy"><strong>CorVIA</strong><small>Clinical OS</small></span>
      </NavLink>
      <nav className="ccc-nav__scroll">
        <NavLink to="/" end className={({ isActive }) => `ccc-nav__item ccc-nav__home${isActive ? " is-active" : ""}`}><IconeHoje /><span>Página inicial</span></NavLink>
        {sections.map((section) => <Section key={section.title} section={section} isAdmin={usuario?.role === "admin"} />)}
      </nav>
      <NavLink to="/minha-conta" className="ccc-nav__footer ccc-nav__plan" aria-label="Abrir perfil e conta">
        {usuario?.photo_url ? <img className="ccc-nav__plan-photo" src={assetUrl(usuario.photo_url)} alt="" /> : <span className="ccc-nav__plan-avatar">{iniciais(usuario?.full_name)}</span>}
        <span className="ccc-nav__plan-copy"><strong>{usuario?.full_name || "Minha conta"}</strong><small>{usuario?.role === "admin" ? "Administrador · Premium" : "Plano Premium"}</small></span>
      </NavLink>
    </aside>
  );
}
