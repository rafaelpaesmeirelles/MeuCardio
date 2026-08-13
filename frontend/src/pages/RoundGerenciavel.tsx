import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import Icone from "../components/Icone";
import { api, ApiError } from "../lib/api";
import Round from "./Round";

type ProblemaResumo = { id?: number; label: string; status?: string };
type PacienteResumo = {
  id: number;
  record_number: string;
  initials: string;
  bed: string | null;
  unit: string | null;
  archived: boolean;
  archived_at: string | null;
  archive_reason: string | null;
  plan?: string | null;
  pending?: string[];
  medications?: string[];
  problems?: ProblemaResumo[];
  labs?: Record<string, string | number>;
  diagnostic_hypothesis?: string[];
  chief_complaint?: string | null;
};

function valorExame([nome, valor]: [string, string | number]) {
  return <span><strong>{nome}</strong><small>{String(valor)}</small></span>;
}

export default function RoundGerenciavel() {
  const [ativos, setAtivos] = useState<PacienteResumo[]>([]);
  const [arquivados, setArquivados] = useState<PacienteResumo[]>([]);
  const [selecionadoId, setSelecionadoId] = useState<number | null>(null);
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
      setSelecionadoId((atual) => atual && listaAtiva.some((p) => p.id === atual) ? atual : listaAtiva[0]?.id ?? null);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível carregar o gerenciamento do round.");
    }
  }

  useEffect(() => { carregar(); }, []);

  const selecionado = useMemo(() => ativos.find((p) => p.id === selecionadoId) ?? null, [ativos, selecionadoId]);
  const problemas = (selecionado?.problems ?? []).filter((item) => item.status !== "resolvido").slice(0, 4);
  const exames = Object.entries(selecionado?.labs ?? {}).slice(0, 4);
  const medicamentos = (selecionado?.medications ?? []).slice(0, 5);

  async function remover(paciente: PacienteResumo) {
    const confirmar = window.confirm(`Remover ${paciente.initials} (prontuário ${paciente.record_number}) do round?\n\nO registro será arquivado, não apagado, e poderá ser restaurado.`);
    if (!confirmar) return;
    const motivo = window.prompt("Motivo opcional para o arquivamento:") ?? "";
    setProcessando(paciente.id); setErro("");
    try {
      await api.delete(`/round/patients/${paciente.id}`, { reason: motivo.trim() || null });
      await carregar();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível remover o paciente do round.");
    } finally { setProcessando(null); }
  }

  async function restaurar(paciente: PacienteResumo) {
    setProcessando(paciente.id); setErro("");
    try {
      await api.post(`/round/patients/${paciente.id}/restore`, {});
      await carregar();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível restaurar o paciente.");
    } finally { setProcessando(null); }
  }

  return (
    <section className="ccc-patient-command ccc-patient-command--board">
      {selecionado ? (
        <section className="pc-command" aria-label={`Patient Command Center de ${selecionado.initials}`}>
          <header className="pc-command__header">
            <span className="pc-command__avatar">{selecionado.initials}</span>
            <div className="pc-command__identity">
              <h1>{selecionado.initials}</h1>
              <p>{selecionado.unit || "Unidade não informada"}{selecionado.bed ? ` · Leito ${selecionado.bed}` : ""}</p>
              <small>Prontuário {selecionado.record_number}</small>
            </div>
            <div className="pc-command__quick-icons">
              <Link to="/receituario" aria-label="Prescrever"><Icone nome="prescricao" /></Link>
              <Link to="/documentos" aria-label="Documento"><Icone nome="documento" /></Link>
              <Link to="/agenda" aria-label="Agendar"><Icone nome="agenda" /></Link>
              <button type="button" onClick={() => document.getElementById("pc-round-editor")?.scrollIntoView({ behavior: "smooth" })} aria-label="Abrir prontuário completo"><Icone nome="mais" /></button>
            </div>
          </header>

          <nav className="pc-command__tabs" aria-label="Seções do paciente">
            <button className="is-active" type="button">Resumo</button><button type="button" onClick={() => document.getElementById("pc-round-editor")?.scrollIntoView({ behavior: "smooth" })}>Timeline</button><button type="button" onClick={() => document.getElementById("pc-meds")?.scrollIntoView({ behavior: "smooth" })}>Medicamentos</button><button type="button" onClick={() => document.getElementById("pc-exames")?.scrollIntoView({ behavior: "smooth" })}>Exames</button><Link to="/receituario">Prescrições</Link><Link to="/documentos">Documentos</Link>
          </nav>

          <div className="pc-command__body">
            <main className="pc-command__summary">
              <article className="pc-command__clinical-summary">
                <small>Resumo clínico</small>
                <div className="pc-command__columns">
                  <section><span>Diagnósticos ativos</span>{problemas.length ? problemas.map((p, i) => <strong key={`${i}-${p.label}`}>{p.label}</strong>) : (selecionado.diagnostic_hypothesis ?? []).slice(0,3).map((h) => <strong key={h}>{h}</strong>)}{!problemas.length && !(selecionado.diagnostic_hypothesis ?? []).length && <strong>Sem diagnóstico estruturado</strong>}</section>
                  <section id="pc-exames"><span>Últimos exames</span>{exames.length ? exames.map(valorExame) : <strong>Sem exames estruturados</strong>}</section>
                </div>
              </article>
              <article id="pc-meds" className="pc-command__meds"><small>Medicamentos em uso</small>{medicamentos.length ? medicamentos.map((med) => <span key={med}>{med}</span>) : <span>Sem medicamentos estruturados</span>}</article>
            </main>

            <aside className="pc-command__actions">
              <small>Ações rápidas</small>
              <Link to="/receituario"><Icone nome="prescricao" /><span>Prescrever</span></Link>
              <Link to="/documentos"><Icone nome="clinica" /><span>Solicitar exame</span></Link>
              <Link to="/documentos"><Icone nome="documento" /><span>Documento</span></Link>
              <Link to="/agenda"><Icone nome="agenda" /><span>Agendar retorno</span></Link>
              <button type="button" onClick={() => document.getElementById("pc-round-editor")?.scrollIntoView({ behavior: "smooth" })}><Icone nome="check" /><span>Ver plano terapêutico</span></button>
            </aside>
          </div>
        </section>
      ) : (
        <header className="ccc-patient-command__header"><div className="ccc-patient-command__identity"><span className="ccc-patient-command__icon"><Icone nome="pacientes" /></span><div><p className="eyebrow">Patient Command Center</p><h1>Pacientes e Round</h1><p>Adicione o primeiro paciente para abrir o command center.</p></div></div></header>
      )}

      <section className="ccc-patient-command__manager" aria-label="Gerenciar pacientes do round">
        <div className="ccc-patient-command__manager-head">
          <div><p className="eyebrow">Gerenciar round</p><strong>Pacientes ativos agora</strong></div>
          <button type="button" className="botao botao--secundario" onClick={() => setMostraArquivados((valor) => !valor)}><Icone nome="pacientes" />{mostraArquivados ? "Ocultar arquivados" : `Arquivados (${arquivados.length})`}</button>
        </div>

        {erro && <p role="alert" className="ccc-patient-command__error">{erro}</p>}

        {ativos.length > 0 && <div className="ccc-patient-command__active-list">{ativos.map((paciente) => <article key={paciente.id} className={`ccc-patient-command__active-row${paciente.id === selecionadoId ? " is-selected" : ""}`}>
          <button type="button" className="ccc-patient-command__select" onClick={() => setSelecionadoId(paciente.id)} aria-label={`Abrir command center de ${paciente.initials}`}><span className="ccc-patient-command__bed">{paciente.bed || "—"}</span><span className="ccc-patient-command__patient"><strong>{paciente.initials}</strong><small>{paciente.unit || "sem unidade"} · prontuário {paciente.record_number}</small></span></button>
          <button type="button" className="ccc-patient-command__archive" disabled={processando === paciente.id} onClick={() => remover(paciente)}>{processando === paciente.id ? "Arquivando…" : "Arquivar"}</button>
        </article>)}</div>}

        {ativos.length === 0 && <p className="ccc-patient-command__empty">Nenhum paciente ativo no round.</p>}

        {mostraArquivados && <div className="ccc-patient-command__archive-list"><p className="eyebrow">Arquivo do round</p>{arquivados.length === 0 ? <p className="ccc-patient-command__empty">Nenhum paciente arquivado.</p> : arquivados.map((paciente) => <article key={paciente.id} className="ccc-patient-command__active-row is-archived"><span className="ccc-patient-command__bed">{paciente.bed || "—"}</span><span className="ccc-patient-command__patient"><strong>{paciente.initials}</strong><small>prontuário {paciente.record_number}{paciente.archive_reason ? ` · ${paciente.archive_reason}` : ""}</small></span><button type="button" className="ccc-patient-command__archive" disabled={processando === paciente.id} onClick={() => restaurar(paciente)}>Restaurar</button></article>)}</div>}
      </section>

      <div id="pc-round-editor" className="ccc-patient-command__clinical"><Round /></div>
    </section>
  );
}
