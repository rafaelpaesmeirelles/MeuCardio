import { type FormEvent, useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Icone, { type NomeIcone } from "../components/Icone";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";

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

type Rota = {
  duration_seconds: number;
  distance_meters?: number;
  traffic_duration_seconds?: number | null;
};

type Deslocamento = {
  status: string;
  provider?: string;
  destination: ProximoLocal | null;
  routes: Rota[];
  tips: string[];
};

type Catalogo = { total: number; published_total?: number };
type ListaComTotal = { total?: number };
type ResumoEmail = { disponivel: boolean; pendentes?: unknown[] };

type Acao = {
  to: string;
  label: string;
  detail: string;
  icon: NomeIcone;
  tone: "teal" | "blue" | "purple" | "amber" | "red" | "green";
};

type RecentItem = {
  to: string;
  label: string;
  type: string;
  icon: NomeIcone;
};

const ACTIONS: Acao[] = [
  { to: "/receituario", label: "Prescrever", detail: "Novo receituário", icon: "prescricao", tone: "teal" },
  { to: "/documentos", label: "Solicitar exames", detail: "Pedido complementar", icon: "clinica", tone: "blue" },
  { to: "/documentos", label: "Documento", detail: "Atestado, relatório…", icon: "documento", tone: "purple" },
  { to: "/calculadoras", label: "Calculadoras", detail: "Escores e índices", icon: "calculadora", tone: "amber" },
  { to: "/emergencia", label: "Emergências", detail: "Condutas rápidas", icon: "emergencia", tone: "red" },
  { to: "/medicamentos", label: "Medicamentos", detail: "Doses e interações", icon: "medicamento", tone: "green" },
  { to: "/diretrizes", label: "Guidelines", detail: "Diretrizes atuais", icon: "conhecimento", tone: "amber" },
  { to: "/assistente", label: "CorVIA AI", detail: "Pergunte ao CorVIA", icon: "assistente", tone: "purple" },
];

const DEFAULT_RECENTS: RecentItem[] = [
  { to: "/doencas", label: "Condições clínicas", type: "Clínica", icon: "doencas" },
  { to: "/medicamentos", label: "Medicamentos", type: "Farmacologia", icon: "medicamento" },
  { to: "/evidencias", label: "Evidências", type: "Ciência", icon: "evidencia" },
  { to: "/calculadoras", label: "Calculadoras", type: "Ferramenta", icon: "calculadora" },
];

const AREA_LINKS = [
  { label: "Cardiologia Clínica", to: "/biblioteca" },
  { label: "Arritmias", to: "/biblioteca?tema=Arritmias" },
  { label: "Insuficiência Cardíaca", to: "/biblioteca?tema=Insufici%C3%AAncia%20card%C3%ADaca" },
  { label: "Coronariopatia", to: "/biblioteca?tema=Doen%C3%A7a%20arterial%20coronariana" },
  { label: "Valvopatias", to: "/biblioteca?tema=Valvopatias" },
  { label: "Hipertensão", to: "/biblioteca?tema=Hipertens%C3%A3o" },
  { label: "Imagem", to: "/exames" },
  { label: "Prevenção CV", to: "/biblioteca?tema=Preven%C3%A7%C3%A3o" },
];

function saudacao() {
  const hora = new Date().getHours();
  if (hora < 12) return "Bom dia";
  if (hora < 18) return "Boa tarde";
  return "Boa noite";
}

function mesmoDia(a: Date, b: Date) {
  return a.getFullYear() === b.getFullYear()
    && a.getMonth() === b.getMonth()
    && a.getDate() === b.getDate();
}

function hora(data: string | Date) {
  return new Date(data).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
}

function duracao(segundos: number) {
  const minutos = Math.max(1, Math.round(segundos / 60));
  if (minutos < 60) return `${minutos} min`;
  const h = Math.floor(minutos / 60);
  const m = minutos % 60;
  return m ? `${h} h ${m} min` : `${h} h`;
}

function interpretCommand(raw: string) {
  const termo = raw.trim();
  const normal = termo.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  if (/\b(prescrev|receita|receituario)\b/.test(normal)) return "/receituario";
  if (/\b(solicitar exames|pedido de exames|atestado|documento|relatorio|declaracao)\b/.test(normal)) return "/documentos";
  if (/\b(calcular|calculadora|escore|cha2ds2|has-bled|grace|timi|wells)\b/.test(normal)) return "/calculadoras";
  if (/\b(emergencia|urgencia|choque|pcr|parada)\b/.test(normal)) return "/emergencia";
  if (/\b(agenda|compromisso|consulta)\b/.test(normal)) return "/agenda";
  if (/\b(paciente|round)\b/.test(normal)) return "/round";
  if (/\b(email|e-mail|mail)\b/.test(normal)) return "/corvia-mail";
  return `/busca?q=${encodeURIComponent(termo)}`;
}

function abreChatGlobal() {
  const botao = document.querySelector<HTMLButtonElement>('button[aria-label^="Abrir o CorvIA Chat"]');
  botao?.click();
}

export default function ClinicalCommandCenterHome() {
  const { usuario } = useAuth();
  const navigate = useNavigate();
  const [command, setCommand] = useState("");
  const [agenda, setAgenda] = useState<Agendamento[] | null>(null);
  const [mobility, setMobility] = useState<PreferenciaMobilidade | null>(null);
  const [nextLocations, setNextLocations] = useState<ProximoLocal[]>([]);
  const [commute, setCommute] = useState<Deslocamento | null>(null);
  const [locationMessage, setLocationMessage] = useState("");
  const [catalog, setCatalog] = useState<Catalogo | null>(null);
  const [evidenceTotal, setEvidenceTotal] = useState<number | null>(null);
  const [studiesTotal, setStudiesTotal] = useState<number | null>(null);
  const [pendingMail, setPendingMail] = useState<number | null>(null);
  const [recents, setRecents] = useState<RecentItem[]>(DEFAULT_RECENTS);

  useEffect(() => {
    const total = (path: string) => api.get<ListaComTotal>(path).then((r) => r.total ?? 0).catch(() => null);
    api.get<Agendamento[]>("/appointments").then(setAgenda).catch(() => setAgenda([]));
    api.get<PreferenciaMobilidade>("/agenda/mobility/preferences").then(setMobility).catch(() => setMobility(null));
    api.get<ProximoLocal[]>("/agenda/workday/next-locations").then(setNextLocations).catch(() => setNextLocations([]));
    api.get<Catalogo>("/library/catalog").then(setCatalog).catch(() => setCatalog(null));
    total("/evidence?limit=1").then(setEvidenceTotal);
    total("/studies?limit=1").then(setStudiesTotal);
    api.get<ResumoEmail>("/email/resumo")
      .then((resumo) => setPendingMail(resumo.disponivel ? (resumo.pendentes?.length ?? 0) : null))
      .catch(() => setPendingMail(null));

    try {
      const key = `corvia.cc.recents.${usuario?.id ?? "user"}`;
      const stored = JSON.parse(localStorage.getItem(key) || "[]") as RecentItem[];
      if (Array.isArray(stored) && stored.length) setRecents(stored.slice(0, 5));
    } catch {
      setRecents(DEFAULT_RECENTS);
    }
  }, [usuario?.id]);

  useEffect(() => {
    if (!mobility?.enabled || !mobility.automatic_foreground_refresh || !navigator.geolocation) return;
    let active = true;
    const update = () => navigator.geolocation.getCurrentPosition(
      (position) => {
        if (!active) return;
        setLocationMessage("");
        api.post<Deslocamento>("/agenda/mobility/commute", {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        }).then((result) => { if (active) setCommute(result); })
          .catch(() => { if (active) setLocationMessage("Trânsito temporariamente indisponível."); });
      },
      (error) => {
        if (!active) return;
        setLocationMessage(error.code === error.PERMISSION_DENIED
          ? "Localização desativada. Ative-a para receber horário de saída."
          : "Não foi possível obter sua localização agora.");
      },
      { enableHighAccuracy: false, timeout: 12_000, maximumAge: 120_000 },
    );
    update();
    const interval = window.setInterval(update, Math.max(2, mobility.refresh_interval_minutes) * 60_000);
    return () => { active = false; window.clearInterval(interval); };
  }, [mobility]);

  const todayAppointments = useMemo(() => {
    if (!agenda) return [];
    const today = new Date();
    return agenda
      .filter((item) => item.status !== "cancelado" && mesmoDia(new Date(item.scheduled_at), today))
      .sort((a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at));
  }, [agenda]);

  const nextAppointment = useMemo(() => {
    const now = Date.now();
    return (agenda ?? [])
      .filter((item) => item.status !== "cancelado" && +new Date(item.scheduled_at) >= now)
      .sort((a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at))[0] ?? null;
  }, [agenda]);

  const nextDestination = nextLocations[0] ?? null;
  const bestRoute = commute?.routes?.[0] ?? null;
  const recommendedDeparture = nextDestination && bestRoute
    ? new Date(new Date(nextDestination.starts_at).getTime()
      - (bestRoute.duration_seconds + nextDestination.arrival_buffer_minutes * 60) * 1000)
    : null;

  const firstName = usuario?.full_name?.trim().split(/\s+/)[0] || "Doutor(a)";

  function submitCommand(event: FormEvent) {
    event.preventDefault();
    const value = command.trim();
    if (value.length < 2) return;
    navigate(interpretCommand(value));
    setCommand("");
  }

  return (
    <div className="cc-home">
      <section className="cc-home__hero">
        <div className="cc-home__hero-main">
          <p className="cc-kicker">Clinical Command Center</p>
          <h1>{saudacao()}, {firstName}! <span aria-hidden="true">👋</span></h1>
          <p className="cc-home__subtitle">O que você precisa resolver agora?</p>
          <form className="cc-command" onSubmit={submitCommand}>
            <span className="cc-command__spark" aria-hidden="true">✦</span>
            <input
              value={command}
              onChange={(event) => setCommand(event.target.value)}
              placeholder="Pergunte, pesquise ou execute uma ação…"
              aria-label="Comando clínico universal"
            />
            <button type="submit" aria-label="Executar"><Icone nome="seta" /></button>
          </form>
          <div className="cc-command__examples" aria-label="Exemplos de comando">
            <span>Exemplos:</span>
            {["tratamento da pericardite", "nebido dose", "critérios de Duke", "prescrever losartana", "calcular CHA₂DS₂-VASc"].map((example) => (
              <button type="button" key={example} onClick={() => setCommand(example)}>{example}</button>
            ))}
          </div>
        </div>
      </section>

      <div className="cc-home__layout">
        <div className="cc-home__workspace">
          <section className="cc-section">
            <div className="cc-section__header"><div><p className="cc-kicker">Acesso imediato</p><h2>Ações rápidas</h2></div><Link to="/favoritos">Personalizar</Link></div>
            <div className="cc-quick-grid">
              {ACTIONS.map((action) => (
                <Link to={action.to} key={`${action.label}-${action.to}`} className={`cc-quick cc-quick--${action.tone}`}>
                  <span className="cc-quick__icon"><Icone nome={action.icon} /></span>
                  <span><strong>{action.label}</strong><small>{action.detail}</small></span>
                  <Icone nome="seta" className="cc-quick__arrow" />
                </Link>
              ))}
            </div>
          </section>

          <section className="cc-section">
            <div className="cc-section__header"><div><p className="cc-kicker">Continuidade</p><h2>Continuar de onde parei</h2></div><Link to="/favoritos">Ver favoritos</Link></div>
            <div className="cc-recent-row">
              {recents.map((item) => (
                <Link to={item.to} key={`${item.to}-${item.label}`} className="cc-recent-card">
                  <span className="cc-recent-card__type">{item.type}</span>
                  <span className="cc-recent-card__icon"><Icone nome={item.icon} /></span>
                  <strong>{item.label}</strong>
                  <small>Abrir contexto</small>
                </Link>
              ))}
            </div>
          </section>

          <section className="cc-section">
            <div className="cc-section__header"><div><p className="cc-kicker">Ciência acionável</p><h2>O que pode importar para você</h2></div><Link to="/evidencias">Explorar ciência</Link></div>
            <div className="cc-update-grid">
              <Link to="/diretrizes" className="cc-update cc-update--guideline">
                <span>GUIDELINES</span><strong>Diretrizes e recomendações</strong><p>Consulte recomendações, mudanças relevantes e documentos científicos disponíveis no CorVIA.</p><small>Abrir guidelines →</small>
              </Link>
              <Link to="/estudos" className="cc-update cc-update--study">
                <span>ESTUDOS</span><strong>{studiesTotal == null ? "Biblioteca de estudos" : `${studiesTotal.toLocaleString("pt-BR")} estudos disponíveis`}</strong><p>Do estudo pivotal à aplicação clínica, conectado às demais entidades do sistema.</p><small>Explorar estudos →</small>
              </Link>
              <Link to="/medicamentos" className="cc-update cc-update--regulatory">
                <span>MEDICAMENTOS</span><strong>{catalog?.published_total ?? catalog?.total ? `${(catalog?.published_total ?? catalog?.total ?? 0).toLocaleString("pt-BR")} conteúdos no catálogo` : "Catálogo clínico"}</strong><p>Farmacologia, apresentações, evidências e relações clínicas em um só contexto.</p><small>Abrir medicamentos →</small>
              </Link>
            </div>
          </section>

          <section className="cc-section cc-section--areas">
            <div className="cc-section__header"><div><p className="cc-kicker">Explorar</p><h2>Por área clínica</h2></div><Link to="/biblioteca">Ver todas</Link></div>
            <div className="cc-area-row">
              {AREA_LINKS.map((area) => <Link to={area.to} key={area.label}>{area.label}</Link>)}
            </div>
          </section>
        </div>

        <aside className="cc-home__rail" aria-label="Inteligência e assistência pessoal">
          <section className="cc-rail-card cc-intelligence">
            <div className="cc-rail-card__title"><span><Icone nome="assistente" /> CorVIA Intelligence</span><Link to="/assistente">Ver tudo</Link></div>
            <div className="cc-intel-list">
              <Link to="/evidencias"><Icone nome="evidencia" /><span><strong>{evidenceTotal == null ? "Evidências clínicas" : `${evidenceTotal.toLocaleString("pt-BR")} evidências`}</strong><small>Conhecimento científico estruturado</small></span></Link>
              <Link to="/estudos"><Icone nome="conhecimento" /><span><strong>{studiesTotal == null ? "Estudos clínicos" : `${studiesTotal.toLocaleString("pt-BR")} estudos`}</strong><small>Estudos conectados ao contexto</small></span></Link>
              <Link to="/medicamentos"><Icone nome="medicamento" /><span><strong>{catalog?.total == null ? "Catálogo de medicamentos" : `${catalog.total.toLocaleString("pt-BR")} itens catalogados`}</strong><small>Conteúdo clínico e prescricional</small></span></Link>
              <Link to="/busca"><Icone nome="busca" /><span><strong>Explorar relações</strong><small>Use o “Tudo com Tudo” para seguir conexões</small></span></Link>
            </div>
            <button type="button" className="cc-rail-card__cta" onClick={abreChatGlobal}>Pergunte qualquer coisa ao CorVIA</button>
          </section>

          <section className="cc-rail-card cc-personal-assistant">
            <div className="cc-rail-card__title"><span><span className="cc-assistant-star">✦</span> Assistente Pessoal</span><Link to="/agenda">Agenda</Link></div>
            <div className="cc-assistant-greeting"><strong>Seu dia, no contexto.</strong><small>Agenda, deslocamento e pendências sem transformar a Home em prontuário.</small></div>

            <div className="cc-assistant-block">
              <span className="cc-assistant-block__icon"><Icone nome="agenda" /></span>
              <div><small>SEU DIA</small><strong>{agenda === null ? "Carregando agenda…" : `${todayAppointments.length} compromisso${todayAppointments.length === 1 ? "" : "s"} hoje`}</strong>
                {nextAppointment && <span>Próximo às {hora(nextAppointment.scheduled_at)}{nextAppointment.patient_name ? ` · ${nextAppointment.patient_name}` : ""}</span>}
              </div>
            </div>

            <div className="cc-assistant-block">
              <span className="cc-assistant-block__icon"><Icone nome="rota" /></span>
              <div><small>DESLOCAMENTO</small>
                {recommendedDeparture && nextDestination && bestRoute ? (
                  <><strong>Saída sugerida: {hora(recommendedDeparture)}</strong><span>{nextDestination.location.name || nextDestination.service_name} · {duracao(bestRoute.traffic_duration_seconds || bestRoute.duration_seconds)}</span></>
                ) : nextDestination ? (
                  <><strong>{nextDestination.location.name || nextDestination.service_name}</strong><span>{locationMessage || (mobility?.enabled ? "Ative localização para estimar o melhor horário de saída." : "Configure mobilidade na Agenda para receber sugestões de saída.")}</span></>
                ) : (
                  <><strong>Nenhum deslocamento pendente</strong><span>{locationMessage || "Quando houver destino configurado, ele aparece aqui."}</span></>
                )}
              </div>
            </div>

            <div className="cc-assistant-block">
              <span className="cc-assistant-block__icon"><Icone nome="mail" /></span>
              <div><small>COMUNICAÇÃO</small><strong>{pendingMail == null ? "CorVIA Mail" : `${pendingMail} mensagem${pendingMail === 1 ? "" : "s"} pendente${pendingMail === 1 ? "" : "s"}`}</strong><span>Abra a caixa de entrada sem perder o contexto do seu dia.</span></div>
            </div>

            <div className="cc-assistant-actions">
              <Link to="/agenda"><Icone nome="agenda" /> Ver agenda</Link>
              <Link to="/corvia-mail"><Icone nome="mail" /> Abrir Mail</Link>
              <Link to="/assistente"><Icone nome="assistente" /> Pedir ajuda</Link>
            </div>
          </section>
        </aside>
      </div>
    </div>
  );
}
