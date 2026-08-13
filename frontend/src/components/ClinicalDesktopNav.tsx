import { NavLink } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { assetUrl } from "../lib/api";
import Icone, { type NomeIcone } from "./Icone";
import { IconeHoje } from "./IdentidadeClinica";

type NavItem = { to: string; label: string; icon: NomeIcone };

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

const ESTUDO_APRENDIZAGEM: NavItem[] = [
  { to: "/evidencias", label: "Evidências", icon: "evidencia" },
  { to: "/estudos", label: "Estudos", icon: "evidencia" },
  { to: "/diretrizes", label: "Guidelines", icon: "conhecimento" },
  { to: "/timeline", label: "Timeline", icon: "seta" },
  { to: "/trilhas", label: "Trilhas", icon: "seta" },
  { to: "/casos-clinicos", label: "Casos clínicos", icon: "doencas" },
  { to: "/biblioteca", label: "Biblioteca científica", icon: "conhecimento" },
  { to: "/galeria", label: "Galeria", icon: "galeria" },
  { to: "/cursos", label: "Cursos", icon: "curso" },
  { to: "/apresentacao", label: "Modo apresentação", icon: "documento" },
];

const TRABALHO_ASSISTENCIA: NavItem[] = [
  { to: "/round", label: "Pacientes", icon: "pacientes" },
  { to: "/receituario", label: "Prescrição", icon: "prescricao" },
  { to: "/documentos", label: "Documentos e Solicitações", icon: "documento" },
  { to: "/material-paciente", label: "Material para paciente", icon: "documento" },
  { to: "/exportar", label: "Exportar conteúdo", icon: "documento" },
  { to: "/agenda", label: "Agenda", icon: "agenda" },
  { to: "/corvia-mail", label: "CorVIA Mail", icon: "mail" },
  { to: "/telediagnostico", label: "Laudo e consultoria", icon: "evidencia" },
  { to: "/indicadores", label: "Meus indicadores", icon: "indicadores" },
  { to: "/usuarios-online", label: "Rede profissional", icon: "pacientes" },
  { to: "/sincronizacao", label: "Contas conectadas", icon: "sincronizar" },
];

const MAIS: NavItem[] = [
  { to: "/tour", label: "Conheça a plataforma", icon: "curso" },
];

function Item({ item }: { item: NavItem }) {
  return <NavLink to={item.to} className={({ isActive }) => `ccc-nav__item${isActive ? " is-active" : ""}`}><Icone nome={item.icon} /><span>{item.label}</span></NavLink>;
}

function iniciais(nome?: string) {
  return (nome || "R").trim().split(/\s+/).slice(0, 2).map((parte) => parte[0]?.toUpperCase()).join("");
}

export default function ClinicalDesktopNav() {
  const { usuario } = useAuth();
  return (
    <aside className="ccc-nav" aria-label="Navegação principal do CorVIA">
      <NavLink to="/" className="ccc-nav__brand" aria-label="CorVIA — Início">
        <span className="ccc-nav__brand-mark"><img src="/corvia-mark-canonical.svg" alt="" /></span>
        <span className="ccc-nav__brand-copy"><strong>CorVIA</strong><small>Clinical OS do médico</small></span>
      </NavLink>
      <nav className="ccc-nav__scroll">
        <NavLink to="/" end className={({ isActive }) => `ccc-nav__item ccc-nav__home${isActive ? " is-active" : ""}`}><IconeHoje /><span>Início</span></NavLink>
        <NavLink to="/busca" className={({ isActive }) => `ccc-nav__item${isActive ? " is-active" : ""}`}><Icone nome="busca" /><span>Buscar</span></NavLink>
        <div className="ccc-nav__section"><p>Clínica & Decisão</p>{CLINICA_DECISAO.map((item) => <Item key={item.to} item={item} />)}</div>
        <div className="ccc-nav__section"><p>Estudo & Aprendizagem</p>{ESTUDO_APRENDIZAGEM.map((item) => <Item key={item.to} item={item} />)}</div>
        <div className="ccc-nav__section"><p>Trabalho & Assistência</p>{TRABALHO_ASSISTENCIA.map((item) => <Item key={item.to} item={item} />)}</div>
        <div className="ccc-nav__section ccc-nav__section--utilities">
          <Item item={{ to: "/assistente", label: "Assistente Clínica", icon: "assistente" }} />
          <Item item={{ to: "/favoritos", label: "Favoritos", icon: "favorito" }} />
          <details className="ccc-nav__more"><summary className="ccc-nav__item"><Icone nome="mais" /><span>Mais</span><Icone nome="chevron" className="ccc-nav__more-chevron" /></summary><div className="ccc-nav__more-items">
            {MAIS.map((item) => <Item key={item.to} item={item} />)}
            <Item item={{ to: "/minha-conta", label: "Minha conta", icon: "conta" }} />
            <Item item={{ to: "/assinatura", label: "Assinatura", icon: "check" }} />
            {usuario?.role === "admin" && <><Item item={{ to: "/admin", label: "Administração", icon: "gestao" }} /><Item item={{ to: "/admin/usuarios", label: "Assinantes", icon: "pacientes" }} /><Item item={{ to: "/fila-telediagnostico", label: "Fila de telediagnóstico", icon: "evidencia" }} /></>}
          </div></details>
        </div>
      </nav>
      <div className="ccc-nav__footer ccc-nav__plan">
        {usuario?.photo_url ? <img className="ccc-nav__plan-photo" src={assetUrl(usuario.photo_url)} alt="" /> : <span className="ccc-nav__plan-avatar">{iniciais(usuario?.full_name)}</span>}
        <span className="ccc-nav__plan-copy"><strong>Plano Premium</strong><small>CorVIA Clinical OS</small></span>
      </div>
    </aside>
  );
}
