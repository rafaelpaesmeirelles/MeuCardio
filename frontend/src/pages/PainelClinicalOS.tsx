import { type FormEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Icone, { type NomeIcone } from "../components/Icone";
import MapaDeslocamento, { type RotaDeslocamento } from "../components/MapaDeslocamento";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";

type AcaoRapida = { to: string; titulo: string; detalhe: string; icone: NomeIcone };
type ContextoRecente = { path: string; titulo: string; detalhe: string; icone: NomeIcone; visitadoEm: number };
type Atualizacao = { id: number; slug: string; org: string; title: string; published_at: string; status: "detected" | "aguardando_revisao" | "revisada"; url: string | null };
type RespostaAtualizacoes = { cutoff: string; items: Atualizacao[] };
type Catalogo = { total: number; published_total?: number };
type Contagem = { total?: number };
type Paciente = { id: number };
type Agendamento = { id: number; patient_name: string | null; scheduled_at: string; appointment_type: string; status: string };
type PreferenciaMobilidade = { enabled: boolean; automatic_foreground_refresh: boolean; refresh_interval_minutes: number; traffic_configured: boolean };
type ProximoLocal = {
  appointment_id: number | null;
  routine_id: number | null;
  starts_at: string;
  ends_at: string | null;
  service_name: string;
  source: "work_routine" | "appointment";
  arrival_buffer_minutes: number;
  location: { id: number; name: string; address: Record<string, string>; latitude: number | null; longitude: number | null };
};
type Deslocamento = { status: string; provider?: string; updated_at?: string; destination: ProximoLocal | null; routes: RotaDeslocamento[]; tips: string[] };
type Origem = { latitude: number; longitude: number } | null;
type ConfigMapa = { provider: string; configured: boolean; api_key: string | null };
type EstadoPermissao = "desconhecida" | "concedida" | "negada" | "indisponivel";

const ACOES: AcaoRapida[] = [
  { to: "/receituario", titulo: "Prescrever", detalhe: "Novo receituário", icone: "prescricao" },
  { to: "/documentos", titulo: "Solicitar exames", detalhe: "Adicionar solicitação", icone: "clinica" },
  { to: "/documentos", titulo: "Documento", detalhe: "Atestado, relatório...", icone: "documento" },
  { to: "/calculadoras", titulo: "Calculadoras", detalhe: "Escores e índices", icone: "calculadora" },
  { to: "/emergencia", titulo: "Emergências", detalhe: "Condutas rápidas", icone: "emergencia" },
  { to: "/medicamentos", titulo: "Medicamentos", detalhe: "Doses, interações...", icone: "medicamento" },
  { to: "/diretrizes", titulo: "Guidelines", detalhe: "Diretrizes atuais", icone: "conhecimento" },
  { to: "/assistente", titulo: "Assistente", detalhe: "Assistente Clínica", icone: "assistente" },
];

const CONTEXTOS_INICIAIS: ContextoRecente[] = [
  { path: "/doencas", titulo: "Insuficiência Cardíaca (ICFER)", detalhe: "Condição", icone: "doencas", visitadoEm: 0 },
  { path: "/medicamentos?slug=sacubitril-valsartana", titulo: "Sacubitril/Valsartana", detalhe: "Medicamento", icone: "medicamento", visitadoEm: 0 },
  { path: "/evidencias", titulo: "Evidências", detalhe: "Recomendações clínicas", icone: "evidencia", visitadoEm: 0 },
  { path: "/round", titulo: "Paciente", detalhe: "Contexto clínico", icone: "pacientes", visitadoEm: 0 },
  { path: "/calculadoras", titulo: "CHA₂DS₂-VASc", detalhe: "Calculadora", icone: "calculadora", visitadoEm: 0 },
];

const EXEMPLOS = ["tratamento da pericardite", "nebido dose", "critérios de Duke", "prescrever losartana", "calcular CHA₂DS₂-VASc"];

function saudacao() {
  const hora = new Date().getHours();
  if (hora < 12) return "Bom dia";
  if (hora < 18) return "Boa tarde";
  return "Boa noite";
}
function primeiroNome(nome?: string) {
  const partes = (nome || "").trim().split(/\s+/).filter(Boolean);
  const primeira = /^(dr|dra)\.?$/i.test(partes[0] || "") ? partes[1] : partes[0];
  return primeira || "Doutor(a)";
}
function chaveContextosRecentes(userId?: number) { return userId ? `corvia:contextos-recentes:${userId}` : ""; }
function mesmoDia(a: Date, b: Date) { return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate(); }
function horario(valor?: string | null) { if (!valor) return "—"; const data = new Date(valor); return Number.isNaN(data.getTime()) ? "—" : data.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }); }
function dataCurta(valor: string) { const data = new Date(valor); return Number.isNaN(data.getTime()) ? "" : data.toLocaleDateString("pt-BR", { day: "2-digit", month: "short", year: "numeric", timeZone: "UTC" }); }
function tempoRelativo(timestamp: number) { if (!timestamp) return "Acesso hoje"; const minutos = Math.max(1, Math.round((Date.now() - timestamp) / 60000)); if (minutos < 60) return `Acesso há ${minutos} min`; const horas = Math.round(minutos / 60); if (horas < 24) return `Acesso há ${horas} h`; return `Acesso há ${Math.round(horas / 24)} d`; }
function statusAtualizacao(item: Atualizacao) { return item.status === "revisada" ? "Principais mudanças nas recomendações" : "Nova publicação detectada para revisão"; }
function transito(valor?: string) { return ({ normal: "livre", leve: "leve", moderado: "moderado", intenso: "intenso" } as Record<string, string>)[valor || ""] || valor || "atualizado"; }
function destinoDoComando(valor: string) {
  const termo = valor.trim(); const normalizado = termo.toLocaleLowerCase("pt-BR");
  if (/\b(prescrev|prescri|receita|receitu)/.test(normalizado)) return "/receituario";
  if (/\b(atestado|documento|relat[oó]rio|encaminhamento|solicitar exames?|pedido de exames?)/.test(normalizado)) return "/documentos";
  if (/\b(calcul|escore|score|cha.?ds.?vasc)/.test(normalizado)) return "/calculadoras";
  if (/\b(emerg[eê]ncia|urg[eê]ncia)/.test(normalizado)) return "/emergencia";
  if (/\b(intera[cç][aã]o)/.test(normalizado)) return "/interacoes";
  if (/\b(medicamento|f[aá]rmaco|dose)/.test(normalizado) && termo.split(/\s+/).length <= 4) return "/medicamentos";
  if (/\b(diretriz|guideline)/.test(normalizado) && termo.split(/\s+/).length <= 4) return "/diretrizes";
  if (/\b(paciente|round|enfermaria)/.test(normalizado) && termo.split(/\s+/).length <= 4) return "/round";
  return `/busca?q=${encodeURIComponent(termo)}`;
}

