import {
  type FormEvent,
  type KeyboardEvent as ReactKeyboardEvent,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { Link, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { api, assetUrl } from "../lib/api";
import BoasVindas from "./BoasVindas";
import ChatFlutuante from "./ChatFlutuante";
import Credito from "./Credito";
import Icone, { type NomeIcone } from "./Icone";
import { IconeEmergencia, IconeHoje } from "./IdentidadeClinica";

type ItemNav = {
  to: string;
  rotulo: string;
  icone: NomeIcone;
  badge?: number;
};

type SecaoNav = {
  id: string;
  rotulo: string;
  icone: NomeIcone;
  itens: ItemNav[];
};

type ContextoRecente = {
  path: string;
  titulo: string;
  detalhe: string;
  icone: NomeIcone;
  visitadoEm: number;
};

const SECOES_BASE: SecaoNav[] = [
  {
    id: "decisao",
    rotulo: "Decisão clínica",
    icone: "clinica",
    itens: [
      { to: "/assistente", rotulo: "CorVIA AI", icone: "assistente" },
      { to: "/doencas", rotulo: "Doenças e condições", icone: "doencas" },
      { to: "/triagem-sintomas", rotulo: "Triagem de sintomas", icone: "triagem" },
      { to: "/calculadoras", rotulo: "Calculadoras e escores", icone: "calculadora" },
      { to: "/medicamentos", rotulo: "Medicamentos", icone: "medicamento" },
      { to: "/interacoes", rotulo: "Interações", icone: "medicamento" },
      { to: "/fluxogramas", rotulo: "Fluxogramas", icone: "seta" },
      { to: "/diretrizes", rotulo: "Diretrizes", icone: "evidencia" },
      { to: "/condicoes", rotulo: "Condições especiais", icone: "check" },
    ],
  },
  {
    id: "pratica",
    rotulo: "Prática clínica",
    icone: "pacientes",
    itens: [
      { to: "/agenda", rotulo: "Agenda", icone: "agenda" },
      { to: "/round", rotulo: "Pacientes e round", icone: "round" },
      { to: "/receituario", rotulo: "Prescrição", icone: "prescricao" },
      { to: "/documentos", rotulo: "Documentos e solicitações", icone: "documento" },
      { to: "/avaliacao-preoperatoria", rotulo: "Avaliação pré-operatória", icone: "clinica" },
      { to: "/exames", rotulo: "Exames e marcadores", icone: "clinica" },
      { to: "/checklists", rotulo: "Checklists", icone: "check" },
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
      { to: "/galeria", rotulo: "Galeria", icone: "galeria" },
      { to: "/trilhas", rotulo: "Trilhas", icone: "seta" },
      { to: "/cursos", rotulo: "Cursos", icone: "curso" },
      { to: "/apresentacao", rotulo: "Modo apresentação", icone: "documento" },
    ],
  },
  {
    id: "comunicacao",
    rotulo: "Comunicação",
    icone: "comunicacao",
    itens: [
      { to: "/corvia-mail", rotulo: "CorVIA Mail", icone: "mail" },
      { to: "/usuarios-online", rotulo: "Rede profissional", icone: "pacientes" },
    ],
  },
  {
    id: "gestao",
    rotulo: "Conta e gestão",
    icone: "gestao",
    itens: [
      { to: "/indicadores", rotulo: "Meus indicadores", icone: "indicadores" },
      { to: "/favoritos", rotulo: "Favoritos", icone: "favorito" },
      { to: "/sincronizacao", rotulo: "Contas conectadas", icone: "sincronizar" },
      { to: "/minha-conta", rotulo: "Minha conta", icone: "conta" },
      { to: "/tour", rotulo: "Conheça a plataforma", icone: "curso" },
    ],
  },
];

const ROTULOS_CONTEXTO: Array<{
  prefixo: string;
  titulo: string;
  detalhe: string;
  icone: NomeIcone;
}> = [
  { prefixo: "/medicamentos", titulo: "Medicamentos", detalhe: "Farmacologia e segurança", icone: "medicamento" },
  { prefixo: "/interacoes", titulo: "Interações", detalhe: "Segurança medicamentosa", icone: "medicamento" },
  { prefixo: "/doencas", titulo: "Doenças e condições", detalhe: "Consulta clínica", icone: "doencas" },
  { prefixo: "/calculadoras", titulo: "Calculadoras", detalhe: "Escores e apoio à decisão", icone: "calculadora" },
  { prefixo: "/diretrizes", titulo: "Diretrizes", detalhe: "Recomendações e atualização", icone: "evidencia" },
  { prefixo: "/evidencias", titulo: "Evidências", detalhe: "Síntese científica", icone: "evidencia" },
  { prefixo: "/estudos", titulo: "Estudos", detalhe: "Literatura original", icone: "evidencia" },
  { prefixo: "/biblioteca", titulo: "Biblioteca", detalhe: "Conhecimento clínico", icone: "conhecimento" },
  { prefixo: "/exames", titulo: "Exames", detalhe: "Diagnóstico e interpretação", icone: "clinica" },
  { prefixo: "/receituario", titulo: "Prescrição", detalhe: "Produção clínica", icone: "prescricao" },
  { prefixo: "/documentos", titulo: "Documentos", detalhe: "Documentos e solicitações", icone: "documento" },
  { prefixo: "/round", titulo: "Pacientes e round", detalhe: "Continuidade do cuidado", icone: "round" },
  { prefixo: "/agenda", titulo: "Agenda", detalhe: "Organização clínica", icone: "agenda" },
  { prefixo: "/assistente", titulo: "CorVIA AI", detalhe: "Assistência contextual", icone: "assistente" },
  { prefixo: "/emergencia", titulo: "Emergência", detalhe: "Protocolos de risco imediato", icone: "emergencia" },
];

function contextoDaRota(pathname: string) {
  return ROTULOS_CONTEXTO.find((item) => pathname.startsWith(item.prefixo))
    ?? { prefixo: pathname, titulo: "CorVIA", detalhe: "Workspace clínico", icone: "clinica" as NomeIcone };
}

function iniciais(nome?: string) {
  return (nome || "Médico")
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((parte) => parte[0]?.toUpperCase())
    .join("");
}

function destinoDoComando(valor: string) {
  const termo = valor.trim();
  const normalizado = termo.toLocaleLowerCase("pt-BR");
  if (/\b(prescrev|prescri|receita|receitu)/.test(normalizado)) return "/receituario";
  if (/\b(atestado|documento|relat[oó]rio|encaminhamento|solicitar exames?|pedido de exames?)/.test(normalizado)) return "/documentos";
  if (/\b(calcul|escore|score)/.test(normalizado)) return "/calculadoras";
  if (/\b(emerg[eê]ncia|urg[eê]ncia|protocolo de emerg)/.test(normalizado)) return "/emergencia";
  if (/\b(intera[cç][aã]o)/.test(normalizado)) return "/interacoes";
  if (/\b(medicamento|f[aá]rmaco|droga)/.test(normalizado) && termo.split(/\s+/).length <= 3) return "/medicamentos";
  if (/\b(diretriz|guideline)/.test(normalizado) && termo.split(/\s+/).length <= 4) return "/diretrizes";
  if (/\b(paciente|round|enfermaria)/.test(normalizado) && termo.split(/\s+/).length <= 4) return "/round";
  return `/busca?q=${encodeURIComponent(termo)}`;
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
    <nav className="cos-nav" aria-label="Áreas da CorVIA">
      <NavLink to="/" end onClick={aoNavegar} className={({ isActive }) => `cos-nav__home${isActive ? " is-active" : ""}`}>
        <IconeHoje />
        <span><strong>Início</strong><small>Clinical Command Center</small></span>
      </NavLink>

      {secoes.map((secao) => {
        const expandida = aberta === secao.id;
        return (
          <section className={`cos-nav-group${secaoAtiva === secao.id ? " is-current" : ""}`} key={secao.id}>
            <button
              type="button"
              className="cos-nav-group__trigger"
              onClick={() => setAberta(expandida ? "" : secao.id)}
              aria-expanded={expandida}
              aria-controls={`cos-nav-${secao.id}`}
            >
              <Icone nome={secao.icone} />
              <span>{secao.rotulo}</span>
              <Icone nome="chevron" className="cos-nav-group__chevron" />
            </button>
            <div id={`cos-nav-${secao.id}`} className={`cos-nav-group__items${expandida ? " is-open" : ""}`} aria-hidden={!expandida}>
              {secao.itens.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  tabIndex={expandida ? undefined : -1}
                  onClick={aoNavegar}
                  className={({ isActive }) => (isActive ? "is-active" : "")}
                >
                  <Icone nome={item.icone} />
                  <span>{item.rotulo}</span>
                  {!!item.badge && <strong>{item.badge}</strong>}
                </NavLink>
              ))}
            </div>
          </section>
        );
      })}
    </nav>
  );
}

