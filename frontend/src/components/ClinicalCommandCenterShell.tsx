import { type FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { assetUrl } from "../lib/api";
import BoasVindas from "./BoasVindas";
import ChatFlutuante from "./ChatFlutuante";
import Credito from "./Credito";
import Icone, { type NomeIcone } from "./Icone";
import { IconeEmergencia } from "./IdentidadeClinica";

type Item = {
  to: string;
  label: string;
  icon: NomeIcone;
  end?: boolean;
};

type Grupo = {
  id: string;
  label: string;
  items: Item[];
};

const PRINCIPAIS: Item[] = [
  { to: "/", label: "Início", icon: "hoje", end: true },
  { to: "/busca", label: "Buscar", icon: "busca" },
];

const GRUPOS: Grupo[] = [
  {
    id: "clinica",
    label: "Clínica",
    items: [
      { to: "/doencas", label: "Condições", icon: "doencas" },
      { to: "/medicamentos", label: "Medicamentos", icon: "medicamento" },
      { to: "/exames", label: "Exames", icon: "clinica" },
      { to: "/evidencias", label: "Evidências", icon: "evidencia" },
      { to: "/estudos", label: "Estudos", icon: "evidencia" },
      { to: "/diretrizes", label: "Guidelines", icon: "conhecimento" },
      { to: "/calculadoras", label: "Calculadoras", icon: "calculadora" },
      { to: "/emergencia", label: "Emergências", icon: "emergencia" },
      { to: "/checklists", label: "Checklists", icon: "check" },
      { to: "/casos-clinicos", label: "Casos clínicos", icon: "pacientes" },
      { to: "/trilhas", label: "Trilhas", icon: "seta" },
    ],
  },
  {
    id: "trabalho",
    label: "Trabalho",
    items: [
      { to: "/round", label: "Pacientes", icon: "pacientes" },
      { to: "/receituario", label: "Prescrição", icon: "prescricao" },
      { to: "/documentos", label: "Documentos e Solicitações", icon: "documento" },
      { to: "/agenda", label: "Agenda", icon: "agenda" },
      { to: "/corvia-mail", label: "CorVIA Mail", icon: "mail" },
    ],
  },
  {
    id: "inteligencia",
    label: "Inteligência",
    items: [
      { to: "/assistente", label: "CorVIA AI", icon: "assistente" },
    ],
  },
];

const MAIS: Item[] = [
  { to: "/favoritos", label: "Favoritos", icon: "favorito" },
  { to: "/material-paciente", label: "Material para paciente", icon: "documento" },
  { to: "/biblioteca", label: "Biblioteca científica", icon: "conhecimento" },
  { to: "/galeria", label: "Galeria", icon: "galeria" },
  { to: "/indicadores", label: "Meus indicadores", icon: "indicadores" },
  { to: "/usuarios-online", label: "Rede profissional", icon: "pacientes" },
  { to: "/sincronizacao", label: "Contas conectadas", icon: "sincronizar" },
  { to: "/minha-conta", label: "Minha conta", icon: "conta" },
  { to: "/assinatura", label: "Assinatura e plano", icon: "check" },
  { to: "/tour", label: "Conheça a plataforma", icon: "curso" },
];

function iniciais(nome?: string) {
  return (nome || "Médico")
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((parte) => parte[0]?.toUpperCase())
    .join("");
}

function itemAtivo(pathname: string, to: string, end?: boolean) {
  return end ? pathname === to : pathname === to || pathname.startsWith(`${to}/`);
}

function NavItem({ item, onNavigate }: { item: Item; onNavigate?: () => void }) {
  return (
    <NavLink
      to={item.to}
      end={item.end}
      onClick={onNavigate}
      className={({ isActive }) => `cc-nav-item${isActive ? " cc-nav-item--active" : ""}`}
    >
      <Icone nome={item.icon} />
      <span>{item.label}</span>
    </NavLink>
  );
}

export default function ClinicalCommandCenterShell() {
  const { usuario, sair } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [query, setQuery] = useState("");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [moreOpen, setMoreOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const searchRef = useRef<HTMLInputElement>(null);
  const naEmergencia = location.pathname.startsWith("/emergencia");

  const gruposAbertos = useMemo(() => {
    const ativo = GRUPOS.find((grupo) => grupo.items.some((item) => itemAtivo(location.pathname, item.to)));
    return new Set(ativo ? [ativo.id] : ["clinica", "trabalho"]);
  }, [location.pathname]);
  const [expanded, setExpanded] = useState<Set<string>>(gruposAbertos);

  useEffect(() => {
    const ativo = GRUPOS.find((grupo) => grupo.items.some((item) => itemAtivo(location.pathname, item.to)));
    if (!ativo) return;
    setExpanded((atual) => new Set([...atual, ativo.id]));
  }, [location.pathname]);

  useEffect(() => {
    function shortcut(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        searchRef.current?.focus();
      }
    }
    document.addEventListener("keydown", shortcut);
    return () => document.removeEventListener("keydown", shortcut);
  }, []);

  useEffect(() => {
    setDrawerOpen(false);
    setMoreOpen(false);
    setProfileOpen(false);
  }, [location.pathname]);

  function submitSearch(event: FormEvent) {
    event.preventDefault();
    const termo = query.trim();
    if (termo.length < 2) return;
    navigate(`/busca?q=${encodeURIComponent(termo)}`);
    setQuery("");
  }

  async function logout() {
    await sair();
    navigate("/entrar", { replace: true });
  }

  const adminItems: Item[] = usuario?.role === "admin"
    ? [
      { to: "/admin", label: "Administração", icon: "gestao" },
      { to: "/admin/usuarios", label: "Assinantes e KYC", icon: "pacientes" },
      { to: "/fila-telediagnostico", label: "Fila de telediagnóstico", icon: "evidencia" },
    ]
    : [];

  const navigation = (
    <>
      <div className="cc-nav-main">
        {PRINCIPAIS.map((item) => <NavItem key={item.to} item={item} />)}
      </div>
      {GRUPOS.map((grupo) => {
        const aberto = expanded.has(grupo.id);
        return (
          <section className="cc-nav-group" key={grupo.id}>
            <button
              type="button"
              className="cc-nav-group__title"
              onClick={() => setExpanded((atual) => {
                const next = new Set(atual);
                if (next.has(grupo.id)) next.delete(grupo.id); else next.add(grupo.id);
                return next;
              })}
              aria-expanded={aberto}
            >
              <span>{grupo.label}</span>
              <span aria-hidden="true">{aberto ? "−" : "+"}</span>
            </button>
            {aberto && (
              <div className="cc-nav-group__items">
                {grupo.items.map((item) => <NavItem key={item.to} item={item} />)}
              </div>
            )}
          </section>
        );
      })}
      <section className="cc-nav-group">
        <button type="button" className="cc-nav-group__title" onClick={() => setMoreOpen((v) => !v)} aria-expanded={moreOpen}>
          <span>Pessoal e mais</span><span aria-hidden="true">{moreOpen ? "−" : "+"}</span>
        </button>
        {moreOpen && (
          <div className="cc-nav-group__items">
            {[...MAIS, ...adminItems].map((item) => <NavItem key={item.to} item={item} />)}
          </div>
        )}
      </section>
    </>
  );

  return (
    <div className="cc-shell">
      <a href="#cc-main" className="pular-conteudo">Pular para o conteúdo</a>

      <aside className="cc-sidebar" aria-label="Navegação principal">
        <NavLink to="/" className="cc-brand" aria-label="CorVIA — início">
          <img src="/corvia-logo-compacta.png" alt="" />
          <span><strong>CorVIA</strong><small>Clinical OS do médico</small></span>
        </NavLink>
        <nav className="cc-sidebar__nav">{navigation}</nav>
        <div className="cc-sidebar__footer">
          <NavLink to="/favoritos" className="cc-sidebar__favorite"><Icone nome="favorito" /> Favoritos</NavLink>
          <button type="button" onClick={() => void logout()}><Icone nome="sair" /> Sair</button>
        </div>
      </aside>

      <div className="cc-shell__body">
        <header className="cc-topbar">
          <button type="button" className="cc-topbar__menu" aria-label="Abrir menu" onClick={() => setDrawerOpen(true)}>
            <Icone nome="menu" />
          </button>
          <NavLink to="/" className="cc-topbar__mobile-brand" aria-label="CorVIA — início">
            <img src="/corvia-logo-compacta.png" alt="" />
          </NavLink>
          <form onSubmit={submitSearch} className="cc-global-search" role="search">
            <Icone nome="busca" />
            <input
              ref={searchRef}
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Pergunte, pesquise ou execute uma ação…"
              aria-label="Pesquisar em toda a CorVIA"
            />
            <kbd>⌘ K</kbd>
            <button type="submit" aria-label="Pesquisar"><Icone nome="seta" /></button>
          </form>
          <div className="cc-topbar__actions">
            <NavLink to="/agenda" className="cc-topbar__icon" aria-label="Abrir agenda"><Icone nome="agenda" /></NavLink>
            <NavLink to="/corvia-mail" className="cc-topbar__icon" aria-label="Abrir CorVIA Mail"><Icone nome="mail" /></NavLink>
            <div className="cc-profile">
              <button type="button" className="cc-profile__button" onClick={() => setProfileOpen((v) => !v)} aria-expanded={profileOpen}>
                {usuario?.photo_url ? <img src={assetUrl(usuario.photo_url)} alt="" /> : <span>{iniciais(usuario?.full_name)}</span>}
                <span className="cc-profile__text"><strong>{usuario?.full_name || "Médico"}</strong><small>{usuario?.role === "admin" ? "Administrador" : "Profissional"}</small></span>
                <Icone nome="chevron" />
              </button>
              {profileOpen && (
                <div className="cc-profile__menu" role="menu">
                  <NavLink to="/minha-conta" role="menuitem"><Icone nome="conta" /> Minha conta</NavLink>
                  <NavLink to="/sincronizacao" role="menuitem"><Icone nome="sincronizar" /> Contas conectadas</NavLink>
                  <NavLink to="/assinatura" role="menuitem"><Icone nome="check" /> Assinatura e plano</NavLink>
                  {usuario?.role === "admin" && <NavLink to="/admin" role="menuitem"><Icone nome="gestao" /> Administração</NavLink>}
                  <button type="button" role="menuitem" onClick={() => void logout()}><Icone nome="sair" /> Sair</button>
                </div>
              )}
            </div>
          </div>
        </header>

        <main id="cc-main" className="cc-main" tabIndex={-1}>
          <Outlet />
          <Credito compacto />
        </main>
      </div>

      <div className={`cc-drawer-backdrop${drawerOpen ? " is-open" : ""}`} onClick={() => setDrawerOpen(false)} aria-hidden="true" />
      <aside className={`cc-drawer${drawerOpen ? " is-open" : ""}`} aria-hidden={!drawerOpen} aria-label="Navegação móvel">
        <div className="cc-drawer__header">
          <NavLink to="/" className="cc-brand"><img src="/corvia-logo-compacta.png" alt="" /><span><strong>CorVIA</strong><small>Clinical OS do médico</small></span></NavLink>
          <button type="button" aria-label="Fechar menu" onClick={() => setDrawerOpen(false)}><Icone nome="fechar" /></button>
        </div>
        <nav className="cc-drawer__nav" onClick={() => setDrawerOpen(false)}>{navigation}</nav>
      </aside>

      <nav className="cc-mobile-nav" aria-label="Atalhos principais">
        <NavLink to="/" end><Icone nome="hoje" /><span>Início</span></NavLink>
        <NavLink to="/busca"><Icone nome="busca" /><span>Buscar</span></NavLink>
        <NavLink to="/round"><Icone nome="pacientes" /><span>Pacientes</span></NavLink>
        <NavLink to="/agenda"><Icone nome="agenda" /><span>Agenda</span></NavLink>
        <button type="button" onClick={() => setDrawerOpen(true)}><Icone nome="mais" /><span>Mais</span></button>
      </nav>

      <BoasVindas />
      {!naEmergencia && (
        <NavLink to="/emergencia" className="cc-emergency-fab" aria-label="Abrir Modo Emergência" title="Modo Emergência">
          <IconeEmergencia />
        </NavLink>
      )}
      {!naEmergencia && <ChatFlutuante />}
    </div>
  );
}
