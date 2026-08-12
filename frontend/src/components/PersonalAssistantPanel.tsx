import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import Icone from "./Icone";

type Agendamento = {
  id: number;
  patient_name: string | null;
  scheduled_at: string;
  appointment_type: string;
  status: string;
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

type PreferenciaMobilidade = {
  enabled: boolean;
  automatic_foreground_refresh: boolean;
  refresh_interval_minutes: number;
  traffic_configured: boolean;
};

type Rota = {
  duration_seconds: number;
  distance_meters: number;
  traffic_delay_seconds: number;
};

type Deslocamento = {
  status: string;
  provider?: string;
  updated_at?: string;
  destination: ProximoLocal | null;
  routes: Rota[];
  tips: string[];
};

type Props = {
  aberto: boolean;
  onClose: () => void;
};

function mesmoDia(a: Date, b: Date) {
  return a.getFullYear() === b.getFullYear()
    && a.getMonth() === b.getMonth()
    && a.getDate() === b.getDate();
}

function tipoCompromisso(tipo: string) {
  return ({ consulta: "Consulta", retorno: "Retorno", exame: "Exame", outro: "Compromisso" } as Record<string, string>)[tipo]
    || "Compromisso";
}

export default function PersonalAssistantPanel({ aberto, onClose }: Props) {
  const [agenda, setAgenda] = useState<Agendamento[] | null>(null);
  const [locais, setLocais] = useState<ProximoLocal[]>([]);
  const [mobilidade, setMobilidade] = useState<PreferenciaMobilidade | null>(null);
  const [deslocamento, setDeslocamento] = useState<Deslocamento | null>(null);
  const [carregandoRota, setCarregandoRota] = useState(false);
  const [erroRota, setErroRota] = useState("");

  useEffect(() => {
    if (!aberto) return;
    let ativo = true;
    Promise.all([
      api.get<Agendamento[]>("/appointments").catch(() => []),
      api.get<ProximoLocal[]>("/agenda/workday/next-locations").catch(() => []),
      api.get<PreferenciaMobilidade>("/agenda/mobility/preferences").catch(() => null),
    ]).then(([compromissos, proximos, preferencias]) => {
      if (!ativo) return;
      setAgenda(compromissos);
      setLocais(proximos);
      setMobilidade(preferencias);
    });
    return () => { ativo = false; };
  }, [aberto]);

  useEffect(() => {
    if (!aberto) return;
    function escapar(evento: KeyboardEvent) {
      if (evento.key === "Escape") onClose();
    }
    document.addEventListener("keydown", escapar);
    return () => document.removeEventListener("keydown", escapar);
  }, [aberto, onClose]);

  const hoje = useMemo(() => {
    const agora = new Date();
    return (agenda ?? [])
      .filter((item) => item.status !== "cancelado" && mesmoDia(new Date(item.scheduled_at), agora))
      .sort((a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at));
  }, [agenda]);

  const proximo = useMemo(() => {
    const agora = Date.now();
    return (agenda ?? [])
      .filter((item) => item.status !== "cancelado" && +new Date(item.scheduled_at) >= agora)
      .sort((a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at))[0];
  }, [agenda]);

  const proximoLocal = locais[0] ?? null;
  const rota = deslocamento?.routes?.[0] ?? null;
  const saidaRecomendada = proximoLocal && rota
    ? new Date(new Date(proximoLocal.starts_at).getTime() - (rota.duration_seconds + proximoLocal.arrival_buffer_minutes * 60) * 1000)
    : null;

  function atualizarDeslocamento() {
    setErroRota("");
    if (!navigator.geolocation) {
      setErroRota("Localização não disponível neste dispositivo.");
      return;
    }
    setCarregandoRota(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        api.post<Deslocamento>("/agenda/mobility/commute", {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        }).then(setDeslocamento)
          .catch(() => setErroRota("Não foi possível calcular o deslocamento agora."))
          .finally(() => setCarregandoRota(false));
      },
      (erro) => {
        setCarregandoRota(false);
        setErroRota(erro.code === erro.PERMISSION_DENIED
          ? "Permissão de localização bloqueada neste dispositivo."
          : "Localização temporariamente indisponível.");
      },
      { enableHighAccuracy: false, timeout: 12000, maximumAge: 120000 },
    );
  }

  return (
    <>
      <div className={`cos-assistant-backdrop${aberto ? " is-visible" : ""}`} onClick={onClose} aria-hidden="true" />
      <aside className={`cos-assistant-panel${aberto ? " is-open" : ""}`} aria-hidden={!aberto} aria-label="Assistente Pessoal CorVIA">
        <header className="cos-assistant-panel__head">
          <div className="cos-assistant-panel__brand">
            <span className="cos-assistant-panel__spark">✦</span>
            <div><small>Seu copiloto de rotina</small><strong>Assistente Pessoal</strong></div>
          </div>
          <button type="button" onClick={onClose} aria-label="Fechar Assistente Pessoal"><Icone nome="fechar" /></button>
        </header>

        <div className="cos-assistant-panel__body">
          <section className="cos-assistant-briefing">
            <p className="eyebrow">Seu dia</p>
            <div className="cos-assistant-briefing__summary">
              <div><strong>{agenda === null ? "—" : hoje.length}</strong><span>compromissos hoje</span></div>
              <div><strong>{proximo ? new Date(proximo.scheduled_at).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }) : "Livre"}</strong><span>próximo horário</span></div>
            </div>
            {proximo ? (
              <div className="cos-assistant-next">
                <span><Icone nome="agenda" /></span>
                <div><small>Próximo compromisso</small><strong>{proximo.patient_name || tipoCompromisso(proximo.appointment_type)}</strong><p>{tipoCompromisso(proximo.appointment_type)} · {new Date(proximo.scheduled_at).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}</p></div>
              </div>
            ) : agenda === null ? (
              <p className="cos-assistant-state">Carregando sua agenda…</p>
            ) : (
              <p className="cos-assistant-state">Nenhum compromisso futuro encontrado na agenda.</p>
            )}
            <Link to="/agenda" onClick={onClose} className="cos-assistant-link">Abrir agenda completa <Icone nome="seta" /></Link>
          </section>

          <section className="cos-assistant-card">
            <div className="cos-assistant-card__head"><span><Icone nome="rota" /></span><div><p className="eyebrow">Deslocamento</p><h3>Chegue no tempo certo</h3></div></div>
            {proximoLocal ? (
              <>
                <div className="cos-assistant-destination"><Icone nome="pin" /><div><small>Próximo local</small><strong>{proximoLocal.location.name}</strong><span>Início às {new Date(proximoLocal.starts_at).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}</span></div></div>
                {rota ? (
                  <div className="cos-assistant-route">
                    <div><strong>{Math.ceil(rota.duration_seconds / 60)} min</strong><small>trajeto</small></div>
                    <div><strong>{(rota.distance_meters / 1000).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} km</strong><small>distância</small></div>
                    <div><strong>{saidaRecomendada?.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }) || "—"}</strong><small>saída sugerida</small></div>
                  </div>
                ) : (
                  <button type="button" className="cos-assistant-route-button" onClick={atualizarDeslocamento} disabled={carregandoRota}>
                    <Icone nome="rota" /> {carregandoRota ? "Calculando rota…" : "Calcular deslocamento agora"}
                  </button>
                )}
                {erroRota && <p className="cos-assistant-warning">{erroRota}</p>}
                {!mobilidade?.enabled && <p className="cos-assistant-hint">Você pode ativar a mobilidade na Agenda para deixar este briefing mais automático.</p>}
              </>
            ) : (
              <div className="cos-assistant-empty"><strong>Nenhum local de trabalho futuro configurado.</strong><small>Cadastre sua rotina e endereços na Agenda para receber assistência de deslocamento.</small><Link to="/agenda" onClick={onClose}>Configurar na Agenda <Icone nome="seta" /></Link></div>
            )}
          </section>

          <section className="cos-assistant-card">
            <div className="cos-assistant-card__head"><span><Icone nome="check" /></span><div><p className="eyebrow">Próximos passos</p><h3>Continue sem perder contexto</h3></div></div>
            <div className="cos-assistant-actions">
              <Link to="/documentos" onClick={onClose}><Icone nome="documento" /><span><strong>Documentos</strong><small>Atestados, relatórios e solicitações</small></span><Icone nome="seta" /></Link>
              <Link to="/corvia-mail" onClick={onClose}><Icone nome="mail" /><span><strong>CorVIA Mail</strong><small>Comunicação profissional</small></span><Icone nome="seta" /></Link>
              <Link to="/favoritos" onClick={onClose}><Icone nome="favorito" /><span><strong>Favoritos</strong><small>Retome conteúdo salvo</small></span><Icone nome="seta" /></Link>
            </div>
          </section>
        </div>

        <footer className="cos-assistant-panel__footer">
          <Link to="/assistente" onClick={onClose}><span className="cos-assistant-panel__spark">✦</span><span><strong>Precisa pensar um caso?</strong><small>Abra a CorVIA AI para assistência clínica contextual.</small></span><Icone nome="seta" /></Link>
        </footer>
      </aside>
    </>
  );
}
