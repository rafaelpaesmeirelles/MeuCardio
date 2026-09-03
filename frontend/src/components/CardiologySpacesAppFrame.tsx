import { type FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { Link, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import usePrescriptionQueueBadge from "../hooks/usePrescriptionQueueBadge";
import { api, assetUrl } from "../lib/api";
import { useAuth } from "../lib/auth";
import { useCorviaTheme } from "../lib/corviaTheme";
import {
  catalogRoutesFor,
  CLINICAL_SPACES,
  quickRoutesFor,
  resolveClinicalRoute,
  type ClinicalRouteDefinition,
  type FunctionalSpace,
} from "../lib/clinicalRouteRegistry";
import { nomeComTratamento } from "../lib/clinicalIdentity";
import BoasVindas from "./BoasVindas";
import ChatFlutuante from "./ChatFlutuante";
import ClinicalFunctionFigure from "./ClinicalFunctionFigure";
import CorviaThemeSelector from "./CorviaThemeSelector";
import Credito from "./Credito";
import Icone from "./Icone";
import { IconeEmergencia } from "./IdentidadeClinica";
import PersonalAssistantPanel from "./PersonalAssistantPanel";

type RecentContext = {
  path: string;
  title: string;
  detail: string;
  visitedAt: number;
};

const SPACE_ORDER: FunctionalSpace[] = ["consultorio", "hospital", "ensino", "pesquisa", "gestao"];

/**
 * Matrizes internas que já possuem composição Cardiology Spaces própria.
 *
 * Estas páginas não recebem a camada de compatibilidade dos módulos legados:
 * seus grids, proporções e estados responsivos são parte do contrato aprovado.
 */
const NATIVE_PAGE_PATHS = new Set([
  "/calculadoras",
  "/emergencia",
  "/trilhas",
  "/evidencias",
  "/indicadores",
]);

const SPACE_ENTRY: Record<FunctionalSpace, string> = {
  consultorio: "/agenda",
  hospital: "/round",
  ensino: "/trilhas",
  pesquisa: "/evidencias",
  gestao: "/indicadores",
};

function initials(name?: string) {
  return (name || "Médico")
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toLocaleUpperCase("pt-BR"))
    .join("");
}

function recentKey(userId?: number) {
  return userId ? `corvia:contextos-recentes:${userId}` : "";
}

function normalized(value: string) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("pt-BR")
    .trim();
}

function commandDestination(value: string) {
  const term = value.trim();
  const text = normalized(term);
  if (/\b(ecg|eletrocardiograma|holter|mapa|ecocardiograma|ressonancia|tomografia|exame cardiovascular)\b/.test(text)) return "/exames-ia";
  if (/\b(prescrev|prescri|receita|receitu)/.test(text)) return "/receituario";
  if (/\b(atestado|documento|relatorio|encaminhamento|solicitar exames?|pedido de exames?)\b/.test(text)) return "/documentos";
  if (/\b(calcul|escore|score|dose)\b/.test(text)) return "/calculadoras";
  if (/\b(emergencia|urgencia)\b/.test(text)) return "/emergencia";
  if (/\b(interacao|interacoes)\b/.test(text)) return "/interacoes";
  return `/busca?q=${encodeURIComponent(term)}`;
}

function navigationLabel(route: ClinicalRouteDefinition) {
  return route.shortName || route.name;
}

function RouteLink({ route, current, badge, onNavigate }: {
  route: ClinicalRouteDefinition;
  current: ClinicalRouteDefinition;
  badge?: number;
  onNavigate?: () => void;
}) {
  const selected = current.path === route.path || current.parent === route.path;
  return (
    <NavLink
      to={route.path}
      onClick={onNavigate}
      className={`cv-nav-link${selected ? " is-current" : ""}${route.featured ? " is-featured" : ""}`}
      data-feature={route.path === "/exames-ia" ? "exam-ai" : undefined}
      aria-current={selected ? "page" : undefined}
    >
      <span className="cv-nav-link__icon"><Icone nome={route.icon} /></span>
      <span className="cv-nav-link__copy"><strong>{navigationLabel(route)}</strong>{route.featured && <small>Destaque</small>}</span>
      {typeof badge === "number" && badge > 0 && <span className="cv-nav-link__badge" aria-label={`${badge} pendentes`}>{badge}</span>}
      <Icone nome="chevron" className="cv-nav-link__chevron" />
    </NavLink>
  );
}

