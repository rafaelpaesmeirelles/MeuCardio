import { useEffect, useState } from "react";
import { api, ApiError } from "../lib/api";
import Round from "./Round";

type PacienteResumo = {
  id: number;
  record_number: string;
  initials: string;
  bed: string | null;
  unit: string | null;
  archived: boolean;
  archived_at: string | null;
  archive_reason: string | null;
};

export default function RoundGerenciavel() {
  const [ativos, setAtivos] = useState<PacienteResumo[]>([]);
  const [arquivados, setArquivados] = useState<PacienteResumo[]>([]);
  const [mostraArquivados, setMostraArquivados] = useState(false);
  const [processando, setProcessando] = useState<number | null>(null);
  const [erro, setErro] = useState("");

  async function carregar() {
    try {
      const [listaAtiva, listaArquivada] = await Promise.all([
        api.get<PacienteResumo[]>("/round/patients"),
        api.get<PacienteResumo[]>("/round/patients?archived=true"),
      ]);
      setAtivos(listaAtiva);
      setArquivados(listaArquivada);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível carregar o gerenciamento do round.");
    }
  }

  useEffect(() => { carregar(); }, []);

  async function remover(paciente: PacienteResumo) {
    const confirmar = window.confirm(
      `Remover ${paciente.initials} (prontuário ${paciente.record_number}) do round?\n\n` +
      "O registro será arquivado, não apagado, e poderá ser restaurado."
    );
    if (!confirmar) return;
    const motivo = window.prompt("Motivo opcional para o arquivamento:") ?? "";
    setProcessando(paciente.id);
    setErro("");
    try {
      await api.delete(`/round/patients/${paciente.id}`, { reason: motivo.trim() || null });
      await carregar();
      window.location.reload();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível remover o paciente do round.");
    } finally {
      setProcessando(null);
    }
  }

  async function restaurar(paciente: PacienteResumo) {
    setProcessando(paciente.id);
    setErro("");
    try {
      await api.post(`/round/patients/${paciente.id}/restore`, {});
      await carregar();
      window.location.reload();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível restaurar o paciente.");
    } finally {
      setProcessando(null);
    }
  }

  return (
    <>
      <section className="cartao" style={{ marginBottom: "1rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
          <div>
            <p className="eyebrow" style={{ margin: 0 }}>Gerenciar round</p>
            <strong>{ativos.length} paciente(s) ativo(s)</strong>
          </div>
          <button
            type="button"
            className="botao botao--secundario"
            onClick={() => setMostraArquivados((valor) => !valor)}
          >
            {mostraArquivados ? "Ocultar arquivados" : `Arquivados (${arquivados.length})`}
          </button>
        </div>

        {erro && <p role="alert" style={{ color: "var(--alerta)" }}>{erro}</p>}

        {ativos.length > 0 && (
          <div style={{ display: "grid", gap: "0.45rem", marginTop: "0.8rem" }}>
            {ativos.map((paciente) => (
              <div key={paciente.id} style={{ display: "flex", alignItems: "center", gap: 10, borderTop: "1px solid var(--linha)", paddingTop: "0.45rem" }}>
                <span className="dado">{paciente.bed || "—"}</span>
                <strong>{paciente.initials}</strong>
                <span style={{ color: "var(--texto-secundario)", fontSize: "0.84rem" }}>
                  {paciente.unit || "sem unidade"} · prontuário {paciente.record_number}
                </span>
                <button
                  type="button"
                  className="botao botao--secundario"
                  style={{ marginLeft: "auto", padding: "0.3rem 0.65rem", fontSize: "0.78rem" }}
                  disabled={processando === paciente.id}
                  onClick={() => remover(paciente)}
                >
                  {processando === paciente.id ? "Removendo…" : "Excluir do round"}
                </button>
              </div>
            ))}
          </div>
        )}

        {mostraArquivados && (
          <div style={{ marginTop: "1rem" }}>
            <p className="eyebrow">Pacientes arquivados</p>
            {arquivados.length === 0 ? (
              <p style={{ color: "var(--texto-secundario)" }}>Nenhum paciente arquivado.</p>
            ) : arquivados.map((paciente) => (
              <div key={paciente.id} style={{ display: "flex", alignItems: "center", gap: 10, borderTop: "1px solid var(--linha)", padding: "0.5rem 0" }}>
                <strong>{paciente.initials}</strong>
                <span style={{ color: "var(--texto-secundario)", fontSize: "0.84rem" }}>
                  prontuário {paciente.record_number}
                  {paciente.archive_reason ? ` · ${paciente.archive_reason}` : ""}
                </span>
                <button
                  type="button"
                  className="botao botao--secundario"
                  style={{ marginLeft: "auto", padding: "0.3rem 0.65rem", fontSize: "0.78rem" }}
                  disabled={processando === paciente.id}
                  onClick={() => restaurar(paciente)}
                >
                  Restaurar
                </button>
              </div>
            ))}
          </div>
        )}
      </section>

      <Round />
    </>
  );
}
