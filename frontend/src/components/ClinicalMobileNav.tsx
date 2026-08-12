import { NavLink } from "react-router-dom";
import Icone from "./Icone";
import { IconeHoje } from "./IdentidadeClinica";

export default function ClinicalMobileNav() {
  function abrirMais() {
    document.querySelector<HTMLButtonElement>(".cos-topbar__menu")?.click();
  }

  return (
    <nav className="cc-mobile-nav" aria-label="Navegação principal móvel">
      <NavLink to="/" end>
        <IconeHoje />
        <span>Início</span>
      </NavLink>
      <NavLink to="/busca" className="cc-mobile-nav__search">
        <Icone nome="busca" />
        <span>Buscar</span>
      </NavLink>
      <NavLink to="/round">
        <Icone nome="pacientes" />
        <span>Pacientes</span>
      </NavLink>
      <NavLink to="/agenda">
        <Icone nome="agenda" />
        <span>Agenda</span>
      </NavLink>
      <button type="button" onClick={abrirMais}>
        <Icone nome="mais" />
        <span>Mais</span>
      </button>
    </nav>
  );
}
