import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import Icone from "../components/Icone";
import { api } from "../lib/api";
import "../styles/ecg-quick-opinion.css";
import "../styles/ecg-quick-camera.css";

type Payload = {
  quality: "adequada" | "limitada" | "inadequada";
  summary: string;
  rhythm: string | null;
  heart_rate_bpm: number | null;
  intervals: { pr_ms: number | null; qrs_ms: number | null; qtc_ms: number | null };
  axis: string | null;
  conduction: string | null;
  st_t: string | null;
  other_findings: string[];
  red_flags: string[];
  limitations: string[];
  urgent_review_recommended: boolean;
  disclaimer: string;
};
type AIStatus = {
  enabled: boolean;
  unavailable_reason: "ai_disabled" | "multimodal_disabled" | "provider_unsupported" | "provider_not_configured" | null;
  supported_media_types: string[];
  max_size_bytes: number;
  stores_file: false;
};
type Analysis = {
  payload: Payload;
  provider: string;
  model: string;
  prompt_version: string;
  stored: false;
};

const MIME_LABELS: Record<string, string> = {
  "image/jpeg": "JPG",
  "image/png": "PNG",
  "image/webp": "WEBP",
  "application/pdf": "PDF",
};

const STATUS_MESSAGES: Record<Exclude<AIStatus["unavailable_reason"], null>, string> = {
  ai_disabled: "A IA clínica está desligada nesta instalação.",
  multimodal_disabled: "A análise visual de ECG ainda não foi habilitada no servidor.",
  provider_unsupported: "O provedor de IA configurado não oferece análise visual de ECG.",
  provider_not_configured: "O provedor multimodal ainda não está configurado no servidor.",
};

function measurements(payload: Payload) {
  return [
    payload.heart_rate_bpm !== null ? `FC ${payload.heart_rate_bpm} bpm` : null,
    payload.intervals.pr_ms !== null ? `PR ${payload.intervals.pr_ms} ms` : null,
    payload.intervals.qrs_ms !== null ? `QRS ${payload.intervals.qrs_ms} ms` : null,
    payload.intervals.qtc_ms !== null ? `QTc ${payload.intervals.qtc_ms} ms` : null,
  ].filter(Boolean).join(" · ");
}

function textResult(payload: Payload) {
  const lines = [payload.summary, measurements(payload)];
  if (payload.rhythm) lines.push(`Ritmo: ${payload.rhythm}`);
  if (payload.axis) lines.push(`Eixo: ${payload.axis}`);
  if (payload.conduction) lines.push(`Condução: ${payload.conduction}`);
  if (payload.st_t) lines.push(`ST-T: ${payload.st_t}`);
  if (payload.other_findings.length) lines.push(`Outros achados: ${payload.other_findings.join("; ")}`);
  if (payload.red_flags.length) lines.push(`Revisão prioritária: ${payload.red_flags.join("; ")}`);
  if (payload.limitations.length) lines.push(`Limitações: ${payload.limitations.join("; ")}`);
  lines.push(payload.disclaimer);
  return lines.filter(Boolean).join("\n");
}

