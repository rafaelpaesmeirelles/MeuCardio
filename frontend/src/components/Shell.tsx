import {
  type FormEvent,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import type { KeyboardEvent as ReactKeyboardEvent } from "react";
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

/**
 * O menu do lançamento deixa de descrever a implementação interna e passa a
 * organizar o CorVIA pela intenção do médico. Paciente é um contexto de
 * trabalho, não o centro universal do produto.
 */
const SECOES_BASE: SecaoNav[] = [
  {
    id: "clinica",
    rotulo: "Clínica",
    icone: "clinica",
    itens: [
      { to: "/biblioteca", rotulo: "Biblioteca clínica", icone: "conhecimento" },
      { to: "/doencas", rotulo: "Condições e doenças", icone: "doencas" },
      { to: "/medicamentos", rotulo: "Medicamentos", icone: "medicamento" },
      { to: "/exames", rotulo: "Exames e marcadores", icone: "clinica" },
      { to: "/evidencias", rotulo: "Evidências", icone: "evidencia" },
      { to: "/estudos", rotulo: "Estudos", icone: "curso" },
      { to: "/diretrizes", rotulo: "Guidelines e alertas", icone: "evidencia" },
      { to: "/calculadoras", rotulo: "Calculadoras e escores", icone: "calculadora" },
      { to: "/emergencia", rotulo: "Emergências", icone: "emergencia" },
      { to: "/checklists", rotulo: "Checklists", icone: "check" },
      { to: "/casos-clinicos", rotulo: "Casos clínicos", icone: "doencas" },
      { to: "/trilhas", rotulo: "Trilhas", icone: "seta" },
      { to: "/interacoes", rotulo: "Interações medicamentosas", icone: "medicamento" },
      { to: "/condicoes", rotulo: "Condições especiais", icone: "check" },
      { to: "/fluxogramas", rotulo: "Fluxogramas clínicos", icone: "seta" },
      { to: "/triagem-sintomas", rotulo: "Triagem de sintomas", icone: "triagem" },
    ],
  },
  {
    id: "trabalho",
    rotulo: "Trabalho",
    icone: "gestao",
    itens: [
      { to: "/round", rotulo: "Pacientes e round", icone: "pacientes" },
      { to: "/receituario", rotulo: "Prescrição", icone: "prescricao" },
      { to: "/documentos", rotulo: "Documentos e solicitações", icone: "documento" },
      { to: "/agenda", rotulo: "Agenda", icone: "agenda" },
      { to: "/corvia-mail", rotulo: "CorVIA Mail", icone: "mail" },
      { to: "/avaliacao-preoperatoria", rotulo: "Avaliação pré-operatória", icone: "clinica" },
      { to: "/telediagnostico", rotulo: "Laudo e consultoria", icone: "evidencia" },
      { to: "/material-paciente", rotulo: "Material para paciente", icone: "documento" },
    ],
  },
  {
    id: "inteligencia",
    rotulo: "Inteligência",
    icone: "assistente",
    itens: [
      { to: "/assistente", rotulo: "Assistentes CorVIA", icone: "assistente" },
      { to: "/busca", rotulo: "Busca universal", icone: "busca" },
    ],
  },
  {
    id: "mais",
    rotulo: "Mais",
    icone: "mais",
    itens: [
      { to: "/favoritos", rotulo: "Favoritos", icone: "favorito" },
      { to: "/indicadores", rotulo: "Meus indicadores", icone: "indicadores" },
      { to: "/usuarios-online", rotulo: "Rede profissional", icone: "pacientes" },
      { to: "/galeria", rotulo: "Galeria de imagens", icone: "galeria" },
      { to: "/cursos", rotulo: "Cursos", icone: "curso" },
      { to: "/apresentacao", rotulo: "Modo apresentação", icone: "documento" },
      { to: "/sincronizacao", rotulo: "Sincronizar contas", icone: "sincronizar" },
      { to: "/minha-conta", rotulo: "Minha conta", icone: "conta" },
      { to: "/tour", rotulo: "Conheça a plataforma", icone: "curso" },
    ],
  },
];

const ACOES_MOBILE: ItemNav[] = [
  { to: "/receituario", rotulo: "Prescrever", icone: "prescricao" },
  { to: "/documentos", rotulo: "Solicitar exames", icone: "documento" },
  { to: "/documentos", rotulo: "Criar documento", icone: "documento" },
  { to: "/calculadoras", rotulo: "Calculadoras", icone: "calculadora" },
  { to: "/emergencia", rotulo: "Emergência", icone: "emergencia" },
  { to: "/medicamentos", rotulo: "Medicamentos", icone: "medicamento" },
];

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
  const [aberta, setAberta] = useState(secaoAtiva || "clinica");

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
        <span className="nav-clinica__hoje-texto">
          <strong>Início</strong>
          <small>Clinical Command Center</small>
        </span>
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
                  key={`${secao.id}-${item.to}-${item.rotulo}`}
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
  const [acoesAberto, setAcoesAberto] = useState(false);
  const [menuContaAberto, setMenuContaAberto] = useState(false);
  const [saindoPeloMenu, setSaindoPeloMenu] = useState(false);
  const [buscaTopo, setBuscaTopo] = useState("");
  const [fotoCabecalhoQuebrada, setFotoCabecalhoQuebrada] = useState(false);
  const buscaRef = useRef<HTMLInputElement>(null);
  const abrirMenuRef = useRef<HTMLButtonElement>(null);
  const fecharRef = useRef<HTMLButtonElement>(null);
  const gavetaRef = useRef<HTMLElement>(null);
  const contaRef = useRef<HTMLDivElement>(null);
  const abrirContaRef = useRef<HTMLButtonElement>(null);
  const menuContaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (usuario?.role !== "admin") return;
    api.get<unknown[]>("/admin/users?status=pendente")
      .then((lista) => setPendentes(lista.length))
      .catch(() => {});
  }, [usuario]);

  useEffect(() => setFotoCabecalhoQuebrada(false), [usuario?.photo_url]);

  useEffect(() => {
    setMenuContaAberto(false);
    setAcoesAberto(false);
  }, [location.pathname]);

  useEffect(() => {
    if (!menuContaAberto) return;

    requestAnimationFrame(() => {
      menuContaRef.current?.querySelector<HTMLElement>('[role="menuitem"]')?.focus();
    });

    function fecharAoClicarFora(evento: PointerEvent) {
      if (!contaRef.current?.contains(evento.target as Node)) setMenuContaAberto(false);
    }

    function fecharComEscape(evento: KeyboardEvent) {
      if (evento.key !== "Escape") return;
      evento.preventDefault();
      setMenuContaAberto(false);
      requestAnimationFrame(() => abrirContaRef.current?.focus());
    }

    document.addEventListener("pointerdown", fecharAoClicarFora);
    document.addEventListener("keydown", fecharComEscape);
    return () => {
      document.removeEventListener("pointerdown", fecharAoClicarFora);
      document.removeEventListener("keydown", fecharComEscape);
    };
  }, [menuContaAberto]);

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
    if (!acoesAberto) return;
    function fecharComEscape(evento: KeyboardEvent) {
      if (evento.key === "Escape") setAcoesAberto(false);
    }
    document.addEventListener("keydown", fecharComEscape);
    document.body.classList.add("acoes-clinicas-abertas");
    return () => {
      document.removeEventListener("keydown", fecharComEscape);
      document.body.classList.remove("acoes-clinicas-abertas");
    };
  }, [acoesAberto]);

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
    setAcoesAberto(false);
    setMenuContaAberto(false);
    setSaindoPeloMenu(true);
    try {
      await sair();
      navigate("/entrar", { replace: true });
    } finally {
      setSaindoPeloMenu(false);
    }
  }

  function buscarDaFaixa(evento: FormEvent) {
    evento.preventDefault();
    const termo = buscaTopo.trim();
    if (termo.length < 2) return;
    navigate(`/busca?q=${encodeURIComponent(termo)}`);
    setBuscaTopo("");
  }

  const secoes = useMemo(() => {
    if (usuario?.role !== "admin") return SECOES_BASE;
    return SECOES_BASE.map((secao) => secao.id !== "mais" ? secao : {
      ...secao,
      itens: [
        ...secao.itens,
        { to: "/admin", rotulo: "Administração", icone: "gestao" as NomeIcone, badge: pendentes },
        { to: "/admin/usuarios", rotulo: "Assinantes", icone: "pacientes" as NomeIcone },
        { to: "/fila-telediagnostico", rotulo: "Fila de telediagnóstico", icone: "evidencia" as NomeIcone, indisponivel: true },
      ],
    });
  }, [pendentes, usuario?.role]);

  const recursosDaConta = useMemo(() => {
    const recursos: ItemNav[] = [
      { to: "/agenda", rotulo: "Agenda integrada", icone: "agenda" },
      { to: "/assinatura", rotulo: "Assinatura e plano", icone: "check" },
      { to: "/corvia-mail", rotulo: "CorVIA Mail", icone: "mail" },
      { to: "/documentos", rotulo: "Documentos", icone: "documento" },
      { to: "/favoritos", rotulo: "Favoritos", icone: "favorito" },
      { to: "/indicadores", rotulo: "Meus indicadores", icone: "indicadores" },
      { to: "/minha-conta", rotulo: "Minha conta", icone: "conta" },
      { to: "/sincronizacao", rotulo: "Sincronize suas contas", icone: "sincronizar" },
      { to: "/tour", rotulo: "Conheça a plataforma", icone: "curso" },
      { to: "/usuarios-online", rotulo: "Rede profissional", icone: "pacientes" },
    ];
    if (usuario?.role === "admin") {
      recursos.push(
        { to: "/admin", rotulo: "Administração", icone: "gestao", badge: pendentes },
        { to: "/admin/usuarios", rotulo: "Assinantes", icone: "pacientes" },
        { to: "/fila-telediagnostico", rotulo: "Fila de telediagnóstico", icone: "evidencia" },
      );
    }
    return recursos.sort((a, b) => a.rotulo.localeCompare(b.rotulo, "pt-BR"));
  }, [pendentes, usuario?.role]);

  function navegarNoMenuConta(evento: ReactKeyboardEvent<HTMLDivElement>) {
    if (!["ArrowDown", "ArrowUp", "Home", "End"].includes(evento.key)) return;
    const itens = Array.from(
      menuContaRef.current?.querySelectorAll<HTMLElement>('[role="menuitem"]:not([disabled])') ?? [],
    );
    if (!itens.length) return;
    evento.preventDefault();
    const atual = itens.indexOf(document.activeElement as HTMLElement);
    if (evento.key === "Home") itens[0].focus();
    else if (evento.key === "End") itens[itens.length - 1].focus();
    else if (evento.key === "ArrowDown") itens[(atual + 1 + itens.length) % itens.length].focus();
    else itens[(atual - 1 + itens.length) % itens.length].focus();
  }

  const interfaceBloqueada = menuAberto || acoesAberto;

  return (
    <div className="app-clinico">
      <a className="pular-conteudo" href="#conteudo-principal">Pular para o conteúdo</a>

      <aside className="lateral" aria-label="Navegação principal">
        <NavLink to="/" className="lateral__marca" aria-label="CorVIA — ir para o Clinical Command Center">
          <span className="lateral__logo"><img src="/corvia-logo-compacta.png" alt="" /></span>
          <span className="lateral__produto">Clinical Workspace</span>
        </NavLink>
        <Navegacao secoes={secoes} />
        <div className="lateral__rodape">
          <button type="button" className="lateral__sair" onClick={encerrarSessao}>
            <Icone nome="sair" />
            <span>Sair do sistema</span>
          </button>
          <span>Conhecimento, contexto, decisão, ação e assistência.</span>
        </div>
      </aside>

      <div className="shell-principal" aria-hidden={interfaceBloqueada || undefined}>
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

          <NavLink to="/" className="topo__marca-mobile" aria-label="CorVIA — ir para o início">
            <img src="/corvia-logo-compacta.png" alt="" />
          </NavLink>

          <form className="topo__busca" onSubmit={buscarDaFaixa} role="search">
            <Icone nome="busca" />
            <input
              ref={buscaRef}
              value={buscaTopo}
              onChange={(e) => setBuscaTopo(e.target.value)}
              placeholder="Buscar em todo o CorVIA"
              aria-label="Buscar em todo o CorVIA"
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
            <NavLink to="/corvia-mail" className="topo__icone" aria-label="Abrir CorVIA Mail">
              <img className="topo__mail-logo" src="/corviamail-icone.svg" alt="" />
            </NavLink>
            <div className="topo__conta" ref={contaRef}>
              <button
                ref={abrirContaRef}
                type="button"
                className={`topo__perfil${menuContaAberto ? " topo__perfil--aberto" : ""}`}
                onClick={() => setMenuContaAberto((aberto) => !aberto)}
                aria-label={`Abrir recursos da conta de ${usuario?.full_name}`}
                aria-haspopup="menu"
                aria-expanded={menuContaAberto}
                aria-controls="menu-recursos-conta"
              >
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
              </button>

              {menuContaAberto && (
                <div
                  ref={menuContaRef}
                  id="menu-recursos-conta"
                  className="menu-conta"
                  role="menu"
                  aria-label="Recursos da conta"
                  onKeyDown={navegarNoMenuConta}
                >
                  <header className="menu-conta__identidade" role="presentation">
                    <span className="menu-conta__nome">{usuario?.full_name}</span>
                    <span className="menu-conta__email">{usuario?.email}</span>
                  </header>
                  <div className="menu-conta__recursos" role="presentation">
                    {recursosDaConta.map((recurso) => (
                      <NavLink
                        key={recurso.to}
                        to={recurso.to}
                        role="menuitem"
                        onClick={() => setMenuContaAberto(false)}
                        className={({ isActive }) => (isActive ? "ativo" : "")}
                      >
                        <Icone nome={recurso.icone} />
                        <span>{recurso.rotulo}</span>
                        {!!recurso.badge && <strong className="menu-conta__badge">{recurso.badge}</strong>}
                      </NavLink>
                    ))}
                  </div>
                  <button
                    type="button"
                    role="menuitem"
                    className="menu-conta__sair"
                    onClick={() => void encerrarSessao()}
                    disabled={saindoPeloMenu}
                  >
                    <Icone nome="sair" />
                    <span>{saindoPeloMenu ? "Saindo…" : "Sair"}</span>
                  </button>
                </div>
              )}
            </div>
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
          <img src="/corvia-logo-compacta.png" alt="CorVIA" className="gaveta__logo" />
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
          <Icone nome="sair" /> Sair da CorVIA
        </button>
      </aside>

      {acoesAberto && (
        <>
          <button className="acoes-mobile__fundo" type="button" aria-label="Fechar ações rápidas" onClick={() => setAcoesAberto(false)} />
          <section className="acoes-mobile" role="dialog" aria-modal="true" aria-label="Ações rápidas">
            <header>
              <div><small>O que você precisa fazer agora?</small><strong>Ações rápidas</strong></div>
              <button type="button" onClick={() => setAcoesAberto(false)} aria-label="Fechar"><Icone nome="fechar" /></button>
            </header>
            <div className="acoes-mobile__grade">
              {ACOES_MOBILE.map((acao, index) => (
                <NavLink key={`${acao.to}-${index}`} to={acao.to} onClick={() => setAcoesAberto(false)}>
                  <span><Icone nome={acao.icone} /></span>
                  <strong>{acao.rotulo}</strong>
                </NavLink>
              ))}
            </div>
          </section>
        </>
      )}

      <nav className="barra-mobile barra-mobile--command" aria-label="Atalhos principais" aria-hidden={interfaceBloqueada || undefined}>
        <NavLink to="/" end><IconeHoje /><span>Início</span></NavLink>
        <NavLink to="/busca"><Icone nome="busca" /><span>Buscar</span></NavLink>
        <button type="button" className="barra-mobile__acao" onClick={() => setAcoesAberto(true)} aria-expanded={acoesAberto}>
          <span className="barra-mobile__acao-icone"><Icone nome="mais" /></span><span>Ação</span>
        </button>
        <NavLink to="/assistente?modo=pessoal"><Icone nome="assistente" /><span>Assistente</span></NavLink>
        <button type="button" onClick={() => setMenuAberto(true)} aria-expanded={menuAberto}>
          <Icone nome="menu" /><span>Mais</span>
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
