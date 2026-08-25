import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import Icone from "../components/Icone";
import { api } from "../lib/api";
import "../styles/cardiovascular-exam-ai.css";

type Quality = "adequada" | "limitada" | "inadequada";
type Measurement = { name: string; value: string; unit: string | null; source: string; file_id: string | null; confidence: string };
type ImageObservation = { file_id: string; observation: string; confidence: string };
type Differential = { diagnosis: string; rationale: string; likelihood: string };
type SuggestedTest = { exam: string; rationale: string; priority: string };
type Management = {
  action: string; rationale: string; urgency: string; evidence_level: string | null;
  prerequisites: string[]; contraindications: string[]; source_urls: string[];
};
type Guideline = {
  organization: string; title: string; year: number | null; url: string;
  evidence_summary: string; section_or_page: string | null;
  recommendation_class: string | null; evidence_level: string | null;
};
type Payload = {
  exam_type: string;
  quality: Quality;
  executive_summary: string;
  report_interpretation: string | null;
  image_analysis: ImageObservation[];
  measurements: Measurement[];
  integrated_impression: string[];
  differential_diagnoses: Differential[];
  red_flags: string[];
  suggested_additional_tests: SuggestedTest[];
  possible_management: Management[];
  guidelines: Guideline[];
  limitations: string[];
  urgent_review_recommended: boolean;
  urgency_assessment: "present" | "absent" | "not_assessable";
  disclaimer: string;
};
type AIStatus = {
  enabled: boolean;
  unavailable_reason: "ai_disabled" | "multimodal_disabled" | "data_controls_not_approved" | "provider_unsupported" | "provider_not_configured" | null;
  supported_media_types: string[];
  exam_types: Record<string, string>;
  max_files: number;
  max_file_bytes: number;
  max_total_bytes: number;
  persists_files_in_corvia: false;
  provider_response_storage_requested: false;
  external_processor: "openai";
  consent_version: string;
  searches_current_guidelines: true;
  raw_dicom_supported: false;
  video_supported: false;
};
type Analysis = {
  payload: Payload;
  web_sources: Array<{ title: string; url: string; cited: boolean }>;
  provider: string;
  model: string;
  prompt_version: string;
  persisted_in_corvia: false;
  provider_response_storage_requested: false;
};

const ACCEPT = ".pdf,.jpg,.jpeg,.png,.webp,.txt,.csv";
const CAMERA_ACCEPT = "image/jpeg,image/png,image/webp";
const MAX_FILES = 5;
const FALLBACK_MAX_FILE_BYTES = 20 * 1024 * 1024;
const FALLBACK_MAX_TOTAL_BYTES = 40 * 1024 * 1024;
const STATUS_MESSAGES: Record<Exclude<AIStatus["unavailable_reason"], null>, string> = {
  ai_disabled: "A IA clínica está desligada nesta instalação.",
  multimodal_disabled: "A análise multimodal ainda não foi habilitada no servidor.",
  data_controls_not_approved: "Os controles contratuais de dados de saúde ainda não foram aprovados para este processador.",
  provider_unsupported: "O provedor atual não oferece a central multimodal completa.",
  provider_not_configured: "A credencial do provedor ainda não está configurada no servidor.",
};

function label(value: string) {
  return value.replaceAll("_", " ");
}

function formatBytes(bytes: number) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}

function ListBlock({ title, items, alert = false }: { title: string; items: string[]; alert?: boolean }) {
  if (!items.length) return null;
  return <section className={`ceai__block${alert ? " is-alert" : ""}`}><h3>{title}</h3><ul>{items.map((item, index) => <li key={`${index}-${item}`}>{item}</li>)}</ul></section>;
}