export default function ECGQuickOpinion() {
  const [status, setStatus] = useState<AIStatus | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [confirmed, setConfirmed] = useState(false);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const cameraInput = useRef<HTMLInputElement>(null);
  const fileInput = useRef<HTMLInputElement>(null);

  useEffect(() => {
    api.get<AIStatus>("/ecg-ia/status").then(setStatus).catch((reason) => {
      setError(reason instanceof Error ? reason.message : "Não foi possível consultar a IA para ECG.");
    });
  }, []);

  const preview = useMemo(() => file?.type.startsWith("image/") ? URL.createObjectURL(file) : "", [file]);
  useEffect(() => () => { if (preview) URL.revokeObjectURL(preview); }, [preview]);

  const accepted = status?.supported_media_types.join(",") || "image/jpeg,image/png,image/webp,application/pdf";
  const formats = (status?.supported_media_types ?? []).map((type) => MIME_LABELS[type] || type).join(", ");

  function choose(next: File | null) {
    setError("");
    setAnalysis(null);
    setCopied(false);
    setConfirmed(false);
    if (!next) return setFile(null);
    if (status && !status.supported_media_types.includes(next.type)) {
      setFile(null);
      setError(`Formato não aceito pelo provedor atual. Use ${formats || "uma imagem compatível"}.`);
      return;
    }
    if (next.size > (status?.max_size_bytes ?? 20 * 1024 * 1024)) {
      setFile(null);
      setError("O ECG precisa ter no máximo 20 MB.");
      return;
    }
    setFile(next);
  }

  function selectedFrom(input: HTMLInputElement, next: File | null) {
    choose(next);
    // Permite fotografar ou selecionar novamente o mesmo arquivo após trocar.
    input.value = "";
  }

  async function analyze() {
    if (!file || !confirmed || !status?.enabled) return;
    setBusy(true);
    setError("");
    setCopied(false);
    try {
      const result = await api.upload<Analysis>("/ecg-ia/analisar", "arquivo", file, {
        confirm_external_processing: "true",
      });
      setAnalysis(result);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Não foi possível analisar o ECG.");
    } finally {
      setBusy(false);
    }
  }

  async function copy() {
    if (!analysis) return;
    try {
      await navigator.clipboard.writeText(textResult(analysis.payload));
      setCopied(true);
    } catch {
      setError("Não foi possível copiar automaticamente. Selecione o texto da sugestão.");
    }
  }

  function restart() {
    setFile(null);
    setConfirmed(false);
    setAnalysis(null);
    setCopied(false);
    setError("");
  }

  const payload = analysis?.payload;
  return <main className="ecgq">
    <header className="ecgq__hero">
      <div className="ecgq__hero-icon"><Icone nome="ecg" /></div>
      <div><p className="eyebrow">Assistência multimodal</p><h1>Opinião rápida da IA sobre ECG</h1><p>Envie o traçado e receba uma segunda leitura, sem cadastrar paciente ou abrir prontuário.</p></div>
      <span className="ecgq__badge">Modo rápido</span>
    </header>

    <section className="ecgq__privacy" aria-label="Privacidade do modo rápido">
      <strong>Sem cadastro e sem armazenamento</strong>
      <span>O arquivo é processado em memória e não é salvo no prontuário. Ao sair ou iniciar outra análise, o resultado deixa esta tela.</span>
    </section>

    {!analysis && <section className="ecgq__workspace">
      <div className="ecgq__upload">
        <div className={`ecgq__drop${file ? " has-file" : ""}`}>
          {preview ? <img src={preview} alt="Prévia do ECG selecionado" /> : <span className="ecgq__drop-icon"><Icone nome="ecg" /></span>}
          <strong>{file ? file.name : "Selecionar foto ou PDF do ECG"}</strong>
          <small>{file ? `${(file.size / 1024 / 1024).toFixed(2)} MB · pronto para análise` : `${formats || "JPG, PNG, WEBP ou PDF"} · até 20 MB`}</small>
          <div className="ecgq__source-actions">
            <button type="button" className="botao ecgq__camera" onClick={() => cameraInput.current?.click()}>
              <Icone nome="camera" /> Tirar foto do ECG
            </button>
            <button type="button" className="botao botao--secundario" onClick={() => fileInput.current?.click()}>
              {file ? "Trocar arquivo" : "Escolher arquivo"}
            </button>
          </div>
          <input
            ref={cameraInput}
            className="ecgq__hidden-input"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            capture="environment"
            onChange={(event) => selectedFrom(event.currentTarget, event.currentTarget.files?.[0] || null)}
          />
          <input
            ref={fileInput}
            className="ecgq__hidden-input"
            type="file"
            accept={accepted}
            onChange={(event) => selectedFrom(event.currentTarget, event.currentTarget.files?.[0] || null)}
          />
        </div>
      </div>
      <div className="ecgq__controls">
        <div><p className="eyebrow">Como funciona</p><h2>Só o traçado, direto à análise</h2></div>
        <ol><li>Fotografe o ECG ou escolha uma imagem/PDF.</li><li>Autorize o processamento pelo provedor de IA.</li><li>Revise a sugestão clínica na própria tela.</li></ol>
        <label className="ecgq__consent">
          <input type="checkbox" checked={confirmed} onChange={(event) => setConfirmed(event.target.checked)} />
          <span>Confirmo o envio deste ECG ao provedor de IA para processamento. Removi identificadores desnecessários do paciente.</span>
        </label>
        {status && !status.enabled && <p className="ecgq__warning" role="status">
          {status.unavailable_reason ? STATUS_MESSAGES[status.unavailable_reason] : "A IA multimodal está indisponível nesta instalação no momento."}
        </p>}
        {error && <p className="ecgq__error" role="alert">{error}</p>}
        <button className="botao ecgq__analyze" disabled={!file || !confirmed || !status?.enabled || busy} onClick={analyze}>
          {busy ? "Analisando o traçado…" : "Analisar ECG agora"}
        </button>
        <small className="ecgq__notice">Esta função oferece apoio à decisão. Não emite laudo e não substitui a interpretação médica.</small>
      </div>
    </section>}

    {payload && <section className="ecgq__result" aria-live="polite">
      <header><div><p className="eyebrow">Sugestão da IA</p><h2>Leitura para revisão médica</h2></div><span className={`ecgq__quality is-${payload.quality}`}>Qualidade {payload.quality}</span></header>
      {payload.urgent_review_recommended && <div className="ecgq__urgent" role="alert"><strong>Revisão médica prioritária sugerida</strong><span>A IA identificou achados que merecem conferência imediata no traçado e no contexto clínico.</span></div>}
      <div className="ecgq__summary"><p>{payload.summary}</p>{measurements(payload) && <strong>{measurements(payload)}</strong>}</div>
      <div className="ecgq__findings">
        {payload.rhythm && <article><small>Ritmo</small><p>{payload.rhythm}</p></article>}
        {payload.axis && <article><small>Eixo</small><p>{payload.axis}</p></article>}
        {payload.conduction && <article><small>Condução</small><p>{payload.conduction}</p></article>}
        {payload.st_t && <article><small>ST-T</small><p>{payload.st_t}</p></article>}
      </div>
      {!!payload.other_findings.length && <div className="ecgq__list"><strong>Outros achados</strong><ul>{payload.other_findings.map((item) => <li key={item}>{item}</li>)}</ul></div>}
      {!!payload.red_flags.length && <div className="ecgq__list is-alert"><strong>Sinais para revisão prioritária</strong><ul>{payload.red_flags.map((item) => <li key={item}>{item}</li>)}</ul></div>}
      {!!payload.limitations.length && <div className="ecgq__list"><strong>Limitações</strong><ul>{payload.limitations.map((item) => <li key={item}>{item}</li>)}</ul></div>}
      <p className="ecgq__disclaimer">{payload.disclaimer}</p>
      <footer><button className="botao botao--secundario" onClick={copy}>{copied ? "Copiado" : "Copiar sugestão"}</button><button className="botao" onClick={restart}>Analisar outro ECG</button></footer>
    </section>}

    <section className="ecgq__full-flow">
      <div><strong>Precisa guardar no histórico do paciente?</strong><span>Use o fluxo completo para vincular o ECG, revisar a sugestão e registrar a interpretação no prontuário.</span></div>
      <Link className="botao botao--secundario" to="/prontuario?acao=ecg">Abrir fluxo de prontuário</Link>
    </section>
  </main>;
}
