import { useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useAuth } from "../lib/auth";
import BotaoFavorito from "../components/BotaoFavorito";
import PrivateScientificOriginal from "../components/PrivateScientificOriginal";
import { formatBRL } from "../lib/commercialPlans";
import { api, ApiError, READ_TIMEOUT_MS } from "../lib/api";
import { ClinicalPageHeader, ClinicalSection } from "../components/ClinicalCommandPrimitives";

type DocumentQuote = {
  quote_id: number;
  maximum_credit_centavos: number;
  available_credit_centavos: number;
  expires_at: string;
  includes_translation: boolean;
  currency: "BRL";
};

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
  const { usuario } = useAuth();
  return <ScientificDocumentWorkspace key={usuario?.id ?? "anonymous"} />;
}

function ScientificDocumentWorkspace() {
  const [params, setParams] = useSearchParams();
  const rawDocument = params.get("document");
  const parsedDocument = rawDocument && /^[1-9]\d*$/.test(rawDocument) ? Number(rawDocument) : null;
  const requestedDocument = parsedDocument !== null && Number.isSafeInteger(parsedDocument) ? parsedDocument : null;
  const reading = params.get("leitura");
  const requestedRef = useRef(requestedDocument);
  requestedRef.current = requestedDocument;
  const [items, setItems] = useState<ScientificDocument[]>([]);
  const [selected, setSelected] = useState<ScientificDocument | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [listError, setListError] = useState("");
  const [listLoading, setListLoading] = useState(true);
  const [listAttempt, setListAttempt] = useState(0);
  const [detailError, setDetailError] = useState("");
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailAttempt, setDetailAttempt] = useState(0);
  const listRequest = useRef(0);
  const detailRequest = useRef(0);
  const [quote, setQuote] = useState<(DocumentQuote & { documentId: number }) | null>(null);

  async function refresh(documentId = selected?.id) {
    const id = ++listRequest.current;
    const detailId = detailRequest.current;
    let refreshed = true;
    setListLoading(true); setListError("");
    try {
      const rows = await api.get<ScientificDocument[]>("/documentos-cientificos-ia", { timeoutMs: READ_TIMEOUT_MS });
      if (listRequest.current === id) setItems(rows);
    } catch (error) {
      if (listRequest.current === id) setListError(erroTexto(error));
      refreshed = false;
    } finally {
      if (listRequest.current === id) setListLoading(false);
    }
    if (documentId && requestedRef.current === documentId && detailRequest.current === detailId) {
      setDetailError("");
      try {
        const detail = await api.get<ScientificDocument>(`/documentos-cientificos-ia/${documentId}`, { timeoutMs: READ_TIMEOUT_MS });
        if (requestedRef.current === documentId && detailRequest.current === detailId) setSelected(detail);
      } catch (error) {
        if (requestedRef.current === documentId && detailRequest.current === detailId) setDetailError(erroTexto(error));
        refreshed = false;
      }
    }
    return refreshed;
  }

  useEffect(() => {
    const id = ++listRequest.current;
    const controller = new AbortController();
    setListLoading(true); setListError("");
    api.get<ScientificDocument[]>("/documentos-cientificos-ia", { timeoutMs: READ_TIMEOUT_MS, signal: controller.signal })
      .then(rows => { if (listRequest.current === id) setItems(rows); })
      .catch(error => { if (listRequest.current === id) setListError(erroTexto(error)); })
      .finally(() => { if (listRequest.current === id) setListLoading(false); });
    return () => { ++listRequest.current; controller.abort(); };
  }, [listAttempt]);

  useEffect(() => {
    let active = true;
    const controller = new AbortController();
    ++detailRequest.current;
    // Retry de leitura preserva uma resposta já confirmada para o mesmo item.
    setSelected(current => current?.id === requestedDocument ? current : null);
    setQuote(null); setMessage(""); setDetailError("");
    if (rawDocument !== null && requestedDocument === null) {
      setDetailLoading(false); setDetailError("O endereço do documento é inválido.");
    } else if (requestedDocument !== null) {
      setDetailLoading(true);
      api.get<ScientificDocument>(`/documentos-cientificos-ia/${requestedDocument}`, { timeoutMs: READ_TIMEOUT_MS, signal: controller.signal }).then(detail => {
        if (active) setSelected(detail);
      }).catch(error => { if (active) setDetailError(erroTexto(error)); })
        .finally(() => { if (active) setDetailLoading(false); });
    } else setDetailLoading(false);
    return () => { active = false; ++detailRequest.current; controller.abort(); };
  }, [rawDocument, requestedDocument, detailAttempt]);

  useEffect(() => {
    if (!selected || selected.id !== requestedDocument || !["original", "resumo", "traduzido"].includes(reading ?? "")) return;
    const section = document.getElementById(`leitura-privada-${reading}`);
    section?.scrollIntoView({ block: "nearest", behavior: "smooth" });
    section?.focus({ preventScroll: true });
  }, [selected?.id, requestedDocument, reading]);

  async function upload() {
    if (!file || busy || detailLoading) return;
    const context = detailRequest.current;
    setBusy(true); setMessage(""); setQuote(null);
    try {
      const row = await api.upload<ScientificDocument>("/documentos-cientificos-ia", "arquivo", file);
      if (detailRequest.current !== context) return;
      setFile(null);
      const detail = await api.get<ScientificDocument>(`/documentos-cientificos-ia/${row.id}`, { timeoutMs: READ_TIMEOUT_MS });
      if (detailRequest.current !== context) return;
      setSelected(detail);
      setParams({ document: String(row.id) });
      await refresh(row.id);
      if (requestedRef.current === row.id) setMessage("Arquivo salvo de forma privada. Agora você pode solicitar a análise da IA.");
    } catch (error) { if (detailRequest.current === context) setMessage(erroTexto(error)); }
    finally { setBusy(false); }
  }

  async function estimate() {
    if (!selected || busy || detailLoading) return;
    const context = detailRequest.current;
    setBusy(true); setMessage(""); setQuote(null);
    try {
      const result = await api.post<DocumentQuote>(`/documentos-cientificos-ia/${selected.id}/orcamento`);
      if (detailRequest.current !== context) return;
      if (result.currency !== "BRL" || !Number.isSafeInteger(result.quote_id) ||
          !Number.isSafeInteger(result.maximum_credit_centavos) || result.maximum_credit_centavos < 0 ||
          !Number.isSafeInteger(result.available_credit_centavos) || !Number.isFinite(Date.parse(result.expires_at))) {
        throw new Error("invalid quote");
      }
      setQuote({ ...result, documentId: selected.id });
    } catch (error) { if (detailRequest.current === context) setMessage(erroTexto(error)); }
    finally { setBusy(false); }
  }

  async function analyze() {
    if (!selected || busy || detailLoading || !quote || quote.documentId !== selected.id) return;
    if (Date.parse(quote.expires_at) <= Date.now()) {
      setQuote(null); setMessage("O orçamento expirou. Calcule um novo orçamento antes de analisar."); return;
    }
    if (quote.maximum_credit_centavos > quote.available_credit_centavos) return;
    const context = detailRequest.current;
    setBusy(true); setMessage("Analisando o documento e preparando a versão em português…");
    const acceptedQuote = quote;
    setQuote(null);
    try {
      const detail = await api.post<ScientificDocument>(`/documentos-cientificos-ia/${selected.id}/analisar`, {
        quote_id: acceptedQuote.quote_id, approved_max_credit_centavos: acceptedQuote.maximum_credit_centavos,
      });
      if (detailRequest.current !== context) return;
      setSelected(detail);
      setMessage("Análise concluída. O original permanece privado na sua biblioteca.");
      const refreshed = await refresh(selected.id);
      if (detailRequest.current !== context) return;
      if (!refreshed) setMessage("Análise concluída. A atualização da biblioteca está indisponível; o resultado confirmado foi preservado. Tente novamente apenas a leitura.");
    } catch (error) { if (detailRequest.current === context) setMessage(erroTexto(error)); }
    finally { setBusy(false); }
  }

  function selectDocument(id: number) {
    if (busy) return;
    setParams({ document: String(id) });
  }

  async function incorporate() {
    if (!selected || busy || detailLoading) return;
    if (!window.confirm("Incorporar este documento ao acervo compartilhado do CorVIA e ao Tudo com Tudo?")) return;
    const context = detailRequest.current;
    setBusy(true); setMessage("");
    try {
      const result = await api.uploadFormulario<{ incorporated: boolean; duplicate: boolean; slug?: string }>(
        `/documentos-cientificos-ia/${selected.id}/incorporar`, [], { confirm_incorporation: "true" },
      );
      if (detailRequest.current !== context) return;
      const refreshed = await refresh();
      if (detailRequest.current !== context) return;
      setMessage((result.duplicate ? "O documento já estava representado no acervo CorVIA." : "Documento incorporado ao acervo e conectado ao Tudo com Tudo.")
        + (refreshed ? "" : " A atualização da biblioteca está indisponível. Tente novamente apenas a leitura."));
    } catch (error) { if (detailRequest.current === context) setMessage(erroTexto(error)); }
    finally { setBusy(false); }
  }

  function selectReading(variant: string) {
    if (selected) setParams({ document: String(selected.id), leitura: variant });
  }

  return (
    <div className="cc-page scientific-document-page">
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
          <button className="btn primario" type="button" disabled={!file || busy || detailLoading} onClick={() => void upload()}>{busy ? "Processando…" : "Salvar na biblioteca"}</button>
        </div>
        {message && <p className="texto-secundario" role="status">{message}</p>}
      </ClinicalSection>

      <div className="cc-context-grid" style={{ alignItems: "start" }}>
        <ClinicalSection eyebrow="Sua biblioteca" title={`${items.length} documento(s)`}>
          {listLoading && <p role="status">Consultando biblioteca privada…</p>}
          {listError && <div role="alert"><p>{listError}</p><button type="button" className="btn" onClick={() => setListAttempt(value => value + 1)}>Tentar carregar biblioteca novamente</button></div>}
          <div className="lista-simples">
            {items.map((item) => (
              <button key={item.id} type="button" className="item-lista" aria-current={requestedDocument === item.id ? "true" : undefined} disabled={busy} onClick={() => void selectDocument(item.id)}>
                <strong>{item.title}</strong>
                <small>{item.document_type} · {item.analysis_status}{item.incorporation_status === "incorporado" ? " · incorporado" : ""}</small>
              </button>
            ))}
            {items.length === 0 && !listLoading && !listError && <p className="texto-secundario">Nenhum documento enviado ainda.</p>}
          </div>
        </ClinicalSection>

        <ClinicalSection eyebrow="Análise" title={selected?.id === requestedDocument ? selected.title : "Selecione um documento"}>
          {detailLoading && <p role="status">Carregando documento…</p>}
          {detailError && <div role="alert"><p>{detailError}</p>{requestedDocument !== null && <button type="button" className="btn" disabled={busy} onClick={() => { if (!busy) setDetailAttempt(value => value + 1); }}>Tentar carregar documento novamente</button>}</div>}
          {!selected || selected.id !== requestedDocument ? (!detailLoading && !detailError && <p className="texto-secundario">Abra um item da sua biblioteca para analisar ou revisar depois.</p>) : (
            <div className="stack">
              <div className="acoes-linha">
                <BotaoFavorito itemType="documento_cientifico_privado" itemId={selected.id} />
                <button className="btn" type="button" onClick={() => selectReading("original")}>Abrir original</button>
                <button className="btn" type="button" onClick={() => selectReading("resumo")}>Resumo em português</button>
                <button className="btn" type="button" onClick={() => selectReading("traduzido")}>Tradução em português</button>
                <button className="btn primario" type="button" disabled={busy || detailLoading || selected.analysis_status === "processando"} onClick={() => void estimate()}>{quote ? "Atualizar orçamento" : "Calcular orçamento de IA"}</button>
                {selected.incorporation_recommended && selected.incorporation_status === "aguardando_consentimento" && <button className="btn" type="button" disabled={busy || detailLoading} onClick={() => void incorporate()}>Autorizar incorporação ao CorVIA</button>}
              </div>

              {reading === "original" && <div id="leitura-privada-original" tabIndex={-1}><PrivateScientificOriginal key={selected.id} documentId={selected.id} title={selected.title} /></div>}
              <article id="leitura-privada-resumo" className="card" tabIndex={-1}><h3>Resumo clínico em português</h3><p>{selected.summary_pt || selected.analysis?.summary_pt || "O resumo em português ainda não está disponível. Você pode solicitar uma análise mediante orçamento e confirmação."}</p></article>
              {reading === "traduzido" && !selected.translation_available && <article id="leitura-privada-traduzido" className="card" tabIndex={-1}><h3>Tradução em português</h3><p>{selected.language?.toLowerCase().startsWith("pt") ? "O documento já está em português. Consulte o original." : "A tradução ainda não está disponível. Abrir esta seção não inicia uma análise nem consome créditos."}</p></article>}
              {quote && quote.documentId === selected.id && <article className="card" aria-label="Orçamento da análise">
                <h3>Até {formatBRL(quote.maximum_credit_centavos)} em créditos</h3>
                <p>Saldo disponível: {formatBRL(quote.available_credit_centavos)}. O teto inclui a análise e eventual tradução integral. Uso efetivo debitado; restante liberado.</p>
                <p className="texto-secundario">O cálculo do orçamento não consome créditos. Ao confirmar, você autoriza o uso de IA até esse valor.</p>
                {quote.maximum_credit_centavos > quote.available_credit_centavos && <p role="status">Saldo ou limite disponível insuficiente. <Link to="/assinatura">Consultar créditos e limite de uso</Link>.</p>}
                <button className="btn primario" type="button" disabled={busy || detailLoading || quote.maximum_credit_centavos > quote.available_credit_centavos} onClick={() => void analyze()}>
                  Confirmar análise por até {formatBRL(quote.maximum_credit_centavos)}
                </button>
              </article>}

              {selected.analysis_status === "concluido" && selected.analysis && <>
                <article className="card"><h3>Pontos-chave</h3><ul>{(selected.analysis.key_points_pt ?? []).map((x) => <li key={x}>{x}</li>)}</ul></article>
                <article className="card"><h3>Metodologia e população</h3><p>{selected.analysis.methodology_pt}</p><p>{selected.analysis.population_pt}</p></article>
                <article className="card"><h3>Resultados e implicações</h3><p>{selected.analysis.results_pt}</p><ul>{(selected.analysis.clinical_implications_pt ?? []).map((x) => <li key={x}>{x}</li>)}</ul></article>
                <article className="card"><h3>Limitações</h3><ul>{(selected.analysis.limitations_pt ?? []).map((x) => <li key={x}>{x}</li>)}</ul></article>
                <article id={selected.translation_available ? "leitura-privada-traduzido" : "leitura-privada-extraido"} tabIndex={-1} className="card"><h3>Texto {selected.translation_available ? "traduzido" : "extraído"}</h3><pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit", maxHeight: "34rem", overflow: "auto" }}>{selected.translated_text || selected.extracted_text}</pre></article>
                {selected.incorporation_reason_pt && <article className="card"><h3>Comparação com o acervo CorVIA</h3><p>{selected.incorporation_reason_pt}</p></article>}
              </>}
            </div>
          )}
        </ClinicalSection>
      </div>
    </div>
  );
}
