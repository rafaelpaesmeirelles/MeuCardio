import { useEffect, useMemo, useRef, useState } from "react";
import type { CSSProperties } from "react";
import { Link } from "react-router-dom";
import Icone from "../components/Icone";
import LogoProvedor from "../components/LogoProvedor";
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
  id: number | string;
  calendar_kind?: "appointment" | "commitment";
  series_id?: number;
  occurrence_date?: string;
  title?: string;
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
  integration_id?: number | null;
  sync_status: string;
  conflict_reason: string | null;
  version: number;
  recurrence?: "none" | "daily" | "weekly" | "monthly";
  blocks_scheduling?: boolean;
  is_exception?: boolean;
  color?: string;
};

type SerieCompromisso = {
  id: number; title: string; category: string; location_id: number | null;
  location: LocalAgenda | null; timezone: string; starts_on: string; start_time: string;
  duration_minutes: number; recurrence: "none" | "daily" | "weekly" | "monthly";
  recurrence_interval: number; weekdays: number[]; month_day: number | null;
  ends_on: string | null; blocks_scheduling: boolean; color: string; active: boolean;
};

type Integracao = {
  id: number;
  provider: string;
  display_name: string;
  status: string;
  sync_strategy: string;
  enabled: boolean;
  write_enabled: boolean;
  contacts_enabled: boolean;
  sync_calendar?: boolean;
  sync_mail?: boolean;
  contact_count: number;
  has_credentials: boolean;
  last_success_at: string | null;
  last_error_message: string | null;
  capabilities?: Record<string, boolean>;
};

type Capacidades = {
  integrations_enabled: boolean;
  external_writes_enabled: boolean;
  traffic_configured: boolean;
  traffic_provider: string;
  google_oauth_modo_teste: boolean;
  connectors: Array<{
    provider: string;
    name: string;
    status: string;
    oauth_configured?: boolean;
    capabilities: Record<string, boolean>;
  }>;
};

