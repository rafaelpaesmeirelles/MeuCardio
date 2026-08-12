import { useEffect, useState } from "react";
import Icone from "../components/Icone";
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
    <section className="ccc-patient-command">
      <header className="ccc-patient-command__header">
        <div className="ccc-patient-command__identity">
          <span className="ccc-patient-command__icon"><Icone nome="pacientes" /></span>
          <div>
            <p className="eyebrow">Patient Command Center</p>
            <h1>Pacientes e Round</h1>
            <p>Contexto clínico, continuidade e ações do round em uma única superfície.</p>
          </div>
        </div>
        <div className="ccc-patient-command__metrics" aria-label="Resumo do round">
          <span><strong>{ativos.length}</strong><small>ativos</small></span>
          <span><strong>{arquivados.length}</strong><small>arquivados</small></span>
        </div>
      </header>

      <section className="ccc-patient-command__manager" aria-label="Gerenciar pacientes do round">
        <div className="ccc-patient-command__manager-head">
          <div>
            <p className="eyebrow">Gerenciar round</p>
            <strong>Pacientes ativos agora</strong>
          </div>
          <button
            type="button"
            className="botao botao--secundario"
            onClick={() => setMostraArquivados((valor) => !valor)}
          >
            <Icone nome="pacientes" />
            {mostraArquivados ? "Ocultar arquivados" : `Arquivados (${arquivados.length})`}
          </button>
        </div>

        {erro && <p role="alert" className="ccc-patient-command__error">{erro}</p>}

        {ativos.length > 0 && (
          <div className="ccc-patient-command__active-list">
            {ativos.map((paciente) => (
              <article key={paciente.id} className="ccc-patient-command__active-row">
                <span className="ccc-patient-command__bed">{paciente.bed || "—"}</span>
                <span className="ccc-patient-command__patient">
                  <strong>{paciente.initials}</strong>
                  <small>{paciente.unit || "sem unidade"} · prontuário {paciente.record_number}</small>
                </span>
                <button
                  type="button"
                  className="ccc-patient-command__archive"
                  disabled={processando === paciente.id}
                  onClick={() => remover(paciente)}
                >
                  {processando === paciente.id ? "Arquivando…" : "Arquivar"}
                </button>
              </article>
            ))}
          </div>
        )}

        {ativos.length === 0 && <p className="ccc-patient-command__empty">Nenhum paciente ativo no round.</p>}

        {mostraArquivados && (
          <div className="ccc-patient-command__archive-list">
            <p className="eyebrow">Arquivo do round</p>
            {arquivados.length === 0 ? (
              <p className="ccc-patient-command__empty">Nenhum paciente arquivado.</p>
            ) : arquivados.map((paciente) => (
              <article key={paciente.id} className="ccc-patient-command__active-row is-archived">
                <span className="ccc-patient-command__bed">{paciente.bed || "—"}</span>
                <span className="ccc-patient-command__patient">
                  <strong>{paciente.initials}</strong>
                  <small>prontuário {paciente.record_number}{paciente.archive_reason ? ` · ${paciente.archive_reason}` : ""}</small>
                </span>
                <button
                  type="button"
                  className="ccc-patient-command__archive"
                  disabled={processando === paciente.id}
                  onClick={() => restaurar(paciente)}
                >
                  Restaurar
                </button>
              </article>
            ))}
          </div>
        )}
      </section>

      <div className="ccc-patient-command__clinical">
        <Round />
      </div>
    </section>
  );
}