function IntelligenceRail({ pathname }: { pathname: string }) {
  const contexto = contextoDaRota(pathname);
  const conteudo = useMemo(() => {
    if (pathname.startsWith("/medicamentos") || pathname.startsWith("/interacoes")) {
      return {
        titulo: "Inteligência farmacológica",
        texto: "Conecte medicamento, indicação, segurança, evidência e ação clínica sem sair do contexto.",
        links: [
          { to: "/interacoes", rotulo: "Revisar interações", icone: "medicamento" as NomeIcone },
          { to: "/evidencias", rotulo: "Abrir evidências", icone: "evidencia" as NomeIcone },
          { to: "/receituario", rotulo: "Ir para prescrição", icone: "prescricao" as NomeIcone },
        ],
      };
    }
    if (pathname.startsWith("/doencas") || pathname.startsWith("/triagem-sintomas")) {
      return {
        titulo: "Inteligência clínica",
        texto: "Navegue da condição para diretrizes, fármacos, escores, exames e evidências relacionadas.",
        links: [
          { to: "/diretrizes", rotulo: "Ver diretrizes", icone: "evidencia" as NomeIcone },
          { to: "/calculadoras", rotulo: "Abrir escores", icone: "calculadora" as NomeIcone },
          { to: "/medicamentos", rotulo: "Explorar fármacos", icone: "medicamento" as NomeIcone },
        ],
      };
    }
    if (pathname.startsWith("/evidencias") || pathname.startsWith("/estudos") || pathname.startsWith("/diretrizes")) {
      return {
        titulo: "Inteligência científica",
        texto: "Cruze estudos, sínteses de evidência, recomendações e aplicação prática.",
        links: [
          { to: "/biblioteca", rotulo: "Abrir biblioteca", icone: "conhecimento" as NomeIcone },
          { to: "/estudos", rotulo: "Estudos relacionados", icone: "evidencia" as NomeIcone },
          { to: "/assistente", rotulo: "Discutir com CorVIA AI", icone: "assistente" as NomeIcone },
        ],
      };
    }
    if (pathname.startsWith("/exames") || pathname.startsWith("/galeria")) {
      return {
        titulo: "Inteligência diagnóstica",
        texto: "Relacione achados, critérios, condições clínicas e próximos passos diagnósticos.",
        links: [
          { to: "/doencas", rotulo: "Condições relacionadas", icone: "doencas" as NomeIcone },
          { to: "/calculadoras", rotulo: "Critérios e escores", icone: "calculadora" as NomeIcone },
          { to: "/assistente", rotulo: "Analisar contexto", icone: "assistente" as NomeIcone },
        ],
      };
    }
    return {
      titulo: "CorVIA Intelligence",
      texto: "O sistema acompanha seu contexto e aproxima conhecimento, decisão e ação clínica.",
      links: [
        { to: "/assistente", rotulo: "Perguntar à CorVIA AI", icone: "assistente" as NomeIcone },
        { to: "/diretrizes", rotulo: "Atualização clínica", icone: "evidencia" as NomeIcone },
        { to: "/favoritos", rotulo: "Abrir favoritos", icone: "favorito" as NomeIcone },
      ],
    };
  }, [pathname]);

  return (
    <aside className="cos-intelligence" aria-label="CorVIA Intelligence">
      <div className="cos-intelligence__status"><i /> contexto ativo</div>
      <div className="cos-intelligence__context">
        <span><Icone nome={contexto.icone} /></span>
        <div><small>Você está em</small><strong>{contexto.titulo}</strong></div>
      </div>
      <section className="cos-intelligence__card">
        <p className="eyebrow">CorVIA Intelligence</p>
        <h2>{conteudo.titulo}</h2>
        <p>{conteudo.texto}</p>
        <div className="cos-intelligence__links">
          {conteudo.links.map((link) => (
            <Link to={link.to} key={link.to + link.rotulo}><Icone nome={link.icone} /><span>{link.rotulo}</span><Icone nome="seta" /></Link>
          ))}
        </div>
      </section>
      <section className="cos-intelligence__graph">
        <span className="cos-intelligence__graph-icon">◎</span>
        <div><strong>Tudo com Tudo</strong><small>Explore relações entre conhecimento, evidência e prática.</small></div>
        <Link to="/busca" aria-label="Explorar relações"><Icone nome="seta" /></Link>
      </section>
      <Link className="cos-intelligence__ask" to="/assistente"><Icone nome="assistente" /><span><strong>Perguntar no contexto</strong><small>A CorVIA AI usa a área atual como ponto de partida.</small></span></Link>
    </aside>
  );
}

