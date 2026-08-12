import { NavLink } from "react-router-dom";
import { useAuth } from "../lib/auth";
import Icone, { type NomeIcone } from "./Icone";
import { IconeHoje } from "./IdentidadeClinica";

type NavItem = {
  to: string;
  label: string;
  icon: NomeIcone;
};

const CLINICA: NavItem[] = [
  { to: "/doencas", label: "Condições", icon: "doencas" },
  { to: "/medicamentos", label: "Medicamentos", icon: "medicamento" },
  { to: "/exames", label: "Exames", icon: "clinica" },
  { to: "/evidencias", label: "Evidências", icon: "evidencia" },
  { to: "/estudos", label: "Estudos", icon: "evidencia" },
  { to: "/diretrizes", label: "Guidelines", icon: "conhecimento" },
  { to: "/calculadoras", label: "Calculadoras", icon: "calculadora" },
  { to: "/emergencia", label: "Emergências", icon: "emergencia" },
  { to: "/checklists", label: "Checklists", icon: "check" },
  { to: "/casos-clinicos", label: "Casos clínicos", icon: "doencas" },
  { to: "/trilhas", label: "Trilhas", icon: "seta" },
];

const TRABALHO: NavItem[] = [
  { to: "/round", label: "Pacientes", icon: "pacientes" },
  { to: "/receituario", label: "Prescrição", icon: "prescricao" },
  { to: "/documentos", label: "Documentos e Solicitações", icon: "documento" },
  { to: "/agenda", label: "Agenda", icon: "agenda" },
  { to: "/corvia-mail", label: "CorVIA Mail", icon: "mail" },
];

function Item({ item }: { item: NavItem }) {
  return (
    <NavLink
      to={item.to}
      className={({ isActive }) => `ccc-nav__item${isActive ? " is-active" : ""}`}
    >
      <Icone nome={item.icon} />
      <span>{item.label}</span>
    </NavLink>
  );
}

export default function ClinicalDesktopNav() {
  const { usuario } = useAuth();

  function abrirAssistente() {
    window.dispatchEvent(new Event("corvia:abrir-assistente-pessoal"));
  }

  return (
    <aside className="ccc-nav" aria-label="Navegação principal do CorVIA">
      <NavLink to="/" className="ccc-nav__brand" aria-label="CorVIA — Início">
        <img src="/corvia-logo-compacta.png" alt="" />
        <span>
          <strong>CorVIA</strong>
          <small>Clinical OS do médico</small>
        </span>
      </NavLink>

      <nav className="ccc-nav__scroll">
        <NavLink to="/" end className={({ isActive }) => `ccc-nav__item ccc-nav__home${isActive ? " is-active" : ""}`}>
          <IconeHoje />
          <span>Início</span>
        </NavLink>
        <NavLink to="/busca" className={({ isActive }) => `ccc-nav__item${isActive ? " is-active" : ""}`}>
          <Icone nome="busca" />
          <span>Buscar</span>
        </NavLink>

        <div className="ccc-nav__section">
          <p>Clínica</p>
          {CLINICA.map((item) => <Item key={item.to} item={item} />)}
        </div>

        <div className="ccc-nav__section">
          <p>Trabalho</p>
          {TRABALHO.map((item) => <Item key={item.to} item={item} />)}
        </div>

        <div className="ccc-nav__section ccc-nav__section--utilities">
          <button type="button" className="ccc-nav__item ccc-nav__assistant" onClick={abrirAssistente}>
            <Icone nome="assistente" />
            <span>Assistente</span>
          </button>
          <Item item={{ to: "/favoritos", label: "Favoritos", icon: "favorito" }} />
          <details className="ccc-nav__more">
            <summary className="ccc-nav__item">
              <Icone nome="mais" />
              <span>Mais</span>
              <Icone nome="chevron" className="ccc-nav__more-chevron" />
            </summary>
            <div className="ccc-nav__more-items">
              <Item item={{ to: "/material-paciente", label: "Material para paciente", icon: "documento" }} />
              <Item item={{ to: "/galeria", label: "Galeria", icon: "galeria" }} />
              <Item item={{ to: "/sincronizacao", label: "Contas conectadas", icon: "sincronizar" }} />
              <Item item={{ to: "/minha-conta", label: "Minha conta", icon: "conta" }} />
              <Item item={{ to: "/assinatura", label: "Assinatura", icon: "check" }} />
              {usuario?.role === "admin" && <Item item={{ to: "/admin", label: "Administração", icon: "gestao" }} />}
            </div>
          </details>
        </div>
      </nav>

      <div className="ccc-nav__footer">
        <span className="ccc-nav__footer-mark">✦</span>
        <span>
          <strong>Clinical Command Center</strong>
          <small>Conhecimento → decisão → ação</small>
        </span>
      </div>
    </aside>
  );
}
