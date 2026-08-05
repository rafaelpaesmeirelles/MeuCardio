import { useEffect, useMemo, useRef, useState } from "react";
import type { CSSProperties } from "react";
import Icone from "../components/Icone";
import { ApiError, api } from "../lib/api";

type Visao = "dia" | "semana" | "mes" | "lista";

type LocalAgenda = {
  id: number;
  name: string;
  timezone: string;
  address: Record<string, string>;
  latitude: number | null;
  longitude: number | null;
  default_arrival_buffer_minutes: number;
  color: string;
  active: boolean;
};

type Servico = {
  id: number;
  location_id: number | null;
  code: string;
  name: string;
  duration_minutes: number;
  visit_mode: string;
  payment_mode: string;
  private_price_cents: number | null;
  allow_extra_slot: boolean;
  color: string;
  active: boolean;
};

type Agendamento = {
  id: number;
  patient_name: string | null;
  patient_phone: string | null;
  starts_at: string;
  ends_at: string;
  duration_minutes: number;
  appointment_type: string;
  status: string;
  notes: string | null;
  location: LocalAgenda | null;
  service: Servico | null;
  visit_mode: string;
  payment_mode: string;
  price_cents: number | null;
  source: string;
  sync_status: string;
  conflict_reason: string | null;
  version: number;
};

type Integracao = {
  id: number;
  provider: string;
  display_name: string;
  status: string;
  sync_strategy: string;
  enabled: boolean;
  write_enabled: boolean;
  has_credentials: boolean;
  last_success_at: string | null;
  last_error_message: string | null;
};

type Capacidades = {
  integrations_enabled: boolean;
  external_writes_enabled: boolean;
  traffic_configured: boolean;
  traffic_provider: string;
  connectors: Array<{
    provider: string;
    name: string;
    status: string;
    capabilities: Record<string, boolean>;
  }>;
};

type PreferenciaMobilidade = {
  enabled: boolean;
  consent_at: string | null;
  automatic_foreground_refresh: boolean;
  refresh_interval_minutes: number;
  traffic_configured: boolean;
};

type RotinaTrabalho = {
  id: number;
  location_id: number;
  service_id: number | null;
  weekday: number;
  start_time: string;
  end_time: string;
  label: string;
  routine_type: string;
  visit_mode: string;
  arrival_buffer_minutes: number;
  planning_notes: string | null;
  active: boolean;
  location: LocalAgenda | null;
  service: Servico | null;
};

const DIAS_SEMANA = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"];

const STATUS: Record<string, string> = {
  pending_external: "Aguardando sistema externo",
  proposed: "Proposto",
  pendente: "Pendente",
  confirmado: "Confirmado",
  booked: "Confirmado",
  arrived: "Paciente chegou",
  realizado: "Realizado",
  faltou: "Faltou",
  cancelado: "Cancelado",
};

const ORIGEM: Record<string, string> = {
  corvia: "Corvia",
  google_calendar: "Google",
  microsoft_365: "Microsoft 365",
  feegow: "Feegow",
};

function localDateTime(date = new Date()) {
  const copy = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
  return copy.toISOString().slice(0, 16);
}

function inicioDia(date: Date) {
  const copy = new Date(date);
  copy.setHours(0, 0, 0, 0);
  return copy;
}

function inicioSemana(date: Date) {
  const copy = inicioDia(date);
  const offset = (copy.getDay() + 6) % 7;
  copy.setDate(copy.getDate() - offset);
  return copy;
}

function somaDias(date: Date, days: number) {
  const copy = new Date(date);
  copy.setDate(copy.getDate() + days);
  return copy;
}

function mesmoDia(value: string | Date, date: Date) {
  const first = new Date(value);
  return first.getFullYear() === date.getFullYear()
    && first.getMonth() === date.getMonth()
    && first.getDate() === date.getDate();
}

function horario(value: string) {
  return new Date(value).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
}

function dataCurta(date: Date) {
  return date.toLocaleDateString("pt-BR", { weekday: "short", day: "2-digit", month: "short" });
}