export default function ShellClinicalOS() {
  const { usuario, sair } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [pendentes, setPendentes] = useState(0);
  const [menuAberto, setMenuAberto] = useState(false);
  const [contaAberta, setContaAberta] = useState(false);
  const [comando, setComando] = useState("");
  const [fotoQuebrada, setFotoQuebrada] = useState(false);
  const buscaRef = useRef<HTMLInputElement>(null);
  const contaRef = useRef<HTMLDivElement>(null);

  const naEmergencia = location.pathname.startsWith("/emergencia");
  const modoFoco = [
    "/emergencia",
    "/receituario",
    "/documentos",
    "/agenda",
    "/round",
    "/corvia-mail",
    "/caixa-de-email",
    "/avaliacao-preoperatoria",
  ].some((prefixo) => location.pathname.startsWith(prefixo));

  useEffect(() => {
    if (usuario?.role !== "admin") return;
    api.get<unknown[]>("/admin/users?status=pendente")
      .then((lista) => setPendentes(lista.length))
      .catch(() => undefined);
  }, [usuario?.role]);

  useEffect(() => setFotoQuebrada(false), [usuario?.photo_url]);
  useEffect(() => {
    setContaAberta(false);
    setMenuAberto(false);
  }, [location.pathname]);

  useEffect(() => {
    if (location.pathname === "/" || location.pathname.startsWith("/admin")) return;
    const meta = contextoDaRota(location.pathname);
    const novo: ContextoRecente = {
      path: location.pathname,
      titulo: meta.titulo,
      detalhe: meta.detalhe,
      icone: meta.icone,
      visitadoEm: Date.now(),
    };
    try {
      const anteriores = JSON.parse(localStorage.getItem("corvia:contextos-recentes") || "[]") as ContextoRecente[];
      const atualizados = [novo, ...anteriores.filter((item) => item.path !== novo.path)].slice(0, 6);
      localStorage.setItem("corvia:contextos-recentes", JSON.stringify(atualizados));
    } catch {
      // Navegação nunca deve falhar por indisponibilidade de armazenamento local.
    }
  }, [location.pathname]);

  useEffect(() => {
    function atalho(evento: KeyboardEvent) {
      if ((evento.ctrlKey || evento.metaKey) && evento.key.toLocaleLowerCase() === "k") {
        evento.preventDefault();
        buscaRef.current?.focus();
      }
      if (evento.key === "Escape") {
        setContaAberta(false);
        setMenuAberto(false);
      }
    }
    document.addEventListener("keydown", atalho);
    return () => document.removeEventListener("keydown", atalho);
  }, []);

  useEffect(() => {
    if (!contaAberta) return;
    function fora(evento: PointerEvent) {
      if (!contaRef.current?.contains(evento.target as Node)) setContaAberta(false);
    }
    document.addEventListener("pointerdown", fora);
    return () => document.removeEventListener("pointerdown", fora);
  }, [contaAberta]);

  useEffect(() => {
    document.body.classList.toggle("menu-clinico-aberto", menuAberto);
    return () => document.body.classList.remove("menu-clinico-aberto");
  }, [menuAberto]);

  const secoes = useMemo(() => {
    if (usuario?.role !== "admin") return SECOES_BASE;
    return SECOES_BASE.map((secao) => secao.id !== "gestao" ? secao : {
      ...secao,
      itens: [
        ...secao.itens,
        { to: "/admin", rotulo: "Administração", icone: "gestao" as NomeIcone, badge: pendentes },
        { to: "/admin/usuarios", rotulo: "Assinantes", icone: "pacientes" as NomeIcone },
        { to: "/fila-telediagnostico", rotulo: "Fila de telediagnóstico", icone: "evidencia" as NomeIcone },
      ],
    });
  }, [pendentes, usuario?.role]);

  function executarComando(evento: FormEvent) {
    evento.preventDefault();
    if (comando.trim().length < 2) return;
    navigate(destinoDoComando(comando));
    setComando("");
  }

  async function encerrarSessao() {
    setMenuAberto(false);
    setContaAberta(false);
    await sair();
    navigate("/entrar", { replace: true });
  }

  function navegarConta(evento: ReactKeyboardEvent<HTMLDivElement>) {
    if (!["ArrowDown", "ArrowUp", "Home", "End"].includes(evento.key)) return;
    const itens = Array.from(evento.currentTarget.querySelectorAll<HTMLElement>('[role="menuitem"]'));
    if (!itens.length) return;
    evento.preventDefault();
    const atual = itens.indexOf(document.activeElement as HTMLElement);
    if (evento.key === "Home") itens[0].focus();
    else if (evento.key === "End") itens[itens.length - 1].focus();
    else if (evento.key === "ArrowDown") itens[(atual + 1 + itens.length) % itens.length].focus();
    else itens[(atual - 1 + itens.length) % itens.length].focus();
  }

  return (
    <div className={`app-clinico clinical-os${modoFoco ? " clinical-os--focus" : ""}${naEmergencia ? " clinical-os--emergency" : ""}`}>
      <a className="pular-conteudo" href="#conteudo-principal">Pular para o conteúdo</a>

      <aside className="cos-sidebar" aria-label="Navegação principal">
        <NavLink to="/" className="cos-brand" aria-label="CorVIA — início">
          <span className="cos-brand__mark"><img src="/corvia-logo-compacta.png" alt="" /></span>
          <span className="cos-brand__text"><strong>CorVIA</strong><small>Clinical OS</small></span>
        </NavLink>
        <Navegacao secoes={secoes} />
        <div className="cos-sidebar__footer">
          <Link to="/busca" className="cos-relations"><span>◎</span><span><strong>Explorar relações</strong><small>Knowledge Graph</small></span></Link>
          <button type="button" onClick={() => void encerrarSessao()}><Icone nome="sair" /><span>Sair</span></button>
          <small>Suporte à decisão. O julgamento clínico permanece do médico.</small>
        </div>
      </aside>

      <div className="cos-shell">
        <header className="cos-topbar">
          <button type="button" className="cos-topbar__menu" onClick={() => setMenuAberto(true)} aria-label="Abrir navegação" aria-expanded={menuAberto}>
            <Icone nome="menu" />
          </button>
          <NavLink to="/" className="cos-topbar__mobile-brand" aria-label="CorVIA — início"><img src="/corvia-logo-compacta.png" alt="" /></NavLink>

          <form className="cos-command-mini" role="search" onSubmit={executarComando}>
            <Icone nome="busca" />
            <input
              ref={buscaRef}
              value={comando}
              onChange={(evento) => setComando(evento.target.value)}
              placeholder="Pesquisar ou executar uma ação..."
              aria-label="Pesquisar ou executar uma ação na CorVIA"
            />
            <kbd aria-hidden="true">⌘ K</kbd>
            <button type="submit" aria-label="Executar"><Icone nome="seta" /></button>
          </form>

          <div className="cos-topbar__actions">
            {!naEmergencia && (
              <button type="button" className="cos-emergency" onClick={() => navigate("/emergencia")}>
                <IconeEmergencia /><span>Emergência</span>
              </button>
            )}
            <NavLink to="/corvia-mail" className="cos-topbar__icon" aria-label="CorVIA Mail"><Icone nome="mail" /></NavLink>
            <div className="cos-account" ref={contaRef}>
              <button
                type="button"
                className={`cos-account__trigger${contaAberta ? " is-open" : ""}`}
                onClick={() => setContaAberta((valor) => !valor)}
                aria-haspopup="menu"
                aria-expanded={contaAberta}
              >
                {usuario?.photo_url && !fotoQuebrada ? (
                  <img src={assetUrl(usuario.photo_url)} alt="" onError={() => setFotoQuebrada(true)} />
                ) : <span className="cos-account__avatar">{iniciais(usuario?.full_name)}</span>}
                <span className="cos-account__identity"><strong>{usuario?.full_name}</strong><small>{usuario?.role === "admin" ? "Administrador" : "Profissional"}</small></span>
                <Icone nome="chevron" />
              </button>
              {contaAberta && (
                <div className="cos-account-menu" role="menu" onKeyDown={navegarConta}>
                  <div className="cos-account-menu__head"><strong>{usuario?.full_name}</strong><small>{usuario?.email}</small></div>
                  <NavLink to="/minha-conta" role="menuitem"><Icone nome="conta" />Minha conta</NavLink>
                  <NavLink to="/assinatura" role="menuitem"><Icone nome="check" />Assinatura e plano</NavLink>
                  <NavLink to="/sincronizacao" role="menuitem"><Icone nome="sincronizar" />Contas conectadas</NavLink>
                  <NavLink to="/favoritos" role="menuitem"><Icone nome="favorito" />Favoritos</NavLink>
                  {usuario?.role === "admin" && <NavLink to="/admin" role="menuitem"><Icone nome="gestao" />Administração {pendentes > 0 && <strong className="cos-account-menu__badge">{pendentes}</strong>}</NavLink>}
                  <button type="button" role="menuitem" onClick={() => void encerrarSessao()}><Icone nome="sair" />Sair</button>
                </div>
              )}
            </div>
          </div>
        </header>

        <div className={`cos-workspace${modoFoco ? " cos-workspace--focus" : ""}`}>
          <main className="conteudo cos-content" id="conteudo-principal" tabIndex={-1}>
            <Outlet />
            <Credito compacto />
          </main>
          {!modoFoco && <IntelligenceRail pathname={location.pathname} />}
        </div>
      </div>

      <div className={`cos-drawer-backdrop${menuAberto ? " is-visible" : ""}`} onClick={() => setMenuAberto(false)} aria-hidden="true" />
      <aside className={`cos-drawer${menuAberto ? " is-open" : ""}`} aria-hidden={!menuAberto} aria-label="Navegação móvel">
        <div className="cos-drawer__head"><NavLink to="/" onClick={() => setMenuAberto(false)}><img src="/corvia-logo-compacta.png" alt="CorVIA" /></NavLink><button type="button" onClick={() => setMenuAberto(false)} aria-label="Fechar navegação"><Icone nome="fechar" /></button></div>
        <Navegacao secoes={secoes} aoNavegar={() => setMenuAberto(false)} />
      </aside>

      <nav className="cos-mobilebar" aria-label="Ações principais">
        <NavLink to="/" end><IconeHoje /><span>Início</span></NavLink>
        <NavLink to="/receituario"><Icone nome="prescricao" /><span>Prescrever</span></NavLink>
        <NavLink to="/busca"><Icone nome="busca" /><span>Buscar</span></NavLink>
        <button type="button" onClick={() => setMenuAberto(true)}><Icone nome="mais" /><span>Mais</span></button>
      </nav>

      <BoasVindas />
      {!naEmergencia && <ChatFlutuante />}
      {!naEmergencia && (
        <NavLink className="cos-emergency-fab" to="/emergencia" aria-label="Abrir Modo Emergência"><IconeEmergencia /></NavLink>
      )}
    </div>
  );
}
