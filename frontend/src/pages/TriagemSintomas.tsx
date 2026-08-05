import { useEffect, useMemo, useState } from "react";
import { Carregando, Erro } from "../components/Estado";
import { api } from "../lib/api";

type Option = { value: string; label: string };
type Question = {
  id: string;
  label: string;
  type: "boolean" | "number" | "select" | "multiselect" | "text";
  required?: boolean;
  unit?: string;
  min?: number;
  max?: number;
  section?: string;
  help?: string;
  options?: Option[];
};

type TriageSummary = {
  slug: string;
  name: string;
  aliases: string[];
  areas: string[];
  summary: string;
  tags: string[];
};

type TriageDetail = TriageSummary & {
  questions: Question[];
  default_tests: unknown[];
  differentials: unknown[];
  red_flags: unknown[];
  ambulatory_flow: unknown[];
  emergency_flow: unknown[];
  source_refs: string[];
  source_urls: string[];
  review_status: string;
};

type Assessment = {
  risk: string;
  red_flags: unknown[];
  suggested_tests: unknown[];
  differentials: unknown[];
  recommended_flow: unknown[];
  messages: unknown[];
  missing_information: string[];
  disclaimer: string;
  incomplete: boolean;
};

function textOf(value: unknown) {
  if (typeof value === "string") return value;
  if (value && typeof value === "object") {
    const record = value as Record<string, unknown>;
    return String(record.label || record.name || record.text || record.test || JSON.stringify(value));
  }
  return String(value ?? "");
}

function ResultList({ title, items, alert = false }: { title: string; items: unknown[]; alert?: boolean }) {
  if (!items.length) return null;
  return (
    <div className={`cartao ${alert ? "painel__funcao--destaque" : ""}`} style={{ marginTop: "0.7rem" }}>
      <h3>{title}</h3>
      <ul>{items.map((item, index) => <li key={index}>{textOf(item)}</li>)}</ul>
    </div>
  );
}

const RISK_LABEL: Record<string, string> = {
  informativo: "Informativo",
  rotina: "Rotina",
  prioritario: "Prioritário",
  urgente: "Urgente",
  emergencia: "Emergência",
};

