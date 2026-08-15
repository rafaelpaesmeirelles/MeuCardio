import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import Icone from "./Icone";
import MapaDeslocamento, { type RotaDeslocamento } from "./MapaDeslocamento";

type Agendamento = { id: number; patient_name: string | null; scheduled_at: string; appointment_type: string; status: string };
type AgendamentoIntegrado = { id: number; patient_name: string | null; starts_at: string; appointment_type: string; status: string };
type ProximoLocal = {
  target_key: string; target_type: "appointment" | "work_routine" | "commitment" | string;
  appointment_id: number | null; routine_id: number | null; commitment_id?: string | null;
  starts_at: string; ends_at: string | null; service_name: string; title?: string;
  source: "work_routine" | "appointment" | "commitment"; arrival_buffer_minutes: number;
  location: { id: number; name: string; address: Record<string, string>; latitude: number | null; longitude: number | null } | null;
};
type PreferenciaMobilidade = { enabled: boolean; automatic_foreground_refresh: boolean; refresh_interval_minutes: number; traffic_configured: boolean };
type ConfiguracaoMapa = { provider: string; configured: boolean; api_key: string | null };
type Deslocamento = { status: string; provider?: string; updated_at?: string; destination: ProximoLocal | null; routes: RotaDeslocamento[]; tips: string[] };
type MensagemEmail = { messageId?: string; id?: string; subject?: string; fromAddress?: string; sender?: string; receivedTime?: string; sentDateInGMT?: string; date?: string };
type ResumoEmail = { disponivel: boolean; email_address: string | null; pendentes: MensagemEmail[] };
type Props = { aberto: boolean; onClose: () => void };

function mesmoDia(a: Date, b: Date) { return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate(); }
function tipoCompromisso(tipo: string) { return ({ consulta: "Consulta", retorno: "Retorno", exame: "Exame", outro: "Compromisso", reuniao: "Reunião", trabalho: "Trabalho", plantao: "Plantão", estudo: "Estudo", pessoal: "Compromisso pessoal" } as Record<string, string>)[tipo] || "Compromisso"; }
function dataDoEmail(mensagem: MensagemEmail) {
  const bruto = mensagem.receivedTime ?? mensagem.sentDateInGMT ?? mensagem.date;
  if (!bruto) return null;
  const numero = Number(bruto);
  const data = Number.isFinite(numero) && String(bruto).length > 8 ? new Date(numero) : new Date(bruto);
  return Number.isNaN(data.getTime()) ? null : data;
}
function dataCurtaDoEmail(mensagem: MensagemEmail) {
  const data = dataDoEmail(mensagem);
  if (!data) return "";
  return data.toDateString() === new Date().toDateString() ? data.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }) : data.toLocaleDateString("pt-BR", { day: "2-digit", month: "short" });
}
function normalizarAgendamento(item: AgendamentoIntegrado): Agendamento {
  return { id: item.id, patient_name: item.patient_name, scheduled_at: item.starts_at, appointment_type: item.appointment_type, status: item.status };
}

