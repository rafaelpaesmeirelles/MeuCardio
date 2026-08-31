import { type FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { Link, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { api, assetUrl } from "../lib/api";
import { useAuth } from "../lib/auth";
import { heartTeamEnabled, whatsappAssistantEnabled } from "../lib/aiFeatureFlags";
import { nomeComTratamento } from "../lib/clinicalIdentity";
import BoasVindas from "./BoasVindas";
import ChatFlutuante from "./ChatFlutuante";
import Credito from "./Credito";
import Icone, { type NomeIcone } from "./Icone";
import { IconeEmergencia, IconeHoje } from "./IdentidadeClinica";
import PersonalAssistantPanel from "./PersonalAssistantPanel";
import { CoracaoHolografico } from "./PreHomeBrand";

type Item = { to: string; rotulo: string; icone: NomeIcone; badge?: number };
type Secao = { id: string; rotulo: string; icone: NomeIcone; itens: Item[] };
type Recente = { path: string; titulo: string; detalhe: string; icone: NomeIcone; visitadoEm: number };

const BASE: Secao[] = [
  {
    id: "decisao",
    rotulo: "Decisão clínica",
    icone: "clinica",
    itens: [
      { to: "/assistente", rotulo: "Assistente", icone: "assistente" },
      ...(heartTeamEnabled() ? [{ to: "/heart-team", rotulo: "Heart Team Virtual", icone: "round" as NomeIcone }] : []),
      { to: "/doencas", rotulo: "Guia de Doenças", icone: "doencas" },
      { to: "/triagem-sintomas", rotulo: "Triagem de sintomas", icone: "triagem" },
      { to: "/calculadoras", rotulo: "Calculadoras e escores", icone: "calculadora" },
      { to: "/cardiologia-intensiva", rotulo: "Cardiologia Intensiva & UCO", icone: "clinica" },
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
      { to: "/exames-ia", rotulo: "IA para Exames · destaque", icone: "ecg" },
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
      ...(whatsappAssistantEnabled() ? [{ to: "/whatsapp-assistant", rotulo: "Assistente no WhatsApp", icone: "comunicacao" as NomeIcone }] : []),
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

const CONTEXTOS: Array<{ prefixo: string; titulo: string; detalhe: string; icone: NomeIcone }> = [
  { prefixo: "/heart-team", titulo: "Heart Team Virtual", detalhe: "Conselho clínico independente", icone: "round" },
  { prefixo: "/whatsapp-assistant", titulo: "Assistente no WhatsApp", detalhe: "Rotina profissional com confirmação", icone: "comunicacao" },
  { prefixo: "/cardiologia-intensiva", titulo: "Cardiologia Intensiva & UCO", detalhe: "Cockpit assistencial", icone: "clinica" },
  { prefixo: "/medicamentos", titulo: "Medicamentos", detalhe: "Farmacologia e segurança", icone: "medicamento" },
  { prefixo: "/interacoes", titulo: "Interações", detalhe: "Segurança medicamentosa", icone: "medicamento" },
  { prefixo: "/doencas", titulo: "Guia de Doenças", detalhe: "Consulta clínica", icone: "doencas" },
  { prefixo: "/calculadoras", titulo: "Calculadoras", detalhe: "Escores e decisão", icone: "calculadora" },
  { prefixo: "/diretrizes", titulo: "Diretrizes", detalhe: "Recomendações e atualização", icone: "evidencia" },
  { prefixo: "/evidencias", titulo: "Evidências", detalhe: "Síntese científica", icone: "evidencia" },
  { prefixo: "/estudos", titulo: "Estudos", detalhe: "Literatura original", icone: "evidencia" },
  { prefixo: "/biblioteca", titulo: "Biblioteca", detalhe: "Conhecimento clínico", icone: "conhecimento" },
  { prefixo: "/exames", titulo: "Exames", detalhe: "Diagnóstico e interpretação", icone: "clinica" },
  { prefixo: "/receituario", titulo: "Prescrição", detalhe: "Produção clínica", icone: "prescricao" },
  { prefixo: "/documentos", titulo: "Documentos", detalhe: "Documentos e solicitações", icone: "documento" },
  { prefixo: "/exames-ia", titulo: "IA para Exames", detalhe: "Análise multimodal cardiovascular", icone: "ecg" },
  { prefixo: "/ecg-ia", titulo: "IA para Exames", detalhe: "Análise multimodal cardiovascular", icone: "ecg" },
  { prefixo: "/prontuario", titulo: "Prontuário", detalhe: "Registro clínico longitudinal", icone: "pacientes" },
  { prefixo: "/round", titulo: "Pacientes e round", detalhe: "Continuidade do cuidado", icone: "round" },
  { prefixo: "/agenda", titulo: "Agenda", detalhe: "Organização clínica", icone: "agenda" },
  { prefixo: "/assistente", titulo: "Assistente", detalhe: "Assistência contextual", icone: "assistente" },
  { prefixo: "/emergencia", titulo: "Emergência", detalhe: "Protocolos de risco imediato", icone: "emergencia" },
];

function meta(pathname: string) {
  return CONTEXTOS.find((item) => pathname.startsWith(item.prefixo))
    ?? { prefixo: pathname, titulo: "CorVIA", detalhe: "Workspace clínico", icone: "clinica" as NomeIcone };
}

function iniciais(nome?: string) {
  return (nome || "Médico").trim().split(/\s+/).slice(0, 2).map((parte) => parte[0]?.toUpperCase()).join("");
}

function chaveContextosRecentes(userId?: number) {
  return userId ? `corvia:contextos-recentes:${userId}` : "";
}

function destino(valor: string) {
  const termo = valor.trim();
  const normalizado = termo.toLocaleLowerCase("pt-BR");
  if (/\b(ecg|eletrocardiograma|holter|mapa|ecocardiograma|resson[aâ]ncia|tomografia|exame cardiovascular)\b/.test(normalizado)) return "/exames-ia";
  if (/\b(prescrev|prescri|receita|receitu)/.test(normalizado)) return "/receituario";
  if (/\b(atestado|documento|relat[oó]rio|encaminhamento|solicitar exames?|pedido de exames?)/.test(normalizado)) return "/documentos";
  if (/\b(calcul|escore|score)/.test(normalizado)) return "/calculadoras";
  if (/\b(emerg[eê]ncia|urg[eê]ncia)/.test(normalizado)) return "/emergencia";
  if (/\b(intera[cç][aã]o)/.test(normalizado)) return "/interacoes";
  return `/busca?q=${encodeURIComponent(termo)}`;
}

function Navegacao({ secoes, onNavigate }: { secoes: Secao[]; onNavigate?: () => void }) {
  const { pathname } = useLocation();
  const ativa = secoes.find((secao) => secao.itens.some((item) => {const path=item.to.split("?")[0];return pathname===path||pathname.startsWith(`${path}/`);}))?.id;
  const [aberta, setAberta] = useState(ativa || "decisao");
  useEffect(() => { if (ativa) setAberta(ativa); }, [ativa]);

  return (
    <nav className="cos-nav" aria-label="Áreas da CorVIA">
      <NavLink to="/" end onClick={onNavigate} className={({ isActive }) => `cos-nav__home${isActive ? " is-active" : ""}`}>
        <IconeHoje /><span><strong>Início</strong><small>Clinical Command Center</small></span>
      </NavLink>
      {secoes.map((secao) => {
        const expandida = aberta === secao.id;
        return (
          <section className={`cos-nav-group${ativa === secao.id ? " is-current" : ""}`} key={secao.id}>
            <button type="button" className="cos-nav-group__trigger" onClick={() => setAberta(expandida ? "" : secao.id)} aria-expanded={expandida}>
              <Icone nome={secao.icone} /><span>{secao.rotulo}</span><Icone nome="chevron" className="cos-nav-group__chevron" />
            </button>
            <div className={`cos-nav-group__items${expandida ? " is-open" : ""}`} aria-hidden={!expandida}>
              {secao.itens.map((item) => (
                <NavLink key={item.to} to={item.to} tabIndex={expandida ? undefined : -1} onClick={onNavigate} className={({ isActive }) => isActive ? "is-active" : ""}>
                  <Icone nome={item.icone} /><span>{item.rotulo}</span>{!!item.badge && <strong>{item.badge}</strong>}
                </NavLink>
              ))}
            </div>
          </section>
        );
      })}
    </nav>
  );
}

function Intelligence({ pathname }: { pathname: string }) {
  const contexto = meta(pathname);
  const mapa = useMemo(() => {
    if (pathname.startsWith("/medicamentos") || pathname.startsWith("/interacoes")) return {
      titulo: "Inteligência farmacológica",
      texto: "Conecte medicamento, segurança, evidência e ação clínica.",
      links: [["/interacoes", "Revisar interações", "medicamento"], ["/evidencias", "Abrir evidências", "evidencia"], ["/receituario", "Ir para prescrição", "prescricao"]] as [string, string, NomeIcone][],
    };
    if (pathname.startsWith("/doencas") || pathname.startsWith("/triagem-sintomas")) return {
      titulo: "Inteligência clínica",
      texto: "Navegue da doença para diretrizes, fármacos, escores e exames.",
      links: [["/diretrizes", "Ver diretrizes", "evidencia"], ["/calculadoras", "Abrir escores", "calculadora"], ["/medicamentos", "Explorar fármacos", "medicamento"]] as [string, string, NomeIcone][],
    };
    if (pathname.startsWith("/evidencias") || pathname.startsWith("/estudos") || pathname.startsWith("/diretrizes")) return {
      titulo: "Inteligência científica",
      texto: "Cruze estudos, recomendações e aplicação prática.",
      links: [["/biblioteca", "Abrir biblioteca", "conhecimento"], ["/estudos", "Estudos relacionados", "evidencia"], ["/assistente", "Discutir com o Assistente", "assistente"]] as [string, string, NomeIcone][],
    };
    if (pathname.startsWith("/exames") || pathname.startsWith("/galeria")) return {
      titulo: "Inteligência diagnóstica",
      texto: "Relacione achados, critérios, condições e próximos passos.",
      links: [["/doencas", "Doenças relacionadas", "doencas"], ["/calculadoras", "Critérios e escores", "calculadora"], ["/assistente", "Analisar contexto", "assistente"]] as [string, string, NomeIcone][],
    };
    return {
      titulo: "CorVIA Intelligence",
      texto: "O sistema aproxima conhecimento, decisão e ação conforme seu contexto.",
      links: [["/assistente", "Perguntar ao Assistente", "assistente"], ["/diretrizes", "Atualização clínica", "evidencia"], ["/favoritos", "Abrir favoritos", "favorito"]] as [string, string, NomeIcone][],
    };
  }, [pathname]);

  return (
    <aside className="cos-intelligence" aria-label="CorVIA Intelligence">
      <div className="cos-intelligence__status"><i /> contexto ativo</div>
      <div className="cos-intelligence__context"><span><Icone nome={contexto.icone} /></span><div><small>Você está em</small><strong>{contexto.titulo}</strong></div></div>
      <section className="cos-intelligence__card">
        <p className="eyebrow">CorVIA Intelligence</p><h2>{mapa.titulo}</h2><p>{mapa.texto}</p>
        <div className="cos-intelligence__links">
          {mapa.links.map(([to, rotulo, icone]) => <Link to={to} key={to + rotulo}><Icone nome={icone} /><span>{rotulo}</span><Icone nome="seta" /></Link>)}
        </div>
      </section>
      <Link to="/busca" className="cos-intelligence__graph"><span>◎</span><span><strong>Tudo com Tudo</strong><small>Explorar relações clínicas</small></span><Icone nome="seta" /></Link>
      <Link to="/assistente" className="cos-intelligence__ask"><span>✦</span><span><strong>Perguntar no contexto</strong><small>Leve este contexto para o Assistente.</small></span><Icone nome="seta" /></Link>
    </aside>
  );
}

export default function ShellClinicalOSLaunch() {
  const { usuario, sair } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [pendentes, setPendentes] = useState(0);
  const [drawer, setDrawer] = useState(false);
  const [conta, setConta] = useState(false);
  const [assistente, setAssistente] = useState(false);
  const [comando, setComando] = useState("");
  const [fotoQuebrada, setFotoQuebrada] = useState(false);
  const buscaRef = useRef<HTMLInputElement>(null);
  const contaRef = useRef<HTMLDivElement>(null);
  const drawerRef = useRef<HTMLElement>(null);
  const fecharDrawerRef = useRef<HTMLButtonElement>(null);
  const disparadorDrawerRef = useRef<HTMLElement | null>(null);

  const naEmergencia = location.pathname.startsWith("/emergencia");
  const foco = ["/emergencia", "/receituario", "/documentos", "/agenda", "/round", "/corvia-mail", "/caixa-de-email", "/avaliacao-preoperatoria"].some((prefixo) => location.pathname.startsWith(prefixo));

  useEffect(() => {
    if (usuario?.role !== "admin") return;
    api.get<unknown[]>("/admin/users?status=pendente").then((lista) => setPendentes(lista.length)).catch(() => undefined);
  }, [usuario?.role]);

  useEffect(() => { setFotoQuebrada(false); }, [usuario?.photo_url]);
  useEffect(() => { setDrawer(false); setConta(false); }, [location.pathname]);

  useEffect(() => {
    if (location.pathname === "/" || location.pathname.startsWith("/admin")) return;
    const chave = chaveContextosRecentes(usuario?.id);
    if (!chave) return;
    const contexto = meta(location.pathname);
    const novo: Recente = { path: location.pathname, titulo: contexto.titulo, detalhe: contexto.detalhe, icone: contexto.icone, visitadoEm: Date.now() };
    try {
      const anteriores = JSON.parse(sessionStorage.getItem(chave) || "[]") as Recente[];
      sessionStorage.setItem(chave, JSON.stringify([novo, ...anteriores.filter((item) => item.path !== novo.path)].slice(0, 6)));
    } catch { /* continuidade é melhoria; navegação nunca depende do storage */ }
  }, [location.pathname, usuario?.id]);

  useEffect(() => {
    function abrirAssistentePessoal() { setDrawer(false); setConta(false); setAssistente(true); }
    window.addEventListener("corvia:abrir-assistente-pessoal", abrirAssistentePessoal);
    return () => window.removeEventListener("corvia:abrir-assistente-pessoal", abrirAssistentePessoal);
  }, []);

  useEffect(() => {
    function teclado(evento: KeyboardEvent) {
      if ((evento.ctrlKey || evento.metaKey) && evento.key.toLocaleLowerCase() === "k") { evento.preventDefault(); buscaRef.current?.focus(); }
      if (evento.key === "Escape") { setConta(false); setAssistente(false); }
    }
    document.addEventListener("keydown", teclado);
    return () => document.removeEventListener("keydown", teclado);
  }, []);

  useEffect(() => {
    if (!drawer) return;
    requestAnimationFrame(() => fecharDrawerRef.current?.focus());
    function prenderFoco(evento: KeyboardEvent) {
      if (evento.key === "Escape") { evento.preventDefault(); fecharDrawer(true); return; }
      if (evento.key !== "Tab") return;
      const elementos = Array.from(drawerRef.current?.querySelectorAll<HTMLElement>('a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])') ?? []).filter((elemento) => elemento.offsetParent !== null);
      if (elementos.length === 0) return;
      const primeiro = elementos[0]; const ultimo = elementos[elementos.length - 1];
      if (evento.shiftKey && document.activeElement === primeiro) { evento.preventDefault(); ultimo.focus(); }
      else if (!evento.shiftKey && document.activeElement === ultimo) { evento.preventDefault(); primeiro.focus(); }
    }
    document.addEventListener("keydown", prenderFoco);
    return () => document.removeEventListener("keydown", prenderFoco);
  }, [drawer]);

  useEffect(() => {
    if (!conta) return;
    function fora(evento: PointerEvent) { if (!contaRef.current?.contains(evento.target as Node)) setConta(false); }
    document.addEventListener("pointerdown", fora);
    return () => document.removeEventListener("pointerdown", fora);
  }, [conta]);

  useEffect(() => {
    document.body.classList.toggle("menu-clinico-aberto", drawer || assistente);
    return () => document.body.classList.remove("menu-clinico-aberto");
  }, [drawer, assistente]);

  const secoes = useMemo(() => usuario?.role !== "admin" ? BASE : BASE.map((secao) => secao.id !== "gestao" ? secao : {
    ...secao,
    itens: [...secao.itens, { to: "/admin", rotulo: "Administração", icone: "gestao" as NomeIcone, badge: pendentes }, { to: "/admin/usuarios", rotulo: "Assinantes", icone: "pacientes" as NomeIcone }, ...((heartTeamEnabled() || whatsappAssistantEnabled()) ? [{ to: "/admin/operacoes-ia", rotulo: "Operações de IA", icone: "indicadores" as NomeIcone }] : []), { to: "/fila-telediagnostico", rotulo: "Fila de telediagnóstico", icone: "evidencia" as NomeIcone }],
  }), [pendentes, usuario?.role]);

  function abrirDrawer(disparador: HTMLElement) {
    disparadorDrawerRef.current = disparador;
    setAssistente(false); setConta(false); setDrawer(true);
  }

  function fecharDrawer(restaurarFoco: boolean) {
    setDrawer(false);
    if (restaurarFoco) requestAnimationFrame(() => disparadorDrawerRef.current?.focus());
  }

  function executar(evento: FormEvent) {
    evento.preventDefault();
    if (comando.trim().length < 2) return;
    navigate(destino(comando));
    setComando("");
  }

  async function encerrar() {
    setDrawer(false); setConta(false); setAssistente(false);
    const chave = chaveContextosRecentes(usuario?.id);
    if (chave) {
      try { sessionStorage.removeItem(chave); } catch { /* logout não depende do storage do navegador */ }
    }
    await sair();
    navigate("/entrar", { replace: true });
  }

  return (
    <div className={`app-clinico clinical-os${foco ? " clinical-os--focus" : ""}${naEmergencia ? " clinical-os--emergency" : ""}`}>
      <a className="pular-conteudo" href="#conteudo-principal">Pular para o conteúdo</a>
      <div className="cos-shell-heart" aria-hidden="true"><CoracaoHolografico /></div>
      <aside className="cos-sidebar" aria-label="Navegação principal">
        <NavLink to="/" className="cos-brand" aria-label="CorVIA — início"><span className="cos-brand__mark"><img src="/corvia-mark-canonical.svg" alt="" /></span><span className="cos-brand__text"><strong>Cor<span className="corvia-via">VIA</span></strong><small>Cardiology Spaces</small></span></NavLink>
        <Navegacao secoes={secoes} />
        <div className="cos-sidebar__footer">
          <button type="button" className="cos-assistant-sidebar" onClick={() => { setDrawer(false); setConta(false); setAssistente(true); }}><span>✦</span><span><strong>Assistente Pessoal</strong><small>Agenda, deslocamento e rotina</small></span></button>
          <Link to="/busca" className="cos-relations"><span>◎</span><span><strong>Explorar relações</strong><small>Knowledge Graph</small></span></Link>
          <button type="button" className="cos-signout" onClick={() => void encerrar()}><Icone nome="sair" /><span>Sair</span></button>
        </div>
      </aside>

      <div className="cos-shell">
        <header className="cos-topbar">
          <button type="button" className="cos-topbar__menu" onClick={(evento) => abrirDrawer(evento.currentTarget)} aria-label="Abrir navegação"><Icone nome="menu" /></button>
          <NavLink to="/" className="cos-topbar__mobile-brand" aria-label="CorVIA — início"><img src="/corvia-mark-canonical.svg" alt="" /><span>Cor<span className="corvia-via">VIA</span></span></NavLink>
          <form className="cos-command-mini" role="search" onSubmit={executar}><Icone nome="busca" /><input ref={buscaRef} value={comando} onChange={(e) => setComando(e.target.value)} placeholder="Pergunte, pesquise ou execute uma ação..." aria-label="Pergunte, pesquise ou execute uma ação" /><kbd>⌘ K</kbd><button type="submit" aria-label="Executar"><Icone nome="seta" /></button></form>
          <div className="cos-topbar__actions">
            <button type="button" className="cos-topbar__icon cos-topbar__quick" onClick={() => navigate("/documentos")} aria-label="Criar nova ação"><Icone nome="adicionar" /></button>
            <NavLink to="/diretrizes" className="cos-topbar__icon cos-topbar__notifications" aria-label="Atualizações e notificações"><Icone nome="notificacao" /></NavLink>
            <NavLink to="/corvia-mail" className="cos-topbar__icon" aria-label="CorVIA Mail"><Icone nome="mail" /></NavLink>
            <div className="cos-account" ref={contaRef}>
              <button type="button" className="cos-account__trigger" onClick={() => setConta((valor) => !valor)} aria-haspopup="menu" aria-expanded={conta}>
                {usuario?.photo_url && !fotoQuebrada ? <img src={assetUrl(usuario.photo_url)} alt="" onError={() => setFotoQuebrada(true)} /> : <span className="cos-account__avatar">{iniciais(usuario?.full_name)}</span>}
                <span className="cos-account__identity"><strong><span className="cos-account__nome-completo">{nomeComTratamento(usuario)}</span><span className="cos-account__nome-curto">{nomeComTratamento(usuario, true)}</span></strong><small>{usuario?.role === "admin" ? "Administrador" : "Profissional"}</small></span><Icone nome="chevron" />
              </button>
              {conta && <div className="cos-account-menu" role="menu"><div className="cos-account-menu__head"><strong>{nomeComTratamento(usuario)}</strong><small>{usuario?.email}</small></div><NavLink to="/minha-conta" role="menuitem"><Icone nome="conta" />Minha conta</NavLink><NavLink to="/tour?retorno=/minha-conta" role="menuitem"><Icone nome="curso" />Tour Cardiology Spaces</NavLink><NavLink to="/sincronizacao" role="menuitem"><Icone nome="sincronizar" />Contas conectadas</NavLink><NavLink to="/favoritos" role="menuitem"><Icone nome="favorito" />Favoritos</NavLink>{usuario?.role === "admin" && <NavLink to="/admin" role="menuitem"><Icone nome="gestao" />Administração {pendentes > 0 && <strong className="cos-account-menu__badge">{pendentes}</strong>}</NavLink>}<button type="button" role="menuitem" onClick={() => void encerrar()}><Icone nome="sair" />Sair</button></div>}
            </div>
          </div>
        </header>
        <div className={`cos-workspace${foco ? " cos-workspace--focus" : ""}`}>
          <main className="conteudo cos-content" id="conteudo-principal" tabIndex={-1}><Outlet /><Credito compacto /></main>
          {!foco && <Intelligence pathname={location.pathname} />}
        </div>
      </div>

      <div className={`cos-drawer-backdrop${drawer ? " is-visible" : ""}`} onClick={() => fecharDrawer(true)} aria-hidden="true" />
      <aside ref={drawerRef} className={`cos-drawer${drawer ? " is-open" : ""}`} aria-hidden={!drawer} aria-label="Navegação móvel"><div className="cos-drawer__head"><NavLink to="/" onClick={() => setDrawer(false)}><img src="/corvia-logo-spaces-dark.svg" alt="CorVIA Cardiology Spaces" /></NavLink><button ref={fecharDrawerRef} type="button" onClick={() => fecharDrawer(true)} aria-label="Fechar navegação"><Icone nome="fechar" /></button></div><button type="button" className="cos-drawer__assistant" onClick={() => { setDrawer(false); setAssistente(true); }}><span>✦</span><span><strong>Assistente Pessoal</strong><small>Seu dia, deslocamentos e pendências</small></span><Icone nome="seta" /></button><Navegacao secoes={secoes} onNavigate={() => setDrawer(false)} /></aside>

      <nav className="cos-mobilebar" aria-label="Ações principais"><NavLink to="/" end><IconeHoje /><span>Início</span></NavLink><NavLink to="/busca"><Icone nome="busca" /><span>Buscar</span></NavLink><button type="button" className="cos-mobilebar__assistant" onClick={() => { setDrawer(false); setAssistente(true); }}><span>✦</span><span>Assistente</span></button><NavLink to="/agenda"><Icone nome="agenda" /><span>Agenda</span></NavLink><button type="button" onClick={(evento) => abrirDrawer(evento.currentTarget)}><Icone nome="mais" /><span>Mais</span></button></nav>

      <PersonalAssistantPanel aberto={assistente} onClose={() => setAssistente(false)} />
      <BoasVindas />
      {!naEmergencia && <ChatFlutuante />}
      {!naEmergencia && <NavLink className="cos-emergency-fab" to="/emergencia" aria-label="Abrir Modo Emergência"><IconeEmergencia /></NavLink>}
    </div>
  );
}
