import { useEffect, useState } from "react";
import { api } from "../lib/api";

type Evento = { tipo: string; data: string; titulo: string; resumo: string };

const ICONE: Record<string, string> = {
  evolucao: "📝", auxilio_ia: "🤖", prescricao: "💊", documento: "📄", consulta: "📅",
};

export default function PatientTimeline({ patientId }: { patientId: number }) {
  const [eventos, setEventos] = useState<Evento[] | null>(null);

  useEffect(() => {
    api.get<Evento[]>(`/timeline/patient/${patientId}`).then(setEventos);
  }, [patientId]);

  return (
    <div className="cartao" style={{ background: "var(--cinza-fundo)" }}>
      <p className="eyebrow" style={{ margin: 0 }}>Timeline</p>
      {eventos === null ? (
        <p style={{ fontSize: "0.86rem", color: "var(--cinza-texto)" }}>Carregando…</p>
      ) : eventos.length === 0 ? (
        <p style={{ fontSize: "0.86rem", color: "var(--cinza-texto)" }}>Nenhum evento registrado ainda.</p>
      ) : (
        <div style={{ marginTop: "0.5rem" }}>
          {eventos.map((e, i) => (
            <div key={i} style={{
              display: "flex", gap: 10, padding: "0.5rem 0",
              borderBottom: i < eventos.length - 1 ? "1px solid var(--cinza-borda)" : "none",
            }}>
              <span style={{ fontSize: "1.1rem" }}>{ICONE[e.tipo] ?? "•"}</span>
              <div>
                <p style={{ margin: 0, fontSize: "0.88rem", fontWeight: 600 }}>{e.titulo}</p>
                <p style={{ margin: 0, fontSize: "0.8rem", color: "var(--cinza-texto)" }}>
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
