import { useEffect, useState } from "react";
import { api } from "../lib/api";

type Evento = { tipo: string; data: string; titulo: string; resumo: string };

const ICONE: Record<string, string> = {
  evolucao: "📝", auxilio_ia: "🤖", prescricao: "💊", documento: "📄", consulta: "📅",
};

export default function PatientTimeline({ patientId }: { patientId: number }) {
  const [estado, setEstado] = useState<{ patientId: number; eventos: Evento[] | null; erro: string }>({ patientId, eventos: null, erro: "" });
  const [tentativa, setTentativa] = useState(0);

  useEffect(() => {
    let ativo = true;
    setEstado({ patientId, eventos: null, erro: "" });
    api.get<Evento[]>(`/timeline/patient/${patientId}`)
      .then((eventos) => { if (ativo) setEstado({ patientId, eventos, erro: "" }); })
      .catch(() => {
        if (ativo) setEstado({ patientId, eventos: null, erro: "Não foi possível carregar o histórico deste paciente. Tente novamente." });
      });
    return () => { ativo = false; };
  }, [patientId, tentativa]);

  // Do not paint another patient's history, even before effect cleanup runs.
  const { eventos, erro } = estado.patientId === patientId ? estado : { eventos: null, erro: "" };

  return (
    <div className="cartao" style={{ background: "var(--fundo)" }}>
      <p className="eyebrow patient-round-heading" style={{ margin: 0 }}>Timeline</p>
      {erro ? (
        <>
          <p role="alert" style={{ color: "var(--alerta)" }}>{erro}</p>
          <button className="botao botao--secundario" onClick={() => setTentativa((valor) => valor + 1)}>Recarregar histórico</button>
        </>
      ) : eventos === null ? (
        <p style={{ fontSize: "0.86rem", color: "var(--texto-secundario)" }}>Carregando…</p>
      ) : eventos.length === 0 ? (
        <p className="patient-round-empty" style={{ fontSize: "0.86rem", color: "var(--texto-secundario)" }}>Nenhum evento registrado ainda.</p>
      ) : (
        <div style={{ marginTop: "0.5rem" }}>
          {eventos.map((e, i) => (
            <div key={i} style={{
              display: "flex", gap: 10, padding: "0.5rem 0",
              borderBottom: i < eventos.length - 1 ? "1px solid var(--borda)" : "none",
            }}>
              <span style={{ fontSize: "1.1rem" }}>{ICONE[e.tipo] ?? "•"}</span>
              <div>
                <p style={{ margin: 0, fontSize: "0.88rem", fontWeight: 600 }}>{e.titulo}</p>
                <p style={{ margin: 0, fontSize: "0.8rem", color: "var(--texto-secundario)" }}>
                  {new Date(e.data).toLocaleString("pt-BR")}
                </p>
                {e.resumo && e.resumo !== "—" && (
                  <p style={{ margin: "0.2rem 0 0", fontSize: "0.84rem" }}>{e.resumo}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
