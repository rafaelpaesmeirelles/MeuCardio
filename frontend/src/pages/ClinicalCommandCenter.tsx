import { type FormEvent, useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Icone, { type NomeIcone } from "../components/Icone";
import MapaDeslocamento, { type RotaDeslocamento } from "../components/MapaDeslocamento";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";

type Catalogo = { total: number; published_total?: number };
type ListaComTotal = { total?: number };
type Estudo = { slug: string; title: string; study_type: string; journal: string; year: number; theme: string };
type EstudosResponse = { total?: number; items: Estudo[] };
type Guideline = { id: number; slug: string; org: string; title: string; published_at: string; status: string };
type GuidelineNotification = { notification_id: number; read_at: string | null; message: string; guideline: Guideline };
type GuidelineNotifications = { cutoff: string; items: GuidelineNotification[] };
type Agendamento = {
  id: number;
  patient_name: string | null;
  scheduled_at: string;
  appointment_type: string;
  status: string;
};
type PreferenciaMobilidade = {
  enabled: boolean;
  automatic_foreground_refresh: boolean;
  refresh_interval_minutes: number;
  traffic_configured: boolean;
};
type ConfiguracaoMapa = { provider: string; configured: boolean; api_key: string | null };
type ProximoLocal = {
  appointment_id: number | null;
  routine_id: number | null;
  starts_at: string;
  ends_at: string | null;
  service_name: string;
  source: "work_routine" | "appointment";
  arrival_buffer_minutes: number;
  location: {
    id: number;
    name: string;
    address: Record<string, string>;
    latitude: number | null;
    longitude: number | null;
  };
};
type Deslocamento = {
  status: string;
  provider?: string;
  updated_at?: string;
  destination: ProximoLocal | null;
  routes: RotaDeslocamento[];
  tips: string[];
};
type StatusEmail = { status: string; incluido_no_plano: boolean };
type ContaEmail = { ativa: boolean; email_address?: string };
type MensagemEmail = { messageId?: string; id?: string; subject?: string; fromAddress?: string };
type ResumoEmail = { disponivel: boolean; email_address: string | null; pendentes: MensagemEmail[] };
type HistoricoComando = { termo: string; to: string; tipo: "busca" | "acao" | "assistente"; em: number };
type RailMode = "intelligence" | "assistant";

type AcaoRapida = {
  nome: string;
  descricao: string;
  to: string;
  icone: NomeIcone;
  tom: "teal" | "blue" | "purple" | "amber" | "red" | "green";
};

const ACOES: AcaoRapida[] = [
  { nome: "Prescrever", descricao: "Novo receituário", to: "/receituario", icone: "prescricao", tom: "teal" },
  { nome: "Solicitar exames", descricao: "Documento clínico", to: "/documentos", icone: "documento", tom: "blue" },
  { nome: "Documento", descricao: "Atestado, relatório…", to: "/documentos", icone: "documento", tom: "purple" },
  { nome: "Calculadoras", descricao: "Escores e índices", to: "/calculadoras", icone: "calculadora", tom: "amber" },
  { nome: "Emergências", descricao: "Condutas rápidas", to: "/emergencia", icone: "emergencia", tom: "red" },
  { nome: "Medicamentos", descricao: "Doses e interações", to: "/medicamentos", icone: "medicamento", tom: "green" },
  { nome: "Guidelines", descricao: "Diretrizes atuais", to: "/diretrizes", icone: "evidencia", tom: "amber" },
  { nome: "CorVIA AI", descricao: "Pergunte ao CorVIA", to: "/assistente?modo=clinica", icone: "assistente", tom: "purple" },
];

const AREAS = [
  ["Cardiologia clínica", "/biblioteca", "clinica"],
  ["Arritmias", "/biblioteca?tema=Arritmias", "doencas"],
  ["Insuficiência cardíaca", "/biblioteca?tema=Insufici%C3%AAncia%20card%C3%ADaca", "doencas"],
  ["Doença coronariana", "/biblioteca?tema=Doen%C3%A7a%20coronariana", "clinica"],
  ["Valvopatias", "/biblioteca?tema=Valvopatias", "doencas"],
  ["Hipertensão", "/biblioteca?tema=Hipertens%C3%A3o", "clinica"],
  ["Imagem cardiovascular", "/exames", "galeria"],
  ["Prevenção CV", "/biblioteca?tema=Preven%C3%A7%C3%A3o", "check"],
] as const;

const EXEMPLOS = ["tratamento da pericardite", "Nebido dose", "critérios de Duke", "prescrever losartana", "CHA₂DS₂-VASc"];
const HISTORY_KEY = "corvia:command-history:v1";

function saudacao() {
  const hora = new Date().getHours();
  if (hora < 12) return "Bom dia";
  if (hora < 18) return "Boa tarde";
  return "Boa noite";
}

function dataLonga() {
  const texto = new Intl.DateTimeFormat("pt-BR", {
    weekday: "long",
    day: "2-digit",
    month: "long",
  }).format(new Date());
  return texto.charAt(0).toUpperCase() + texto.slice(1);
}

function mesmoDia(a: Date, b: Date) {
  return a.getFullYear() === b.getFullYear()
    && a.getMonth() === b.getMonth()
    && a.getDate() === b.getDate();
}

function hora(valor?: string | null) {
  if (!valor) return "—";
  const d = new Date(valor);
  return Number.isNaN(d.getTime()) ? "—" : d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
}

function dataCurta(valor: string) {
  const d = new Date(valor);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleDateString("pt-BR", { day: "2-digit", month: "short" });
}

function abreviarTipo(tipo: string) {
  return ({ consulta: "Consulta", retorno: "Retorno", exame: "Exame", outro: "Compromisso" } as Record<string, string>)[tipo] || "Compromisso";
}

function lerHistorico(): HistoricoComando[] {
  try {
    const bruto = localStorage.getItem(HISTORY_KEY);
    if (!bruto) return [];
    const itens = JSON.parse(bruto) as HistoricoComando[];
    return Array.isArray(itens) ? itens.slice(0, 6) : [];
  } catch {
    return [];
  }
}

function classificarComando(termo: string): { to: string; tipo: HistoricoComando["tipo"] } {
  const normal = termo.toLocaleLowerCase("pt-BR").normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  if (/prescrev|receit/.test(normal)) return { to: "/receituario", tipo: "acao" };
  if (/solicitar? exames?|pedido de exame/.test(normal)) return { to: "/documentos", tipo: "acao" };
  if (/atestado|documento|relatorio|declaracao|encaminhamento/.test(normal)) return { to: "/documentos", tipo: "acao" };
  if (/calcul|cha2|has.bled|grace|timi|wells|rcri/.test(normal)) return { to: "/calculadoras", tipo: "acao" };
  if (/emerg|choque|parada|sca|infarto agudo/.test(normal)) return { to: "/emergencia", tipo: "acao" };
  if (/agenda|compromisso|consulta de hoje/.test(normal)) return { to: "/agenda", tipo: "acao" };
  if (/mail|email|e-mail/.test(normal)) return { to: "/corvia-mail", tipo: "acao" };
  if (/^(abrir|ver|buscar|procurar) paciente\b|^meus pacientes\b|^round\b/.test(normal)) return { to: "/round", tipo: "acao" };
  if (/^(qual|como|quando|por que|porque|compare|resuma|explique|analise|revisar?)\b/.test(normal) || termo.includes("?")) {
    return { to: "/assistente?modo=clinica", tipo: "assistente" };
  }
  return { to: `/busca?q=${encodeURIComponent(termo)}`, tipo: "busca" };
}

export default function ClinicalCommandCenter() {
  const { usuario } = useAuth();
  const navigate = useNavigate();
  const [comando, setComando] = useState("");
  const [railMode, setRailMode] = useState<RailMode>("intelligence");
  const [catalogo, setCatalogo] = useState<Catalogo | null>(null);
  const [evidencias, setEvidencias] = useState<number | null>(null);
  const [estudosTotal, setEstudosTotal] = useState<number | null>(null);
  const [estudos, setEstudos] = useState<Estudo[]>([]);
  const [guidelines, setGuidelines] = useState<GuidelineNotification[]>([]);
  const [agenda, setAgenda] = useState<Agendamento[]>([]);
  const [mobilidade, setMobilidade] = useState<PreferenciaMobilidade | null>(null);
  const [configuracaoMapa, setConfiguracaoMapa] = useState<ConfiguracaoMapa | null>(null);
  const [proximosLocais, setProximosLocais] = useState<ProximoLocal[]>([]);
  const [deslocamento, setDeslocamento] = useState<Deslocamento | null>(null);
  const [origemDeslocamento, setOrigemDeslocamento] = useState<{ latitude: number; longitude: number } | null>(null);
  const [erroLocalizacao, setErroLocalizacao] = useState("");
  const [statusEmail, setStatusEmail] = useState<StatusEmail | null>(null);
  const [contaEmail, setContaEmail] = useState<ContaEmail | null>(null);
  const [emailsPendentes, setEmailsPendentes] = useState<MensagemEmail[]>([]);
  const [historico, setHistorico] = useState<HistoricoComando[]>(() => lerHistorico());

  useEffect(() => {
    document.body.classList.add("command-center-active");
    return () => document.body.classList.remove("command-center-active");
  }, []);

  useEffect(() => {
    const total = (rota: string) => api.get<ListaComTotal>(rota).then((r) => r.total ?? 0).catch(() => null);
    api.get<Catalogo>("/library/catalog").then(setCatalogo).catch(() => setCatalogo(null));
    total("/evidence?limit=1").then(setEvidencias);
    api.get<EstudosResponse>("/studies?limit=3")
      .then((r) => { setEstudos(r.items ?? []); setEstudosTotal(r.total ?? null); })
      .catch(() => { setEstudos([]); setEstudosTotal(null); });
    api.get<GuidelineNotifications>("/guideline-updates/me?include_read=true")
      .then((r) => setGuidelines((r.items ?? []).filter((item) => !item.read_at)))
      .catch(() => setGuidelines([]));
    api.get<Agendamento[]>("/appointments").then(setAgenda).catch(() => setAgenda([]));
    api.get<PreferenciaMobilidade>("/agenda/mobility/preferences").then(setMobilidade).catch(() => setMobilidade(null));
    api.get<ConfiguracaoMapa>("/agenda/mobility/map-config").then(setConfiguracaoMapa).catch(() => setConfiguracaoMapa(null));
    api.get<ProximoLocal[]>("/agenda/workday/next-locations").then(setProximosLocais).catch(() => setProximosLocais([]));
    api.get<StatusEmail>("/billing/status-email").then(setStatusEmail).catch(() => setStatusEmail(null));
    api.get<ContaEmail>("/email/conta").then(setContaEmail).catch(() => setContaEmail(null));
    api.get<ResumoEmail>("/email/resumo")
      .then((r) => setEmailsPendentes(r.disponivel ? (r.pendentes ?? []) : []))
      .catch(() => setEmailsPendentes([]));
  }, []);

  useEffect(() => {
    if (!mobilidade?.enabled || !mobilidade.automatic_foreground_refresh || !navigator.geolocation) return;
    let ativo = true;
    const atualizar = () => navigator.geolocation.getCurrentPosition(
      (position) => {
        if (!ativo) return;
        setErroLocalizacao("");
        api.post<Deslocamento>("/agenda/mobility/commute", {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        }).then((result) => {
          if (!ativo) return;
          setOrigemDeslocamento({ latitude: position.coords.latitude, longitude: position.coords.longitude });
          setDeslocamento(result);
        }).catch(() => { if (ativo) setErroLocalizacao("Trânsito indisponível no momento."); });
      },
      (error) => {
        if (!ativo) return;
        setErroLocalizacao(error.code === error.PERMISSION_DENIED
          ? "Localização desativada neste aparelho."
          : "Localização indisponível no momento.");
      },
      { enableHighAccuracy: false, timeout: 12_000, maximumAge: 120_000 },
    );
    atualizar();
    return () => { ativo = false; };
  }, [mobilidade]);

  const primeiroNome = usuario?.full_name?.trim().split(/\s+/)[0] || "Doutor(a)";
  const agora = Date.now();
  const compromissosHoje = useMemo(() => agenda
    .filter((item) => item.status !== "cancelado" && mesmoDia(new Date(item.scheduled_at), new Date()))
    .sort((a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at)), [agenda]);
  const proximo = useMemo(() => agenda
    .filter((item) => item.status !== "cancelado" && +new Date(item.scheduled_at) >= agora)
    .sort((a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at))[0], [agenda, agora]);
  const proximoLocal = proximosLocais[0] ?? null;
  const rota = deslocamento?.status === "live" ? deslocamento.routes[0] : undefined;
  const saidaRecomendada = proximoLocal && rota
    ? new Date(new Date(proximoLocal.starts_at).getTime() - (rota.duration_seconds + proximoLocal.arrival_buffer_minutes * 60) * 1000)
    : null;
  const assinaturaEmailAtiva = !!statusEmail && ["ativo", "teste", "inadimplente"].includes(statusEmail.status) && !!contaEmail?.ativa;
  const totalAcervo = catalogo?.published_total ?? catalogo?.total ?? null;

  function executar(termoOriginal?: string) {
    const termo = (termoOriginal ?? comando).trim();
    if (termo.length < 2) return;
    const destino = classificarComando(termo);
    const novo: HistoricoComando = { termo, to: destino.to, tipo: destino.tipo, em: Date.now() };
    const atualizados = [novo, ...historico.filter((item) => item.termo.toLocaleLowerCase("pt-BR") !== termo.toLocaleLowerCase("pt-BR"))].slice(0, 6);
    setHistorico(atualizados);
    try { localStorage.setItem(HISTORY_KEY, JSON.stringify(atualizados)); } catch { /* armazenamento opcional */ }
    setComando("");
    navigate(destino.to);
  }

  function submeter(e: FormEvent) {
    e.preventDefault();
    executar();
  }

  return (
    <div className="command-center">
      <div className="command-center__workspace">
        <section className="command-hero" aria-labelledby="command-title">
          <div className="command-hero__title">
            <span className="command-hero__signal" aria-hidden="true" />
            <div>
              <p>{dataLonga()}</p>
              <h1 id="command-title">{saudacao()}, {primeiroNome}.</h1>
              <strong>O que você precisa resolver agora?</strong>
            </div>
          </div>

          <form className="clinical-command" onSubmit={submeter} role="search" aria-label="Pesquisar, perguntar ou executar ação">
            <Icone nome="busca" />
            <input
              value={comando}
              onChange={(e) => setComando(e.target.value)}
              placeholder="Pergunte, pesquise ou execute uma ação…"
              aria-label="Comando clínico universal"
            />
            <span className="clinical-command__mode">Buscar · Perguntar · Agir</span>
            <button type="submit" aria-label="Executar"><Icone nome="seta" /></button>
          </form>
          <div className="clinical-command__examples" aria-label="Exemplos de comando">
            <span>Experimente:</span>
            {EXEMPLOS.map((item) => <button key={item} type="button" onClick={() => executar(item)}>{item}</button>)}
          </div>
        </section>

        <section className="command-section" aria-labelledby="acoes-rapidas">
          <header className="command-section__header">
            <div><p className="command-kicker">Atalhos universais</p><h2 id="acoes-rapidas">Ações rápidas</h2></div>
            <Link to="/favoritos"><Icone nome="favorito" /> Favoritos</Link>
          </header>
          <div className="quick-actions">
            {ACOES.map((acao) => (
              <Link key={acao.nome} to={acao.to} className={`quick-action quick-action--${acao.tom}`}>
                <span className="quick-action__icon"><Icone nome={acao.icone} /></span>
                <span><strong>{acao.nome}</strong><small>{acao.descricao}</small></span>
                <Icone nome="chevron" className="quick-action__chevron" />
              </Link>
            ))}
          </div>
        </section>

        <section className="command-section" aria-labelledby="continuar">
          <header className="command-section__header">
            <div><p className="command-kicker">Continuidade sem presumir sua rotina</p><h2 id="continuar">Continuar de onde parei</h2></div>
            {historico.length > 0 && <button type="button" className="command-text-button" onClick={() => { setHistorico([]); try { localStorage.removeItem(HISTORY_KEY); } catch { /* noop */ } }}>Limpar</button>}
          </header>
          {historico.length > 0 ? (
            <div className="context-strip">
              {historico.map((item) => (
                <Link key={`${item.em}-${item.termo}`} to={item.to} className="context-card">
                  <span className={`context-card__type context-card__type--${item.tipo}`}>
                    <Icone nome={item.tipo === "assistente" ? "assistente" : item.tipo === "acao" ? "seta" : "busca"} />
                    {item.tipo === "assistente" ? "Pergunta" : item.tipo === "acao" ? "Ação" : "Pesquisa"}
                  </span>
                  <strong>{item.termo}</strong>
                  <small>{new Date(item.em).toLocaleDateString("pt-BR", { day: "2-digit", month: "short" })}</small>
                </Link>
              ))}
            </div>
          ) : (
            <div className="context-empty">
              <span><Icone nome="sincronizar" /></span>
              <div><strong>Seu contexto começa aqui.</strong><p>Pesquise, pergunte ou execute uma ação; o CorVIA passa a oferecer retomada rápida sem transformar pacientes em centro obrigatório da Home.</p></div>
            </div>
          )}
        </section>

        <section className="command-section" aria-labelledby="radar-clinico">
          <header className="command-section__header">
            <div><p className="command-kicker">Curadoria verificável</p><h2 id="radar-clinico">Radar clínico</h2></div>
            <Link to="/diretrizes">Ver atualizações</Link>
          </header>
          <div className="clinical-radar">
            {guidelines.length > 0 ? guidelines.slice(0, 2).map((item) => (
              <Link key={item.notification_id} className="radar-card radar-card--guideline" to="/diretrizes">
                <span className="radar-card__tag">Diretriz detectada · {item.guideline.org}</span>
                <strong>{item.guideline.title}</strong>
                <p>{item.message}</p>
                <small>{dataCurta(item.guideline.published_at)} · revisão humana preservada</small>
              </Link>
            )) : (
              <Link className="radar-card radar-card--guideline" to="/diretrizes">
                <span className="radar-card__tag">Diretrizes</span>
                <strong>Nenhum alerta novo pendente para você.</strong>
                <p>O monitor oficial continua ativo; recomendações não mudam silenciosamente.</p>
                <small>Abrir monitor de diretrizes</small>
              </Link>
            )}
            {estudos.slice(0, 1).map((item) => (
              <Link key={item.slug} className="radar-card radar-card--study" to={`/estudos/${item.slug}`}>
                <span className="radar-card__tag">Do acervo de estudos</span>
                <strong>{item.title}</strong>
                <p>{item.theme} · {item.journal || item.study_type}</p>
                <small>{item.year} · abrir resumo e implicação clínica</small>
              </Link>
            ))}
            <Link className="radar-card radar-card--knowledge" to="/busca">
              <span className="radar-card__tag">Tudo com Tudo</span>
              <strong>Explore o conhecimento conectado.</strong>
              <p>Doença, medicamento, exame, evidência, estudo, guideline, cálculo e material relacionados.</p>
              <small>Explorar relações clínicas</small>
            </Link>
          </div>
        </section>

        <section className="command-section command-section--areas" aria-labelledby="areas-clinicas">
          <header className="command-section__header">
            <div><p className="command-kicker">Conhecimento sem becos sem saída</p><h2 id="areas-clinicas">Explorar por área clínica</h2></div>
            <Link to="/biblioteca">Todo o acervo</Link>
          </header>
          <div className="clinical-areas">
            {AREAS.map(([nome, to, icone]) => (
              <Link key={nome} to={to}><span><Icone nome={icone as NomeIcone} /></span><strong>{nome}</strong><Icone nome="seta" /></Link>
            ))}
          </div>
        </section>
      </div>

      <aside className="command-rail" aria-label="Inteligência e Assistente Pessoal">
        <div className="command-rail__tabs" role="tablist" aria-label="Contexto do CorVIA">
          <button type="button" role="tab" aria-selected={railMode === "intelligence"} className={railMode === "intelligence" ? "ativo" : ""} onClick={() => setRailMode("intelligence")}>
            <Icone nome="conhecimento" /> Intelligence
          </button>
          <button type="button" role="tab" aria-selected={railMode === "assistant"} className={railMode === "assistant" ? "ativo" : ""} onClick={() => setRailMode("assistant")}>
            <Icone nome="assistente" /> Assistente
          </button>
        </div>

        {railMode === "intelligence" ? (
          <div className="rail-panel rail-panel--intelligence">
            <header><span><Icone nome="conhecimento" /></span><div><p>CorVIA Intelligence</p><strong>O que está relacionado ao que importa agora</strong></div></header>
            <div className="intelligence-metrics">
              <Link to="/biblioteca"><span><Icone nome="conhecimento" /></span><div><strong>{totalAcervo == null ? "—" : totalAcervo.toLocaleString("pt-BR")}</strong><small>conteúdos publicados</small></div></Link>
              <Link to="/evidencias"><span><Icone nome="evidencia" /></span><div><strong>{evidencias == null ? "—" : evidencias.toLocaleString("pt-BR")}</strong><small>evidências estruturadas</small></div></Link>
              <Link to="/estudos"><span><Icone nome="curso" /></span><div><strong>{estudosTotal == null ? "—" : estudosTotal.toLocaleString("pt-BR")}</strong><small>estudos no acervo</small></div></Link>
              <Link to="/diretrizes"><span><Icone nome="check" /></span><div><strong>{guidelines.length}</strong><small>alertas de diretriz não lidos</small></div></Link>
            </div>
            <Link to="/busca" className="rail-callout">
              <span className="rail-callout__icon"><Icone nome="busca" /></span>
              <span><strong>Explorar relações</strong><small>Veja o “Tudo com Tudo” a partir de qualquer tema.</small></span>
              <Icone nome="seta" />
            </Link>
            <Link to="/assistente?modo=clinica" className="rail-primary"><Icone nome="assistente" /> Pergunte qualquer coisa ao CorVIA</Link>
          </div>
        ) : (
          <div className="rail-panel rail-panel--assistant">
            <header><span><Icone nome="assistente" /></span><div><p>Assistente Pessoal</p><strong>Sua rotina profissional, sem perder o contexto</strong></div></header>

            <section className="assistant-block">
              <div className="assistant-block__title"><span><Icone nome="agenda" /></span><div><strong>Seu dia</strong><small>{compromissosHoje.length} compromisso{compromissosHoje.length === 1 ? "" : "s"} hoje</small></div></div>
              {proximo ? (
                <Link to="/agenda" className="assistant-next">
                  <span className="assistant-next__time">{hora(proximo.scheduled_at)}</span>
                  <span><strong>{proximo.patient_name || abreviarTipo(proximo.appointment_type)}</strong><small>{abreviarTipo(proximo.appointment_type)} · próximo compromisso</small></span>
                  <Icone nome="chevron" />
                </Link>
              ) : <p className="assistant-empty">Nenhum compromisso futuro carregado.</p>}
            </section>

            <section className="assistant-block">
              <div className="assistant-block__title"><span><Icone nome="rota" /></span><div><strong>Deslocamento</strong><small>Somente quando você autoriza localização</small></div></div>
              {proximoLocal ? (
                <>
                  <div className="assistant-route-summary">
                    <strong>{proximoLocal.location.name}</strong>
                    <span>Início às {hora(proximoLocal.starts_at)}</span>
                    {rota && <span>{Math.ceil(rota.duration_seconds / 60)} min · {(rota.distance_meters / 1000).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} km</span>}
                    {saidaRecomendada && <em>Saída sugerida: {saidaRecomendada.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}</em>}
                  </div>
                  {rota && origemDeslocamento && (
                    <div className="assistant-map">
                      <MapaDeslocamento
                        rotas={deslocamento?.routes ?? []}
                        origem={origemDeslocamento}
                        destino={{ name: proximoLocal.location.name, latitude: proximoLocal.location.latitude, longitude: proximoLocal.location.longitude }}
                        provider={deslocamento?.provider}
                        updatedAt={deslocamento?.updated_at}
                        googleMapsApiKey={configuracaoMapa?.api_key}
                      />
                    </div>
                  )}
                  {!rota && <p className="assistant-empty">{erroLocalizacao || (mobilidade?.enabled ? "Destino conhecido; estimativa de trânsito ainda indisponível." : "Ative mobilidade na Agenda para receber horários de saída.")}</p>}
                </>
              ) : <p className="assistant-empty">Cadastre locais/rotina na Agenda para o assistente preparar deslocamentos.</p>}
            </section>

            <section className="assistant-block">
              <div className="assistant-block__title"><span><Icone nome="mail" /></span><div><strong>Comunicação</strong><small>CorVIA Mail</small></div></div>
              {assinaturaEmailAtiva ? (
                <Link to="/caixa-de-email" className="assistant-inline-link"><strong>{emailsPendentes.length}</strong><span>mensagem{emailsPendentes.length === 1 ? "" : "ns"} pendente{emailsPendentes.length === 1 ? "" : "s"}</span><Icone nome="chevron" /></Link>
              ) : (
                <Link to="/corvia-mail" className="assistant-inline-link"><Icone nome="mail" /><span>Configurar CorVIA Mail</span><Icone nome="chevron" /></Link>
              )}
            </section>

            <Link to="/assistente?modo=pessoal" className="rail-primary rail-primary--assistant"><Icone nome="assistente" /> Abrir meu Assistente Pessoal</Link>
          </div>
        )}
      </aside>
    </div>
  );
}
