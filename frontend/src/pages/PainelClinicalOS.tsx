import { type FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Icone, { type NomeIcone } from "../components/Icone";
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
type Rota = { duration_seconds: number; distance_meters: number; traffic_delay_seconds: number };
type Deslocamento = { status: string; provider?: string; updated_at?: string; destination: ProximoLocal | null; routes: Rota[]; tips: string[] };

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
function primeiroNome(nome?: string) { return nome?.trim().split(/\s+/)[0] || "Doutor(a)"; }
function chaveContextosRecentes(userId?: number) { return userId ? `corvia:contextos-recentes:${userId}` : ""; }
function mesmoDia(a: Date, b: Date) { return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate(); }
function horario(valor?: string | null) { if (!valor) return "—"; const data = new Date(valor); return Number.isNaN(data.getTime()) ? "—" : data.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }); }
function dataCurta(valor: string) { const data = new Date(valor); return Number.isNaN(data.getTime()) ? "" : data.toLocaleDateString("pt-BR", { day: "2-digit", month: "short", year: "numeric", timeZone: "UTC" }); }
function tempoRelativo(timestamp: number) { if (!timestamp) return "Acesso hoje"; const minutos = Math.max(1, Math.round((Date.now() - timestamp) / 60000)); if (minutos < 60) return `Acesso há ${minutos} min`; const horas = Math.round(minutos / 60); if (horas < 24) return `Acesso há ${horas} h`; return `Acesso há ${Math.round(horas / 24)} d`; }
function statusAtualizacao(item: Atualizacao) { return item.status === "revisada" ? "Principais mudanças nas recomendações" : "Nova publicação detectada para revisão"; }
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
  const inputRef = useRef<HTMLInputElement>(null);

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
    api.get<Agendamento[]>("/appointments").then(setAgenda).catch(() => setAgenda([]));
    api.get<ProximoLocal[]>("/agenda/workday/next-locations").then(setProximosLocais).catch(() => setProximosLocais([]));
    api.get<PreferenciaMobilidade>("/agenda/mobility/preferences").then(setMobilidade).catch(() => setMobilidade(null));
  }, []);

  useEffect(() => {
    if (!mobilidade?.enabled || !navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition((position) => {
      api.post<Deslocamento>("/agenda/mobility/commute", { latitude: position.coords.latitude, longitude: position.coords.longitude }).then(setDeslocamento).catch(() => setDeslocamento(null));
    }, () => setDeslocamento(null), { enableHighAccuracy: false, timeout: 8000, maximumAge: 120000 });
  }, [mobilidade?.enabled]);

  useEffect(() => {
    function focar(evento: KeyboardEvent) { if (evento.key === "/" && document.activeElement?.tagName !== "INPUT" && document.activeElement?.tagName !== "TEXTAREA") { evento.preventDefault(); inputRef.current?.focus(); } }
    document.addEventListener("keydown", focar); return () => document.removeEventListener("keydown", focar);
  }, []);

  const contextos = useMemo(() => recentes.length ? recentes : CONTEXTOS_INICIAIS, [recentes]);
  const compromissosHoje = useMemo(() => agenda.filter((item) => item.status !== "cancelado" && mesmoDia(new Date(item.scheduled_at), new Date())).sort((a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at)), [agenda]);
  const proximo = useMemo(() => agenda.filter((item) => item.status !== "cancelado" && +new Date(item.scheduled_at) >= Date.now()).sort((a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at))[0], [agenda]);
  const pendencias = useMemo(() => agenda.filter((item) => ["pendente", "pending_external", "proposed"].includes(item.status)).length, [agenda]);
  const rota = deslocamento?.routes?.[0];
  const destino = proximosLocais[0];
  const saidaRecomendada = destino && rota ? new Date(new Date(destino.starts_at).getTime() - (rota.duration_seconds + destino.arrival_buffer_minutes * 60) * 1000) : null;

  function executar(evento: FormEvent) { evento.preventDefault(); if (comando.trim().length < 2) return; navigate(destinoDoComando(comando)); }
  function usarExemplo(texto: string) { setComando(texto); inputRef.current?.focus(); }
  function abrirAssistentePessoal() { window.dispatchEvent(new Event("corvia:abrir-assistente-pessoal")); }

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
          <button className="ccc-mobile-summary__card ccc-mobile-summary__card--assistant" type="button" onClick={abrirAssistentePessoal}><span><small>Assistente</small><strong>{pendencias || pacientes || 0} item(ns) para acompanhar</strong><p>Agenda, pendências e deslocamentos</p></span><span className="ccc-spark">✦</span></button>
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

          <div className="ccc-assistant-block"><small>Próximo compromisso</small><div className="ccc-assistant-row"><span><Icone nome="pin" /></span><div><strong>{destino?.location.name || proximo?.patient_name || "Agenda disponível"}</strong><p>{destino ? `${destino.service_name} · ${horario(destino.starts_at)}` : proximo ? `${proximo.appointment_type} · ${horario(proximo.scheduled_at)}` : "Sem próximo compromisso definido"}</p></div></div><Link to="/agenda" className="ccc-assistant-inline-action">Ver agenda</Link></div>

          <div className="ccc-assistant-block"><small>Deslocamento</small><div className="ccc-assistant-row"><span><Icone nome="rota" /></span><div><strong>{saidaRecomendada ? `Sair às ${saidaRecomendada.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}` : mobilidade?.enabled ? "Atualizando rota" : "Planejamento disponível"}</strong><p>{rota ? `Trânsito: ${Math.ceil(rota.duration_seconds / 60)} min${rota.traffic_delay_seconds > 60 ? ` · +${Math.ceil(rota.traffic_delay_seconds / 60)} min` : ""}` : "Ative/consulte a rota na Agenda"}</p></div></div><Link to="/agenda" className="ccc-assistant-inline-action">Ver rota</Link></div>

          <div className="ccc-assistant-block"><small>Pendências</small><div className="ccc-assistant-checks"><span><i />{pendencias} agendamento{pendencias === 1 ? "" : "s"} a revisar</span><span><i />{pacientes ?? 0} paciente{pacientes === 1 ? "" : "s"} no round</span></div></div>

          <button type="button" className="ccc-assistant-input" onClick={abrirAssistentePessoal}><span>Pergunte ou peça algo...</span><Icone nome="assistente" /></button>
        </section>
      </aside>
    </div>
  );
}