function copyText(payload: Payload, sources: Analysis["web_sources"], files: File[], fileNotes: string[]) {
  const lines = [
    payload.executive_summary,
    ...files.map((_, index) => `Arquivo analisado arquivo-${index + 1}${fileNotes[index]?.trim() ? ` — ${fileNotes[index].trim()}` : ""}`),
    ...payload.image_analysis.map((item) => `Observação ${item.file_id} (confiança ${label(item.confidence)}): ${item.observation}`),
    ...payload.measurements.map((item) => `Medida${item.file_id ? ` ${item.file_id}` : ""}: ${item.name} — ${item.value}${item.unit ? ` ${item.unit}` : ""} (${label(item.source)}; confiança ${label(item.confidence)})`),
    ...payload.integrated_impression.map((item) => `• ${item}`),
    ...payload.red_flags.map((item) => `ALERTA: ${item}`),
    ...payload.suggested_additional_tests.map((item) => `Exame sugerido (${label(item.priority)}): ${item.exam} — ${item.rationale}`),
    ...payload.possible_management.map((item) => [
      `Possibilidade de conduta (${label(item.urgency)}): ${item.action} — ${item.rationale}`,
      item.prerequisites.length ? `Pré-condições: ${item.prerequisites.join("; ")}` : "",
      item.contraindications.length ? `Contraindicações/ressalvas: ${item.contraindications.join("; ")}` : "",
      item.evidence_level ? `Nível de evidência: ${item.evidence_level}` : "",
      ...item.source_urls.map((url) => `Fonte da conduta: ${url}`),
    ].filter(Boolean).join("\n")),
    ...payload.guidelines.map((item) => `${item.organization} ${item.year ?? ""}: ${item.title}${item.section_or_page ? ` — seção/página sugerida ${item.section_or_page}` : ""} — síntese assistiva: ${item.evidence_summary} — ${item.url}`),
    ...sources.map((item) => `Fonte consultada: ${item.title} — ${item.url}`),
    ...payload.limitations.map((item) => `Limitação: ${item}`),
    payload.disclaimer,
  ];
  return lines.filter(Boolean).join("\n");
}

