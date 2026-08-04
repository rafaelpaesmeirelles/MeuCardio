import { FormEvent, useEffect, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { api } from "../lib/api";
import Credito from "./Credito";
import BoasVindas from "./BoasVindas";
import ChatFlutuante from "./ChatFlutuante";

type ItemNav = { to: string; rotulo: string; curto: string; fim?: boolean };

const NAV_BASE: ItemNav[] = [
  { to: "/agenda", rotulo: "Agenda", curto: "Agenda" },
  { to: "/condicoes", rotulo: "Alerta por condição", curto: "Condições" },
  { to: "/diretrizes", rotulo: "Alertas de diretriz", curto: "Diretrizes" },
  { to: "/assistente", rotulo: "Assistente clínico", curto: "Assistente" },
  { to: "/biblioteca", rotulo: "Biblioteca científica", curto: "Biblioteca" },
  { to: "/busca", rotulo: "Busca", curto: "Busca" },
  { to: "/calculadoras", rotulo: "Calculadoras", curto: "Escores" },
  { to: "/casos-clinicos", rotulo: "Casos clínicos interativos", curto: "Casos" },
  { to: "/interacoes", rotulo: "Checador de Interação Medicamentosa", curto: "Interações" },
  { to: "/checklists", rotulo: "Checklist de alta", curto: "Alta" },
  { to: "/corvia-mail", rotulo: "CorvIA Mail", curto: "Mail" },
  { to: "/cursos", rotulo: "Cursos parceiros", curto: "Cursos" },
  { to: "/documentos", rotulo: "Emissão de Documentos Online", curto: "Documentos" },
  { to: "/estudos", rotulo: "Estudos", curto: "Estudos" },
  { to: "/evidencias", rotulo: "Evidências", curto: "Evidências" },
  { to: "/exames", rotulo: "Exames", curto: "Exames" },
  { to: "/favoritos", rotulo: "Favoritos", curto: "Favoritos" },
  { to: "/fluxogramas", rotulo: "Fluxogramas clínicos", curto: "Fluxogramas" },
  { to: "/galeria", rotulo: "Galeria de imagens", curto: "Galeria" },
  { to: "/telediagnostico", rotulo: "Laudo e consultoria", curto: "Laudo" },
  { to: "/material-paciente", rotulo: "Material para o paciente", curto: "Paciente" },
  { to: "/medicamentos", rotulo: "Medicamentos", curto: "Fármacos" },
  { to: "/receituario", rotulo: "Prescrição Eletrônica", curto: "Prescrição" },
  { to: "/round", rotulo: "Round hospitalar", curto: "Round" },
  { to: "/trilhas", rotulo: "Trilhas de estudo", curto: "Trilhas" },
  { to: "/usuarios-online", rotulo: "Usuários online", curto: "Online" },
];

const PAINEL: ItemNav = { to: "/", rotulo: "Painel", curto: "Painel", fim: true };
const INDICADORES: ItemNav = { to: "/indicadores", rotulo: "Meus indicadores", curto: "Indicadores" };
const CONTA: ItemNav = { to: "/minha-conta", rotulo: "Minha conta", curto: "Conta" };

export default function Shell() {
  const { usuario, sair } = useAuth();
  const navigate = useNavigate();
  const naEmergencia = useLocation().pathname.startsWith("/emergencia");
  const [pendentes, setPendentes] = useState(0);
  const [menuAberto, setMenuAberto] = useState(false);
  const [buscaTopo, setBuscaTopo] = useState("");

  useEffect(() => {
    if (usuario?.role !== "admin") return;
    api.get<any[]>("/admin/users?status=pendente").then((lista) => setPendentes(lista.length)).catch(() => {});
  }, [usuario]);

  function buscarDaFaixa(evento: FormEvent) {
    evento.preventDefault();
    const termo = buscaTopo.trim();
    if (termo.length < 2) return;
    navigate(`/busca?q=${encodeURIComponent(termo)}`);
    setBuscaTopo("");
  }

  const ADMIN: ItemNav = {
    to: "/admin",
    rotulo: pendentes > 0 ? `Administração (${pendentes})` : "Administração",
    curto: pendentes > 0 ? `Admin (${pendentes})` : "Admin",
  };

  const nav: ItemNav[] = usuario?.role === "admin"
    ? [PAINEL, ...NAV_BASE, INDICADORES, ADMIN, CONTA]
    : [PAINEL, ...NAV_BASE, INDICADORES, CONTA];

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
          <span className="topo__logo">
            <img src="/corvia-logo-compacta.png" alt="Corvia" />
          </span>
          <span className="topo__servico">O caminho do coração</span>
        </div>

        <form className="topo__busca" onSubmit={buscarDaFaixa} role="search">
          <input
            value={buscaTopo}
            onChange={(e) => setBuscaTopo(e.target.value)}
            placeholder="Buscar em toda a Corvia — condição, fármaco, escore…"
            aria-label="Buscar em toda a Corvia"
          />
          <button type="submit" aria-label="Buscar">🔍</button>
        </form>

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
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.fim}
              className={({ isActive }) => (isActive ? "ativo" : "")}
            >
              {item.rotulo}
            </NavLink>
          ))}
        </nav>

        <main className="conteudo">
          <Outlet />
          <Credito compacto />
        </main>
      </div>

      <BoasVindas />
      {!naEmergencia && <ChatFlutuante />}

      {menuAberto && (
        <div className="gaveta-fundo" onClick={() => setMenuAberto(false)} aria-hidden="true" />
      )}
      <nav
        className={`gaveta ${menuAberto ? "gaveta--aberta" : ""}`}
        aria-label="Navegação principal"
      >
        <div className="gaveta__topo">
          <img src="/corvia-logo-compacta.png" alt="Corvia" className="gaveta__logo" />
          <button
            className="botao botao--secundario"
            style={{ padding: "0.3rem 0.6rem" }}
            onClick={() => setMenuAberto(false)}
            aria-label="Fechar menu"
          >
            ✕
          </button>
        </div>
        {nav.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.fim}
            onClick={() => setMenuAberto(false)}
            className={({ isActive }) => (isActive ? "ativo" : "")}
          >
            {item.rotulo}
          </NavLink>
        ))}
      </nav>

      {!naEmergencia && (
        <button
          className="emerg-atalho"
          onClick={() => navigate("/emergencia")}
          aria-label="Abrir o modo emergência"
          title="Protocolos de risco imediato de vida"
        >
          <svg aria-hidden="true" viewBox="0 0 24 24" width="30" height="30">
            <path d="M9.5 3h5v6.5H21v5h-6.5V21h-5v-6.5H3v-5h6.5V3Z" fill="currentColor" />
          </svg>
          <span className="sr-only">Modo Emergência</span>
        </button>
      )}
    </div>
  );
}