export default function PainelClinicalOS() {
  const { usuario } = useAuth();
  const navigate = useNavigate();
  const [comando, setComando] = useState("");
  const [recentes, setRecentes] = useState<ContextoRecente[]>([]);
  const [atualizacoes, setAtualizacoes] = useState<Atualizacao[]>([]);
  const [catalogo, setCatalogo] = useState<Catalogo | null>(null);
  const [evidencias, setEvidencias] = useState<number | null>(null);
  const [estudos, setEstudos] = useState<number | null>(null);
  const [pacientes, setPacientes] = useState<number | null>(null);
  const [agenda, setAgenda] = useState<Agendamento[]>([]);
  const [proximosLocais, setProximosLocais] = useState<ProximoLocal[]>([]);
  const [mobilidade, setMobilidade] = useState<PreferenciaMobilidade | null>(null);
  const [deslocamento, setDeslocamento] = useState<Deslocamento | null>(null);
  const [origem, setOrigem] = useState<Origem>(null);
  const [configMapa, setConfigMapa] = useState<ConfigMapa | null>(null);
  const [permissao, setPermissao] = useState<EstadoPermissao>("desconhecida");
  const [calculandoRota, setCalculandoRota] = useState(false);
  const [erroRota, setErroRota] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const chamadaRotaEmCurso = useRef(false);
  const ultimaRotaEm = useRef(0);

  useEffect(() => { document.body.classList.add("ccc-home-active"); return () => document.body.classList.remove("ccc-home-active"); }, []);

  useEffect(() => {
    const chave = chaveContextosRecentes(usuario?.id);
    if (!chave) return setRecentes([]);
    try { const salvos = JSON.parse(sessionStorage.getItem(chave) || "[]") as ContextoRecente[]; setRecentes(salvos.filter((item) => item?.path && item?.titulo).slice(0, 5)); }
    catch { setRecentes([]); }
  }, [usuario?.id]);

  useEffect(() => {
    api.get<RespostaAtualizacoes>("/guideline-updates").then((r) => setAtualizacoes((r.items ?? []).slice(0, 3))).catch(() => setAtualizacoes([]));
    api.get<Catalogo>("/library/catalog").then(setCatalogo).catch(() => setCatalogo(null));
    api.get<Contagem>("/evidence?limit=1").then((r) => setEvidencias(r.total ?? null)).catch(() => setEvidencias(null));
    api.get<Contagem>("/studies?limit=1").then((r) => setEstudos(r.total ?? null)).catch(() => setEstudos(null));
    api.get<Paciente[]>("/round/patients").then((r) => setPacientes(r.length)).catch(() => setPacientes(null));
    api.get<Array<{ id: number; patient_name: string | null; starts_at: string; appointment_type: string; status: string }>>("/agenda/appointments").then((items) => setAgenda(items.map((item) => ({ id: item.id, patient_name: item.patient_name, scheduled_at: item.starts_at, appointment_type: item.appointment_type, status: item.status })))).catch(() => setAgenda([]));
    api.get<ProximoLocal[]>("/agenda/workday/next-locations?limit=10").then(setProximosLocais).catch(() => setProximosLocais([]));
    api.get<PreferenciaMobilidade>("/agenda/mobility/preferences").then(setMobilidade).catch(() => setMobilidade(null));
    api.get<ConfigMapa>("/agenda/mobility/map-config").then(setConfigMapa).catch(() => setConfigMapa(null));
  }, []);

  useEffect(() => {
    if (!mobilidade?.enabled) { setPermissao("desconhecida"); return; }
    if (!navigator.geolocation) { setPermissao("indisponivel"); return; }
    if (!navigator.permissions?.query) return;
    let ativo = true;
    let status: PermissionStatus | null = null;
    navigator.permissions.query({ name: "geolocation" }).then((resultado) => {
      if (!ativo) return;
      status = resultado;
      const aplicar = () => setPermissao(resultado.state === "granted" ? "concedida" : resultado.state === "denied" ? "negada" : "desconhecida");
      aplicar();
      resultado.onchange = aplicar;
    }).catch(() => undefined);
    return () => { ativo = false; if (status) status.onchange = null; };
  }, [mobilidade?.enabled]);

  useEffect(() => {
    function focar(evento: KeyboardEvent) { if (evento.key === "/" && document.activeElement?.tagName !== "INPUT" && document.activeElement?.tagName !== "TEXTAREA") { evento.preventDefault(); inputRef.current?.focus(); } }
    document.addEventListener("keydown", focar); return () => document.removeEventListener("keydown", focar);
  }, []);

  const contextos = useMemo(() => recentes.length ? recentes : CONTEXTOS_INICIAIS, [recentes]);
  const compromissosHoje = useMemo(() => agenda.filter((item) => item.status !== "cancelado" && mesmoDia(new Date(item.scheduled_at), new Date())).sort((a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at)), [agenda]);
  const proximo = useMemo(() => agenda.filter((item) => item.status !== "cancelado" && +new Date(item.scheduled_at) >= Date.now()).sort((a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at))[0], [agenda]);
  const destino = useMemo(() => proximo ? proximosLocais.find((item) => item.source === "appointment" && item.appointment_id === proximo.id) ?? null : null, [proximo, proximosLocais]);
  const pendencias = useMemo(() => agenda.filter((item) => ["pendente", "pending_external", "proposed"].includes(item.status)).length, [agenda]);
  const rota = deslocamento?.destination?.appointment_id === proximo?.id ? deslocamento.routes?.[0] : undefined;
  const saidaRecomendada = destino && rota ? new Date(new Date(proximo.scheduled_at).getTime() - (rota.duration_seconds + destino.arrival_buffer_minutes * 60) * 1000) : null;
  const chegadaPrevista = rota ? new Date((deslocamento?.updated_at ? new Date(deslocamento.updated_at).getTime() : Date.now()) + rota.duration_seconds * 1000) : null;

  const calcularDeslocamento = useCallback((solicitarPermissao = false) => {
    if (!mobilidade?.enabled || !proximo || !destino || destino.appointment_id !== proximo.id) return;
    if (destino.location.latitude == null || destino.location.longitude == null) return;
    if (!navigator.geolocation || chamadaRotaEmCurso.current) return;
    if (!solicitarPermissao && permissao !== "concedida") return;

    chamadaRotaEmCurso.current = true;
    setCalculandoRota(true);
    setErroRota(null);
    navigator.geolocation.getCurrentPosition((position) => {
      const origemAtual = { latitude: position.coords.latitude, longitude: position.coords.longitude };
      setOrigem(origemAtual);
      setPermissao("concedida");
      api.post<Deslocamento>("/agenda/mobility/commute-appointment", {
        ...origemAtual,
        appointment_id: proximo.id,
      }).then((resultado) => {
        if (resultado.destination?.appointment_id !== proximo.id) {
          setDeslocamento({ ...resultado, status: "destination_mismatch", destination: null, routes: [] });
          setErroRota("O destino retornado não corresponde ao compromisso exibido.");
          return;
        }
        setDeslocamento(resultado);
        ultimaRotaEm.current = Date.now();
        if (!resultado.routes?.length && resultado.status !== "ok") setErroRota("O provedor não retornou uma rota utilizável.");
      }).catch(() => {
        setErroRota("Não foi possível atualizar a rota agora.");
      }).finally(() => {
        chamadaRotaEmCurso.current = false;
        setCalculandoRota(false);
      });
    }, (erro) => {
      if (erro.code === erro.PERMISSION_DENIED) { setPermissao("negada"); setErroRota("A localização foi negada no navegador."); }
      else setErroRota("Não foi possível obter sua localização atual.");
      chamadaRotaEmCurso.current = false;
      setCalculandoRota(false);
    }, { enableHighAccuracy: false, timeout: 8000, maximumAge: 120000 });
  }, [destino, mobilidade?.enabled, permissao, proximo]);

  useEffect(() => {
    if (!mobilidade?.enabled || !mobilidade.automatic_foreground_refresh || permissao !== "concedida" || !destino || destino.appointment_id !== proximo?.id) return;
    const intervaloMs = Math.max(2, mobilidade.refresh_interval_minutes || 5) * 60000;
    const atualizarSeVisivel = () => {
      if (document.visibilityState !== "visible") return;
      if (Date.now() - ultimaRotaEm.current < intervaloMs && ultimaRotaEm.current) return;
      calcularDeslocamento(false);
    };
    atualizarSeVisivel();
    const timer = window.setInterval(atualizarSeVisivel, intervaloMs);
    const visibilidade = () => { if (document.visibilityState === "visible") atualizarSeVisivel(); };
    document.addEventListener("visibilitychange", visibilidade);
    return () => { window.clearInterval(timer); document.removeEventListener("visibilitychange", visibilidade); };
  }, [calcularDeslocamento, destino, mobilidade?.automatic_foreground_refresh, mobilidade?.enabled, mobilidade?.refresh_interval_minutes, permissao, proximo?.id]);

  function executar(evento: FormEvent) { evento.preventDefault(); if (comando.trim().length < 2) return; navigate(destinoDoComando(comando)); }
  function usarExemplo(texto: string) { setComando(texto); inputRef.current?.focus(); }
  function abrirAssistentePessoal() { window.dispatchEvent(new Event("corvia:abrir-assistente-pessoal")); }

  const descricaoDeslocamento = !proximo
    ? "Sem compromisso futuro"
    : !destino
      ? "Este compromisso não possui endereço/local disponível para rota"
      : destino.location.latitude == null || destino.location.longitude == null
        ? "Local sem coordenadas configuradas"
        : !mobilidade?.enabled
          ? "Mobilidade desabilitada"
          : permissao === "negada"
            ? "Localização negada no navegador"
            : !mobilidade.traffic_configured
              ? "Provider de trânsito indisponível"
              : calculandoRota
                ? "Calculando rota com trânsito atual..."
                : rota
                  ? `${Math.ceil(rota.duration_seconds / 60)} min · ${(rota.distance_meters / 1000).toFixed(1)} km · trânsito ${transito(rota.congestion)}`
                  : erroRota || "Rota ainda não calculada";

  return (
    <div className="ccc-home ccc-home--board">
      <main className="ccc-home__main">
        <header className="ccc-home__welcome"><h1>{saudacao()}, Dr. {primeiroNome(usuario?.full_name)}! <span aria-hidden="true">👋</span></h1><p>O que você precisa resolver agora?</p></header>

        <form className="ccc-command" onSubmit={executar} role="search">
          <Icone nome="busca" /><input ref={inputRef} value={comando} onChange={(e) => setComando(e.target.value)} placeholder="Pergunte, pesquise ou execute uma ação..." aria-label="Pergunte, pesquise ou execute uma ação" autoComplete="off" /><kbd>⌘ K</kbd><button type="submit" aria-label="Executar comando"><Icone nome="seta" /></button>
        </form>
        <div className="ccc-examples" aria-label="Exemplos de comandos"><span>Exemplos:</span>{EXEMPLOS.map((texto) => <button key={texto} type="button" onClick={() => usarExemplo(texto)}>{texto}</button>)}</div>

        <section className="ccc-section" aria-labelledby="ccc-actions-title">
          <div className="ccc-section__head"><h2 id="ccc-actions-title">Ações rápidas</h2><Link to="/busca"><Icone nome="configuracao" /> Personalizar</Link></div>
          <div className="ccc-actions">{ACOES.map((acao) => <Link to={acao.to} key={acao.titulo} className={`ccc-action ccc-action--${acao.icone}`}><span className="ccc-action__icon"><Icone nome={acao.icone} /></span><span><strong>{acao.titulo}</strong><small>{acao.detalhe}</small></span></Link>)}</div>
        </section>

        <section className="ccc-mobile-summary" aria-label="Resumo móvel">
          <Link className="ccc-mobile-summary__card" to="/agenda"><span><small>Seu dia</small><strong>{compromissosHoje.length} compromisso{compromissosHoje.length === 1 ? "" : "s"} hoje</strong><p>{proximo ? `Próximo: ${horario(proximo.scheduled_at)} · ${proximo.patient_name || "Compromisso"}` : "Agenda livre para novos compromissos"}</p></span><Icone nome="agenda" /></Link>

          <article className="ccc-mobile-commute" aria-label="Deslocamento">
            <header><span><small>Deslocamento</small><strong>{destino?.location.name || "Próximo compromisso"}</strong>{proximo && <p>{proximo.appointment_type} · {horario(proximo.scheduled_at)}</p>}</span><span className="ccc-mobile-commute__icon"><Icone nome="rota" /></span></header>
            {rota && destino ? <>
              <div className="ccc-mobile-commute__metrics">
                <span><small>Sair às</small><strong>{saidaRecomendada ? horario(saidaRecomendada.toISOString()) : "—"}</strong></span>
                <span><small>Tempo</small><strong>{Math.ceil(rota.duration_seconds / 60)} min</strong></span>
                <span><small>Distância</small><strong>{(rota.distance_meters / 1000).toFixed(1)} km</strong></span>
                <span><small>Trânsito</small><strong>{transito(rota.congestion)}</strong></span>
                {rota.traffic_delay_seconds > 0 && <span><small>Atraso</small><strong>+{Math.ceil(rota.traffic_delay_seconds / 60)} min</strong></span>}
                <span><small>Chegada</small><strong>{chegadaPrevista ? horario(chegadaPrevista.toISOString()) : "—"}</strong></span>
              </div>
              <div className="ccc-mobile-commute__map">
                <MapaDeslocamento rotas={deslocamento?.routes || []} origem={origem} destino={{ latitude: destino.location.latitude, longitude: destino.location.longitude, name: destino.location.name }} provider={deslocamento?.provider} updatedAt={deslocamento?.updated_at} googleMapsApiKey={configMapa?.api_key} />
              </div>
            </> : <div className={`ccc-mobile-commute__state${calculandoRota ? " is-loading" : ""}`}><span><Icone nome={calculandoRota ? "sincronizar" : "pin"} /></span><p>{descricaoDeslocamento}</p></div>}
            <footer><Link to="/agenda">{rota ? "Ver rota" : "Abrir Agenda"} <Icone nome="seta" /></Link>{mobilidade?.enabled && destino && destino.location.latitude != null && destino.location.longitude != null && (!mobilidade.automatic_foreground_refresh || !rota || erroRota) && <button type="button" onClick={() => calcularDeslocamento(true)} disabled={calculandoRota}>{calculandoRota ? "Atualizando..." : permissao === "negada" ? "Tentar novamente" : "Atualizar rota"}</button>}</footer>
          </article>

          <button className="ccc-mobile-summary__card ccc-mobile-summary__card--assistant" type="button" onClick={abrirAssistentePessoal}><span><small>Assistente</small><strong>{pendencias || pacientes || 0} item(ns) para acompanhar</strong><p>Agenda, pendências e comunicação</p></span><span className="ccc-spark">✦</span></button>
          <Link className="ccc-mobile-summary__card" to="/diretrizes"><span><small>Atualizações</small><strong>{atualizacoes.length ? `${atualizacoes.length} atualização(ões)` : "Central científica"}</strong><p>{atualizacoes[0]?.title || "Guidelines e estudos recentes"}</p></span><Icone nome="evidencia" /></Link>
        </section>

        <section className="ccc-section ccc-recent-section" aria-labelledby="ccc-recent-title">
          <div className="ccc-section__head"><h2 id="ccc-recent-title">Continuar de onde parei</h2></div>
          <div className="ccc-recent">{contextos.map((item) => <Link to={item.path} className="ccc-recent__card" key={item.path}><span className="ccc-recent__icon"><Icone nome={item.icone} /></span><span className="ccc-recent__meta">{item.detalhe}</span><strong>{item.titulo}</strong><small>{tempoRelativo(item.visitadoEm)}</small><i aria-hidden="true" /></Link>)}<Link to="/busca" className="ccc-recent__more" aria-label="Explorar mais contextos"><Icone nome="chevron" /></Link></div>
        </section>

        <section className="ccc-section ccc-updates-section" aria-labelledby="ccc-updates-title">
          <div className="ccc-section__head"><h2 id="ccc-updates-title">Atualizações que podem importar para você</h2><Link to="/diretrizes">Ver central <Icone nome="seta" /></Link></div>
          <div className="ccc-updates">{atualizacoes.length ? atualizacoes.map((item, indice) => <Link to="/diretrizes" key={item.id} className={`ccc-update ccc-update--${indice + 1}`}><small>{item.org || "Atualização científica"} · {dataCurta(item.published_at)}</small><strong>{item.title}</strong><p>{statusAtualizacao(item)}</p><span>{indice === 0 ? "Ver o que mudou" : indice === 1 ? "Resumo do estudo" : "Saiba mais"} <Icone nome="seta" /></span></Link>) : <Link to="/diretrizes" className="ccc-update ccc-update--empty"><small>Central científica</small><strong>Atualizações clínicas revisadas</strong><p>Novas publicações oficiais aparecem aqui quando detectadas.</p><span>Abrir central <Icone nome="seta" /></span></Link>}</div>
        </section>

        <section className="ccc-section ccc-home-fronts" aria-labelledby="ccc-fronts-title">
          <div className="ccc-section__head"><h2 id="ccc-fronts-title">Seu CorVIA</h2><Link to="/favoritos">Favoritos <Icone nome="seta" /></Link></div>
          <div className="ccc-home-fronts__grid">
            <Link to="/doencas"><small>Clínica & Decisão</small><strong>Resolver o caso</strong><p>Condições, medicamentos, exames, cálculos, triagem e fluxos conectados.</p><span>Entrar <Icone nome="seta" /></span></Link>
            <Link to="/estudos"><small>Estudo & Aprendizagem</small><strong>Entender e aprofundar</strong><p>{atualizacoes[0]?.title || "Evidências, estudos, guidelines, Timeline, casos e trilhas."}</p><span>Continuar estudando <Icone nome="seta" /></span></Link>
            <Link to="/round"><small>Trabalho & Assistência</small><strong>Executar e organizar</strong><p>Pacientes, prescrição, documentos, Agenda, CorVIA Mail e indicadores.</p><span>Abrir trabalho <Icone nome="seta" /></span></Link>
            <Link to="/busca" className="ccc-home-fronts__connections"><small>Tudo com Tudo</small><strong>Explore conexões clínicas</strong><p>Assunto canônico, evidências, estudos, guidelines, medicamentos e condutas relacionados.</p><span>Explorar relações <Icone nome="seta" /></span></Link>
          </div>
        </section>
      </main>

      <aside className="ccc-home__intelligence" aria-label="CorVIA Intelligence">
        <section className="ccc-rail-card ccc-intelligence-card">
          <header><span><Icone nome="assistente" /> CorVIA Intelligence</span><Link to="/busca">Ver tudo</Link></header>
          <div className="ccc-intelligence-list">
            <Link to="/diretrizes"><span><Icone nome="evidencia" /></span><strong>{atualizacoes.length || "—"}</strong><p>atualizações científicas nas últimas 24 horas</p></Link>
            <Link to="/diretrizes"><span><Icone nome="conhecimento" /></span><strong>{atualizacoes[0] ? "1" : "—"}</strong><p>{atualizacoes[0]?.title || "Guideline nova"}</p></Link>
            <Link to="/biblioteca"><span><Icone nome="check" /></span><strong>{catalogo?.published_total ?? catalogo?.total ?? "—"}</strong><p>conteúdos clínicos disponíveis</p></Link>
            <Link to="/busca"><span><Icone nome="busca" /></span><strong>↻</strong><p>Continuar sua última pesquisa</p></Link>
          </div>
          <Link to="/busca" className="ccc-intelligence-graph"><span>◎</span><span><strong>Explorar relações</strong><small>Tudo com Tudo</small></span><Icone nome="seta" /></Link>
          <div className="ccc-intelligence-metrics"><span><strong>{evidencias ?? "—"}</strong><small>evidências</small></span><span><strong>{estudos ?? "—"}</strong><small>estudos</small></span></div>
        </section>
      </aside>

      <aside className="ccc-home__assistant" aria-label="Assistente Pessoal">
        <section className="ccc-rail-card ccc-assistant-card ccc-assistant-card--window">
          <header><span><span className="ccc-spark">✦</span> Assistente Pessoal</span><span className="ccc-assistant-window-controls" aria-hidden="true"><i>−</i><i>×</i></span></header>
          <div className="ccc-assistant-greeting"><span className="ccc-spark">✦</span><div><strong>{saudacao()}, Dr. {primeiroNome(usuario?.full_name)}!</strong><small>Aqui está o resumo do seu dia.</small></div></div>

          <div className="ccc-assistant-block"><small>Seu dia</small><div className="ccc-assistant-row"><span><Icone nome="agenda" /></span><div><strong>{compromissosHoje.length} compromisso{compromissosHoje.length === 1 ? "" : "s"}</strong><p>{proximo ? `${dataCurta(proximo.scheduled_at)} · ${horario(proximo.scheduled_at)}` : "Nenhum compromisso pendente"}</p></div></div></div>

          <div className="ccc-assistant-block"><small>Próximo compromisso</small><div className="ccc-assistant-row"><span><Icone nome="pin" /></span><div><strong>{destino?.location.name || proximo?.patient_name || "Agenda disponível"}</strong><p>{destino ? `${destino.service_name} · ${horario(proximo?.scheduled_at)}` : proximo ? `${proximo.appointment_type} · ${horario(proximo.scheduled_at)}` : "Sem próximo compromisso definido"}</p></div></div><Link to="/agenda" className="ccc-assistant-inline-action">Ver agenda</Link></div>

          <div className="ccc-assistant-block"><small>Deslocamento</small><div className="ccc-assistant-row"><span><Icone nome="rota" /></span><div><strong>{saidaRecomendada ? `Sair às ${horario(saidaRecomendada.toISOString())}` : descricaoDeslocamento}</strong><p>{rota ? `${Math.ceil(rota.duration_seconds / 60)} min · ${(rota.distance_meters / 1000).toFixed(1)} km${rota.traffic_delay_seconds > 0 ? ` · +${Math.ceil(rota.traffic_delay_seconds / 60)} min` : ""}` : "A rota nunca é substituída por outro compromisso."}</p></div></div><Link to="/agenda" className="ccc-assistant-inline-action">Ver rota</Link></div>

          <div className="ccc-assistant-block"><small>Pendências</small><div className="ccc-assistant-checks"><span><i />{pendencias} agendamento{pendencias === 1 ? "" : "s"} a revisar</span><span><i />{pacientes ?? 0} paciente{pacientes === 1 ? "" : "s"} no round</span></div></div>

          <button type="button" className="ccc-assistant-input" onClick={abrirAssistentePessoal}><span>Pergunte ou peça algo...</span><Icone nome="assistente" /></button>
        </section>
      </aside>
    </div>
  );
}
