import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { api } from "../lib/api";
import Credito from "./Credito";

const NAV_BASE = [
  { to: "/", rotulo: "Painel", curto: "Painel", fim: true },
  { to: "/assistente", rotulo: "Assistente clínico", curto: "Assistente" },
  { to: "/biblioteca", rotulo: "Biblioteca científica", curto: "Biblioteca" },
  { to: "/busca", rotulo: "Busca", curto: "Busca" },
  { to: "/calculadoras", rotulo: "Calculadoras", curto: "Escores" },
  { to: "/medicamentos", rotulo: "Medicamentos", curto: "Fármacos" },
  { to: "/galeria", rotulo: "Galeria de imagens", curto: "Galeria" },
  { to: "/exames", rotulo: "Exames", curto: "Exames" },
  { to: "/evidencias", rotulo: "Evidências", curto: "Evidências" },
  { to: "/estudos", rotulo: "Estudos", curto: "Estudos" },
  { to: "/favoritos", rotulo: "Favoritos", curto: "Favoritos" },
  { to: "/round", rotulo: "Round hospitalar", curto: "Round" },
];

export default function Shell() {
  const { usuario, sair } = useAuth();
  const [pendentes, setPendentes] = useState(0);
  const [menuAberto, setMenuAberto] = useState(false);

  useEffect(() => {
    if (usuario?.role !== "admin") return;
    api.get<any[]>("/admin/users?status=pendente").then((l) => setPendentes(l.length)).catch(() => {});
  }, [usuario]);

  const nav =
    usuario?.role === "admin"
      ? [...NAV_BASE, {
          to: "/admin",
          rotulo: pendentes > 0 ? `Administração (${pendentes})` : "Administração",
          curto: pendentes > 0 ? `Admin (${pendentes})` : "Admin",
        }]
      : NAV_BASE;

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
        
        <div>
          <span className="topo__servico">Serviço de Cardiologia</span>
          <span className="topo__marca">MeuCardio</span>
        </div>
        <div className="topo__usuario">
          {usuario?.full_name}
          <button
            onClick={sair}
            className="botao botao--secundario"
            style={{ color: "#fff", borderColor: "#a4535e", marginLeft: 10, padding: "0.3rem 0.7rem" }}
          >
            Sair
          </button>
        </div>
      </header>
      <div className="fio-dourado" />

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
          <span className="topo__marca" style={{ color: "var(--bordo)" }}>MeuCardio</span>
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
