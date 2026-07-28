import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { api } from "../lib/api";
import Credito from "./Credito";

type ItemNav = { to: string; rotulo: string; curto: string; fim?: boolean };

const NAV_BASE: ItemNav[] = [
  { to: "/", rotulo: "Painel", curto: "Painel", fim: true },
  { to: "/assistente", rotulo: "Assistente clínico", curto: "Assistente" },
  { to: "/biblioteca", rotulo: "Biblioteca científica", curto: "Biblioteca" },
  { to: "/fluxogramas", rotulo: "Fluxogramas clínicos", curto: "Fluxogramas" },
  { to: "/busca", rotulo: "Busca", curto: "Busca" },
  { to: "/calculadoras", rotulo: "Calculadoras", curto: "Escores" },
  { to: "/medicamentos", rotulo: "Medicamentos", curto: "Fármacos" },
  { to: "/galeria", rotulo: "Galeria de imagens", curto: "Galeria" },
  { to: "/exames", rotulo: "Exames", curto: "Exames" },
  { to: "/evidencias", rotulo: "Evidências", curto: "Evidências" },
  { to: "/estudos", rotulo: "Estudos", curto: "Estudos" },
  { to: "/favoritos", rotulo: "Favoritos", curto: "Favoritos" },
  { to: "/round", rotulo: "Round hospitalar", curto: "Round" },
  { to: "/agenda", rotulo: "Agenda", curto: "Agenda" },
  { to: "/documentos", rotulo: "Modelos de documento", curto: "Documentos" },
  { to: "/indicadores", rotulo: "Meus indicadores", curto: "Indicadores" },
  { to: "/cursos", rotulo: "Cursos parceiros", curto: "Cursos" },
  { to: "/telediagnostico", rotulo: "Laudo e consultoria", curto: "Laudo" },
];

export default function Shell() {
  const { usuario, sair } = useAuth();
  const [pendentes, setPendentes] = useState(0);
  const [menuAberto, setMenuAberto] = useState(false);

  useEffect(() => {
    if (usuario?.role !== "admin") return;
    api.get<any[]>("/admin/users?status=pendente").then((l) => setPendentes(l.length)).catch(() => {});
  }, [usuario]);

  const CONTA: ItemNav = { to: "/minha-conta", rotulo: "Minha conta", curto: "Conta" };

  const nav: ItemNav[] =
    usuario?.role === "admin"
      ? [...NAV_BASE, {
          to: "/admin",
          rotulo: pendentes > 0 ? `Administração (${pendentes})` : "Administração",
          curto: pendentes > 0 ? `Admin (${pendentes})` : "Admin",
        }, { to: "/fila-telediagnostico", rotulo: "Fila de telediagnóstico", curto: "Fila" }, CONTA]
      : [...NAV_BASE, CONTA];

  return (
    <div>
      <header className="topo">
        <button
          className="topo__menu"
          onClick={() => setMenuAberto(true)}
          aria-label="Abrir menu"
          aria-expanded={menuAberto}
        >
          <span /><span /><span />
        </button>
        
        <div className="topo__identidade">
          {/* A logo já traz o nome "MeuCardio" na própria arte — repetir em texto
              ao lado era duplicata. A placa clara existe porque metade da arte é
              navy (#003048) e o cabeçalho também: sobre o fundo do topo esse
              trecho fica com 1,02:1 de contraste, ou seja, invisível. */}
          <span className="topo__logo">
            <img src="/logo-marca.png" alt="MeuCardio" />
          </span>
          <span className="topo__servico">Guia de Cardiologia</span>
        </div>
        <div className="topo__usuario">
          <NavLink to="/minha-conta" style={{ color: "inherit" }}>
            {usuario?.full_name}
          </NavLink>
          <button
            onClick={sair}
            className="botao botao--secundario"
            style={{ color: "var(--branco)", borderColor: "var(--acento-claro)", marginLeft: 10, padding: "0.3rem 0.7rem" }}
          >
            Sair
          </button>
        </div>
      </header>

      <div className="shell">
        <nav className="lateral" aria-label="Navegação principal">
          {nav.map((i) => (
            <NavLink
              key={i.to}
              to={i.to}
              end={i.fim}
              className={({ isActive }) => (isActive ? "ativo" : "")}
            >
              {i.rotulo}
            </NavLink>
          ))}
        </nav>

        <main className="conteudo">
          <Outlet />
          <Credito compacto />
        </main>
      </div>

      {menuAberto && (
        <div className="gaveta-fundo" onClick={() => setMenuAberto(false)} aria-hidden="true" />
      )}
      <nav
        className={`gaveta ${menuAberto ? "gaveta--aberta" : ""}`}
        aria-label="Navegação principal"
      >
        <div className="gaveta__topo">
          <img src="/logo-marca.png" alt="MeuCardio" className="gaveta__logo" />
          <button className="botao botao--secundario" style={{ padding: "0.3rem 0.6rem" }}
                  onClick={() => setMenuAberto(false)} aria-label="Fechar menu">
            ✕
          </button>
        </div>
        {nav.map((i) => (
          <NavLink
            key={i.to}
            to={i.to}
            end={i.fim}
            onClick={() => setMenuAberto(false)}
            className={({ isActive }) => (isActive ? "ativo" : "")}
          >
            {i.rotulo}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
