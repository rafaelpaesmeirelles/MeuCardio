import {
  type FormEvent,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { api, assetUrl } from "../lib/api";
import Credito from "./Credito";
import BoasVindas from "./BoasVindas";
import ChatFlutuante from "./ChatFlutuante";
import Icone, { type NomeIcone } from "./Icone";
import { IconeEmergencia, IconeHoje } from "./IdentidadeClinica";

type ItemNav = {
  to: string;
  rotulo: string;
  icone: NomeIcone;
  fim?: boolean;
  badge?: number;
  indisponivel?: boolean;
};

type SecaoNav = {
  id: string;
  rotulo: string;
  icone: NomeIcone;
  itens: ItemNav[];
};

const SECOES_BASE: SecaoNav[] = [
  {
    id: "decisao",
    rotulo: "Decisão clínica",
    icone: "clinica",
    itens: [
      { to: "/assistente", rotulo: "Assistente clínico", icone: "assistente" },
      { to: "/doencas", rotulo: "Guia de doenças", icone: "doencas" },
      { to: "/triagem-sintomas", rotulo: "Triagem de sintomas", icone: "triagem" },
      { to: "/condicoes", rotulo: "Condições especiais", icone: "check" },
      { to: "/calculadoras", rotulo: "Calculadoras e escores", icone: "calculadora" },
      { to: "/interacoes", rotulo: "Interações medicamentosas", icone: "medicamento" },
      { to: "/medicamentos", rotulo: "Medicamentos", icone: "medicamento" },
      { to: "/fluxogramas", rotulo: "Fluxogramas clínicos", icone: "seta" },
      { to: "/diretrizes", rotulo: "Alertas de diretriz", icone: "evidencia" },
    ],
  },
  {
    id: "pratica",
    rotulo: "Pacientes e prática",
    icone: "pacientes",
    itens: [
      { to: "/agenda", rotulo: "Agenda", icone: "agenda" },
      { to: "/round", rotulo: "Round hospitalar", icone: "round" },
      { to: "/receituario", rotulo: "Prescrição eletrônica", icone: "prescricao" },
      { to: "/documentos", rotulo: "Documentos", icone: "documento" },
      { to: "/exames", rotulo: "Exames e marcadores", icone: "clinica" },
      { to: "/checklists", rotulo: "Checklist de alta", icone: "check" },
      { to: "/material-paciente", rotulo: "Material ao paciente", icone: "documento" },
      { to: "/telediagnostico", rotulo: "Laudo e consultoria", icone: "evidencia" },
    ],
  },
  {
    id: "conhecimento",
    rotulo: "Conhecimento",
    icone: "conhecimento",
    itens: [
      { to: "/biblioteca", rotulo: "Biblioteca científica", icone: "conhecimento" },
      { to: "/busca", rotulo: "Busca avançada", icone: "busca" },
      { to: "/evidencias", rotulo: "Evidências", icone: "evidencia" },
      { to: "/estudos", rotulo: "Estudos", icone: "evidencia" },
      { to: "/casos-clinicos", rotulo: "Casos clínicos", icone: "doencas" },
      { to: "/galeria", rotulo: "Galeria de imagens", icone: "galeria" },
      { to: "/trilhas", rotulo: "Trilhas de estudo", icone: "seta" },
      { to: "/cursos", rotulo: "Cursos", icone: "curso" },
      { to: "/apresentacao", rotulo: "Modo apresentação", icone: "documento" },
    ],
  },
  {
    id: "comunicacao",
    rotulo: "Comunicação",
    icone: "comunicacao",
    itens: [
      { to: "/corvia-mail", rotulo: "Corvia Mail", icone: "mail" },
      { to: "/usuarios-online", rotulo: "Rede profissional", icone: "pacientes" },
    ],
  },
  {
    id: "gestao",
    rotulo: "Gestão",
    icone: "gestao",
    itens: [
      { to: "/indicadores", rotulo: "Meus indicadores", icone: "indicadores" },
      { to: "/favoritos", rotulo: "Favoritos", icone: "favorito" },
      { to: "/minha-conta", rotulo: "Minha conta", icone: "conta" },
    ],
  },
];

const PAINEL: ItemNav = { to: "/", rotulo: "Hoje", icone: "hoje", fim: true };
const INDICADORES: ItemNav = { to: "/indicadores", rotulo: "Meus indicadores", icone: "indicadores" };
const CONTA: ItemNav = { to: "/minha-conta", rotulo: "Minha conta", icone: "conta" };
const NAV_BASE: ItemNav[] = SECOES_BASE.flatMap((secao) => secao.itens).filter(
  (item) => item.to !== INDICADORES.to && item.to !== CONTA.to,
);

function iniciais(nome?: string) {
  return (nome || "Médico")
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((parte) => parte[0]?.toUpperCase())
    .join("");
}

function Navegacao({
  secoes,
  aoNavegar,
}: {
  secoes: SecaoNav[];
  aoNavegar?: () => void;
}) {
  const { pathname } = useLocation();
  const secaoAtiva = secoes.find((secao) =>
    secao.itens.some((item) => pathname === item.to || pathname.startsWith(`${item.to}/`)),
  )?.id;
  const [aberta, setAberta] = useState(secaoAtiva || "decisao");

  useEffect(() => {
    if (secaoAtiva) setAberta(secaoAtiva);
  }, [secaoAtiva]);

  return (
    <div className="nav-clinica">
      <NavLink
        to="/"
        end
        onClick={aoNavegar}
        className={({ isActive }) => `nav-clinica__hoje${isActive ? " ativo" : ""}`}
      >
        <span className="nav-clinica__hoje-logo"><IconeHoje /></span>
        <span>Hoje</span>
      </NavLink>

      <div className="nav-clinica__separador" />

      {secoes.map((secao) => {
        const expandida = aberta === secao.id;
        return (
          <section className="nav-grupo" key={secao.id}>
            <button
              type="button"
              className={`nav-grupo__botao${secaoAtiva === secao.id ? " nav-grupo__botao--ativo" : ""}`}
              onClick={() => setAberta(expandida ? "" : secao.id)}
              aria-expanded={expandida}
              aria-controls={`nav-grupo-${secao.id}`}
            >
              <Icone nome={secao.icone} />
              <span>{secao.rotulo}</span>
              <Icone nome="chevron" className="nav-grupo__chevron" />
            </button>
            <div
              id={`nav-grupo-${secao.id}`}
              className={`nav-grupo__itens${expandida ? " nav-grupo__itens--aberto" : ""}`}
              aria-hidden={!expandida}
            >
              {secao.itens.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.fim}
                  tabIndex={expandida ? undefined : -1}
                  onClick={aoNavegar}
                  className={({ isActive }) => (isActive ? "ativo" : "")}
                >
                  <Icone nome={item.icone} />
                  <span>{item.rotulo}</span>
                  {!!item.badge && <span className="nav-clinica__badge">{item.badge}</span>}
                </NavLink>
              ))}
            </div>
          </section>
        );
      })}
    </div>
  );
}