type StatusTesteGoogle = {
  status: "pendente" | "liberado" | null;
  google_email?: string;
  created_at?: string;
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

const PROVEDOR_POR_TIPO_INTEGRACAO: Record<string, "google" | "microsoft" | "apple" | "yahoo"> = {
  google_calendar: "google", microsoft_365: "microsoft", apple_icloud: "apple", yahoo_mail: "yahoo",
};

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
  corvia_manual: "Compromisso manual",
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

function dataApi(date: Date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function recorrenciaLabel(item: SerieCompromisso) {
  if (item.recurrence === "none") return "Evento único";
  const intervalo = item.recurrence_interval > 1 ? ` a cada ${item.recurrence_interval}` : "";
  if (item.recurrence === "daily") return `Diário${intervalo}${item.recurrence_interval > 1 ? " dias" : ""}`;
  if (item.recurrence === "weekly") {
    const dias = item.weekdays.map((day) => DIAS_SEMANA[day]).join(", ");
    return `Semanal${intervalo}${item.recurrence_interval > 1 ? " semanas" : ""} · ${dias}`;
  }
  return `Mensal${intervalo}${item.recurrence_interval > 1 ? " meses" : ""} · dia ${item.month_day}`;
}

function formatarDinheiro(value: number | null) {
  return value == null ? "Não definido" : (value / 100).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function endereco(local: LocalAgenda) {
  return [local.address?.street, local.address?.number, local.address?.city, local.address?.state].filter(Boolean).join(" · ") || "Endereço não informado";
}

function Evento({ item, aoCancelar, aoAjustar }: {
  item: Agendamento; aoCancelar: (item: Agendamento) => void;
  aoAjustar: (item: Agendamento) => void;
}) {
  const compromisso = item.calendar_kind === "commitment";
  return (
    <article className={`agenda-evento agenda-evento--${item.status}${compromisso ? " agenda-evento--compromisso" : ""}`} style={{ "--evento-cor": item.color || item.service?.color || item.location?.color || "#087E8B" } as CSSProperties}>
      <div className="agenda-evento__hora"><strong>{horario(item.starts_at)}</strong><span>{item.duration_minutes} min</span></div>
      <div className="agenda-evento__corpo">
        <div className="agenda-evento__linha">
          <h3>{compromisso ? item.title : item.patient_name || "Paciente não informado"}</h3>
          <span className="agenda-pill">{STATUS[item.status] || item.status}</span>
        </div>
        <p>{compromisso ? `${item.appointment_type} · ${item.location?.name || "Sem local"}` : `${item.service?.name || item.appointment_type} · ${item.visit_mode === "teleconsulta" ? "Teleconsulta" : item.location?.name || "Local a definir"}`}</p>
        <div className="agenda-evento__meta">
          <span><Icone nome="sincronizar" /> {ORIGEM[item.source] || item.source}</span>
          {item.conflict_reason && <span className="agenda-evento__conflito">Encaixe</span>}
          {item.sync_status === "pending_external" && <span>Sincronizando…</span>}
          {compromisso && item.recurrence !== "none" && <span>Recorrente{item.is_exception ? " · ajustado" : ""}</span>}
        </div>
      </div>
      {!['cancelado', 'realizado'].includes(item.status) && (
        <button className="agenda-evento__mais" onClick={() => compromisso ? aoAjustar(item) : aoCancelar(item)} aria-label={compromisso ? `Alterar ${item.title}` : `Cancelar agendamento de ${item.patient_name || "paciente"}`}><Icone nome="mais" /></button>
      )}
    </article>
  );
}

export default function Agenda() {
  const [visao, setVisao] = useState<Visao>("semana");
  const [referencia, setReferencia] = useState(new Date());
  const [agendamentos, setAgendamentos] = useState<Agendamento[] | null>(null);
  const [compromissos, setCompromissos] = useState<Agendamento[]>([]);
  const [series, setSeries] = useState<SerieCompromisso[]>([]);
  const [locais, setLocais] = useState<LocalAgenda[]>([]);
  const [servicos, setServicos] = useState<Servico[]>([]);
  const [integracoes, setIntegracoes] = useState<Integracao[]>([]);
  const [rotinas, setRotinas] = useState<RotinaTrabalho[]>([]);
  const [capacidades, setCapacidades] = useState<Capacidades | null>(null);
  const [mobilidade, setMobilidade] = useState<PreferenciaMobilidade | null>(null);
  const [busca, setBusca] = useState("");
  const [filtroLocal, setFiltroLocal] = useState("");
  // Trabalho 16 (07/08/2026): `null` = mostrar todas as origens juntas
  // (padrão); um Set = mostrar só as origens marcadas — combinando
  // Corvia, compromissos pessoais e qualquer conta externa conectada
  // (uma, várias ou todas de uma vez), inclusive mais de uma conta da
  // mesma empresa. Chave: "corvia" | "corvia_manual" | id da integração.
  const [contasVisiveis, setContasVisiveis] = useState<Set<string> | null>(null);
  const [seletorContasAberto, setSeletorContasAberto] = useState(false);
  const [novoAberto, setNovoAberto] = useState(false);
  const [compromissoAberto, setCompromissoAberto] = useState(false);
  const [ajustando, setAjustando] = useState<Agendamento | null>(null);
  const [configAberta, setConfigAberta] = useState(false);
  const [focarContasExternas, setFocarContasExternas] = useState(false);
  const [cancelando, setCancelando] = useState<Agendamento | null>(null);
  const [motivoCancelamento, setMotivoCancelamento] = useState("");
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");
  const [mensagem, setMensagem] = useState("");
  const [contaEmConexao, setContaEmConexao] = useState<"google" | "microsoft" | null>(null);
  const [integracaoSincronizando, setIntegracaoSincronizando] = useState<number | null>(null);
  const [statusTesteGoogle, setStatusTesteGoogle] = useState<StatusTesteGoogle | null>(null);
  const [testeGoogleAberto, setTesteGoogleAberto] = useState(false);
  const [emailTesteGoogle, setEmailTesteGoogle] = useState("");
  const [enviandoTesteGoogle, setEnviandoTesteGoogle] = useState(false);
  const [novo, setNovo] = useState({
    patient_name: "", patient_phone: "", patient_email: "", email_consent: false,
    starts_at: localDateTime(), service_id: "", location_id: "", duration_minutes: 30,
    visit_mode: "presencial", payment_mode: "particular", insurance_name: "", notes: "",
  });
  const [novoCompromisso, setNovoCompromisso] = useState({
    title: "", category: "compromisso", starts_at: localDateTime(), duration_minutes: 60,
    location_id: "", recurrence: "none", recurrence_interval: 1, weekdays: [] as number[],
    ends_on: "", blocks_scheduling: true, description: "", color: "#6B4EFF",
  });
  const [ajusteCompromisso, setAjusteCompromisso] = useState({
    starts_at: "", ends_at: "", title: "", location_id: "", notes: "",
  });
  const [novaIntegracao, setNovaIntegracao] = useState({ provider: "feegow", display_name: "" });
  const [apple, setApple] = useState({ apple_id: "", app_specific_password: "", consent_accepted: false, mail: false, mail_consent_accepted: false });
  const [yahoo, setYahoo] = useState({ endereco: "", senha_de_app: "", consent_accepted: false });
  const [consentimentoContas, setConsentimentoContas] = useState(false);
  const [novoLocal, setNovoLocal] = useState({ name: "", city: "", state: "", latitude: "", longitude: "" });
  const [novoServico, setNovoServico] = useState({ name: "", code: "", location_id: "", duration_minutes: 30, price: "", allow_extra_slot: false });
  const [novaRotina, setNovaRotina] = useState({
    label: "Rotina de atendimento", location_id: "", service_id: "", weekdays: [0, 1, 2, 3, 4],
    start_time: "08:00", end_time: "18:00", routine_type: "atendimento", visit_mode: "presencial",
    arrival_buffer_minutes: 15, planning_notes: "",
  });
  const novoModalRef = useRef<HTMLDivElement>(null);
  const compromissoModalRef = useRef<HTMLDivElement>(null);
  const ajusteModalRef = useRef<HTMLDivElement>(null);
  const configModalRef = useRef<HTMLDivElement>(null);
  const contasExternasRef = useRef<HTMLElement>(null);
  const cancelarModalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const panel = ajustando ? ajusteModalRef.current : cancelando ? cancelarModalRef.current : configAberta ? configModalRef.current : compromissoAberto ? compromissoModalRef.current : novoAberto ? novoModalRef.current : null;
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
        if (ajustando) setAjustando(null);
        else if (cancelando) { setCancelando(null); setMotivoCancelamento(""); }
        else if (configAberta) setConfigAberta(false);
        else if (compromissoAberto) setCompromissoAberto(false);
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
  }, [novoAberto, compromissoAberto, configAberta, cancelando, ajustando]);

  useEffect(() => {
    if (!configAberta || !focarContasExternas) return;
    const timer = window.setTimeout(() => {
      contasExternasRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      contasExternasRef.current?.focus({ preventScroll: true });
      setFocarContasExternas(false);
    }, 100);
    return () => window.clearTimeout(timer);
  }, [configAberta, focarContasExternas]);

  async function carregar() {
    const [appointments, locations, services, integrations, capabilities, mobility, routines, commitmentSeries, testeGoogle] = await Promise.all([
      api.get<Agendamento[]>("/agenda/appointments"),
      api.get<LocalAgenda[]>("/agenda/locations"),
      api.get<Servico[]>("/agenda/services"),
      api.get<Integracao[]>("/agenda/integrations"),
      api.get<Capacidades>("/agenda/capabilities"),
      api.get<PreferenciaMobilidade>("/agenda/mobility/preferences"),
      api.get<RotinaTrabalho[]>("/agenda/work-routines"),
      api.get<SerieCompromisso[]>("/agenda/commitment-series"),
      api.get<StatusTesteGoogle>("/agenda/google-teste/status"),
    ]);
    setAgendamentos(appointments); setLocais(locations); setServicos(services);
    setIntegracoes(integrations); setCapacidades(capabilities); setMobilidade(mobility); setRotinas(routines); setSeries(commitmentSeries);
    setStatusTesteGoogle(testeGoogle);
  }

  async function solicitarTesteGoogle() {
    setEnviandoTesteGoogle(true);
    try {
      await api.post("/agenda/google-teste/solicitar", { google_email: emailTesteGoogle.trim().toLowerCase() });
      setStatusTesteGoogle({ status: "pendente", google_email: emailTesteGoogle.trim().toLowerCase() });
      setTesteGoogleAberto(false);
      setMensagem("Pedido enviado — avisaremos por e-mail assim que sua conexão com o Google estiver liberada.");
    } finally {
      setEnviandoTesteGoogle(false);
    }
  }

  function conectarOuSolicitarGoogle() {
    if (capacidades?.google_oauth_modo_teste && statusTesteGoogle?.status !== "liberado") {
      setEmailTesteGoogle(statusTesteGoogle?.google_email || "");
      setTesteGoogleAberto(true);
      return Promise.resolve();
    }
    return conectarConta("google");
  }

  async function carregarCompromissos(reference = referencia) {
    const start = somaDias(reference, -90);
    const end = somaDias(reference, 300);
    setCompromissos(await api.get<Agendamento[]>(`/agenda/commitments?start=${dataApi(start)}&end=${dataApi(end)}`));
  }

  async function atualizarAgenda() {
    await Promise.all([carregar(), carregarCompromissos()]);
  }

  useEffect(() => { carregar().catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível abrir a agenda.")); }, []);
  useEffect(() => { carregarCompromissos(referencia).catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível carregar os compromissos pessoais.")); }, [referencia]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const conectada = params.get("conta_conectada");
    const falha = params.get("conta_erro");
    const sincronizacao = params.get("sincronizacao");
    if (conectada) {
      const nome = conectada === "google_calendar" ? "Google" : conectada === "microsoft_365" ? "Microsoft" : "externa";
      setMensagem(sincronizacao === "pendente"
        ? `Conta ${nome} conectada. A primeira sincronização ficou pendente; use “Sincronizar” para tentar novamente.`
        : `Conta ${nome} conectada. Calendário e contatos foram atualizados.`);
    } else if (falha) {
      const mensagens: Record<string, string> = {
        autorizacao_cancelada: "A autorização foi cancelada antes de concluir a conexão.",
        invalid_oauth_state: "A autorização expirou ou já foi utilizada. Inicie a conexão novamente.",
        oauth_exchange_error: "O provedor recusou a autorização. Confira o aplicativo OAuth e tente novamente.",
        oauth_refresh_token_missing: "O provedor não concedeu acesso contínuo. Remova a autorização anterior e conecte novamente.",
      };
      setErro(mensagens[falha] || "Não foi possível concluir a conexão com a conta externa.");
    }
    if (conectada || falha) window.history.replaceState({}, "", window.location.pathname);
  }, []);

  // Chave de origem de um item: compromisso pessoal (corvia_manual),
  // atendimento nativo (corvia), ou a conta externa que sincronizou (o
  // integration_id como string) — é o que o seletor de contas usa para
  // decidir o que mostrar.
  function chaveOrigem(item: Agendamento): string {
    if (item.calendar_kind === "commitment") return "corvia_manual";
    if (item.integration_id) return String(item.integration_id);
    return item.source || "corvia";
  }

  const filtrados = useMemo(() => [...(agendamentos ?? []), ...compromissos].filter((item) => {
    const query = busca.trim().toLocaleLowerCase("pt-BR");
    if (query && !`${item.title || ""} ${item.patient_name || ""} ${item.service?.name || ""} ${item.location?.name || ""}`.toLocaleLowerCase("pt-BR").includes(query)) return false;
    if (filtroLocal && item.location?.id !== Number(filtroLocal)) return false;
    if (contasVisiveis && !contasVisiveis.has(chaveOrigem(item))) return false;
    return true;
  }), [agendamentos, compromissos, busca, filtroLocal, contasVisiveis]);

  // Trabalho 16: opções do seletor de contas — Corvia + compromissos
  // pessoais sempre presentes, mais uma entrada por conta externa
  // conectada com sincronização de agenda ligada (a mesma preferência
  // gerenciada em /sincronizacao). Duas contas da mesma empresa aparecem
  // como duas entradas distintas, cada uma com o próprio nome.
  const opcoesOrigem = useMemo(() => {
    const base: Array<{ chave: string; rotulo: string; provedor?: "google" | "microsoft" | "apple" }> = [
      { chave: "corvia", rotulo: "Atendimentos Corvia" },
      { chave: "corvia_manual", rotulo: "Compromissos pessoais" },
    ];
    const mapaLogo: Record<string, "google" | "microsoft" | "apple"> = {
      google_calendar: "google", microsoft_365: "microsoft", apple_icloud: "apple",
    };
    const externas = integracoes
      .filter((i) => mapaLogo[i.provider] && i.enabled && i.sync_calendar !== false)
      .map((i) => ({ chave: String(i.id), rotulo: i.display_name, provedor: mapaLogo[i.provider] }));
    return [...base, ...externas];
  }, [integracoes]);

  function alternarConta(chave: string, marcado: boolean) {
    const atual = contasVisiveis ?? new Set(opcoesOrigem.map((o) => o.chave));
    const novo = new Set(atual);
    if (marcado) novo.add(chave); else novo.delete(chave);
    // Todas marcadas de novo volta a ser "sem filtro" — evita um Set idêntico
    // ao universo inteiro se comportando diferente de null por acidente.
    setContasVisiveis(novo.size >= opcoesOrigem.length ? null : novo);
  }

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

  function alternarDiaCompromisso(day: number) {
    setNovoCompromisso((current) => ({
      ...current,
      weekdays: current.weekdays.includes(day)
        ? current.weekdays.filter((item) => item !== day)
        : [...current.weekdays, day].sort(),
    }));
  }

  async function salvarCompromisso() {
    if (!novoCompromisso.title.trim() || !novoCompromisso.starts_at) return;
    setSalvando(true); setErro("");
    try {
      const [startsOn, startTime] = novoCompromisso.starts_at.split("T");
      const selectedLocation = locais.find((item) => item.id === Number(novoCompromisso.location_id));
      await api.post("/agenda/commitment-series", {
        title: novoCompromisso.title.trim(), category: novoCompromisso.category,
        description: novoCompromisso.description || null,
        location_id: novoCompromisso.location_id ? Number(novoCompromisso.location_id) : null,
        timezone: selectedLocation?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || "America/Sao_Paulo",
        starts_on: startsOn, start_time: startTime,
        duration_minutes: novoCompromisso.duration_minutes,
        recurrence: novoCompromisso.recurrence,
        recurrence_interval: novoCompromisso.recurrence_interval,
        weekdays: novoCompromisso.recurrence === "weekly" ? novoCompromisso.weekdays : [],
        month_day: novoCompromisso.recurrence === "monthly" ? Number(startsOn.slice(8, 10)) : null,
        ends_on: novoCompromisso.recurrence !== "none" && novoCompromisso.ends_on ? novoCompromisso.ends_on : null,
        blocks_scheduling: novoCompromisso.blocks_scheduling,
        color: novoCompromisso.color,
      });
      setCompromissoAberto(false);
      setNovoCompromisso({ title: "", category: "compromisso", starts_at: localDateTime(), duration_minutes: 60, location_id: "", recurrence: "none", recurrence_interval: 1, weekdays: [], ends_on: "", blocks_scheduling: true, description: "", color: "#6B4EFF" });
      await atualizarAgenda();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível salvar o compromisso.");
    } finally { setSalvando(false); }
  }

  function abrirAjusteCompromisso(item: Agendamento) {
    setAjusteCompromisso({
      starts_at: localDateTime(new Date(item.starts_at)), ends_at: localDateTime(new Date(item.ends_at)),
      title: item.title || "", location_id: item.location ? String(item.location.id) : "", notes: item.notes || "",
    });
    setAjustando(item);
  }

  async function salvarExcecaoCompromisso(action: "cancel" | "override") {
    if (!ajustando?.series_id || !ajustando.occurrence_date) return;
    setSalvando(true); setErro("");
    try {
      await api.put(`/agenda/commitment-series/${ajustando.series_id}/exceptions`, {
        occurrence_date: ajustando.occurrence_date, action,
        starts_at: action === "override" ? new Date(ajusteCompromisso.starts_at).toISOString() : null,
        ends_at: action === "override" ? new Date(ajusteCompromisso.ends_at).toISOString() : null,
        title: action === "override" ? ajusteCompromisso.title.trim() || null : null,
        location_id: action === "override" && ajusteCompromisso.location_id ? Number(ajusteCompromisso.location_id) : null,
        notes: ajusteCompromisso.notes || null,
      });
      setAjustando(null);
      await carregarCompromissos();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível alterar esta ocorrência.");
    } finally { setSalvando(false); }
  }

  async function removerSerie(id: number) {
    await api.delete(`/agenda/commitment-series/${id}`);
    await atualizarAgenda();
  }

  async function prepararIntegracao() {
    if (!novaIntegracao.display_name.trim()) return;
    await api.post("/agenda/integrations", {
      provider: novaIntegracao.provider, display_name: novaIntegracao.display_name.trim(),
      sync_strategy: "external_authoritative", configuration: {}, credentials: {},
      enabled: false, write_enabled: false, consent_accepted: false,
    });
    setNovaIntegracao((current) => ({ ...current, display_name: "" }));
    await carregar();
  }

  async function conectarConta(provider: "google" | "microsoft") {
    setContaEmConexao(provider); setErro(""); setMensagem("");
    try {
      const result = await api.get<{ authorization_url: string }>(`/agenda/oauth/${provider}/start?contacts=true&mail=true&calendar_write=false&consent_accepted=true`);
      window.location.assign(result.authorization_url);
    } catch (error) {
      setContaEmConexao(null);
      throw error;
    }
  }

  async function conectarApple() {
    await api.post("/agenda/integrations/apple", { ...apple, contacts: true });
    setApple({ apple_id: "", app_specific_password: "", consent_accepted: false, mail: false, mail_consent_accepted: false });
    await carregar();
  }

  async function conectarYahoo() {
    // Diferente de Apple/Google/Microsoft, é rota do CorvIA Mail
    // (/api/email/...), não da Agenda — a Yahoo não sincroniza calendário
    // nem contatos, só e-mail (ver docs/adr-... e o serviço yahoo_mail.py).
    await api.post("/email/conectar-yahoo", { ...yahoo, senha_de_app: yahoo.senha_de_app });
    setYahoo({ endereco: "", senha_de_app: "", consent_accepted: false });
    await carregar();
  }

  async function sincronizarConta(id: number) {
    setIntegracaoSincronizando(id); setErro(""); setMensagem("");
    try {
      await api.post(`/agenda/integrations/${id}/sync-all?full=false`, {});
      await carregar();
      setMensagem("Calendário e contatos atualizados com sucesso.");
    } finally { setIntegracaoSincronizando(null); }
  }

  async function desconectarConta(id: number) {
    if (!window.confirm("Desconectar esta conta e remover seus contatos sincronizados do Corvia?")) return;
    await api.delete(`/agenda/integrations/${id}`);
    await carregar();
  }

  function abrirContasExternas() {
    setFocarContasExternas(true);
    setConfigAberta(true);
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
  const proximos = filtrados
    .filter((item) => new Date(item.starts_at).getTime() >= Date.now() && item.status !== "cancelado")
    .sort((first, second) => +new Date(first.starts_at) - +new Date(second.starts_at));

  return (
    <div className="agenda-integrada">
      <header className="agenda-cabecalho">
        <div><p className="eyebrow">Operação clínica</p><h1>Agenda Integrada</h1><p>Horários, locais, recursos e sistemas externos em uma única visão.</p></div>
        <div className="agenda-cabecalho__acoes">
          <button className="botao botao--secundario" onClick={() => setConfigAberta(true)}><Icone nome="configuracao" /> Configurar</button>
          <button className="botao botao--secundario" onClick={() => setCompromissoAberto(true)}><Icone nome="agenda" /> Compromisso pessoal</button>
          <button className="botao" onClick={() => setNovoAberto(true)}><Icone nome="agenda" /> Novo atendimento</button>
        </div>
      </header>

      <section className="agenda-status" aria-label="Status da agenda">
        <span className="agenda-status__ok"><i /> Agenda Corvia ativa</span>
        <span><Icone nome="sincronizar" /> {integracoes.filter((item) => item.status === "connected").length} integrações conectadas</span>
        <span>{capacidades?.external_writes_enabled ? "Escrita externa homologada" : "Escrita externa protegida"}</span>
        <button onClick={() => atualizarAgenda().catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível atualizar."))}><Icone nome="sincronizar" /> Atualizar</button>
      </section>

      <section className="agenda-contas-destaque" aria-labelledby="agenda-contas-titulo">
        <div className="agenda-contas-destaque__topo">
          <div>
            <p className="eyebrow">Sincronização externa</p>
            <h2 id="agenda-contas-titulo">Conecte seus Calendários, Contatos e Contas de E-mail</h2>
            <p>Google, Microsoft, Apple e Yahoo — quantas contas quiser, de uma ou várias empresas ao mesmo tempo.</p>
          </div>
          <Link to="/sincronizacao" className="botao botao--secundario"><Icone nome="configuracao" /> Gerenciar conexões</Link>
        </div>
        {/* 07/08/2026: esta seção mostrava só Google/Microsoft/Apple, com Google e
         * Microsoft em cartões grandes e Apple relegado a uma linha secundária —
         * Rafael reportou como "sem sentido" e "Yahoo faltando". A tela dedicada
         * /sincronizacao (Trabalho 16) já trata os 4 provedores em pé de
         * igualdade, com conectar/sincronizar/preferências por conta — em vez de
         * manter duas telas de conta divergindo com o tempo (o defeito que este
         * projeto já gastou semanas removendo antes), esta seção virou um resumo
         * que aponta para lá. */}
        <div className="agenda-contas-destaque__grade">
          {(["google_calendar", "microsoft_365", "apple_icloud", "yahoo_mail"] as const).map((provider) => {
            const nome = { google_calendar: "Google", microsoft_365: "Microsoft", apple_icloud: "Apple iCloud", yahoo_mail: "Yahoo Mail" }[provider];
            const acao = { google_calendar: "google", microsoft_365: "microsoft", apple_icloud: "apple", yahoo_mail: "yahoo" }[provider] as "google" | "microsoft" | "apple" | "yahoo";
            const conectadas = integracoes.filter((item) => item.provider === provider && item.enabled);
            return (
              <Link to="/sincronizacao" key={provider} className="agenda-conta-provider agenda-conta-provider--link">
                <LogoProvedor provedor={acao} />
                <div>
                  <strong>{nome}</strong>
                  <small>{conectadas.length > 0 ? `${conectadas.length} conta${conectadas.length > 1 ? "s" : ""} conectada${conectadas.length > 1 ? "s" : ""}` : "Não conectado"}</small>
                </div>
              </Link>
            );
          })}
        </div>
      </section>

      {mensagem && <div className="agenda-alerta agenda-alerta--sucesso" role="status"><strong>Sincronização</strong><span>{mensagem}</span><button onClick={() => setMensagem("")} aria-label="Fechar"><Icone nome="fechar" /></button></div>}
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
        <label className="agenda-busca"><Icone nome="busca" /><span className="sr-only">Buscar</span><input value={busca} onChange={(e) => setBusca(e.target.value)} placeholder="Paciente, compromisso, serviço ou local" /></label>
        <label><Icone nome="pin" /><span className="sr-only">Filtrar local</span><select value={filtroLocal} onChange={(e) => setFiltroLocal(e.target.value)}><option value="">Todos os locais</option>{locais.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
        <div className="agenda-filtro-contas" style={{ position: "relative" }}>
          <button type="button" className="botao botao--secundario" onClick={() => setSeletorContasAberto((v) => !v)}
                  aria-expanded={seletorContasAberto} aria-haspopup="true">
            <Icone nome="sincronizar" />{" "}
            {contasVisiveis === null ? "Todas as contas" : `${contasVisiveis.size} conta${contasVisiveis.size === 1 ? "" : "s"}`}
          </button>
          {seletorContasAberto && (
            <div role="menu" style={{
              position: "absolute", top: "calc(100% + 4px)", left: 0, zIndex: 30,
              background: "var(--superficie)", border: "1px solid var(--borda)", borderRadius: "var(--r)",
              padding: "0.5rem 0.7rem", minWidth: 240, boxShadow: "var(--sombra)",
            }}>
              <label style={{ display: "flex", gap: 6, alignItems: "center", fontSize: "0.84rem", padding: "0.2rem 0", fontWeight: 600 }}>
                <input type="checkbox" checked={contasVisiveis === null} onChange={() => setContasVisiveis(null)} />
                Todas juntas
              </label>
              <hr style={{ margin: "0.3rem 0", border: "none", borderTop: "1px solid var(--borda)" }} />
              {opcoesOrigem.map((opcao) => (
                <label key={opcao.chave} style={{ display: "flex", gap: 6, alignItems: "center", fontSize: "0.84rem", padding: "0.2rem 0" }}>
                  <input type="checkbox"
                         checked={contasVisiveis === null || contasVisiveis.has(opcao.chave)}
                         onChange={(e) => alternarConta(opcao.chave, e.target.checked)} />
                  {opcao.provedor && <LogoProvedor provedor={opcao.provedor} />}
                  {opcao.rotulo}
                </label>
              ))}
              <button type="button" className="botao botao--secundario" style={{ marginTop: "0.4rem", padding: "0.2rem 0.6rem", fontSize: "0.78rem" }}
                      onClick={() => setSeletorContasAberto(false)}>
                Fechar
              </button>
            </div>
          )}
        </div>
      </section>

      <div className="agenda-layout">
        <main className="agenda-calendario">
          {agendamentos === null ? <p className="agenda-carregando">Organizando sua agenda…</p> : visao === "lista" ? (
            <div className="agenda-lista">
              {proximos.length === 0 ? <p className="agenda-vazio">Nenhum compromisso encontrado.</p> : proximos.slice(0, 100).map((item) => <div key={item.id} className="agenda-lista__linha"><time>{new Date(item.starts_at).toLocaleDateString("pt-BR", { day: "2-digit", month: "short" })}</time><Evento item={item} aoCancelar={setCancelando} aoAjustar={abrirAjusteCompromisso} /></div>)}
            </div>
          ) : (
            <div className={`agenda-grade agenda-grade--${visao}`}>
              {diasVisiveis.map((dia) => {
                const items = filtrados.filter((item) => mesmoDia(item.starts_at, dia)).sort((a, b) => +new Date(a.starts_at) - +new Date(b.starts_at));
                const outside = visao === "mes" && dia.getMonth() !== referencia.getMonth();
                return <section key={dia.toISOString()} className={`agenda-dia${mesmoDia(dia, hoje) ? " agenda-dia--hoje" : ""}${outside ? " agenda-dia--fora" : ""}`}>
                  <header><span>{dataCurta(dia)}</span>{mesmoDia(dia, hoje) && <i>Hoje</i>}</header>
                  <div>{items.length ? items.map((item) => <Evento key={item.id} item={item} aoCancelar={setCancelando} aoAjustar={abrirAjusteCompromisso} />) : <button className="agenda-dia__livre" onClick={() => { const slot = new Date(dia); slot.setHours(9, 0, 0, 0); setNovo((current) => ({ ...current, starts_at: localDateTime(slot) })); setNovoAberto(true); }}>Horário livre <span>+</span></button>}</div>
                </section>;
              })}
            </div>
          )}
        </main>

        <aside className="agenda-insights" aria-label="Inteligência da agenda">
          <article><p className="eyebrow">Próximo compromisso</p>{proximos[0] ? <><strong>{horario(proximos[0].starts_at)} · {proximos[0].title || proximos[0].patient_name || "Compromisso"}</strong><span>{proximos[0].location?.name || "Local a definir"}</span></> : <span>Agenda livre.</span>}</article>
          <article><p className="eyebrow">Operação</p><div className="agenda-insights__metricas"><span><strong>{proximos.length}</strong> próximos</span><span><strong>{conflitos}</strong> encaixes</span><span><strong>{locais.length}</strong> locais</span></div></article>
          <article className="agenda-insights__mobilidade"><p className="eyebrow">Deslocamento inteligente</p><strong>{mobilidade?.enabled ? "Atualização automática ativa" : "Ative o trânsito no painel"}</strong><span>{capacidades?.traffic_configured ? `Trânsito por ${capacidades.traffic_provider}` : "Aguardando credencial do provedor de trânsito"}</span><button onClick={() => setConfigAberta(true)}>Configurar mobilidade <Icone nome="seta" /></button></article>
          <article><p className="eyebrow">Sincronização</p>{integracoes.length ? integracoes.map((item) => <div className="agenda-integracao-mini" key={item.id}><i className={`status-${item.status}`} /><span><strong>{item.display_name}</strong><small>{item.last_success_at ? `Atualizada ${new Date(item.last_success_at).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}` : item.status}</small></span></div>) : <span>Nenhum sistema externo conectado.</span>}</article>
        </aside>
      </div>

      {compromissoAberto && <div className="agenda-modal" role="dialog" aria-modal="true" aria-labelledby="novo-compromisso-titulo"><div className="agenda-modal__painel" ref={compromissoModalRef} tabIndex={-1}>
        <header><div><p className="eyebrow">Agenda pessoal e profissional</p><h2 id="novo-compromisso-titulo">Novo compromisso</h2></div><button onClick={() => setCompromissoAberto(false)} aria-label="Fechar"><Icone nome="fechar" /></button></header>
        <div className="agenda-form-grid">
          <label className="span-2">Título<input autoFocus value={novoCompromisso.title} onChange={(e) => setNovoCompromisso({ ...novoCompromisso, title: e.target.value })} placeholder="Ex.: reunião clínica, plantão ou atividade administrativa" /></label>
          <label>Tipo<select value={novoCompromisso.category} onChange={(e) => setNovoCompromisso({ ...novoCompromisso, category: e.target.value })}><option value="compromisso">Compromisso</option><option value="trabalho">Trabalho</option><option value="reuniao">Reunião</option><option value="plantao">Plantão</option><option value="estudo">Estudo</option><option value="pessoal">Pessoal</option><option value="outro">Outro</option></select></label>
          <label>Local<select value={novoCompromisso.location_id} onChange={(e) => setNovoCompromisso({ ...novoCompromisso, location_id: e.target.value })}><option value="">Sem local definido</option>{locais.filter((item) => item.active).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
          <label>Primeira ocorrência<input type="datetime-local" value={novoCompromisso.starts_at} onChange={(e) => setNovoCompromisso({ ...novoCompromisso, starts_at: e.target.value })} /></label>
          <label>Duração (min)<input type="number" min={5} max={1440} value={novoCompromisso.duration_minutes} onChange={(e) => setNovoCompromisso({ ...novoCompromisso, duration_minutes: Number(e.target.value) })} /></label>
          <label>Repetição<select value={novoCompromisso.recurrence} onChange={(e) => setNovoCompromisso({ ...novoCompromisso, recurrence: e.target.value })}><option value="none">Não repetir</option><option value="daily">Diariamente</option><option value="weekly">Semanalmente</option><option value="monthly">Mensalmente</option></select></label>
          {novoCompromisso.recurrence !== "none" && <label>Intervalo<input type="number" min={1} max={52} value={novoCompromisso.recurrence_interval} onChange={(e) => setNovoCompromisso({ ...novoCompromisso, recurrence_interval: Number(e.target.value) })} /><small>A cada {novoCompromisso.recurrence_interval} {novoCompromisso.recurrence === "daily" ? "dia(s)" : novoCompromisso.recurrence === "weekly" ? "semana(s)" : "mês(es)"}</small></label>}
          {novoCompromisso.recurrence === "weekly" && <fieldset className="agenda-rotina__dias span-2"><legend>Dias da semana</legend><div>{DIAS_SEMANA.map((day, index) => <button key={day} type="button" className={novoCompromisso.weekdays.includes(index) ? "ativo" : ""} aria-pressed={novoCompromisso.weekdays.includes(index)} onClick={() => alternarDiaCompromisso(index)}>{day}</button>)}</div></fieldset>}
          {novoCompromisso.recurrence !== "none" && <label>Repetir até<input type="date" min={novoCompromisso.starts_at.slice(0, 10)} value={novoCompromisso.ends_on} onChange={(e) => setNovoCompromisso({ ...novoCompromisso, ends_on: e.target.value })} /><small>Deixe vazio para manter a rotina ativa.</small></label>}
          <label>Cor<input type="color" value={novoCompromisso.color} onChange={(e) => setNovoCompromisso({ ...novoCompromisso, color: e.target.value })} /></label>
          <label className="agenda-check span-2"><input type="checkbox" checked={novoCompromisso.blocks_scheduling} onChange={(e) => setNovoCompromisso({ ...novoCompromisso, blocks_scheduling: e.target.checked })} /> Bloquear este período para novos atendimentos e evitar conflitos.</label>
          <label className="span-2">Observações<textarea rows={3} value={novoCompromisso.description} onChange={(e) => setNovoCompromisso({ ...novoCompromisso, description: e.target.value })} placeholder="Informações úteis para sua rotina" /></label>
          <p className="agenda-config-help span-2">Uma rotina contínua será exibida na agenda sem criar eventos infinitos. Depois, cada data poderá ser alterada ou cancelada isoladamente.</p>
        </div>
        <footer><button className="botao botao--secundario" onClick={() => setCompromissoAberto(false)}>Cancelar</button><button className="botao" disabled={salvando || !novoCompromisso.title.trim()} onClick={salvarCompromisso}>{salvando ? "Salvando…" : "Criar compromisso"}</button></footer>
      </div></div>}

      {ajustando && <div className="agenda-modal" role="dialog" aria-modal="true" aria-labelledby="ajustar-compromisso-titulo"><div className="agenda-modal__painel agenda-modal__painel--compacto" ref={ajusteModalRef} tabIndex={-1}>
        <header><div><p className="eyebrow">Alteração pontual</p><h2 id="ajustar-compromisso-titulo">Ajustar somente esta ocorrência</h2></div><button onClick={() => setAjustando(null)} aria-label="Fechar"><Icone nome="fechar" /></button></header>
        <div className="agenda-form-grid">
          <p className="span-2 agenda-modal__destaque">As demais ocorrências da rotina continuarão inalteradas.</p>
          <label className="span-2">Título<input autoFocus value={ajusteCompromisso.title} onChange={(e) => setAjusteCompromisso({ ...ajusteCompromisso, title: e.target.value })} /></label>
          <label>Início<input type="datetime-local" value={ajusteCompromisso.starts_at} onChange={(e) => setAjusteCompromisso({ ...ajusteCompromisso, starts_at: e.target.value })} /></label>
          <label>Fim<input type="datetime-local" value={ajusteCompromisso.ends_at} onChange={(e) => setAjusteCompromisso({ ...ajusteCompromisso, ends_at: e.target.value })} /></label>
          <label className="span-2">Local<select value={ajusteCompromisso.location_id} onChange={(e) => setAjusteCompromisso({ ...ajusteCompromisso, location_id: e.target.value })}><option value="">Sem local definido</option>{locais.filter((item) => item.active).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
          <label className="span-2">Observações<textarea rows={3} value={ajusteCompromisso.notes} onChange={(e) => setAjusteCompromisso({ ...ajusteCompromisso, notes: e.target.value })} /></label>
        </div>
        <footer className="agenda-modal__acoes-distribuidas"><button className="botao agenda-botao--perigo" disabled={salvando} onClick={() => salvarExcecaoCompromisso("cancel")}>Cancelar esta data</button><div><button className="botao botao--secundario" onClick={() => setAjustando(null)}>Voltar</button><button className="botao" disabled={salvando || !ajusteCompromisso.starts_at || !ajusteCompromisso.ends_at || new Date(ajusteCompromisso.ends_at) <= new Date(ajusteCompromisso.starts_at)} onClick={() => salvarExcecaoCompromisso("override")}>{salvando ? "Salvando…" : "Salvar alteração"}</button></div></footer>
      </div></div>}

      {novoAberto && <div className="agenda-modal" role="dialog" aria-modal="true" aria-labelledby="novo-agendamento-titulo"><div className="agenda-modal__painel" ref={novoModalRef} tabIndex={-1}>
        <header><div><p className="eyebrow">Novo atendimento</p><h2 id="novo-agendamento-titulo">Agendar paciente</h2></div><button onClick={() => setNovoAberto(false)} aria-label="Fechar"><Icone nome="fechar" /></button></header>
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

      {testeGoogleAberto && <div className="agenda-modal" role="dialog" aria-modal="true" aria-labelledby="teste-google-titulo"><div className="agenda-modal__painel agenda-modal__painel--compacto">
        <header><div><p className="eyebrow">Conexão com o Google</p><h2 id="teste-google-titulo">Integração em fase de testes</h2></div><button onClick={() => setTesteGoogleAberto(false)} aria-label="Fechar"><Icone nome="fechar" /></button></header>
        <div className="agenda-form-grid">
          <p className="span-2">Essa integração está momentaneamente limitada a Calendário/Agenda enquanto concluímos a homologação com o Google. Digite o e-mail da sua conta Google e avisaremos assim que o e-mail também estiver sincronizado — geralmente em poucas horas.</p>
          <label className="span-2">E-mail do Google<input type="email" autoFocus value={emailTesteGoogle} onChange={(e) => setEmailTesteGoogle(e.target.value)} placeholder="voce@gmail.com" /></label>
        </div>
        <footer><button className="botao botao--secundario" onClick={() => setTesteGoogleAberto(false)}>Cancelar</button><button className="botao" disabled={enviandoTesteGoogle || !emailTesteGoogle.includes("@")} onClick={() => solicitarTesteGoogle().catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível enviar o pedido."))}>{enviandoTesteGoogle ? "Enviando…" : "Enviar pedido"}</button></footer>
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
        <section className="agenda-config-section">
          <div className="agenda-config-section__title"><div><h3>Compromissos recorrentes</h3><p>Rotinas visíveis no calendário, com exceções pontuais por data.</p></div><span>{series.filter((item) => item.active).length}</span></div>
          <div className="agenda-series-lista">
            {series.filter((item) => item.active).length ? series.filter((item) => item.active).map((item) => <div className="agenda-config-item" key={item.id}>
              <i style={{ background: item.color }} />
              <span><strong>{item.title}</strong><small>{recorrenciaLabel(item)} · {item.start_time.slice(0, 5)} · {item.duration_minutes} min{item.location ? ` · ${item.location.name}` : ""}{item.blocks_scheduling ? " · bloqueia horários" : ""}</small></span>
              <button className="agenda-icon-button" onClick={() => removerSerie(item.id).catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível encerrar a rotina."))} aria-label={`Encerrar rotina ${item.title}`} title="Encerrar toda a série"><Icone nome="fechar" /></button>
            </div>) : <p className="agenda-config-vazio">Nenhum compromisso recorrente ativo. Use “Compromisso pessoal” no topo da agenda.</p>}
          </div>
        </section>
        <section className="agenda-config-section"><div className="agenda-config-section__title"><div><h3>Catálogo de serviços</h3><p>Duração, preço, modalidade e política de encaixe.</p></div><span>{servicos.length}</span></div>{servicos.map((item) => <div className="agenda-config-item" key={item.id}><i style={{ background: item.color }} /><span><strong>{item.name} · {item.duration_minutes} min</strong><small>{item.visit_mode} · {formatarDinheiro(item.private_price_cents)}{item.allow_extra_slot ? " · aceita encaixe" : ""}</small></span></div>)}<div className="agenda-config-form agenda-config-form--service"><input placeholder="Nome do serviço" value={novoServico.name} onChange={(e) => setNovoServico({ ...novoServico, name: e.target.value, code: e.target.value })} /><select value={novoServico.location_id} onChange={(e) => setNovoServico({ ...novoServico, location_id: e.target.value })}><option value="">Todos os locais</option>{locais.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select><input type="number" min={5} value={novoServico.duration_minutes} onChange={(e) => setNovoServico({ ...novoServico, duration_minutes: Number(e.target.value) })} /><input inputMode="decimal" placeholder="Preço particular" value={novoServico.price} onChange={(e) => setNovoServico({ ...novoServico, price: e.target.value })} /><label className="agenda-check"><input type="checkbox" checked={novoServico.allow_extra_slot} onChange={(e) => setNovoServico({ ...novoServico, allow_extra_slot: e.target.checked })} /> Permitir encaixe</label><button className="botao botao--secundario" onClick={() => adicionarServico().catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível adicionar o serviço."))}>Adicionar serviço</button></div></section>
        <section className="agenda-config-section"><div className="agenda-config-section__title"><div><h3>Deslocamento inteligente</h3><p>A posição atual não é armazenada; a permissão permanece sob controle do aparelho.</p></div><button className={`agenda-switch${mobilidade?.enabled ? " ativo" : ""}`} role="switch" aria-checked={mobilidade?.enabled || false} onClick={() => alternarMobilidade().catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível alterar a mobilidade."))}><span /></button></div><div className="agenda-config-note"><Icone nome="rota" /><span><strong>{mobilidade?.enabled ? "Atualização automática em primeiro plano" : "Recurso desativado"}</strong><small>{capacidades?.traffic_configured ? "Trânsito em tempo real disponível." : "É preciso configurar uma credencial de trânsito no servidor."}</small></span></div></section>
        <section className="agenda-config-section" ref={contasExternasRef} tabIndex={-1} style={{ scrollMarginTop: "1rem" }}>
          {/* 07/08/2026: este painel duplicava, com texto e comportamento
           * divergentes, a tela dedicada /sincronizacao (Trabalho 16) — Rafael
           * reportou os dois efeitos colaterais dessa duplicação (Google/
           * Microsoft em destaque com Apple/Yahoo relegados, "sincronizar" sem
           * efeito visível numa conta desconectada). Substituído por um
           * ponteiro, mesmo padrão já usado no resumo da Minha Conta — uma
           * fonte só de verdade para conectar/sincronizar/gerenciar. */}
          <div className="agenda-config-section__title">
            <div>
              <h3>Administre suas contas</h3>
              <p>Conectar, sincronizar e desconectar Google, Microsoft, Apple e Yahoo agora é tudo numa página só.</p>
            </div>
            <span>{integracoes.filter((item) => ["google_calendar", "microsoft_365", "apple_icloud", "yahoo_mail"].includes(item.provider) && item.enabled).length}</span>
          </div>
          <Link to="/sincronizacao" className="botao botao--secundario">Abrir Sincronização de contas</Link>
        </section>
        <section className="agenda-config-section">
          <div className="agenda-config-section__title"><div><h3>Importar agendas de clínicas e hospitais</h3><p>Prepare uma conexão para cada local de trabalho. Ativação e escrita exigem API oficial, credenciais e homologação do fornecedor.</p></div><span>{integracoes.length}</span></div>
          {integracoes.map((item) => <div className="agenda-config-item" key={item.id}><i className={item.status === "connected" ? "conectavel" : "em-breve"} /><span><strong>{item.display_name}</strong><small>{capacidades?.connectors.find((connector) => connector.provider === item.provider)?.name || item.provider} · {item.status === "draft" ? "preparada, aguardando configuração" : item.status === "connected" ? "conectada" : item.last_error_message || item.status}</small></span><span className="agenda-pill">{item.enabled ? "Ativa" : "Rascunho"}</span></div>)}
          <div className="agenda-config-form agenda-integracao-form">
            <label>Sistema<select value={novaIntegracao.provider} onChange={(e) => setNovaIntegracao({ ...novaIntegracao, provider: e.target.value })}>{capacidades?.connectors.filter((item) => !["google_calendar", "microsoft_365", "apple_icloud"].includes(item.provider)).map((item) => <option key={item.provider} value={item.provider}>{item.name}</option>)}</select></label>
            <label>Clínica ou hospital<input value={novaIntegracao.display_name} onChange={(e) => setNovaIntegracao({ ...novaIntegracao, display_name: e.target.value })} placeholder="Ex.: Hospital Central · agenda principal" /></label>
            <p className="agenda-config-help span-2">Esta etapa registra a solicitação sem enviar senhas. O conector só será ativado após consentimento e validação técnica; fornecedores sem API homologada permanecem identificados como pendentes.</p>
            <button className="botao botao--secundario" disabled={!novaIntegracao.display_name.trim()} onClick={() => prepararIntegracao().catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível preparar a integração."))}>Preparar integração</button>
          </div>
          <details className="agenda-conectores-catalogo"><summary>Ver disponibilidade por sistema</summary>{capacidades?.connectors.map((item) => <div className="agenda-config-item" key={item.provider}><i className={item.status === "adapter_available" ? "conectavel" : "em-breve"} /><span><strong>{item.name}</strong><small>{item.status === "adapter_available" ? "Adaptador oficial disponível" : item.status === "homologation_required" ? "Depende de homologação oficial" : "Integração planejada"}</small></span><span className="agenda-pill">{item.capabilities.create_appointment ? "Bidirecional" : item.capabilities.read_appointments ? "Leitura" : "Pendente"}</span></div>)}</details>
        </section>
        <footer><button className="botao" onClick={() => setConfigAberta(false)}>Concluir configuração</button></footer>
      </div></div>}
    </div>
  );
}
