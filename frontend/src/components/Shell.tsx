import { FormEvent, useEffect, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { api } from "../lib/api";
import Credito from "./Credito";
import BoasVindas from "./BoasVindas";
import ChatFlutuante from "./ChatFlutuante";

type ItemNav = { to: string; rotulo: string; curto: string; fim?: boolean };

// Lista única, em ordem alfabética por rótulo — pedido do Rafael em
// 31/07/2026. Só Administração e Minha conta (acrescidas mais abaixo, fora
// deste array) ficam de fora da ordenação, sempre por último.
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
  // Aponta para /corvia-mail (login/assinatura próprios do add-on), não
  // direto pra /caixa-de-email — o e-mail tem senha separada da conta
  // Corvia desde 30/07/2026, então precisa passar pelo login dele primeiro.
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
];

const PAINEL: ItemNav = { to: "/", rotulo: "Painel", curto: "Painel", fim: true };
const INDICADORES: ItemNav = { to: "/indicadores", rotulo: "Meus indicadores", curto: "Indicadores" };
const CONTA: ItemNav = { to: "/minha-conta", rotulo: "Minha conta", curto: "Conta" };

export default function Shell() {
  const { usuario, sair } = useAuth();
  const navigate = useNavigate();
  // O atalho não aparece dentro do próprio modo emergência: lá ele seria um
  // botão que não leva a lugar nenhum, ocupando o canto que a tela usa.
  const naEmergencia = useLocation().pathname.startsWith("/emergencia");
  const [pendentes, setPendentes] = useState(0);
  const [menuAberto, setMenuAberto] = useState(false);
  const [buscaTopo, setBuscaTopo] = useState("");

  useEffect(() => {
    if (usuario?.role !== "admin") return;
    api.get<any[]>("/admin/users?status=pendente").then((l) => setPendentes(l.length)).catch(() => {});
  }, [usuario]);

  function buscarDaFaixa(e: FormEvent) {
    e.preventDefault();
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
    ? [
        PAINEL,
        ...NAV_BASE,
        { to: "/fila-telediagnostico", rotulo: "Fila de telediagnóstico", curto: "Fila" },
        { to: "/admin/usuarios-online", rotulo: "Usuários online", curto: "Online" },
        INDICADORES,
        ADMIN,
        CONTA,
      ]
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
          {/* A logo já traz o nome "CorvIA" na própria arte — repetir em texto
              ao lado era duplicata. A placa clara existe porque metade da arte é
              navy (#003048) e o cabeçalho também: sobre o fundo do topo esse
              trecho fica com 1,02:1 de contraste, ou seja, invisível. */}
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

      <BoasVindas />

      {/* CorvIA Chat — widget flutuante, disponível de qualquer tela. Fica fora
          do modo emergência pelo mesmo motivo do atalho vermelho: lá a tela é
          para uma coisa só. O botão do chat é posicionado acima do atalho de
          emergência para não cobri-lo. */}
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
    
      {/* Tarefa 15 — acesso ao Modo Emergência em um toque, de qualquer tela.
          Fica fora do menu de propósito: o requisito é chegar lá sob pressão,
          e um item de menu já custa o toque de abrir o menu. */}
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
