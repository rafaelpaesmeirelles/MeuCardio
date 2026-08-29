import { useEffect, useState } from "react";
import { api, ApiError } from "../lib/api";
import { ClinicalPageHeader, ClinicalSection } from "../components/ClinicalCommandPrimitives";

type Analysis = {
  title?: string;
  document_type?: string;
  language?: string;
  summary_pt?: string;
  methodology_pt?: string;
  population_pt?: string;
  interventions_pt?: string;
  outcomes_pt?: string;
  results_pt?: string;
  limitations_pt?: string[];
  clinical_implications_pt?: string[];
  key_points_pt?: string[];
  topics?: string[];
  evidence_strength?: string;
  incorporation_reason_pt?: string;
};

type ScientificDocument = {
  id: number;
  title: string;
  document_type: string;
  language: string | null;
  doi: string | null;
  source_url: string | null;
  media_type: string;
  size_bytes: number;
  analysis_status: "pendente" | "processando" | "concluido" | "erro";
  analysis_error?: string | null;
  incorporation_recommended: boolean;
  incorporation_status: string;
  incorporated_document_id: number | null;
  summary_pt?: string | null;
  incorporation_reason_pt?: string | null;
  created_at: string;
  analysis?: Analysis;
  extracted_text?: string;
  translated_text?: string;
  translation_available?: boolean;
};

function erroTexto(error: unknown) {
  return error instanceof ApiError ? error.message : "Não foi possível concluir a operação.";
}