function ContextIntelligence({ route, space, routes }: {
  route: ClinicalRouteDefinition;
  space: FunctionalSpace;
  routes: ClinicalRouteDefinition[];
}) {
  const related = routes.filter((candidate) => candidate.path !== route.path && candidate.path !== route.parent).slice(0, 3);
  return (
    <aside className="cv-intelligence" aria-label="Inteligência contextual">
      <div className="cv-intelligence__status"><i aria-hidden="true" /> contexto conectado</div>
      <div className="cv-intelligence__route">
        <span><Icone nome={route.icon} /></span>
        <div><small>Você está em</small><strong>{route.shortName || route.name}</strong></div>
      </div>

      <section className="cv-intelligence__hero">
        <span className="cv-intelligence__spark" aria-hidden="true">✦</span>
        <p>CORVIA INTELLIGENCE</p>
        <h2>Tudo com Tudo, dentro do seu contexto.</h2>
        <span>{CLINICAL_SPACES[space].description}</span>
        <Link to="/busca?modo=tudo-com-tudo"><Icone nome="sincronizar" /><strong>Explorar relações</strong><Icone nome="seta" /></Link>
      </section>

      <section className="cv-intelligence__related">
        <header><span>CONEXÕES IMEDIATAS</span><small>{related.length}</small></header>
        <div>
          {related.map((candidate) => (
            <Link to={candidate.path} key={candidate.path}>
              <span><Icone nome={candidate.icon} /></span>
              <strong>{navigationLabel(candidate)}</strong>
              <Icone nome="seta" />
            </Link>
          ))}
        </div>
      </section>

      <button type="button" className="cv-intelligence__ask" onClick={() => window.dispatchEvent(new Event("corvia:abrir-assistente-pessoal"))}>
        <span aria-hidden="true">✦</span>
        <span><strong>Perguntar no contexto</strong><small>Levar esta tela ao Apoio CorVIA</small></span>
        <Icone nome="seta" />
      </button>

      <p className="cv-intelligence__safety"><Icone nome="check" /> A decisão clínica permanece sob responsabilidade do médico.</p>
    </aside>
  );
}