export default function CardiovascularExamAI() {
  const { pathname } = useLocation();
  const [status, setStatus] = useState<AIStatus | null>(null);
  const [examType, setExamType] = useState(pathname.startsWith("/ecg-ia") ? "ecg" : "ecg");
  const [files, setFiles] = useState<File[]>([]);
  const [fileNotes, setFileNotes] = useState<string[]>([]);
  const [question, setQuestion] = useState("");
  const [report, setReport] = useState("");
  const [context, setContext] = useState("");
  const [externalConfirmed, setExternalConfirmed] = useState(false);
  const [deidentifiedConfirmed, setDeidentifiedConfirmed] = useState(false);
  const [sameCaseConfirmed, setSameCaseConfirmed] = useState(false);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const cameraInputRef = useRef<HTMLInputElement>(null);
  const filesInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    api.get<AIStatus>("/exames-ia/status").then(setStatus).catch((reason) => {
      setError(reason instanceof Error ? reason.message : "Não foi possível consultar a central de exames.");
    });
  }, []);

  const totalBytes = useMemo(() => files.reduce((sum, file) => sum + file.size, 0), [files]);
  const maxFiles = Math.min(status?.max_files ?? MAX_FILES, MAX_FILES);
  const maxFileBytes = status?.max_file_bytes ?? FALLBACK_MAX_FILE_BYTES;
  const maxTotalBytes = status?.max_total_bytes ?? FALLBACK_MAX_TOTAL_BYTES;
  const remainingFiles = Math.max(0, maxFiles - files.length);
  const canAnalyze = !!status?.enabled && !!(files.length || report.trim() || context.trim())
    && externalConfirmed && deidentifiedConfirmed && (files.length < 2 || sameCaseConfirmed) && !busy;

  function invalidateConsent() {
    setExternalConfirmed(false); setDeidentifiedConfirmed(false); setSameCaseConfirmed(false);
    setAnalysis(null); setCopied(false);
  }

  function addFiles(selected: FileList | null) {
    if (!selected?.length) return;
    setError(""); setAnalysis(null); setCopied(false);
    const merged = [...files];
    for (const file of Array.from(selected)) {
      if (file.size > maxFileBytes) return setError(`${file.name} excede o limite de ${formatBytes(maxFileBytes)} por arquivo.`);
      if (!merged.some((item) => item.name === file.name && item.size === file.size && item.lastModified === file.lastModified)) merged.push(file);
    }
    if (merged.length > maxFiles) return setError(`Envie no máximo ${maxFiles} arquivos por análise. Remova um item para adicionar outro.`);
    if (merged.reduce((sum, file) => sum + file.size, 0) > maxTotalBytes) return setError(`Os arquivos excedem o limite total de ${formatBytes(maxTotalBytes)}.`);
    setFiles(merged);
    setFileNotes((current) => [...current, ...Array(Math.max(0, merged.length - current.length)).fill("")]);
    invalidateConsent();
  }

  function removeFile(index: number) {
    setFiles((current) => current.filter((_, itemIndex) => itemIndex !== index));
    setFileNotes((current) => current.filter((_, itemIndex) => itemIndex !== index));
    invalidateConsent(); setError("");
  }

  async function analyze() {
    if (!canAnalyze) return;
    setBusy(true); setError(""); setCopied(false);
    try {
      const result = await api.uploadFormulario<Analysis>(
        "/exames-ia/analisar",
        files.map((arquivo) => ({ campo: "arquivos", arquivo })),
        {
          exam_type: examType,
          clinical_question: question.trim(),
          report_text: report.trim(),
          clinical_context: context.trim(),
          file_notes: JSON.stringify(fileNotes.map((item) => item.trim())),
          confirm_external_processing: "true",
          confirm_deidentified: "true",
          confirm_same_case: files.length < 2 || sameCaseConfirmed ? "true" : "false",
          consent_version: status?.consent_version ?? "",
        },
      );
      setAnalysis(result);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Não foi possível analisar o exame.");
    } finally {
      setBusy(false);
    }
  }

  async function copy() {
    if (!analysis) return;
    try { await navigator.clipboard.writeText(copyText(analysis.payload, analysis.web_sources, files, fileNotes)); setCopied(true); }
    catch { setError("Não foi possível copiar automaticamente."); }
  }

  function restart() {
    setFiles([]); setFileNotes([]); setQuestion(""); setReport(""); setContext(""); setExternalConfirmed(false);
    setDeidentifiedConfirmed(false); setSameCaseConfirmed(false); setAnalysis(null); setCopied(false); setError("");
  }

  const payload = analysis?.payload;
  return <main className="ceai">
    <header className="ceai__hero">
      <span className="ceai__hero-icon"><Icone nome="ecg" /></span>
      <div><p className="eyebrow">Inteligência cardiovascular multimodal</p><h1>IA para exames cardiovasculares</h1><p>Integre imagens, laudos, resultados e contexto clínico com busca das diretrizes atuais.</p></div>
      <span className="ceai__badge">Modo assistivo</span>
    </header>

    <section className="ceai__privacy">
      <strong>Desidentificado e transitório</strong>
      <span>O CorVIA não incorpora estes dados ao prontuário. Uma cópia sanitizada é enviada ao processador externo com solicitação de não armazenar a resposta; aplicam-se os controles contratuais do provedor.</span>
    </section>

    {!analysis && <section className="ceai__workspace" aria-busy={busy}>
      <div className="ceai__form">
        <label>Tipo de exame<select disabled={busy} value={examType} onChange={(event) => { setExamType(event.target.value); invalidateConsent(); }}>
          {Object.entries(status?.exam_types ?? { ecg: "Eletrocardiograma" }).map(([value, text]) => <option key={value} value={value}>{text}</option>)}
        </select></label>
        <label>Objetivo ou pergunta clínica <span>opcional</span><textarea disabled={busy} value={question} maxLength={16000} onChange={(event) => { setQuestion(event.target.value); invalidateConsent(); }} placeholder="Ex.: correlacionar achados com dispneia e definir próximos passos diagnósticos." /></label>
        <label>Laudo ou resultados <span>opcional</span><textarea disabled={busy} value={report} maxLength={16000} onChange={(event) => { setReport(event.target.value); invalidateConsent(); }} placeholder="Cole o laudo, medidas, valores laboratoriais e respectivos intervalos de referência, sem nome ou identificadores." /></label>
        <label>Contexto clínico desidentificado <span>opcional</span><textarea disabled={busy} value={context} maxLength={16000} onChange={(event) => { setContext(event.target.value); invalidateConsent(); }} placeholder="Idade aproximada, sexo, sintomas, comorbidades, medicamentos e evolução — sem nome, CPF, telefone, endereço ou prontuário." /></label>
      </div>
      <aside className="ceai__files">
        <div className={`ceai__drop${files.length ? " has-files" : ""}`}>
          <span className="ceai__drop-icon"><Icone nome="camera" /></span>
          <strong>{files.length ? `${files.length} de ${maxFiles} arquivos adicionados` : "Adicione fotos, imagens ou arquivos"}</strong>
          <small>{remainingFiles ? `Você ainda pode adicionar ${remainingFiles} ${remainingFiles === 1 ? "item" : "itens"}` : "Limite de arquivos atingido"} · {formatBytes(maxFileBytes)} cada · {formatBytes(maxTotalBytes)} no total</small>
          <div className="ceai__source-actions">
            <button type="button" className="botao ceai__camera" disabled={busy || !remainingFiles} onClick={() => cameraInputRef.current?.click()}>
              <Icone nome="camera" /> Tirar foto
            </button>
            <button type="button" className="botao botao--secundario" disabled={busy || !remainingFiles} onClick={() => filesInputRef.current?.click()}>
              <Icone nome="galeria" /> Escolher arquivos
            </button>
          </div>
          <input
            ref={cameraInputRef}
            className="ceai__hidden-input"
            type="file"
            disabled={busy}
            accept={CAMERA_ACCEPT}
            capture="environment"
            onChange={(event) => { addFiles(event.currentTarget.files); event.currentTarget.value = ""; }}
          />
          <input
            ref={filesInputRef}
            className="ceai__hidden-input"
            multiple
            type="file"
            disabled={busy}
            accept={ACCEPT}
            onChange={(event) => { addFiles(event.currentTarget.files); event.currentTarget.value = ""; }}
          />
        </div>
        {!!files.length && <div className="ceai__file-list" aria-label="Arquivos selecionados">
          <ol>{files.map((file, index) => <li key={`${file.name}-${file.size}-${file.lastModified}`}>
            <span className="ceai__file-number" aria-hidden="true">{index + 1}</span>
            <span className="ceai__file-details"><strong>{file.name}</strong><small>{formatBytes(file.size)}{file.type ? ` · ${file.type.replace("image/", "")}` : ""}</small></span>
            <button type="button" disabled={busy} onClick={() => removeFile(index)} aria-label={`Remover arquivo ${index + 1}: ${file.name}`}><Icone nome="fechar" /></button>
            <input className="ceai__file-note" disabled={busy} value={fileNotes[index] ?? ""} maxLength={300} onChange={(event) => {
              const value = event.target.value; setFileNotes((current) => current.map((item, itemIndex) => itemIndex === index ? value : item)); invalidateConsent();
            }} placeholder="Legenda opcional: vista, derivação, fase…" aria-label={`Legenda do arquivo ${index + 1}`} />
          </li>)}</ol>
          <small className="ceai__file-total">Total: {formatBytes(totalBytes)} · {files.length}/{maxFiles} arquivos</small>
        </div>}
        <p className="ceai__format-note"><strong>Compatíveis:</strong> até cinco imagens/arquivos, com no máximo um PDF de 12 páginas. Imagens e PDFs passam por sanitização local. DICOM, cine/vídeo, DOCX e XLSX ainda não são aceitos.</p>
        <label className="ceai__consent"><input type="checkbox" disabled={busy} checked={deidentifiedConfirmed} onChange={(event) => setDeidentifiedConfirmed(event.target.checked)} /><span>{files.length ? "Confirmei também a área visível de cada imagem e removi nome, data de nascimento, prontuário e outros identificadores." : "Confirmei que removi dos textos nome, data de nascimento, prontuário e outros identificadores."}</span></label>
        {files.length > 1 && <label className="ceai__consent"><input type="checkbox" disabled={busy} checked={sameCaseConfirmed} onChange={(event) => setSameCaseConfirmed(event.target.checked)} /><span>Confirmo que todos os arquivos pertencem ao mesmo paciente e episódio clínico.</span></label>}
        <label className="ceai__consent"><input type="checkbox" disabled={busy} checked={externalConfirmed} onChange={(event) => setExternalConfirmed(event.target.checked)} /><span>Autorizo o envio da cópia sanitizada ao provedor de IA e a busca web em fontes médicas oficiais.</span></label>
        {status && !status.enabled && <p className="ceai__warning">{status.unavailable_reason ? STATUS_MESSAGES[status.unavailable_reason] : "Central indisponível."}</p>}
        {error && <p className="ceai__error" role="alert">{error}</p>}
        <button className="botao ceai__analyze" disabled={!canAnalyze} onClick={analyze}>{busy ? "Analisando exame e diretrizes…" : "Analisar com IA cardiovascular"}</button>
        <small className="ceai__notice">A saída é uma sugestão para revisão médica. Não constitui laudo, diagnóstico autônomo ou prescrição.</small>
      </aside>
    </section>}

    {payload && <section className="ceai__result" aria-live="polite">
      <header><div><p className="eyebrow">Análise integrada</p><h2>{payload.exam_type}</h2></div><span className={`ceai__quality is-${payload.quality}`}>Qualidade {payload.quality}</span></header>
      <div className={`ceai__urgent${payload.urgent_review_recommended ? "" : " is-neutral"}`}>
        <strong>{payload.urgent_review_recommended ? "Revisão médica prioritária" : payload.urgency_assessment === "not_assessable" ? "Urgência não avaliável" : "Triagem sem alerta identificado"}</strong>
        <span>{payload.urgent_review_recommended ? "Confira imediatamente o exame original e o contexto clínico." : payload.urgency_assessment === "not_assessable" ? "Os dados não permitem avaliar urgência com segurança. Revise o caso e o exame original antes de decidir a prioridade." : "A ausência de alerta pela IA não exclui emergência ou necessidade de revisão imediata."}</span>
      </div>
      {!!files.length && <section className="ceai__block"><h3>Arquivos analisados e proveniência</h3><div className="ceai__table-wrap"><table><thead><tr><th>Identificador</th><th>Arquivo local (nome não enviado à IA)</th><th>Legenda informada</th></tr></thead><tbody>{files.map((file, index) => <tr key={`${file.name}-${file.size}-${file.lastModified}`}><td>{`arquivo-${index + 1}`}</td><td>{file.name}</td><td>{fileNotes[index]?.trim() || "—"}</td></tr>)}</tbody></table></div></section>}
      <section className="ceai__summary"><h3>Síntese executiva</h3><p>{payload.executive_summary}</p></section>
      {payload.report_interpretation && <section className="ceai__block"><h3>Interpretação do laudo/resultados</h3><p>{payload.report_interpretation}</p></section>}
      {!!payload.image_analysis.length && <section className="ceai__block"><h3>Análise das imagens</h3><div className="ceai__cards">{payload.image_analysis.map((item, index) => <article key={`${item.file_id}-${index}`}><span>{item.file_id} · confiança {label(item.confidence)}</span><p>{item.observation}</p></article>)}</div></section>}
      {!!payload.measurements.length && <section className="ceai__block"><h3>Medidas e dados extraídos</h3><div className="ceai__table-wrap"><table><thead><tr><th>Dado</th><th>Valor</th><th>Origem</th><th>Confiança</th></tr></thead><tbody>{payload.measurements.map((item, index) => <tr key={`${item.name}-${index}`}><td>{item.name}</td><td>{item.value}{item.unit ? ` ${item.unit}` : ""}</td><td>{label(item.source)}{item.file_id ? ` · ${item.file_id}` : ""}</td><td>{label(item.confidence)}</td></tr>)}</tbody></table></div></section>}
      <ListBlock title="Impressão integrada" items={payload.integrated_impression} />
      <ListBlock title="Sinais de alerta" items={payload.red_flags} alert />
      {!!payload.differential_diagnoses.length && <section className="ceai__block"><h3>Diagnósticos diferenciais</h3><div className="ceai__cards">{payload.differential_diagnoses.map((item, index) => <article key={`${item.diagnosis}-${index}`}><span>{label(item.likelihood)}</span><strong>{item.diagnosis}</strong><p>{item.rationale}</p></article>)}</div></section>}
      {!!payload.suggested_additional_tests.length && <section className="ceai__block"><h3>Exames adicionais sugeridos</h3><div className="ceai__cards">{payload.suggested_additional_tests.map((item, index) => <article key={`${item.exam}-${index}`}><span>{label(item.priority)}</span><strong>{item.exam}</strong><p>{item.rationale}</p></article>)}</div></section>}
      {!!payload.possible_management.length && <section className="ceai__block"><h3>Possibilidades de conduta para discussão clínica</h3><div className="ceai__cards">{payload.possible_management.map((item, index) => <article key={`${item.action}-${index}`}><span>{label(item.urgency)}</span><strong>{item.action}</strong><p>{item.rationale}</p>{!!item.prerequisites.length && <small>Pré-condições: {item.prerequisites.join("; ")}</small>}{!!item.contraindications.length && <small>Contraindicações/ressalvas: {item.contraindications.join("; ")}</small>}{item.evidence_level && <small>{item.evidence_level}</small>}<div className="ceai__evidence-links">{item.source_urls.map((url) => <a key={url} href={url} target="_blank" rel="noopener noreferrer">Fonte da conduta</a>)}</div></article>)}</div></section>}
      {!!payload.guidelines.length && <section className="ceai__block"><h3>Diretrizes localizadas para conferência</h3><div className="ceai__guidelines">{payload.guidelines.map((item, index) => <article key={`${item.url}-${index}`}><a href={item.url} target="_blank" rel="noopener noreferrer"><strong>{item.organization}{item.year ? ` · ${item.year}` : ""}</strong><span>{item.title}</span></a><p>{item.evidence_summary}</p>{item.section_or_page && <small>Seção/página sugerida: {item.section_or_page}</small>}<small>{[item.recommendation_class, item.evidence_level].filter(Boolean).join(" · ") || "Síntese assistiva: confirme a recomendação, classe e nível no documento original"}</small></article>)}</div></section>}
      {!!analysis.web_sources.length && <section className="ceai__block"><h3>Fontes web efetivamente consultadas</h3><div className="ceai__sources">{analysis.web_sources.map((source) => <a key={source.url} href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a>)}</div></section>}
      <ListBlock title="Limitações e incertezas" items={payload.limitations} />
      <p className="ceai__disclaimer">{payload.disclaimer}</p>
      <footer><button className="botao botao--secundario" onClick={copy}>{copied ? "Copiado" : "Copiar análise"}</button><button className="botao" onClick={restart}>Analisar outro exame</button></footer>
    </section>}

    <section className="ceai__longitudinal"><div><strong>Deseja registrar a interpretação no prontuário?</strong><span>Revise a sugestão e registre somente a sua conclusão médica no fluxo longitudinal.</span></div><Link className="botao botao--secundario" to="/prontuario">Abrir prontuário</Link></section>
  </main>;
}