export default function Shell() {
  const { usuario, sair } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const naEmergencia = location.pathname.startsWith("/emergencia");
  const [pendentes, setPendentes] = useState(0);
  const [menuAberto, setMenuAberto] = useState(false);
  const [buscaTopo, setBuscaTopo] = useState("");
  const [fotoCabecalhoQuebrada, setFotoCabecalhoQuebrada] = useState(false);
  const buscaRef = useRef<HTMLInputElement>(null);
  const abrirMenuRef = useRef<HTMLButtonElement>(null);
  const fecharRef = useRef<HTMLButtonElement>(null);
  const gavetaRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (usuario?.role !== "admin") return;
    api.get<unknown[]>("/admin/users?status=pendente")
      .then((lista) => setPendentes(lista.length))
      .catch(() => {});
  }, [usuario]);

  useEffect(() => setFotoCabecalhoQuebrada(false), [usuario?.photo_url]);

  useEffect(() => {
    function atalhoBusca(evento: KeyboardEvent) {
      if ((evento.metaKey || evento.ctrlKey) && evento.key.toLowerCase() === "k") {
        evento.preventDefault();
        buscaRef.current?.focus();
      }
    }
    document.addEventListener("keydown", atalhoBusca);
    return () => document.removeEventListener("keydown", atalhoBusca);
  }, []);

  useEffect(() => {
    if (menuAberto) {
      fecharRef.current?.focus();
      const prenderFoco = (evento: KeyboardEvent) => {
        if (evento.key === "Escape") {
          evento.preventDefault();
          setMenuAberto(false);
          requestAnimationFrame(() => abrirMenuRef.current?.focus());
          return;
        }
        if (evento.key !== "Tab") return;
        const elementos = Array.from(
          gavetaRef.current?.querySelectorAll<HTMLElement>(
            'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
          ) ?? [],
        ).filter((elemento) => elemento.offsetParent !== null);
        if (elementos.length === 0) return;
        const primeiro = elementos[0];
        const ultimo = elementos[elementos.length - 1];
        if (evento.shiftKey && document.activeElement === primeiro) {
          evento.preventDefault();
          ultimo.focus();
        } else if (!evento.shiftKey && document.activeElement === ultimo) {
          evento.preventDefault();
          primeiro.focus();
        }
      };
      document.addEventListener("keydown", prenderFoco);
      document.body.classList.add("menu-clinico-aberto");
      return () => {
        document.removeEventListener("keydown", prenderFoco);
        document.body.classList.remove("menu-clinico-aberto");
      };
    }
    document.body.classList.toggle("menu-clinico-aberto", menuAberto);
    return () => document.body.classList.remove("menu-clinico-aberto");
  }, [menuAberto]);

  function fecharMenu() {
    setMenuAberto(false);
    requestAnimationFrame(() => abrirMenuRef.current?.focus());
  }

  async function encerrarSessao() {
    setMenuAberto(false);
    await sair();
    navigate("/entrar", { replace: true });
  }

  function buscarDaFaixa(evento: FormEvent) {
    evento.preventDefault();
    const termo = buscaTopo.trim();
    if (termo.length < 2) return;
    navigate(`/busca?q=${encodeURIComponent(termo)}`);
    setBuscaTopo("");
  }

  const secoes = useMemo(() => {
    const ADMIN: ItemNav = {
      to: "/admin", rotulo: "Administração", icone: "gestao", badge: pendentes,
    };
    const nav: ItemNav[] = usuario?.role === "admin"
      ? [
        PAINEL,
        ...NAV_BASE,
        INDICADORES,
        ADMIN,
        CONTA,
      ]
      : [PAINEL, ...NAV_BASE, INDICADORES, CONTA];

    if (usuario?.role === "admin") {
      nav.splice(nav.length - 1, 0, { to: "/fila-telediagnostico", rotulo: "Fila de telediagnóstico", icone: "evidencia", indisponivel: true });
    }
    if (usuario?.role !== "admin") return SECOES_BASE;
    const extrasGestao = nav.filter((item) => item.to === "/admin" || item.to === "/fila-telediagnostico");
    return SECOES_BASE.map((secao) =>
      secao.id !== "gestao"
        ? secao
        : {
            ...secao,
            itens: [
              ...secao.itens,
              ...extrasGestao,
            ],
          },
    );
  }, [pendentes, usuario?.role]);

  return (
    <div className="app-clinico">
      <a className="pular-conteudo" href="#conteudo-principal">Pular para o conteúdo</a>

      <aside className="lateral" aria-label="Navegação principal">
        <NavLink to="/" className="lateral__marca" aria-label="Corvia — ir para Hoje">
          <span className="lateral__logo"><img src="/corvia-logo-compacta.png" alt="" /></span>
          <span className="lateral__produto">Ecossistema clínico</span>
        </NavLink>
        <Navegacao secoes={secoes} />
        <div className="lateral__rodape">
          <button type="button" className="lateral__sair" onClick={encerrarSessao}>
            <Icone nome="sair" />
            <span>Sair do sistema</span>
          </button>
          <span>Suporte à decisão, não substitui julgamento clínico.</span>
        </div>
      </aside>

      <div className="shell-principal" aria-hidden={menuAberto || undefined}>
        <header className="topo">
          <button
            ref={abrirMenuRef}
            type="button"
            className="topo__menu"
            onClick={() => setMenuAberto(true)}
            aria-label="Abrir navegação"
            aria-expanded={menuAberto}
          >
            <Icone nome="menu" />
          </button>

          <NavLink to="/" className="topo__marca-mobile" aria-label="Corvia — ir para Hoje">
            <img src="/corvia-logo-compacta.png" alt="" />
          </NavLink>

          <form className="topo__busca" onSubmit={buscarDaFaixa} role="search">
            <Icone nome="busca" />
            <input
              ref={buscaRef}
              value={buscaTopo}
              onChange={(e) => setBuscaTopo(e.target.value)}
              placeholder="Buscar condição, fármaco, escore ou diretriz"
              aria-label="Buscar em toda a Corvia"
            />
            <kbd aria-hidden="true">⌘ K</kbd>
            <button type="submit" aria-label="Executar busca"><Icone nome="seta" /></button>
          </form>

          <div className="topo__acoes">
            {!naEmergencia && (
              <button
                type="button"
                className="topo__emergencia"
                onClick={() => navigate("/emergencia")}
              >
                <IconeEmergencia />
                <span>Emergência</span>
              </button>
            )}
            <NavLink to="/corvia-mail" className="topo__icone" aria-label="Abrir Corvia Mail">
              <img className="topo__mail-logo" src="/corviamail-icone.svg" alt="" />
            </NavLink>
            <NavLink to="/minha-conta" className="topo__perfil" aria-label={`Abrir conta de ${usuario?.full_name}`}>
              {usuario?.photo_url && !fotoCabecalhoQuebrada ? (
                <img className="topo__avatar topo__avatar--foto" src={assetUrl(usuario.photo_url)} alt=""
                     onError={() => setFotoCabecalhoQuebrada(true)} />
              ) : (
                <span className="topo__avatar">{iniciais(usuario?.full_name)}</span>
              )}
              <span className="topo__perfil-texto">
                <strong>{usuario?.full_name}</strong>
                <small>{usuario?.role === "admin" ? "Administrador" : "Profissional"}</small>
              </span>
              <Icone nome="chevron" />
            </NavLink>
          </div>
        </header>

        <main className="conteudo" id="conteudo-principal" tabIndex={-1}>
          <Outlet />
          <Credito compacto />
        </main>
      </div>

      <div
        className={`gaveta-fundo${menuAberto ? " gaveta-fundo--visivel" : ""}`}
        onClick={fecharMenu}
        aria-hidden="true"
      />
      <aside
        ref={gavetaRef}
        className={`gaveta${menuAberto ? " gaveta--aberta" : ""}`}
        role="dialog"
        aria-modal="true"
        aria-label="Navegação móvel"
        aria-hidden={!menuAberto}
      >
        <div className="gaveta__topo">
          <img src="/corvia-logo-compacta.png" alt="Corvia" className="gaveta__logo" />
          <button
            ref={fecharRef}
            type="button"
            className="gaveta__fechar"
            onClick={fecharMenu}
            aria-label="Fechar navegação"
          >
            <Icone nome="fechar" />
          </button>
        </div>
        <Navegacao secoes={secoes} aoNavegar={() => setMenuAberto(false)} />
        <button type="button" className="gaveta__sair" onClick={encerrarSessao}>
          <Icone nome="sair" /> Sair da Corvia
        </button>
      </aside>

      <nav className="barra-mobile" aria-label="Atalhos principais" aria-hidden={menuAberto || undefined}>
        <NavLink to="/" end><IconeHoje /><span>Hoje</span></NavLink>
        <NavLink to="/round"><Icone nome="pacientes" /><span>Pacientes</span></NavLink>
        <NavLink to="/busca"><Icone nome="busca" /><span>Buscar</span></NavLink>
        <button type="button" onClick={() => setMenuAberto(true)} aria-expanded={menuAberto}>
          <Icone nome="mais" /><span>Mais</span>
        </button>
      </nav>

      <BoasVindas />
      {!naEmergencia && (
        <NavLink
          to="/emergencia"
          className="emergencia-flutuante"
          aria-label="Abrir o Modo Emergência"
          title="Modo Emergência — protocolos de risco imediato"
        >
          <IconeEmergencia />
        </NavLink>
      )}
      {!naEmergencia && <ChatFlutuante />}
    </div>
  );
}