export default function TriagemSintomas() {
  const [catalog, setCatalog] = useState<TriageSummary[] | null>(null);
  const [selectedSlug, setSelectedSlug] = useState("");
  const [detail, setDetail] = useState<TriageDetail | null>(null);
  const [context, setContext] = useState<"ambulatorio" | "emergencia">("ambulatorio");
  const [answers, setAnswers] = useState<Record<string, unknown>>({});
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [query, setQuery] = useState("");
  const [error, setError] = useState("");
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [assessing, setAssessing] = useState(false);

  useEffect(() => {
    let active = true;
    api.get<TriageSummary[]>("/specialty-guides/triage")
      .then((response) => { if (active) setCatalog(response); })
      .catch((cause) => { if (active) setError(cause.message); });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!selectedSlug) {
      setDetail(null);
      return;
    }
    setLoadingDetail(true);
    setError("");
    setAnswers({});
    setAssessment(null);
    let active = true;
    api.get<TriageDetail>(`/specialty-guides/triage/${selectedSlug}`)
      .then((response) => { if (active) setDetail(response); })
      .catch((cause) => { if (active) setError(cause.message); })
      .finally(() => { if (active) setLoadingDetail(false); });
    return () => { active = false; };
  }, [selectedSlug]);

  const filtered = useMemo(() => {
    const term = query.trim().toLowerCase();
    if (!term) return catalog || [];
    return (catalog || []).filter((item) => [item.name, item.summary, ...item.aliases, ...item.tags].join(" ").toLowerCase().includes(term));
  }, [catalog, query]);

  const sections = useMemo(() => {
    const grouped = new Map<string, Question[]>();
    for (const question of detail?.questions || []) {
      const section = question.section || "Avaliação";
      grouped.set(section, [...(grouped.get(section) || []), question]);
    }
    return [...grouped.entries()];
  }, [detail]);

  function updateAnswer(question: Question, value: unknown) {
    setAssessment(null);
    setAnswers((previous) => ({ ...previous, [question.id]: value }));
  }

  function toggleMultiselect(question: Question, value: string) {
    const current = Array.isArray(answers[question.id]) ? answers[question.id] as string[] : [];
    updateAnswer(question, current.includes(value) ? current.filter((item) => item !== value) : [...current, value]);
  }

  async function assess() {
    if (!detail) return;
    setAssessing(true);
    setError("");
    try {
      setAssessment(await api.post<Assessment>(`/specialty-guides/triage/${detail.slug}/assess`, { context, answers }));
    } catch (cause: any) {
      setError(cause.message);
    } finally {
      setAssessing(false);
    }
  }

  if (!catalog && !error) return <Carregando />;

  return (
    <>
      <p className="eyebrow">Apoio à priorização clínica</p>
      <h1>Triagem de Sintomas</h1>
      <p style={{ maxWidth: "76ch", color: "var(--texto-secundario)" }}>
        Selecione o sintoma e o ambiente. A classificação considera red flags e sugere
        exames e fluxo, sem substituir protocolo institucional ou avaliação presencial.
      </p>

      <section className="cartao" style={{ marginTop: "1rem" }}>
        <h2>1. Ambiente de atendimento</h2>
        <div className="painel__temas">
          <button type="button" className="painel__tema" onClick={() => { setContext("ambulatorio"); setAssessment(null); }} style={context === "ambulatorio" ? { borderColor: "var(--acento)", fontWeight: 700 } : undefined}>Consultório / ambulatório</button>
          <button type="button" className="painel__tema" onClick={() => { setContext("emergencia"); setAssessment(null); }} style={context === "emergencia" ? { borderColor: "var(--acento)", fontWeight: 700 } : undefined}>Emergência</button>
        </div>
      </section>

      <section className="cartao" style={{ marginTop: "0.8rem" }}>
        <h2>2. Sintoma principal</h2>
        <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Pesquisar dor, dispneia, palpitação, síncope…" />
        <div className="painel__temas" style={{ marginTop: "0.7rem" }}>
          {filtered.map((item) => (
            <button type="button" key={item.slug} className="painel__tema" onClick={() => setSelectedSlug(item.slug)} style={selectedSlug === item.slug ? { borderColor: "var(--acento)", fontWeight: 700 } : undefined}>{item.name}</button>
          ))}
        </div>
        {!filtered.length && <p>Nenhum sintoma encontrado.</p>}
      </section>

      {error && <Erro mensagem={error} />}
      {loadingDetail && <Carregando />}

      {detail && !loadingDetail && (
        <>
          <section className="cartao" style={{ marginTop: "0.8rem" }}>
            <h2>{detail.name}</h2>
            <p>{detail.summary}</p>
            {context === "emergencia" && <p><strong>Modo emergência:</strong> na presença de instabilidade, a prioridade é suporte inicial e protocolo local.</p>}
          </section>

          {sections.map(([section, questions]) => (
            <section className="cartao" style={{ marginTop: "0.8rem" }} key={section}>
              <h2>{section}</h2>
              <div style={{ display: "grid", gap: "0.8rem" }}>
                {questions.map((question) => (
                  <label key={question.id}>
                    <strong>{question.label}{question.required ? " *" : ""}</strong>
                    {question.help && <span style={{ display: "block", fontSize: "0.8rem", color: "var(--texto-secundario)" }}>{question.help}</span>}
                    {question.type === "boolean" && (
                      <select value={answers[question.id] === undefined ? "" : String(answers[question.id])} onChange={(event) => updateAnswer(question, event.target.value === "true")} style={{ marginTop: "0.35rem" }}>
                        <option value="">Selecione…</option><option value="true">Sim</option><option value="false">Não</option>
                      </select>
                    )}
                    {question.type === "number" && (
                      <div style={{ display: "flex", gap: "0.4rem", alignItems: "center" }}>
                        <input type="number" min={question.min} max={question.max} value={String(answers[question.id] ?? "")} onChange={(event) => updateAnswer(question, event.target.value === "" ? "" : Number(event.target.value))} style={{ marginTop: "0.35rem" }} />
                        {question.unit && <span>{question.unit}</span>}
                      </div>
                    )}
                    {question.type === "select" && (
                      <select value={String(answers[question.id] ?? "")} onChange={(event) => updateAnswer(question, event.target.value)} style={{ marginTop: "0.35rem" }}>
                        <option value="">Selecione…</option>{(question.options || []).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
                      </select>
                    )}
                    {question.type === "multiselect" && (
                      <div className="painel__temas" style={{ marginTop: "0.35rem" }}>
                        {(question.options || []).map((option) => {
                          const selected = Array.isArray(answers[question.id]) && (answers[question.id] as string[]).includes(option.value);
                          return <button type="button" key={option.value} className="painel__tema" onClick={() => toggleMultiselect(question, option.value)} style={selected ? { borderColor: "var(--acento)" } : undefined}>{option.label}</button>;
                        })}
                      </div>
                    )}
                    {question.type === "text" && <textarea value={String(answers[question.id] ?? "")} onChange={(event) => updateAnswer(question, event.target.value)} style={{ marginTop: "0.35rem" }} />}
                  </label>
                ))}
              </div>
            </section>
          ))}

          <button className="botao" onClick={assess} disabled={assessing} style={{ marginTop: "1rem" }}>{assessing ? "Classificando…" : "Classificar risco e organizar fluxo"}</button>
        </>
      )}

      {assessment && (
        <section className="cartao" style={{ marginTop: "1rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", alignItems: "center" }}>
            <h2>Resultado da triagem</h2>
            <span className="painel__tema" style={{ fontWeight: 800 }}>{RISK_LABEL[assessment.risk] || assessment.risk}</span>
          </div>
          {assessment.incomplete && <p><strong>Dados obrigatórios ausentes.</strong> O resultado pode estar incompleto.</p>}
          <ResultList title="Red flags identificadas" items={assessment.red_flags} alert />
          <ResultList title="Exames que podem ser considerados" items={assessment.suggested_tests} />
          <ResultList title="Diagnósticos diferenciais" items={assessment.differentials} />
          <ResultList title={`Fluxo sugerido — ${context === "emergencia" ? "emergência" : "ambulatório"}`} items={assessment.recommended_flow} />
          <ResultList title="Observações" items={assessment.messages} />
          <p style={{ marginTop: "1rem", fontSize: "0.82rem", color: "var(--texto-secundario)" }}>{assessment.disclaimer}</p>
        </section>
      )}

      {detail && (
        <section className="cartao" style={{ marginTop: "1rem" }}>
          <h2>Fontes</h2>
          <ul>{detail.source_refs.map((reference) => <li key={reference}>{reference}</li>)}</ul>
          <div className="painel__temas">{detail.source_urls.map((url) => <a key={url} href={url} target="_blank" rel="noopener noreferrer" className="painel__tema">Abrir fonte original</a>)}</div>
        </section>
      )}
    </>
  );
}