export default function PersonalAssistantPanel({ aberto, onClose }: Props) {
  const [agenda, setAgenda] = useState<Agendamento[] | null>(null);
  const [proximoAlvo, setProximoAlvo] = useState<ProximoLocal | null>(null);
  const [mobilidade, setMobilidade] = useState<PreferenciaMobilidade | null>(null);
  const [configMapa, setConfigMapa] = useState<ConfiguracaoMapa | null>(null);
  const [deslocamento, setDeslocamento] = useState<Deslocamento | null>(null);
  const [origem, setOrigem] = useState<{ latitude: number; longitude: number } | null>(null);
  const [resumoEmail, setResumoEmail] = useState<ResumoEmail | null | undefined>(undefined);
  const [carregandoRota, setCarregandoRota] = useState(false);
  const [erroRota, setErroRota] = useState("");

  useEffect(() => {
    if (!aberto) return;
    let ativo = true;
    setResumoEmail(undefined);
    Promise.all([
      api.get<AgendamentoIntegrado[]>("/agenda/appointments").then((items) => items.map(normalizarAgendamento)).catch(() => [] as Agendamento[]),
      api.post<ProximoLocal | null>("/agenda/mobility/prepare-next-target", {}).catch(() => api.get<ProximoLocal | null>("/agenda/mobility/next-target")).catch(() => null),
      api.get<PreferenciaMobilidade>("/agenda/mobility/preferences").catch(() => null),
      api.get<ConfiguracaoMapa>("/agenda/mobility/map-config").catch(() => null),
      api.get<ResumoEmail>("/email/resumo").catch(() => null),
    ]).then(([compromissos, alvo, preferencias, mapa, email]) => {
      if (!ativo) return;
      setAgenda(compromissos); setProximoAlvo(alvo); setMobilidade(preferencias); setConfigMapa(mapa); setResumoEmail(email);
    });
    return () => { ativo = false; };
  }, [aberto]);

  useEffect(() => {
    if (!aberto) return;
    function escapar(evento: KeyboardEvent) { if (evento.key === "Escape") onClose(); }
    document.addEventListener("keydown", escapar);
    return () => document.removeEventListener("keydown", escapar);
  }, [aberto, onClose]);

  const hoje = useMemo(() => {
    const agora = new Date();
    return (agenda ?? []).filter((item) => item.status !== "cancelado" && mesmoDia(new Date(item.scheduled_at), agora)).sort((a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at));
  }, [agenda]);
  const proximoAgenda = useMemo(() => {
    const agora = Date.now();
    return (agenda ?? []).filter((item) => item.status !== "cancelado" && +new Date(item.scheduled_at) >= agora).sort((a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at))[0];
  }, [agenda]);
  const proximo = useMemo<Agendamento | undefined>(() => proximoAlvo ? ({
    id: proximoAlvo.appointment_id || 0,
    patient_name: proximoAlvo.title || proximoAlvo.location?.name || proximoAlvo.service_name || null,
    scheduled_at: proximoAlvo.starts_at,
    appointment_type: proximoAlvo.service_name || "Compromisso",
    status: "confirmado",
  }) : proximoAgenda, [proximoAlvo, proximoAgenda]);
  const proximoLocal = proximoAlvo;
  const targetKey = proximoLocal?.target_key || null;
  const rota = deslocamento?.destination?.target_key === targetKey ? deslocamento?.routes?.[0] ?? null : null;
  const saidaRecomendada = proximoLocal && rota && proximo ? new Date(new Date(proximo.scheduled_at).getTime() - (rota.duration_seconds + proximoLocal.arrival_buffer_minutes * 60) * 1000) : null;
  const chegadaPrevista = rota ? new Date((deslocamento?.updated_at ? new Date(deslocamento.updated_at).getTime() : Date.now()) + rota.duration_seconds * 1000) : null;
  const destinoMapeavel = Boolean(proximoLocal?.location && proximoLocal.location.latitude != null && proximoLocal.location.longitude != null);
  const provedorMapa = deslocamento?.provider || configMapa?.provider;

  function atualizarDeslocamento() {
    setErroRota("");
    if (!mobilidade) { setErroRota("Não foi possível confirmar a autorização de mobilidade. Abra a Agenda e revise essa preferência antes de usar sua localização."); return; }
    if (!mobilidade.enabled) { setErroRota("Ative a mobilidade na Agenda antes de solicitar sua localização."); return; }
    if (!proximo) { setErroRota("Nenhum compromisso futuro encontrado."); return; }
    if (!proximoLocal || !targetKey) { setErroRota("O compromisso exibido não possui um destino vinculável. Complete o local na Agenda."); return; }
    if (!proximoLocal.location) { setErroRota("Este compromisso ainda não possui local definido."); return; }
    if (!navigator.geolocation) { setErroRota("Localização não disponível neste dispositivo."); return; }
    setCarregandoRota(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const ponto = { latitude: position.coords.latitude, longitude: position.coords.longitude };
        setOrigem(ponto);
        api.post<Deslocamento>("/agenda/mobility/commute-target", { ...ponto, target_key: targetKey }).then((resultado) => {
          if (resultado.destination?.target_key !== targetKey) {
            setDeslocamento(null);
            setErroRota("A rota retornada não corresponde ao compromisso exibido e foi descartada.");
            return;
          }
          setDeslocamento(resultado);
          setProximoAlvo(resultado.destination);
          if (!resultado.routes?.length && resultado.status !== "ok") {
            setErroRota(resultado.status === "destination_not_geocoded"
              ? "Não foi possível localizar com segurança o endereço. Complete o local na Agenda."
              : resultado.status === "destination_without_location"
                ? "Este compromisso ainda não possui local definido."
                : "Não foi possível calcular uma rota utilizável agora.");
          }
        }).catch(() => setErroRota("Não foi possível calcular o deslocamento agora.")).finally(() => setCarregandoRota(false));
      },
      (erro) => { setCarregandoRota(false); setErroRota(erro.code === erro.PERMISSION_DENIED ? "Permissão de localização bloqueada neste dispositivo." : "Localização temporariamente indisponível."); },
      { enableHighAccuracy: false, timeout: 12000, maximumAge: 120000 },
    );
  }

  if (!aberto) return null;
  const emailsPendentes = resumoEmail?.pendentes ?? [];

  return <>
    <div className="cos-assistant-backdrop is-visible" onClick={onClose} aria-hidden="true" />
    <aside className="cos-assistant-panel is-open" aria-label="Assistente Pessoal CorVIA">
      <header className="cos-assistant-panel__head"><div className="cos-assistant-panel__brand"><span className="cos-assistant-panel__spark">✦</span><div><small>Seu copiloto de rotina</small><strong>Assistente Pessoal</strong></div></div><button type="button" onClick={onClose} aria-label="Fechar Assistente Pessoal"><Icone nome="fechar" /></button></header>
      <div className="cos-assistant-panel__body">
        <section className="cos-assistant-briefing">
          <p className="eyebrow">Seu dia</p>
          <div className="cos-assistant-briefing__summary"><div><strong>{agenda === null ? "—" : hoje.length}</strong><span>compromissos hoje</span></div><div><strong>{proximo ? new Date(proximo.scheduled_at).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }) : "Livre"}</strong><span>próximo horário</span></div></div>
          {proximo ? <div className="cos-assistant-next"><span><Icone nome="agenda" /></span><div><small>Próximo compromisso</small><strong>{proximo.patient_name || tipoCompromisso(proximo.appointment_type)}</strong><p>{tipoCompromisso(proximo.appointment_type)} · {new Date(proximo.scheduled_at).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}</p></div></div> : agenda === null ? <p className="cos-assistant-state">Carregando sua agenda…</p> : <p className="cos-assistant-state">Nenhum compromisso futuro encontrado na agenda.</p>}
          <Link to="/agenda" onClick={onClose} className="cos-assistant-link">Abrir agenda completa <Icone nome="seta" /></Link>
        </section>
        <section className="cos-assistant-card cos-assistant-card--commute">
          <div className="cos-assistant-card__head"><span><Icone nome="rota" /></span><div><p className="eyebrow">Próximo Deslocamento</p><h3>Chegue no tempo certo</h3></div></div>
          {proximoLocal?.location && proximo ? <>
            <div className="cos-assistant-destination"><Icone nome="pin" /><div><small>Destino do compromisso</small><strong>{proximoLocal.location.name}</strong><span>{tipoCompromisso(proximo.appointment_type)} às {new Date(proximo.scheduled_at).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}</span></div></div>
            {destinoMapeavel && <div className="cos-assistant-map"><MapaDeslocamento rotas={deslocamento?.routes || []} origem={origem} destino={{ name: proximoLocal.location.name, latitude: proximoLocal.location.latitude, longitude: proximoLocal.location.longitude }} provider={provedorMapa} updatedAt={deslocamento?.updated_at} googleMapsApiKey={configMapa?.api_key} /></div>}
            {rota ? <div className="cos-assistant-route cos-assistant-route--board"><div><small>Sair às</small><strong>{saidaRecomendada?.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }) || "—"}</strong></div><div><small>Chegada prevista</small><strong>{chegadaPrevista?.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }) || "—"}</strong></div><div><small>Trânsito</small><strong>{rota.congestion || "atualizado"}</strong></div></div> : <button type="button" className="cos-assistant-route-button" onClick={atualizarDeslocamento} disabled={carregandoRota}><Icone nome="rota" /> {carregandoRota ? "Calculando rota…" : destinoMapeavel ? "Calcular rota a partir de onde estou" : "Localizar destino e calcular rota"}</button>}
            {erroRota && <p className="cos-assistant-warning">{erroRota}</p>}
            {!mobilidade?.enabled && <p className="cos-assistant-hint">Você pode ativar a mobilidade na Agenda para deixar este briefing mais automático.</p>}
          </> : <div className="cos-assistant-empty"><strong>{proximo ? "Este compromisso não possui um destino vinculável." : "Nenhum compromisso futuro encontrado."}</strong><small>{proximo ? "Complete o endereço/local desse mesmo compromisso na Agenda. O CorVIA não substitui por outro destino." : "Cadastre seu próximo compromisso na Agenda para receber assistência de deslocamento."}</small><Link to="/agenda" onClick={onClose}>Abrir Agenda <Icone nome="seta" /></Link></div>}
        </section>
        <section className="cos-assistant-card"><div className="cos-assistant-card__head"><span><Icone nome="mail" /></span><div><p className="eyebrow">Comunicação</p><h3>O que merece sua atenção</h3></div></div>{resumoEmail === undefined ? <p className="cos-assistant-state">Verificando seu CorVIA Mail…</p> : resumoEmail?.disponivel ? <><div className="cos-assistant-briefing__summary"><div><strong>{emailsPendentes.length}</strong><span>{emailsPendentes.length === 1 ? "mensagem pendente" : "mensagens pendentes"}</span></div><div><strong>{resumoEmail.email_address ? "Ativo" : "—"}</strong><span>CorVIA Mail</span></div></div>{emailsPendentes.slice(0, 2).map((mensagem, indice) => <div className="cos-assistant-next" key={mensagem.messageId ?? mensagem.id ?? `${mensagem.subject}-${indice}`}><span><Icone nome="mail" /></span><div><small>{mensagem.fromAddress ?? mensagem.sender ?? "Mensagem recebida"}{dataCurtaDoEmail(mensagem) ? ` · ${dataCurtaDoEmail(mensagem)}` : ""}</small><strong>{mensagem.subject || "Sem assunto"}</strong></div></div>)}{emailsPendentes.length === 0 && <p className="cos-assistant-state">Nenhuma mensagem pendente no resumo atual.</p>}<Link to="/corvia-mail" onClick={onClose} className="cos-assistant-link">Abrir CorVIA Mail <Icone nome="seta" /></Link></> : <div className="cos-assistant-empty"><strong>Resumo do Mail indisponível agora.</strong><small>O Assistente continua útil para agenda e deslocamento sem depender do e-mail.</small><Link to="/corvia-mail" onClick={onClose}>Abrir CorVIA Mail <Icone nome="seta" /></Link></div>}</section>
        <section className="cos-assistant-card"><div className="cos-assistant-card__head"><span><Icone nome="check" /></span><div><p className="eyebrow">Próximos passos</p><h3>Continue sem perder contexto</h3></div></div><div className="cos-assistant-actions"><Link to="/documentos" onClick={onClose}><Icone nome="documento" /><span><strong>Documentos</strong><small>Atestados, relatórios e solicitações</small></span><Icone nome="seta" /></Link><Link to="/corvia-mail" onClick={onClose}><Icone nome="mail" /><span><strong>CorVIA Mail</strong><small>Comunicação profissional</small></span><Icone nome="seta" /></Link><Link to="/favoritos" onClick={onClose}><Icone nome="favorito" /><span><strong>Favoritos</strong><small>Retome conteúdo salvo</small></span><Icone nome="seta" /></Link></div></section>
      </div>
      <footer className="cos-assistant-panel__footer"><Link to="/assistente" onClick={onClose}><span className="cos-assistant-panel__spark">✦</span><span><strong>Precisa pensar um caso?</strong><small>Abra o Assistente para assistência clínica contextual.</small></span><Icone nome="seta" /></Link></footer>
    </aside>
  </>;
}