export default function ScientificDocumentAI() {
  const [items, setItems] = useState<ScientificDocument[]>([]);
  const [selected, setSelected] = useState<ScientificDocument | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  async function refresh() {
    const rows = await api.get<ScientificDocument[]>("/documentos-cientificos-ia");
    setItems(rows);
    if (selected) {
      const detail = await api.get<ScientificDocument>(`/documentos-cientificos-ia/${selected.id}`);
      setSelected(detail);
    }
  }

  useEffect(() => { void refresh(); }, []);

  async function upload() {
    if (!file) return;
    setBusy(true); setMessage("");
    try {
      const row = await api.upload<ScientificDocument>("/documentos-cientificos-ia", "arquivo", file);
      setFile(null);
      const detail = await api.get<ScientificDocument>(`/documentos-cientificos-ia/${row.id}`);
      setSelected(detail);
      await refresh();
      setMessage("Arquivo salvo de forma privada. Agora você pode solicitar a análise da IA.");
    } catch (error) { setMessage(erroTexto(error)); }
    finally { setBusy(false); }
  }

  async function analyze() {
    if (!selected) return;
    setBusy(true); setMessage("Analisando o documento e preparando a versão em português…");
    try {
      const detail = await api.post<ScientificDocument>(`/documentos-cientificos-ia/${selected.id}/analisar`);
      setSelected(detail);
      await refresh();
      setMessage("Análise concluída. O original permanece privado na sua biblioteca.");
    } catch (error) { setMessage(erroTexto(error)); }
    finally { setBusy(false); }
  }

  async function incorporate() {
    if (!selected) return;
    if (!window.confirm("Incorporar este documento ao acervo compartilhado do CorVIA e ao Tudo com Tudo?")) return;
    setBusy(true); setMessage("");
    try {
      const result = await api.uploadFormulario<{ incorporated: boolean; duplicate: boolean; slug?: string }>(
        `/documentos-cientificos-ia/${selected.id}/incorporar`, [], { confirm_incorporation: "true" },
      );
      await refresh();
      setMessage(result.duplicate ? "O documento já estava representado no acervo CorVIA." : "Documento incorporado ao acervo e conectado ao Tudo com Tudo.");
    } catch (error) { setMessage(erroTexto(error)); }
    finally { setBusy(false); }
  }

  async function openOriginal() {
    if (!selected) return;
    try {
      const blob = await api.blob(`/documentos-cientificos-ia/${selected.id}/arquivo`);
      const url = URL.createObjectURL(blob);
      window.open(url, "_blank", "noopener,noreferrer");
      window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch (error) { setMessage(erroTexto(error)); }
  }

  return (
    <div className="cc-page">
      <ClinicalPageHeader
        eyebrow="Conhecimento privado + IA clínica"
        title="Análise de documento científico"
        description="Envie diretriz, consenso, artigo, estudo ou evidência. O CorVIA preserva o original na sua biblioteca privada, prepara análise clínica em português e pede sua autorização antes de incorporar algo novo ao acervo compartilhado."
        icon="evidencia"
        meta={<><span className="selo">arquivo privado cifrado</span><span className="selo">incorporação somente com consentimento</span></>}
      />

      <ClinicalSection eyebrow="Novo documento" title="Carregar arquivo científico" description="PDF, DOCX, PPTX, TXT ou CSV · até 25 MB.">
        <div className="cc-filter-grid cc-filter-grid--3">
          <label style={{ gridColumn: "span 2" }}><span>Arquivo</span><input type="file" accept=".pdf,.docx,.pptx,.txt,.csv" onChange={(e) => setFile(e.target.files?.[0] ?? null)} /></label>
          <button className="btn primario" type="button" disabled={!file || busy} onClick={() => void upload()}>{busy ? "Processando…" : "Salvar na biblioteca"}</button>
        </div>
        {message && <p className="texto-secundario" role="status">{message}</p>}
      </ClinicalSection>

      <div className="cc-context-grid" style={{ alignItems: "start" }}>
        <ClinicalSection eyebrow="Sua biblioteca" title={`${items.length} documento(s)`}>
          <div className="lista-simples">
            {items.map((item) => (
              <button key={item.id} type="button" className="item-lista" onClick={async () => setSelected(await api.get<ScientificDocument>(`/documentos-cientificos-ia/${item.id}`))}>
                <strong>{item.title}</strong>
                <small>{item.document_type} · {item.analysis_status}{item.incorporation_status === "incorporado" ? " · incorporado" : ""}</small>
              </button>
            ))}
            {items.length === 0 && <p className="texto-secundario">Nenhum documento enviado ainda.</p>}
          </div>
        </ClinicalSection>

        <ClinicalSection eyebrow="Análise" title={selected?.title ?? "Selecione um documento"}>
          {!selected ? <p className="texto-secundario">Abra um item da sua biblioteca para analisar ou revisar depois.</p> : (
            <div className="stack">
              <div className="acoes-linha">
                <button className="btn" type="button" onClick={() => void openOriginal()}>Abrir original</button>
                <button className="btn primario" type="button" disabled={busy || selected.analysis_status === "processando"} onClick={() => void analyze()}>{selected.analysis_status === "concluido" ? "Reanalisar" : "Analisar com IA"}</button>
                {selected.incorporation_recommended && selected.incorporation_status === "aguardando_consentimento" && <button className="btn" type="button" disabled={busy} onClick={() => void incorporate()}>Autorizar incorporação ao CorVIA</button>}
              </div>

              {selected.analysis_status === "concluido" && selected.analysis && <>
                <article className="card"><h3>Resumo clínico</h3><p>{selected.analysis.summary_pt}</p></article>
                <article className="card"><h3>Pontos-chave</h3><ul>{(selected.analysis.key_points_pt ?? []).map((x) => <li key={x}>{x}</li>)}</ul></article>
                <article className="card"><h3>Metodologia e população</h3><p>{selected.analysis.methodology_pt}</p><p>{selected.analysis.population_pt}</p></article>
                <article className="card"><h3>Resultados e implicações</h3><p>{selected.analysis.results_pt}</p><ul>{(selected.analysis.clinical_implications_pt ?? []).map((x) => <li key={x}>{x}</li>)}</ul></article>
                <article className="card"><h3>Limitações</h3><ul>{(selected.analysis.limitations_pt ?? []).map((x) => <li key={x}>{x}</li>)}</ul></article>
                <article className="card"><h3>Texto {selected.translation_available ? "traduzido" : "extraído"}</h3><pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit", maxHeight: "34rem", overflow: "auto" }}>{selected.translated_text || selected.extracted_text}</pre></article>
                {selected.incorporation_reason_pt && <article className="card"><h3>Comparação com o acervo CorVIA</h3><p>{selected.incorporation_reason_pt}</p></article>}
              </>}
            </div>
          )}
        </ClinicalSection>
      </div>
    </div>
  );
}