function dataTitulo(date: Date, visao: Visao) {
  if (visao === "dia") return date.toLocaleDateString("pt-BR", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
  if (visao === "mes") return date.toLocaleDateString("pt-BR", { month: "long", year: "numeric" });
  const start = inicioSemana(date);
  const end = somaDias(start, 6);
  return `${start.toLocaleDateString("pt-BR", { day: "2-digit", month: "short" })} — ${end.toLocaleDateString("pt-BR", { day: "2-digit", month: "short", year: "numeric" })}`;
}

function formatarDinheiro(value: number | null) {
  return value == null ? "Não definido" : (value / 100).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function endereco(local: LocalAgenda) {
  return [local.address?.street, local.address?.number, local.address?.city, local.address?.state].filter(Boolean).join(" · ") || "Endereço não informado";
}

function Evento({ item, aoCancelar }: { item: Agendamento; aoCancelar: (item: Agendamento) => void }) {
  return (
    <article className={`agenda-evento agenda-evento--${item.status}`} style={{ "--evento-cor": item.service?.color || item.location?.color || "#087E8B" } as CSSProperties}>
      <div className="agenda-evento__hora"><strong>{horario(item.starts_at)}</strong><span>{item.duration_minutes} min</span></div>
      <div className="agenda-evento__corpo">
        <div className="agenda-evento__linha">
          <h3>{item.patient_name || "Paciente não informado"}</h3>
          <span className="agenda-pill">{STATUS[item.status] || item.status}</span>
        </div>
        <p>{item.service?.name || item.appointment_type} · {item.visit_mode === "teleconsulta" ? "Teleconsulta" : item.location?.name || "Local a definir"}</p>
        <div className="agenda-evento__meta">
          <span><Icone nome="sincronizar" /> {ORIGEM[item.source] || item.source}</span>
          {item.conflict_reason && <span className="agenda-evento__conflito">Encaixe</span>}
          {item.sync_status === "pending_external" && <span>Sincronizando…</span>}
        </div>
      </div>
      {!['cancelado', 'realizado'].includes(item.status) && (
        <button className="agenda-evento__mais" onClick={() => aoCancelar(item)} aria-label={`Cancelar agendamento de ${item.patient_name || "paciente"}`}><Icone nome="mais" /></button>
      )}
    </article>
  );
}

export default function Agenda() {
  const [visao, setVisao] = useState<Visao>("semana");
  const [referencia, setReferencia] = useState(new Date());
  const [agendamentos, setAgendamentos] = useState<Agendamento[] | null>(null);
  const [locais, setLocais] = useState<LocalAgenda[]>([]);
  const [servicos, setServicos] = useState<Servico[]>([]);
  const [integracoes, setIntegracoes] = useState<Integracao[]>([]);
  const [rotinas, setRotinas] = useState<RotinaTrabalho[]>([]);
  const [capacidades, setCapacidades] = useState<Capacidades | null>(null);
  const [mobilidade, setMobilidade] = useState<PreferenciaMobilidade | null>(null);
  const [busca, setBusca] = useState("");
  const [filtroLocal, setFiltroLocal] = useState("");
  const [filtroOrigem, setFiltroOrigem] = useState("");
  const [novoAberto, setNovoAberto] = useState(false);
  const [configAberta, setConfigAberta] = useState(false);
  const [cancelando, setCancelando] = useState<Agendamento | null>(null);
  const [motivoCancelamento, setMotivoCancelamento] = useState("");
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");
  const [novo, setNovo] = useState({
    patient_name: "", patient_phone: "", patient_email: "", email_consent: false,
    starts_at: localDateTime(), service_id: "", location_id: "", duration_minutes: 30,
    visit_mode: "presencial", payment_mode: "particular", insurance_name: "", notes: "",
  });
  const [novoLocal, setNovoLocal] = useState({ name: "", city: "", state: "", latitude: "", longitude: "" });
  const [novoServico, setNovoServico] = useState({ name: "", code: "", location_id: "", duration_minutes: 30, price: "", allow_extra_slot: false });
  const [novaRotina, setNovaRotina] = useState({
    label: "Rotina de atendimento", location_id: "", service_id: "", weekdays: [0, 1, 2, 3, 4],
    start_time: "08:00", end_time: "18:00", routine_type: "atendimento", visit_mode: "presencial",
    arrival_buffer_minutes: 15, planning_notes: "",
  });
  const novoModalRef = useRef<HTMLDivElement>(null);
  const configModalRef = useRef<HTMLDivElement>(null);
  const cancelarModalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const panel = cancelando ? cancelarModalRef.current : configAberta ? configModalRef.current : novoAberto ? novoModalRef.current : null;
    if (!panel) return;
    const previous = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const oldOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const focusables = () => Array.from(panel.querySelectorAll<HTMLElement>(
      'button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [href], [tabindex]:not([tabindex="-1"])',
    )).filter((element) => !element.hidden && element.getClientRects().length > 0);
    window.requestAnimationFrame(() => (panel.querySelector<HTMLElement>("[autofocus]") || focusables()[0] || panel).focus());
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        if (cancelando) { setCancelando(null); setMotivoCancelamento(""); }
        else if (configAberta) setConfigAberta(false);
        else setNovoAberto(false);
        return;
      }
      if (event.key !== "Tab") return;
      const items = focusables();
      if (!items.length) { event.preventDefault(); panel.focus(); return; }
      const first = items[0]; const last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = oldOverflow;
      previous?.focus();
    };
  }, [novoAberto, configAberta, cancelando]);

  async function carregar() {
    const [appointments, locations, services, integrations, capabilities, mobility, routines] = await Promise.all([
      api.get<Agendamento[]>("/agenda/appointments"),
      api.get<LocalAgenda[]>("/agenda/locations"),
      api.get<Servico[]>("/agenda/services"),
      api.get<Integracao[]>("/agenda/integrations"),
      api.get<Capacidades>("/agenda/capabilities"),
      api.get<PreferenciaMobilidade>("/agenda/mobility/preferences"),
      api.get<RotinaTrabalho[]>("/agenda/work-routines"),
    ]);
    setAgendamentos(appointments); setLocais(locations); setServicos(services);
    setIntegracoes(integrations); setCapacidades(capabilities); setMobilidade(mobility); setRotinas(routines);
  }

  useEffect(() => { carregar().catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível abrir a agenda.")); }, []);

  const filtrados = useMemo(() => (agendamentos ?? []).filter((item) => {
    const query = busca.trim().toLocaleLowerCase("pt-BR");
    if (query && !`${item.patient_name || ""} ${item.service?.name || ""} ${item.location?.name || ""}`.toLocaleLowerCase("pt-BR").includes(query)) return false;
    if (filtroLocal && item.location?.id !== Number(filtroLocal)) return false;
    if (filtroOrigem && item.source !== filtroOrigem) return false;
    return true;
  }), [agendamentos, busca, filtroLocal, filtroOrigem]);

  const diasVisiveis = useMemo(() => {
    if (visao === "dia") return [inicioDia(referencia)];
    if (visao === "mes") {
      const first = new Date(referencia.getFullYear(), referencia.getMonth(), 1);
      const gridStart = inicioSemana(first);
      return Array.from({ length: 42 }, (_, index) => somaDias(gridStart, index));
    }
    const start = inicioSemana(referencia);
    return Array.from({ length: 7 }, (_, index) => somaDias(start, index));
  }, [referencia, visao]);

  function navegar(direction: number) {
    const copy = new Date(referencia);
    if (visao === "mes") copy.setMonth(copy.getMonth() + direction);
    else copy.setDate(copy.getDate() + direction * (visao === "dia" ? 1 : 7));
    setReferencia(copy);
  }

  function selecionarServico(id: string) {
    const service = servicos.find((item) => item.id === Number(id));
    setNovo((current) => ({ ...current, service_id: id, duration_minutes: service?.duration_minutes || current.duration_minutes, location_id: service?.location_id ? String(service.location_id) : current.location_id, visit_mode: service?.visit_mode || current.visit_mode, payment_mode: service?.payment_mode || current.payment_mode }));
  }

  async function salvarAgendamento() {
    if (!novo.patient_name.trim() || !novo.starts_at) return;
    setSalvando(true); setErro("");
    try {
      await api.post("/agenda/appointments", {
        patient_name: novo.patient_name, patient_phone: novo.patient_phone || null,
        patient_email: novo.patient_email || null, email_consent: novo.email_consent,
        starts_at: new Date(novo.starts_at).toISOString(), duration_minutes: novo.duration_minutes,
        service_id: novo.service_id ? Number(novo.service_id) : null,
        location_id: novo.location_id ? Number(novo.location_id) : null,
        visit_mode: novo.visit_mode, payment_mode: novo.payment_mode,
        insurance_name: novo.insurance_name || null, notes: novo.notes || null,
      });
      setNovoAberto(false);
      setNovo({ patient_name: "", patient_phone: "", patient_email: "", email_consent: false, starts_at: localDateTime(), service_id: "", location_id: "", duration_minutes: 30, visit_mode: "presencial", payment_mode: "particular", insurance_name: "", notes: "" });
      await carregar();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível criar o agendamento.");
    } finally { setSalvando(false); }
  }

  async function confirmarCancelamento() {
    if (!cancelando || !motivoCancelamento.trim()) return;
    try {
      await api.post(`/agenda/appointments/${cancelando.id}/cancel`, { reason: motivoCancelamento, expected_version: cancelando.version });
      setCancelando(null); setMotivoCancelamento("");
      await carregar();
    } catch (e) { setErro(e instanceof ApiError ? e.message : "Não foi possível cancelar."); }
  }

  async function adicionarLocal() {
    if (!novoLocal.name.trim()) return;
    await api.post("/agenda/locations", {
      name: novoLocal.name,
      address: { city: novoLocal.city, state: novoLocal.state.toUpperCase() },
      latitude: novoLocal.latitude ? Number(novoLocal.latitude) : null,
      longitude: novoLocal.longitude ? Number(novoLocal.longitude) : null,
    });
    setNovoLocal({ name: "", city: "", state: "", latitude: "", longitude: "" });
    await carregar();
  }

  async function adicionarServico() {
    if (!novoServico.name.trim() || !novoServico.code.trim()) return;
    await api.post("/agenda/services", {
      name: novoServico.name,
      code: novoServico.code.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9_-]+/g, "-").replace(/^-|-$/g, ""),
      location_id: novoServico.location_id ? Number(novoServico.location_id) : null,
      duration_minutes: novoServico.duration_minutes,
      private_price_cents: novoServico.price ? Math.round(Number(novoServico.price.replace(",", ".")) * 100) : null,
      allow_extra_slot: novoServico.allow_extra_slot,
    });
    setNovoServico({ name: "", code: "", location_id: "", duration_minutes: 30, price: "", allow_extra_slot: false });
    await carregar();
  }

  function alternarDiaRotina(day: number) {
    setNovaRotina((current) => ({
      ...current,
      weekdays: current.weekdays.includes(day)
        ? current.weekdays.filter((item) => item !== day)
        : [...current.weekdays, day].sort(),
    }));
  }

  async function adicionarRotina() {
    if (!novaRotina.location_id || !novaRotina.weekdays.length || !novaRotina.label.trim()) return;
    await api.post("/agenda/work-routines", {
      ...novaRotina,
      location_id: Number(novaRotina.location_id),
      service_id: novaRotina.service_id ? Number(novaRotina.service_id) : null,
      planning_notes: novaRotina.planning_notes || null,
    });
    setNovaRotina((current) => ({ ...current, planning_notes: "" }));
    await carregar();
  }

  async function removerRotina(id: number) {
    await api.delete(`/agenda/work-routines/${id}`);
    await carregar();
  }

  async function alternarMobilidade() {
    const enabled = !mobilidade?.enabled;
    const updated = await api.put<PreferenciaMobilidade>("/agenda/mobility/preferences", {
      enabled, consent_accepted: enabled, automatic_foreground_refresh: true,
      refresh_interval_minutes: mobilidade?.refresh_interval_minutes || 5, travel_mode: "driving",
    });
    setMobilidade(updated);
  }

  const hoje = new Date();
  const conflitos = filtrados.filter((item) => item.conflict_reason).length;
  const proximos = filtrados.filter((item) => new Date(item.starts_at).getTime() >= Date.now() && item.status !== "cancelado");

  return (
    <div className="agenda-integrada">
      <header className="agenda-cabecalho">
        <div><p className="eyebrow">Operação clínica</p><h1>Agenda Integrada</h1><p>Horários, locais, recursos e sistemas externos em uma única visão.</p></div>
        <div className="agenda-cabecalho__acoes">
          <button className="botao botao--secundario" onClick={() => setConfigAberta(true)}><Icone nome="configuracao" /> Configurar</button>
          <button className="botao" onClick={() => setNovoAberto(true)}><Icone nome="agenda" /> Novo agendamento</button>
        </div>
      </header>

      <section className="agenda-status" aria-label="Status da agenda">
        <span className="agenda-status__ok"><i /> Agenda Corvia ativa</span>
        <span><Icone nome="sincronizar" /> {integracoes.filter((item) => item.status === "connected").length} integrações conectadas</span>
        <span>{capacidades?.external_writes_enabled ? "Escrita externa homologada" : "Escrita externa protegida"}</span>
        <button onClick={() => carregar()}><Icone nome="sincronizar" /> Atualizar</button>
      </section>

      {erro && <div className="agenda-alerta" role="alert"><strong>Atenção</strong><span>{erro}</span><button onClick={() => setErro("")} aria-label="Fechar"><Icone nome="fechar" /></button></div>}

      <section className="agenda-ferramentas">
        <div className="agenda-navegacao">
          <button onClick={() => navegar(-1)} aria-label="Período anterior">‹</button>
          <button className="agenda-hoje" onClick={() => setReferencia(new Date())}>Hoje</button>
          <button onClick={() => navegar(1)} aria-label="Próximo período">›</button>
          <h2>{dataTitulo(referencia, visao)}</h2>
        </div>
        <div className="agenda-visoes" aria-label="Visualização">
          {(["dia", "semana", "mes", "lista"] as Visao[]).map((item) => <button key={item} className={visao === item ? "ativo" : ""} onClick={() => setVisao(item)}>{item.charAt(0).toUpperCase() + item.slice(1)}</button>)}
        </div>
      </section>

      <section className="agenda-filtros">
        <label className="agenda-busca"><Icone nome="busca" /><span className="sr-only">Buscar</span><input value={busca} onChange={(e) => setBusca(e.target.value)} placeholder="Paciente, serviço ou local" /></label>
        <label><Icone nome="pin" /><span className="sr-only">Filtrar local</span><select value={filtroLocal} onChange={(e) => setFiltroLocal(e.target.value)}><option value="">Todos os locais</option>{locais.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
        <label><Icone nome="sincronizar" /><span className="sr-only">Filtrar origem</span><select value={filtroOrigem} onChange={(e) => setFiltroOrigem(e.target.value)}><option value="">Todas as origens</option><option value="corvia">Corvia</option><option value="google_calendar">Google</option><option value="microsoft_365">Microsoft 365</option></select></label>
      </section>

      <div className="agenda-layout">
        <main className="agenda-calendario">
          {agendamentos === null ? <p className="agenda-carregando">Organizando sua agenda…</p> : visao === "lista" ? (
            <div className="agenda-lista">
              {proximos.length === 0 ? <p className="agenda-vazio">Nenhum compromisso encontrado.</p> : proximos.slice(0, 100).map((item) => <div key={item.id} className="agenda-lista__linha"><time>{new Date(item.starts_at).toLocaleDateString("pt-BR", { day: "2-digit", month: "short" })}</time><Evento item={item} aoCancelar={setCancelando} /></div>)}
            </div>
          ) : (
            <div className={`agenda-grade agenda-grade--${visao}`}>
              {diasVisiveis.map((dia) => {
                const items = filtrados.filter((item) => mesmoDia(item.starts_at, dia)).sort((a, b) => +new Date(a.starts_at) - +new Date(b.starts_at));
                const outside = visao === "mes" && dia.getMonth() !== referencia.getMonth();
                return <section key={dia.toISOString()} className={`agenda-dia${mesmoDia(dia, hoje) ? " agenda-dia--hoje" : ""}${outside ? " agenda-dia--fora" : ""}`}>
                  <header><span>{dataCurta(dia)}</span>{mesmoDia(dia, hoje) && <i>Hoje</i>}</header>
                  <div>{items.length ? items.map((item) => <Evento key={item.id} item={item} aoCancelar={setCancelando} />) : <button className="agenda-dia__livre" onClick={() => { const slot = new Date(dia); slot.setHours(9, 0, 0, 0); setNovo((current) => ({ ...current, starts_at: localDateTime(slot) })); setNovoAberto(true); }}>Horário livre <span>+</span></button>}</div>
                </section>;
              })}
            </div>
          )}
        </main>

        <aside className="agenda-insights" aria-label="Inteligência da agenda">
          <article><p className="eyebrow">Próximo atendimento</p>{proximos[0] ? <><strong>{horario(proximos[0].starts_at)} · {proximos[0].patient_name}</strong><span>{proximos[0].location?.name || "Local a definir"}</span></> : <span>Agenda livre.</span>}</article>
          <article><p className="eyebrow">Operação</p><div className="agenda-insights__metricas"><span><strong>{proximos.length}</strong> próximos</span><span><strong>{conflitos}</strong> encaixes</span><span><strong>{locais.length}</strong> locais</span></div></article>
          <article className="agenda-insights__mobilidade"><p className="eyebrow">Deslocamento inteligente</p><strong>{mobilidade?.enabled ? "Atualização automática ativa" : "Ative o trânsito no painel"}</strong><span>{capacidades?.traffic_configured ? `Trânsito por ${capacidades.traffic_provider}` : "Aguardando credencial do provedor de trânsito"}</span><button onClick={() => setConfigAberta(true)}>Configurar mobilidade <Icone nome="seta" /></button></article>
          <article><p className="eyebrow">Sincronização</p>{integracoes.length ? integracoes.map((item) => <div className="agenda-integracao-mini" key={item.id}><i className={`status-${item.status}`} /><span><strong>{item.display_name}</strong><small>{item.last_success_at ? `Atualizada ${new Date(item.last_success_at).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}` : item.status}</small></span></div>) : <span>Nenhum sistema externo conectado.</span>}</article>
        </aside>
      </div>

      {novoAberto && <div className="agenda-modal" role="dialog" aria-modal="true" aria-labelledby="novo-agendamento-titulo"><div className="agenda-modal__painel" ref={novoModalRef} tabIndex={-1}>
        <header><div><p className="eyebrow">Novo compromisso</p><h2 id="novo-agendamento-titulo">Agendar atendimento</h2></div><button onClick={() => setNovoAberto(false)} aria-label="Fechar"><Icone nome="fechar" /></button></header>
        <div className="agenda-form-grid">
          <label className="span-2">Paciente<input autoFocus value={novo.patient_name} onChange={(e) => setNovo({ ...novo, patient_name: e.target.value })} placeholder="Nome completo" /></label>
          <label>Telefone<input value={novo.patient_phone} onChange={(e) => setNovo({ ...novo, patient_phone: e.target.value })} /></label>
          <label>E-mail<input type="email" value={novo.patient_email} onChange={(e) => setNovo({ ...novo, patient_email: e.target.value })} /></label>
          {novo.patient_email && <label className="agenda-check span-2"><input type="checkbox" checked={novo.email_consent} onChange={(e) => setNovo({ ...novo, email_consent: e.target.checked })} /> Paciente autorizou receber a confirmação por e-mail.</label>}
          <label>Serviço<select value={novo.service_id} onChange={(e) => selecionarServico(e.target.value)}><option value="">Consulta geral</option>{servicos.filter((item) => item.active).map((item) => <option key={item.id} value={item.id}>{item.name} · {item.duration_minutes} min</option>)}</select></label>
          <label>Local<select value={novo.location_id} onChange={(e) => setNovo({ ...novo, location_id: e.target.value })}><option value="">A definir</option>{locais.filter((item) => item.active).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
          <label>Data e hora<input type="datetime-local" value={novo.starts_at} onChange={(e) => setNovo({ ...novo, starts_at: e.target.value })} /></label>
          <label>Duração<input type="number" min={5} max={1440} value={novo.duration_minutes} onChange={(e) => setNovo({ ...novo, duration_minutes: Number(e.target.value) })} /></label>
          <label>Modalidade<select value={novo.visit_mode} onChange={(e) => setNovo({ ...novo, visit_mode: e.target.value })}><option value="presencial">Presencial</option><option value="teleconsulta">Teleconsulta</option><option value="domiciliar">Domiciliar</option></select></label>
          <label>Pagamento<select value={novo.payment_mode} onChange={(e) => setNovo({ ...novo, payment_mode: e.target.value })}><option value="particular">Particular</option><option value="convenio">Convênio</option><option value="cortesia">Cortesia</option><option value="nao_informado">A definir</option></select></label>
          {novo.payment_mode === "convenio" && <label className="span-2">Convênio<input value={novo.insurance_name} onChange={(e) => setNovo({ ...novo, insurance_name: e.target.value })} /></label>}
          <label className="span-2">Observações<textarea rows={3} value={novo.notes} onChange={(e) => setNovo({ ...novo, notes: e.target.value })} /></label>
        </div>
        <footer><button className="botao botao--secundario" onClick={() => setNovoAberto(false)}>Cancelar</button><button className="botao" disabled={salvando || !novo.patient_name.trim()} onClick={salvarAgendamento}>{salvando ? "Verificando agenda…" : "Confirmar agendamento"}</button></footer>
      </div></div>}

      {cancelando && <div className="agenda-modal" role="dialog" aria-modal="true" aria-labelledby="cancelar-agendamento-titulo"><div className="agenda-modal__painel agenda-modal__painel--compacto" ref={cancelarModalRef} tabIndex={-1}>
        <header><div><p className="eyebrow">Confirmação necessária</p><h2 id="cancelar-agendamento-titulo">Cancelar agendamento</h2></div><button onClick={() => { setCancelando(null); setMotivoCancelamento(""); }} aria-label="Fechar"><Icone nome="fechar" /></button></header>
        <div className="agenda-form-grid"><p className="span-2 agenda-cancelamento-resumo"><strong>{cancelando.patient_name || "Paciente"}</strong><span>{new Date(cancelando.starts_at).toLocaleString("pt-BR", { dateStyle: "medium", timeStyle: "short" })}</span></p><label className="span-2">Motivo do cancelamento<textarea autoFocus rows={3} maxLength={500} value={motivoCancelamento} onChange={(e) => setMotivoCancelamento(e.target.value)} placeholder="Registre o motivo para manter a rastreabilidade" /></label></div>
        <footer><button className="botao botao--secundario" onClick={() => { setCancelando(null); setMotivoCancelamento(""); }}>Manter agendamento</button><button className="botao agenda-botao--perigo" disabled={motivoCancelamento.trim().length < 3} onClick={confirmarCancelamento}>Confirmar cancelamento</button></footer>
      </div></div>}

      {configAberta && <div className="agenda-modal agenda-modal--config" role="dialog" aria-modal="true" aria-labelledby="config-agenda-titulo"><div className="agenda-modal__painel" ref={configModalRef} tabIndex={-1}>
        <header><div><p className="eyebrow">Preferências profissionais</p><h2 id="config-agenda-titulo">Configurar agenda</h2></div><button onClick={() => setConfigAberta(false)} aria-label="Fechar"><Icone nome="fechar" /></button></header>
        <section className="agenda-config-section"><div className="agenda-config-section__title"><div><h3>Locais de atendimento</h3><p>Base para disponibilidade, deslocamento e recursos.</p></div><span>{locais.length}</span></div>{locais.map((item) => <div className="agenda-config-item" key={item.id}><i style={{ background: item.color }} /><span><strong>{item.name}</strong><small>{endereco(item)} · {item.latitude ? "GPS configurado" : "GPS pendente"}</small></span></div>)}<div className="agenda-config-form"><input placeholder="Nome do local" value={novoLocal.name} onChange={(e) => setNovoLocal({ ...novoLocal, name: e.target.value })} /><input placeholder="Cidade" value={novoLocal.city} onChange={(e) => setNovoLocal({ ...novoLocal, city: e.target.value })} /><input placeholder="UF" maxLength={2} value={novoLocal.state} onChange={(e) => setNovoLocal({ ...novoLocal, state: e.target.value })} /><details><summary>Coordenadas para trânsito</summary><div><input inputMode="decimal" placeholder="Latitude" value={novoLocal.latitude} onChange={(e) => setNovoLocal({ ...novoLocal, latitude: e.target.value })} /><input inputMode="decimal" placeholder="Longitude" value={novoLocal.longitude} onChange={(e) => setNovoLocal({ ...novoLocal, longitude: e.target.value })} /></div></details><button className="botao botao--secundario" onClick={() => adicionarLocal().catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível adicionar o local."))}>Adicionar local</button></div></section>
        <section className="agenda-config-section agenda-rotina">
          <div className="agenda-config-section__title"><div><h3>Rotina profissional</h3><p>Entrada, saída, locais e antecedência para organizar automaticamente cada dia.</p></div><span>{rotinas.filter((item) => item.active).length}</span></div>
          <div className="agenda-rotina__lista">
            {rotinas.filter((item) => item.active).length ? rotinas.filter((item) => item.active).map((item) => <div className="agenda-config-item" key={item.id}>
              <i style={{ background: item.location?.color || "#087E8B" }} />
              <span><strong>{DIAS_SEMANA[item.weekday]} · {item.start_time.slice(0, 5)}–{item.end_time.slice(0, 5)} · {item.location?.name}</strong><small>{item.label} · chegar {item.arrival_buffer_minutes} min antes{item.service ? ` · ${item.service.name}` : ""}</small></span>
              <button className="agenda-icon-button" onClick={() => removerRotina(item.id).catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível remover a rotina."))} aria-label={`Remover rotina de ${DIAS_SEMANA[item.weekday]}`}><Icone nome="fechar" /></button>
            </div>) : <p className="agenda-config-vazio">Cadastre a rotina para o Corvia antecipar horários, locais e deslocamentos.</p>}
          </div>
          <div className="agenda-config-form agenda-config-form--routine">
            <label className="span-2">Nome da rotina<input value={novaRotina.label} onChange={(e) => setNovaRotina({ ...novaRotina, label: e.target.value })} placeholder="Ex.: Consultório da manhã" /></label>
            <label>Local<select value={novaRotina.location_id} onChange={(e) => setNovaRotina({ ...novaRotina, location_id: e.target.value })}><option value="">Selecione</option>{locais.filter((item) => item.active).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
            <label>Serviço padrão<select value={novaRotina.service_id} onChange={(e) => setNovaRotina({ ...novaRotina, service_id: e.target.value })}><option value="">Todos</option>{servicos.filter((item) => item.active).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
            <fieldset className="agenda-rotina__dias span-2"><legend>Dias da semana</legend><div>{DIAS_SEMANA.map((day, index) => <button key={day} type="button" className={novaRotina.weekdays.includes(index) ? "ativo" : ""} aria-pressed={novaRotina.weekdays.includes(index)} onClick={() => alternarDiaRotina(index)}>{day}</button>)}</div></fieldset>
            <label>Entrada<input type="time" value={novaRotina.start_time} onChange={(e) => setNovaRotina({ ...novaRotina, start_time: e.target.value })} /></label>
            <label>Saída<input type="time" value={novaRotina.end_time} onChange={(e) => setNovaRotina({ ...novaRotina, end_time: e.target.value })} /></label>
            <label>Tipo<select value={novaRotina.routine_type} onChange={(e) => setNovaRotina({ ...novaRotina, routine_type: e.target.value })}><option value="atendimento">Atendimento</option><option value="plantao">Plantão</option><option value="telemedicina">Telemedicina</option><option value="administrativo">Administrativo</option><option value="outro">Outro</option></select></label>
            <label>Modalidade<select value={novaRotina.visit_mode} onChange={(e) => setNovaRotina({ ...novaRotina, visit_mode: e.target.value })}><option value="presencial">Presencial</option><option value="teleconsulta">Teleconsulta</option><option value="domiciliar">Domiciliar</option></select></label>
            <label>Chegar antes (min)<input type="number" min={0} max={180} value={novaRotina.arrival_buffer_minutes} onChange={(e) => setNovaRotina({ ...novaRotina, arrival_buffer_minutes: Number(e.target.value) })} /></label>
            <label className="span-2">Observações de planejamento<textarea rows={2} value={novaRotina.planning_notes} onChange={(e) => setNovaRotina({ ...novaRotina, planning_notes: e.target.value })} placeholder="Estacionamento, preparo do consultório, intervalo ou orientação relevante" /></label>
            <p className="agenda-config-help span-2">Para intervalos, cadastre dois períodos no mesmo dia. Férias, feriados e plantões excepcionais serão tratados como exceções sem alterar a rotina-base.</p>
            <button className="botao botao--secundario" disabled={!novaRotina.location_id || !novaRotina.weekdays.length || novaRotina.end_time <= novaRotina.start_time} onClick={() => adicionarRotina().catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível cadastrar a rotina."))}>Salvar rotina</button>
          </div>
        </section>
        <section className="agenda-config-section"><div className="agenda-config-section__title"><div><h3>Catálogo de serviços</h3><p>Duração, preço, modalidade e política de encaixe.</p></div><span>{servicos.length}</span></div>{servicos.map((item) => <div className="agenda-config-item" key={item.id}><i style={{ background: item.color }} /><span><strong>{item.name} · {item.duration_minutes} min</strong><small>{item.visit_mode} · {formatarDinheiro(item.private_price_cents)}{item.allow_extra_slot ? " · aceita encaixe" : ""}</small></span></div>)}<div className="agenda-config-form agenda-config-form--service"><input placeholder="Nome do serviço" value={novoServico.name} onChange={(e) => setNovoServico({ ...novoServico, name: e.target.value, code: e.target.value })} /><select value={novoServico.location_id} onChange={(e) => setNovoServico({ ...novoServico, location_id: e.target.value })}><option value="">Todos os locais</option>{locais.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select><input type="number" min={5} value={novoServico.duration_minutes} onChange={(e) => setNovoServico({ ...novoServico, duration_minutes: Number(e.target.value) })} /><input inputMode="decimal" placeholder="Preço particular" value={novoServico.price} onChange={(e) => setNovoServico({ ...novoServico, price: e.target.value })} /><label className="agenda-check"><input type="checkbox" checked={novoServico.allow_extra_slot} onChange={(e) => setNovoServico({ ...novoServico, allow_extra_slot: e.target.checked })} /> Permitir encaixe</label><button className="botao botao--secundario" onClick={() => adicionarServico().catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível adicionar o serviço."))}>Adicionar serviço</button></div></section>
        <section className="agenda-config-section"><div className="agenda-config-section__title"><div><h3>Deslocamento inteligente</h3><p>A posição atual não é armazenada; a permissão permanece sob controle do aparelho.</p></div><button className={`agenda-switch${mobilidade?.enabled ? " ativo" : ""}`} role="switch" aria-checked={mobilidade?.enabled || false} onClick={() => alternarMobilidade().catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível alterar a mobilidade."))}><span /></button></div><div className="agenda-config-note"><Icone nome="rota" /><span><strong>{mobilidade?.enabled ? "Atualização automática em primeiro plano" : "Recurso desativado"}</strong><small>{capacidades?.traffic_configured ? "Trânsito em tempo real disponível." : "É preciso configurar uma credencial de trânsito no servidor."}</small></span></div></section>
        <section className="agenda-config-section"><div className="agenda-config-section__title"><div><h3>Sistemas conectados</h3><p>Capacidades são liberadas somente após documentação e homologação.</p></div></div>{capacidades?.connectors.map((item) => <div className="agenda-config-item" key={item.provider}><i className={item.status === "adapter_available" ? "conectavel" : "em-breve"} /><span><strong>{item.name}</strong><small>{item.status === "adapter_available" ? "Adaptador oficial disponível" : item.status === "homologation_required" ? "Aguardando homologação oficial" : "Em breve"}</small></span><span className="agenda-pill">{item.capabilities.create_appointment ? "Bidirecional" : item.capabilities.read_appointments ? "Leitura" : "Protegido"}</span></div>)}</section>
        <footer><button className="botao" onClick={() => setConfigAberta(false)}>Concluir configuração</button></footer>
      </div></div>}
    </div>
  );
}
