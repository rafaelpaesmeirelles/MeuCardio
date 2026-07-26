import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Carregando, Vazio } from "../components/Estado";

type Agendamento = {
  id: number; patient_id: number | null; patient_name: string | null;
  scheduled_at: string; duration_minutes: number; appointment_type: string;
  status: string; notes: string | null;
};

const RÓTULO_TIPO: Record<string, string> = { consulta: "Consulta", retorno: "Retorno", exame: "Exame", outro: "Outro" };
const RÓTULO_STATUS: Record<string, string> = { confirmado: "Confirmado", cancelado: "Cancelado", realizado: "Realizado", faltou: "Faltou" };
const COR_STATUS: Record<string, string> = {
  confirmado: "var(--bordo)", cancelado: "var(--cinza-texto)", realizado: "#2e7d52", faltou: "var(--alerta)",
};

function agora() {
  const d = new Date();
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
  return d.toISOString().slice(0, 16);
}

export default function Agenda() {
  const [lista, setLista] = useState<Agendamento[] | null>(null);
  const [novo, setNovo] = useState<{
    patient_name_temp: string; patient_phone_temp: string; scheduled_at: string;
    duration_minutes: number; appointment_type: string; notes: string;
  } | null>(null);
  const [salvando, setSalvando] = useState(false);

  const recarregar = () => api.get<Agendamento[]>("/appointments").then(setLista);
  useEffect(() => { recarregar(); }, []);

  async function salvar() {
    if (!novo?.patient_name_temp || !novo.scheduled_at) return;
    setSalvando(true);
    try {
      await api.post("/appointments", {
        ...novo, scheduled_at: new Date(novo.scheduled_at).toISOString(),
      });
      setNovo(null);
      recarregar();
    } finally {
      setSalvando(false);
    }
  }

  async function mudarStatus(id: number, status: string) {
    await api.patch(`/appointments/${id}`, { status });
    recarregar();
  }

  const porDia: Record<string, Agendamento[]> = {};
  (lista ?? []).forEach((a) => {
    const dia = new Date(a.scheduled_at).toLocaleDateString("pt-BR", { weekday: "short", day: "2-digit", month: "short" });
    (porDia[dia] ??= []).push(a);
  });

  return (
    <>
      <p className="eyebrow">Agenda</p>
      <h1>Consultas</h1>

      <button className="botao" style={{ marginTop: "0.5rem" }}
              onClick={() => setNovo({ patient_name_temp: "", patient_phone_temp: "", scheduled_at: agora(), duration_minutes: 30, appointment_type: "consulta", notes: "" })}>
        + Novo agendamento
      </button>

      {novo && (
        <div className="cartao" style={{ marginTop: "0.8rem" }}>
          <label>Nome do paciente</label>
          <input value={novo.patient_name_temp} onChange={(e) => setNovo({ ...novo, patient_name_temp: e.target.value })} />
          <label style={{ marginTop: "0.5rem" }}>Telefone (opcional)</label>
          <input value={novo.patient_phone_temp} onChange={(e) => setNovo({ ...novo, patient_phone_temp: e.target.value })} />
          <label style={{ marginTop: "0.5rem" }}>Data e hora</label>
          <input type="datetime-local" value={novo.scheduled_at} onChange={(e) => setNovo({ ...novo, scheduled_at: e.target.value })} />
          <div className="grade" style={{ gridTemplateColumns: "1fr 1fr", gap: "0.5rem", marginTop: "0.5rem" }}>
            <div>
              <label>Duração (min)</label>
              <input type="number" value={novo.duration_minutes}
                     onChange={(e) => setNovo({ ...novo, duration_minutes: Number(e.target.value) })} />
            </div>
            <div>
              <label>Tipo</label>
              <select value={novo.appointment_type} onChange={(e) => setNovo({ ...novo, appointment_type: e.target.value })}>
                <option value="consulta">Consulta</option>
                <option value="retorno">Retorno</option>
                <option value="exame">Exame</option>
                <option value="outro">Outro</option>
              </select>
            </div>
          </div>
          <label style={{ marginTop: "0.5rem" }}>Observações</label>
          <textarea rows={2} value={novo.notes} onChange={(e) => setNovo({ ...novo, notes: e.target.value })} />
          <div style={{ display: "flex", gap: 8, marginTop: "0.6rem" }}>
            <button className="botao" onClick={salvar} disabled={salvando}>{salvando ? "Salvando…" : "Agendar"}</button>
            <button className="botao botao--secundario" onClick={() => setNovo(null)}>Cancelar</button>
          </div>
        </div>
      )}

      <div style={{ marginTop: "1.2rem" }}>
        {lista === null ? (
          <Carregando />
        ) : lista.length === 0 ? (
          <Vazio titulo="Nenhuma consulta agendada" acao="Crie o primeiro agendamento acima." />
        ) : (
          Object.entries(porDia).map(([dia, itens]) => (
            <div key={dia} style={{ marginBottom: "1rem" }}>
              <p className="eyebrow">{dia}</p>
              {itens.map((a) => (
                <div key={a.id} className="cartao" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.4rem" }}>
                  <div>
                    <strong>{new Date(a.scheduled_at).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}</strong>
                    {" — "}{a.patient_name} · {RÓTULO_TIPO[a.appointment_type]}
                    <div style={{ fontSize: "0.8rem", color: COR_STATUS[a.status] }}>{RÓTULO_STATUS[a.status]}</div>
                  </div>
                  <select value={a.status} onChange={(e) => mudarStatus(a.id, e.target.value)} style={{ width: "auto" }}>
                    <option value="confirmado">Confirmado</option>
                    <option value="realizado">Realizado</option>
                    <option value="cancelado">Cancelado</option>
                    <option value="faltou">Faltou</option>
                  </select>
                </div>
              ))}
            </div>
          ))
        )}
      </div>
    </>
  );
}
