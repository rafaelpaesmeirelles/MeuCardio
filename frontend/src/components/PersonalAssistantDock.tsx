import { useEffect, useMemo, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import Icone from "./Icone";
import { api } from "../lib/api";

type Appointment = {
  id: number;
  patient_name: string | null;
  scheduled_at: string;
  appointment_type: string;
  status: string;
};

type MobilityPreference = {
  enabled: boolean;
  automatic_foreground_refresh: boolean;
  refresh_interval_minutes: number;
  traffic_configured: boolean;
};

type NextLocation = {
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

type Commute = {
  status: string;
  destination: NextLocation | null;
  routes: Array<{
    duration_seconds: number;
    traffic_duration_seconds?: number | null;
    distance_meters?: number;
  }>;
  tips: string[];
};

type EmailSummary = {
  disponivel: boolean;
  pendentes?: unknown[];
};

function sameDay(a: Date, b: Date) {
  return a.getFullYear() === b.getFullYear()
    && a.getMonth() === b.getMonth()
    && a.getDate() === b.getDate();
}

function time(value: string | Date) {
  return new Date(value).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
}

function duration(seconds: number) {
  const minutes = Math.max(1, Math.round(seconds / 60));
  if (minutes < 60) return `${minutes} min`;
  const hours = Math.floor(minutes / 60);
  const rest = minutes % 60;
  return rest ? `${hours} h ${rest} min` : `${hours} h`;
}

export default function PersonalAssistantDock() {
  const location = useLocation();
  const [open, setOpen] = useState(false);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [mobility, setMobility] = useState<MobilityPreference | null>(null);
  const [locations, setLocations] = useState<NextLocation[]>([]);
  const [commute, setCommute] = useState<Commute | null>(null);
  const [mailPending, setMailPending] = useState<number | null>(null);
  const [locationState, setLocationState] = useState("");

  useEffect(() => setOpen(false), [location.pathname]);

  useEffect(() => {
    api.get<Appointment[]>("/appointments").then(setAppointments).catch(() => setAppointments([]));
    api.get<MobilityPreference>("/agenda/mobility/preferences").then(setMobility).catch(() => setMobility(null));
    api.get<NextLocation[]>("/agenda/workday/next-locations").then(setLocations).catch(() => setLocations([]));
    api.get<EmailSummary>("/email/resumo")
      .then((summary) => setMailPending(summary.disponivel ? (summary.pendentes?.length ?? 0) : null))
      .catch(() => setMailPending(null));
  }, []);

  useEffect(() => {
    if (!open || !mobility?.enabled || !navigator.geolocation) return;
    let active = true;
    navigator.geolocation.getCurrentPosition(
      (position) => {
        if (!active) return;
        setLocationState("");
        api.post<Commute>("/agenda/mobility/commute", {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        }).then((result) => { if (active) setCommute(result); })
          .catch(() => { if (active) setLocationState("Não foi possível atualizar o trânsito agora."); });
      },
      (error) => {
        if (!active) return;
        setLocationState(error.code === error.PERMISSION_DENIED
          ? "Localização bloqueada neste aparelho."
          : "Localização temporariamente indisponível.");
      },
      { enableHighAccuracy: false, timeout: 10_000, maximumAge: 120_000 },
    );
    return () => { active = false; };
  }, [open, mobility?.enabled]);

  const today = useMemo(() => {
    const now = new Date();
    return appointments
      .filter((item) => item.status !== "cancelado" && sameDay(new Date(item.scheduled_at), now))
      .sort((a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at));
  }, [appointments]);

  const nextAppointment = useMemo(() => {
    const now = Date.now();
    return appointments
      .filter((item) => item.status !== "cancelado" && +new Date(item.scheduled_at) >= now)
      .sort((a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at))[0] ?? null;
  }, [appointments]);

  const destination = locations[0] ?? null;
  const route = commute?.routes?.[0] ?? null;
  const departure = destination && route
    ? new Date(new Date(destination.starts_at).getTime()
      - (route.duration_seconds + destination.arrival_buffer_minutes * 60) * 1000)
    : null;

  return (
    <div className={`cc-assistant-dock${open ? " is-open" : ""}`}>
      <button
        type="button"
        className="cc-assistant-dock__trigger"
        aria-label={open ? "Fechar Assistente Pessoal" : "Abrir Assistente Pessoal"}
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
      >
        <span aria-hidden="true">✦</span>
        <span className="cc-assistant-dock__trigger-text">Assistente</span>
        {(today.length > 0 || (mailPending ?? 0) > 0) && <strong>{today.length + (mailPending ?? 0)}</strong>}
      </button>

      {open && (
        <aside className="cc-assistant-dock__panel" aria-label="Assistente Pessoal">
          <header>
            <div><span>✦</span><div><strong>Assistente Pessoal</strong><small>Sua rotina profissional em contexto</small></div></div>
            <button type="button" onClick={() => setOpen(false)} aria-label="Fechar"><Icone nome="fechar" /></button>
          </header>

          <section className="cc-assistant-dock__summary">
            <p>SEU DIA</p>
            <strong>{today.length} compromisso{today.length === 1 ? "" : "s"} hoje</strong>
            {nextAppointment ? (
              <span>Próximo às {time(nextAppointment.scheduled_at)}{nextAppointment.patient_name ? ` · ${nextAppointment.patient_name}` : ""}</span>
            ) : <span>Nenhum compromisso futuro na agenda.</span>}
          </section>

          <section className="cc-assistant-dock__item">
            <span className="cc-assistant-dock__icon"><Icone nome="rota" /></span>
            <div>
              <p>DESLOCAMENTO</p>
              {departure && destination && route ? (
                <><strong>Sair às {time(departure)}</strong><span>{destination.location.name || destination.service_name} · {duration(route.traffic_duration_seconds || route.duration_seconds)}</span></>
              ) : destination ? (
                <><strong>{destination.location.name || destination.service_name}</strong><span>{locationState || (mobility?.enabled ? "Permita localização para estimar a saída." : "Ative Mobilidade na Agenda para receber sugestões de saída.")}</span></>
              ) : (
                <><strong>Sem deslocamento pendente</strong><span>O próximo destino configurado aparecerá aqui.</span></>
              )}
            </div>
          </section>

          <section className="cc-assistant-dock__item">
            <span className="cc-assistant-dock__icon"><Icone nome="mail" /></span>
            <div><p>COMUNICAÇÃO</p><strong>{mailPending == null ? "CorVIA Mail" : `${mailPending} mensagem${mailPending === 1 ? "" : "s"} pendente${mailPending === 1 ? "" : "s"}`}</strong><span>Veja o que merece atenção sem sair do fluxo.</span></div>
          </section>

          <section className="cc-assistant-dock__context">
            <p>CONTEXTO ATUAL</p>
            <strong>{location.pathname === "/" ? "Clinical Command Center" : "Você está trabalhando no CorVIA"}</strong>
            <span>O assistente acompanha a rotina sem assumir que todo trabalho começa por um paciente.</span>
          </section>

          <footer>
            <Link to="/agenda"><Icone nome="agenda" /> Agenda</Link>
            <Link to="/corvia-mail"><Icone nome="mail" /> Mail</Link>
            <Link to="/assistente"><Icone nome="assistente" /> CorVIA AI</Link>
          </footer>
        </aside>
      )}
    </div>
  );
}