export default function CardiologySpacesAppFrame() {
  const { usuario, sair } = useAuth();
  const { theme } = useCorviaTheme();
  const location = useLocation();
  const navigate = useNavigate();
  const route = resolveClinicalRoute(location.pathname);
  const space: FunctionalSpace = route.space === "home" ? "consultorio" : route.space;
  const spaceMeta = CLINICAL_SPACES[space];
  const isAdmin = usuario?.role === "admin";
  const signaturePending = usePrescriptionQueueBadge(isAdmin);
  const [adminPending, setAdminPending] = useState(0);
  const [command, setCommand] = useState("");
  const [catalogQuery, setCatalogQuery] = useState("");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [accountOpen, setAccountOpen] = useState(false);
  const [assistantOpen, setAssistantOpen] = useState(false);
  const [brokenPhoto, setBrokenPhoto] = useState(false);
  const searchRef = useRef<HTMLInputElement>(null);
  const accountRef = useRef<HTMLDivElement>(null);
  const drawerRef = useRef<HTMLElement>(null);
  const drawerCloseRef = useRef<HTMLButtonElement>(null);
  const drawerTriggerRef = useRef<HTMLElement | null>(null);

  const catalogBySpace = useMemo(() => SPACE_ORDER.map((candidateSpace) => ({
    space: candidateSpace,
    routes: catalogRoutesFor(candidateSpace, isAdmin),
  })), [isAdmin]);

  const currentRoutes = useMemo(() => {
    const seen = new Set<string>();
    return [...quickRoutesFor(space, isAdmin), ...catalogRoutesFor(space, isAdmin)].filter((candidate) => {
      if (seen.has(candidate.path)) return false;
      seen.add(candidate.path);
      return true;
    });
  }, [isAdmin, space]);

  const filteredCatalog = useMemo(() => {
    const query = normalized(catalogQuery);
    if (!query) return catalogBySpace;
    return catalogBySpace.map((section) => ({
      ...section,
      routes: section.routes.filter((candidate) => normalized(`${candidate.name} ${candidate.shortName || ""}`).includes(query)),
    }));
  }, [catalogBySpace, catalogQuery]);

  const emergency = route.group === "emergencia";
  const nativePage = NATIVE_PAGE_PATHS.has(location.pathname);
  const logoSrc = theme === "light" ? "/corvia-logo-spaces.svg" : "/corvia-logo-spaces-dark.svg";

  useEffect(() => {
    if (!isAdmin) return;
    api.get<unknown[]>("/admin/users?status=pendente").then((users) => setAdminPending(users.length)).catch(() => undefined);
  }, [isAdmin]);

  useEffect(() => { setBrokenPhoto(false); }, [usuario?.photo_url]);
  useEffect(() => { setDrawerOpen(false); setAccountOpen(false); setCatalogQuery(""); }, [location.pathname]);

  useEffect(() => {
    if (location.pathname === "/" || location.pathname.startsWith("/admin")) return;
    const key = recentKey(usuario?.id);
    if (!key) return;
    const recent: RecentContext = {
      path: location.pathname,
      title: route.shortName || route.name,
      detail: spaceMeta.label,
      visitedAt: Date.now(),
    };
    try {
      const previous = JSON.parse(sessionStorage.getItem(key) || "[]") as RecentContext[];
      sessionStorage.setItem(key, JSON.stringify([recent, ...previous.filter((item) => item.path !== recent.path)].slice(0, 6)));
    } catch { /* A navegação não depende do armazenamento de conveniência. */ }
  }, [location.pathname, route.name, route.shortName, spaceMeta.label, usuario?.id]);

  useEffect(() => {
    function openAssistant() { setDrawerOpen(false); setAccountOpen(false); setAssistantOpen(true); }
    window.addEventListener("corvia:abrir-assistente-pessoal", openAssistant);
    return () => window.removeEventListener("corvia:abrir-assistente-pessoal", openAssistant);
  }, []);

  useEffect(() => {
    function keyboard(event: KeyboardEvent) {
      if ((event.ctrlKey || event.metaKey) && event.key.toLocaleLowerCase("pt-BR") === "k") {
        event.preventDefault();
        searchRef.current?.focus();
      }
      if (event.key === "Escape") {
        setAccountOpen(false);
        setAssistantOpen(false);
      }
    }
    document.addEventListener("keydown", keyboard);
    return () => document.removeEventListener("keydown", keyboard);
  }, []);

  useEffect(() => {
    if (!accountOpen) return;
    function outside(event: PointerEvent) {
      if (!accountRef.current?.contains(event.target as Node)) setAccountOpen(false);
    }
    document.addEventListener("pointerdown", outside);
    return () => document.removeEventListener("pointerdown", outside);
  }, [accountOpen]);

  useEffect(() => {
    document.body.classList.toggle("cv-overlay-open", drawerOpen || assistantOpen);
    if (!drawerOpen) return () => document.body.classList.remove("cv-overlay-open");
    requestAnimationFrame(() => drawerCloseRef.current?.focus());
    function trap(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        closeDrawer(true);
        return;
      }
      if (event.key !== "Tab") return;
      const controls = Array.from(drawerRef.current?.querySelectorAll<HTMLElement>('a[href],button:not([disabled]),input:not([disabled]),[tabindex]:not([tabindex="-1"])') || [])
        .filter((element) => element.offsetParent !== null);
      if (!controls.length) return;
      const first = controls[0];
      const last = controls[controls.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }
    document.addEventListener("keydown", trap);
    return () => {
      document.removeEventListener("keydown", trap);
      document.body.classList.remove("cv-overlay-open");
    };
  }, [drawerOpen, assistantOpen]);

  function openDrawer(trigger: HTMLElement) {
    drawerTriggerRef.current = trigger;
    setAssistantOpen(false);
    setAccountOpen(false);
    setDrawerOpen(true);
  }

  function closeDrawer(restoreFocus: boolean) {
    setDrawerOpen(false);
    if (restoreFocus) requestAnimationFrame(() => drawerTriggerRef.current?.focus());
  }

  function executeCommand(event: FormEvent) {
    event.preventDefault();
    if (command.trim().length < 2) return;
    navigate(commandDestination(command));
    setCommand("");
  }

  async function signOut() {
    setDrawerOpen(false);
    setAccountOpen(false);
    setAssistantOpen(false);
    const key = recentKey(usuario?.id);
    if (key) {
      try { sessionStorage.removeItem(key); } catch { /* Logout não depende do storage. */ }
    }
    await sair();
    navigate("/entrar", { replace: true });
  }

  function routeBadge(candidate: ClinicalRouteDefinition) {
    if (candidate.path === "/receitas-para-assinatura") return signaturePending;
    if (candidate.path === "/admin") return adminPending;
    return undefined;
  }

  return (
    <div
      className={`cv-app cv-app--${space}${emergency ? " cv-app--emergency" : ""}`}
      data-space={space}
      data-layout={route.layout}
      data-has-intelligence={route.intelligence ? "true" : "false"}
    >
      <a className="cv-skip" href="#conteudo-principal">Pular para o conteúdo</a>

      <aside className="cv-sidebar" aria-label={`Navegação do espaço ${spaceMeta.label}`}>
        <span className="cv-sidebar__title"><small>MEUS</small><strong>ESPAÇOS</strong></span>
        <nav className="cv-space-switcher" aria-label="Mudar espaço">
          {SPACE_ORDER.map((candidateSpace) => {
            const candidate = CLINICAL_SPACES[candidateSpace];
            return (
              <NavLink
                key={candidateSpace}
                to={SPACE_ENTRY[candidateSpace]}
                className={candidateSpace === space ? "is-active" : undefined}
                aria-current={candidateSpace === space ? "location" : undefined}
                aria-label={candidate.label}
                style={{ "--cv-switch-rgb": candidate.accentRgb } as React.CSSProperties}
              >
                <Icone nome={candidate.icon} /><span>{candidate.label}</span>
              </NavLink>
            );
          })}
        </nav>
        <div className="cv-sidebar__footer">
          <button type="button" className="cv-all-functions" onClick={(event) => openDrawer(event.currentTarget)} aria-label="Todas as funções">
            <Icone nome="mais" /><span>Todas as funções</span>
          </button>
          <button type="button" className="cv-assistant-launch" onClick={() => setAssistantOpen(true)} aria-label="Apoio CorVIA">
            <span aria-hidden="true">✦</span><span>Apoio CorVIA</span>
          </button>
        </div>
      </aside>

      <div className="cv-shell">
        <header className="cv-topbar">
          <button type="button" className="cv-topbar__menu" onClick={(event) => openDrawer(event.currentTarget)} aria-label="Abrir navegação"><Icone nome="menu" /></button>
          <NavLink to="/" className="cv-topbar__brand" aria-label="CorVIA — início"><img src={logoSrc} alt="CorVIA Cardiology Spaces" /></NavLink>
          <div className="cv-topbar__context"><span>{spaceMeta.label}</span><i>·</i><strong>{route.shortName || route.name}</strong></div>
          <form className="cv-command" role="search" onSubmit={executeCommand}>
            <Icone nome="sincronizar" />
            <input ref={searchRef} value={command} onChange={(event) => setCommand(event.target.value)} placeholder="Tudo com Tudo — relações, evidências e funções" aria-label="Tudo com Tudo" />
            <kbd>⌘ K</kbd>
            <button type="submit" aria-label="Executar busca"><Icone nome="seta" /></button>
          </form>
          <div className="cv-topbar__actions">
            <NavLink to="/documentos" className="cv-icon-button" aria-label="Criar documento"><Icone nome="adicionar" /></NavLink>
            <NavLink to="/diretrizes" className="cv-icon-button cv-topbar__updates" aria-label="Atualizações clínicas"><Icone nome="notificacao" /></NavLink>
            <NavLink to="/corvia-mail" className="cv-icon-button cv-topbar__mail" aria-label="CorVIA Mail"><Icone nome="mail" /></NavLink>
            <div className="cv-account" ref={accountRef}>
              <button
                type="button"
                className="cv-account__trigger"
                onClick={() => setAccountOpen((open) => !open)}
                aria-controls="cv-account-panel"
                aria-expanded={accountOpen}
                aria-label={`${accountOpen ? "Fechar" : "Abrir"} menu da conta de ${nomeComTratamento(usuario)}`}
              >
                {usuario?.photo_url && !brokenPhoto
                  ? <img src={assetUrl(usuario.photo_url)} alt="" onError={() => setBrokenPhoto(true)} />
                  : <span className="cv-account__avatar">{initials(usuario?.full_name)}</span>}
                <span className="cv-account__copy"><strong>{nomeComTratamento(usuario, true)}</strong><small>{isAdmin ? "Administrador" : "Profissional"}</small></span>
                <Icone nome="chevron" />
              </button>
              {accountOpen && (
                <div className="cv-account-menu" id="cv-account-panel">
                  <header><strong>{nomeComTratamento(usuario)}</strong><small>{usuario?.email}</small></header>
                  <CorviaThemeSelector variant="menu" />
                  <NavLink to="/minha-conta"><Icone nome="conta" />Minha conta</NavLink>
                  <NavLink to="/sincronizacao"><Icone nome="sincronizar" />Contas conectadas</NavLink>
                  <NavLink to="/favoritos"><Icone nome="favorito" />Notas & Favoritos</NavLink>
                  {isAdmin && <NavLink to="/admin"><Icone nome="gestao" />Administração{adminPending > 0 && <span>{adminPending}</span>}</NavLink>}
                  <button type="button" onClick={() => void signOut()}><Icone nome="sair" />Sair</button>
                </div>
              )}
            </div>
          </div>
        </header>

        <div className="cv-workspace">
          <section className="cv-stage" aria-label={`Espaço ${spaceMeta.label}`}>
            <header
              className={`cv-space-horizon${theme === "light" ? " cv-space-horizon--function" : ""}`}
              style={theme === "dark" ? { "--cv-room": `url(${spaceMeta.roomImage})` } as React.CSSProperties : undefined}
            >
              <div className="cv-space-horizon__signal" aria-hidden="true"><span /><i /><b /></div>
              <div className="cv-space-horizon__copy">
                <p><Icone nome={spaceMeta.icon} /> {spaceMeta.label} <i>·</i> {spaceMeta.eyebrow}</p>
                <strong>{route.shortName || route.name}</strong>
                <span>{spaceMeta.description}</span>
              </div>
              {theme === "light" ? (
                <ClinicalFunctionFigure key={location.pathname} icon={route.icon} group={route.group} space={space} />
              ) : (
                <div className="cv-space-horizon__orb" aria-hidden="true"><span>∑</span><i /><b /></div>
              )}
            </header>

            <nav className="cv-function-deck" aria-label={`Funções rápidas de ${spaceMeta.label}`}>
              <div className="cv-function-deck__label"><span>AGORA</span><strong>{route.shortName || route.name}</strong></div>
              <div className="cv-function-deck__routes">
                {currentRoutes.slice(0, 7).map((candidate) => (
                  <RouteLink key={`deck-${space}-${candidate.path}`} route={candidate} current={route} badge={routeBadge(candidate)} />
                ))}
              </div>
              <button type="button" onClick={(event) => openDrawer(event.currentTarget)} aria-label="Abrir todas as funções"><Icone nome="mais" /></button>
            </nav>

            <main className={`cv-content${nativePage ? "" : " clinical-os"}`} id="conteudo-principal" tabIndex={-1}>
              {nativePage ? (
                <Outlet />
              ) : (
                <div className="conteudo cos-content">
                  <Outlet />
                </div>
              )}
              <Credito compacto />
            </main>
          </section>
          {route.intelligence && <ContextIntelligence route={route} space={space} routes={currentRoutes} />}
        </div>
      </div>

      <nav className="cv-global-dock" aria-label="Ações globais">
        <NavLink to="/receituario"><Icone nome="prescricao" /><span>Prescrever</span></NavLink>
        <NavLink to="/documentos"><Icone nome="clinica" /><span>Solicitar exames</span></NavLink>
        <NavLink to="/prontuario"><Icone nome="pacientes" /><span>Prontuário</span></NavLink>
        <NavLink to="/documentos"><Icone nome="documento" /><span>Documentos</span></NavLink>
        <NavLink to="/busca?modo=tudo-com-tudo"><Icone nome="sincronizar" /><span>Tudo com Tudo</span></NavLink>
        <button type="button" onClick={() => setAssistantOpen(true)}><Icone nome="assistente" /><span>Apoio CorVIA</span></button>
      </nav>

      <div className={`cv-drawer-backdrop${drawerOpen ? " is-open" : ""}`} aria-hidden="true" onClick={() => closeDrawer(true)} />
      <aside ref={drawerRef} className={`cv-drawer${drawerOpen ? " is-open" : ""}`} role="dialog" aria-modal={drawerOpen ? "true" : undefined} aria-hidden={!drawerOpen} aria-label="Todas as funções">
        <header className="cv-drawer__header">
          <NavLink to="/" onClick={() => setDrawerOpen(false)}><img src={logoSrc} alt="CorVIA Cardiology Spaces" /></NavLink>
          <button ref={drawerCloseRef} type="button" onClick={() => closeDrawer(true)} aria-label="Fechar"><Icone nome="fechar" /></button>
        </header>
        <div className="cv-drawer__intro"><span>UNIVERSO CORVIA</span><h2>Todas as funções, um único sistema.</h2><p>O ambiente muda. Suas ferramentas continuam conectadas.</p></div>
        <label className="cv-drawer__search"><Icone nome="busca" /><input type="search" value={catalogQuery} onChange={(event) => setCatalogQuery(event.target.value)} placeholder="Buscar função" /></label>
        <button type="button" className="cv-drawer__assistant" onClick={() => { setDrawerOpen(false); setAssistantOpen(true); }}><span aria-hidden="true">✦</span><span><strong>Apoio CorVIA</strong><small>Leve seu contexto para o assistente</small></span><Icone nome="seta" /></button>
        <div className="cv-drawer__catalog">
          {filteredCatalog.map((section) => {
            const meta = CLINICAL_SPACES[section.space];
            if (!section.routes.length) return null;
            return (
              <section key={section.space} className={`cv-drawer__space cv-drawer__space--${section.space}`}>
                <header><span><Icone nome={meta.icon} /></span><div><small>{meta.eyebrow}</small><strong>{meta.label}</strong></div><i>{section.routes.length}</i></header>
                <div>{section.routes.map((candidate) => <RouteLink key={`drawer-${candidate.path}`} route={candidate} current={route} badge={routeBadge(candidate)} onNavigate={() => setDrawerOpen(false)} />)}</div>
              </section>
            );
          })}
          {filteredCatalog.every((section) => !section.routes.length) && <div className="cv-drawer__empty"><Icone nome="busca" /><strong>Nenhuma função encontrada</strong><span>Tente outro termo.</span></div>}
        </div>
        <footer className="cv-drawer__footer"><NavLink to="/tour" onClick={() => setDrawerOpen(false)}><Icone nome="curso" />Conhecer a plataforma</NavLink><button type="button" onClick={() => void signOut()}><Icone nome="sair" />Sair</button></footer>
      </aside>

      <nav className="cv-mobile-dock" aria-label="Navegação principal móvel">
        <NavLink to="/" end><Icone nome="hoje" /><span>Início</span></NavLink>
        <NavLink to={SPACE_ENTRY[space]}><Icone nome={spaceMeta.icon} /><span>{spaceMeta.label}</span></NavLink>
        <button type="button" className="cv-mobile-dock__assistant" onClick={() => setAssistantOpen(true)}><span aria-hidden="true">✦</span><small>Apoio</small></button>
        <NavLink to="/busca"><Icone nome="busca" /><span>Buscar</span></NavLink>
        <button type="button" onClick={(event) => openDrawer(event.currentTarget)} aria-expanded={drawerOpen}><Icone nome="mais" /><span>Mais</span></button>
      </nav>

      <PersonalAssistantPanel aberto={assistantOpen} onClose={() => setAssistantOpen(false)} />
      <BoasVindas />
      {!emergency && <ChatFlutuante />}
      {!emergency && <NavLink className="cv-emergency-fab" to="/emergencia" aria-label="Abrir Modo Emergência"><IconeEmergencia /></NavLink>}
    </div>
  );
}
