import { useEffect, useMemo, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { Carregando, Erro } from "../components/Estado";
import GrafoRelacionados from "../components/GrafoRelacionados";
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

type Disease = {
  slug: string;
  name: string;
  aliases: string[];
  area: string;
  category: string;
  subtype?: string | null;
  cyanosis_class?: string | null;
  completeness: string;
  summary: string;
  epidemiology?: string | null;
  presentation: unknown[];
  diagnostic_approach: unknown;
  differentials: unknown[];
  tests: unknown[];
  red_flags: unknown[];
  ambulatory_flow: unknown[];
  emergency_flow: unknown[];
  treatment_summary?: string | null;
  monitoring: unknown[];
  special_populations: unknown[];
  assistant_questions: Question[];
  source_refs: string[];
  source_urls: string[];
  related_document_slugs: string[];
  patient_material_slug?: string | null;
  review_status: string;
  review_note?: string | null;
  version: number;
};

type Assessment = {
  risk: string;
  red_flags: unknown[];
  supporting: unknown[];
  opposing: unknown[];
  missing_information: string[];
  suggested_tests: unknown[];
  differentials: unknown[];
  recommended_flow: unknown[];
  messages: unknown[];
  disclaimer: string;
  incomplete: boolean;
};

function textOf(value: unknown): string {
  if (typeof value === "string") return value;
  if (value && typeof value === "object") {
    const record = value as Record<string, unknown>;
    return String(record.label || record.name || record.text || record.test || record.title || JSON.stringify(value));
  }
  return String(value ?? "");
}

function labelOfKey(value: string): string {
  const labels: Record<string, string> = {
    confirmacao: "Confirmação diagnóstica",
    avaliacao_inicial: "Avaliação inicial",
    estratificacao: "Estratificação",
    etiologia: "Etiologia e fatores associados",
    fenotipo: "Fenótipo clínico",
  };
  return labels[value] || value.replaceAll("_", " ").replace(/^./, (letter) => letter.toUpperCase());
}

function labelOfSlug(value: string): string {
  return value.replaceAll("-", " ").replace(/^./, (letter) => letter.toUpperCase());
}

function ListBlock({ title, items, alert = false }: { title: string; items: unknown[]; alert?: boolean }) {
  if (!items?.length) return null;
  return (
    <section className={`cartao ${alert ? "painel__funcao--destaque" : ""}`} style={{ marginTop: "0.8rem" }}>
      <h2>{title}</h2>
      <ul>{items.map((item, index) => <li key={index}>{textOf(item)}</li>)}</ul>
    </section>
  );
}

function StructuredBlock({ title, value }: { title: string; value: unknown }) {
  if (!value || (Array.isArray(value) && value.length === 0)) return null;
  if (typeof value === "string") {
    return <section className="cartao" style={{ marginTop: "0.8rem" }}><h2>{title}</h2><p>{value}</p></section>;
  }
  if (Array.isArray(value)) return <ListBlock title={title} items={value} />;
  if (typeof value !== "object") return null;

  const entries = Object.entries(value as Record<string, unknown>);
  if (!entries.length) return null;
  return (
    <section className="cartao" style={{ marginTop: "0.8rem" }}>
      <h2>{title}</h2>
      <div style={{ display: "grid", gap: "0.75rem" }}>
        {entries.map(([key, item]) => (
          <div key={key}>
            <h3 style={{ marginBottom: "0.3rem" }}>{labelOfKey(key)}</h3>
            {Array.isArray(item)
              ? <ul>{item.map((entry, index) => <li key={index}>{textOf(entry)}</li>)}</ul>
              : <p>{textOf(item)}</p>}
          </div>
        ))}
      </div>
    </section>
  );
}

function RiskBadge({ risk }: { risk: string }) {
  const labels: Record<string, string> = {
    informativo: "Informativo",
    rotina: "Rotina",
    prioritario: "Prioritário",
    urgente: "Urgente",
    emergencia: "Emergência",
  };
  return <span className="painel__tema" style={{ fontWeight: 800 }}>{labels[risk] || risk}</span>;
}

export default function GuiaDoenca() {
  const { slug } = useParams();
  const [params, setParams] = useSearchParams();
  const [disease, setDisease] = useState<Disease | null>(null);
  const [answers, setAnswers] = useState<Record<string, unknown>>({});
  const [context, setContext] = useState<"ambulatorio" | "emergencia">("ambulatorio");
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [loading, setLoading] = useState(true);
  const [assessing, setAssessing] = useState(false);
  const [error, setError] = useState("");
  const assistantMode = params.get("modo") === "assistente";

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    api.get<Disease>(`/specialty-guides/diseases/${slug}`)
      .then((response) => { if (active) setDisease(response); })
      .catch((cause) => { if (active) setError(cause.message); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [slug]);

  const sections = useMemo(() => {
    const grouped = new Map<string, Question[]>();
    for (const question of disease?.assistant_questions || []) {
      const section = question.section || "Avaliação";
      grouped.set(section, [...(grouped.get(section) || []), question]);
    }
    return [...grouped.entries()];
  }, [disease]);

  function updateAnswer(question: Question, value: unknown) {
    setAssessment(null);
    setAnswers((previous) => ({ ...previous, [question.id]: value }));
  }

  function toggleMultiselect(question: Question, value: string) {
    const current = Array.isArray(answers[question.id]) ? answers[question.id] as string[] : [];
    updateAnswer(question, current.includes(value) ? current.filter((item) => item !== value) : [...current, value]);
  }

  async function assess() {
    if (!disease) return;
    setAssessing(true);
    setError("");
    try {
      setAssessment(await api.post<Assessment>(`/specialty-guides/diseases/${disease.slug}/assess`, { context, answers }));
    } catch (cause: any) {
      setError(cause.message);
    } finally {
      setAssessing(false);
    }
  }

  if (loading) return <Carregando />;
  if (error && !disease) return <Erro mensagem={error} />;
  if (!disease) return <Erro mensagem="Doença não encontrada." />;

  return (
    <>
      <p className="eyebrow">{disease.area.replaceAll("_", " ")} · versão {disease.version}</p>
      <h1>{disease.name}</h1>
      <p style={{ maxWidth: "78ch", color: "var(--texto-secundario)" }}>{disease.summary}</p>
      <div className="painel__temas" style={{ marginTop: "0.7rem" }}>
        <Link className="painel__tema" to="/doencas">← Voltar ao guia</Link>
        {disease.assistant_questions.length > 0 && (
          <button
            type="button"
            className="painel__tema"
            onClick={() => setParams(assistantMode ? {} : { modo: "assistente" })}
            style={assistantMode ? { borderColor: "var(--acento)", fontWeight: 700 } : undefined}
          >
            {assistantMode ? "Ver conteúdo" : "Abrir assistente"}
          </button>
        )}
      </div>

      {error && <Erro mensagem={error} />}

      {assistantMode && disease.assistant_questions.length > 0 ? (
        <>
          <section className="cartao" style={{ marginTop: "1rem" }}>
            <h2>Contexto do atendimento</h2>
            <div className="painel__temas">
              <button type="button" className="painel__tema" onClick={() => setContext("ambulatorio")} style={context === "ambulatorio" ? { borderColor: "var(--acento)" } : undefined}>Consultório / ambulatório</button>
              <button type="button" className="painel__tema" onClick={() => setContext("emergencia")} style={context === "emergencia" ? { borderColor: "var(--acento)" } : undefined}>Emergência</button>
            </div>
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
                      <select value={String(answers[question.id] ?? "")} onChange={(event) => updateAnswer(question, event.target.value === "true")} style={{ marginTop: "0.35rem" }}>
                        <option value="">Selecione…</option>
                        <option value="true">Sim</option>
                        <option value="false">Não</option>
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
                        <option value="">Selecione…</option>
                        {(question.options || []).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
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

          <button className="botao" style={{ marginTop: "1rem" }} onClick={assess} disabled={assessing}>{assessing ? "Analisando…" : "Organizar avaliação"}</button>

          {assessment && (
            <section className="cartao" style={{ marginTop: "1rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", alignItems: "center" }}>
                <h2>Resultado estruturado</h2>
                <RiskBadge risk={assessment.risk} />
              </div>
              {assessment.incomplete && <p><strong>Avaliação incompleta:</strong> preencha os campos obrigatórios destacados.</p>}
              <ListBlock title="Sinais de alarme" items={assessment.red_flags} alert />
              <ListBlock title="Elementos que apoiam a hipótese" items={assessment.supporting} />
              <ListBlock title="Elementos que enfraquecem a hipótese" items={assessment.opposing} />
              <ListBlock title="Informações ausentes" items={assessment.missing_information} />
              <ListBlock title="Exames que podem ser considerados" items={assessment.suggested_tests} />
              <ListBlock title="Diagnósticos diferenciais" items={assessment.differentials} />
              <ListBlock title="Fluxo sugerido" items={assessment.recommended_flow} />
              <p style={{ marginTop: "1rem", fontSize: "0.82rem", color: "var(--texto-secundario)" }}>{assessment.disclaimer}</p>
            </section>
          )}
        </>
      ) : (
        <>
          {disease.epidemiology && <section className="cartao" style={{ marginTop: "1rem" }}><h2>Epidemiologia e relevância</h2><p>{disease.epidemiology}</p></section>}
          <ListBlock title="Apresentação clínica" items={disease.presentation} />
          <ListBlock title="Red flags" items={disease.red_flags} alert />
          <StructuredBlock title="Abordagem diagnóstica" value={disease.diagnostic_approach} />
          <ListBlock title="Exames" items={disease.tests} />
          <ListBlock title="Diagnósticos diferenciais" items={disease.differentials} />
          <ListBlock title="Fluxo ambulatorial" items={disease.ambulatory_flow} />
          <ListBlock title="Fluxo de emergência" items={disease.emergency_flow} />
          {disease.treatment_summary && <section className="cartao" style={{ marginTop: "0.8rem" }}><h2>Tratamento e princípios de manejo</h2><p>{disease.treatment_summary}</p></section>}
          <ListBlock title="Monitorização e seguimento" items={disease.monitoring} />
          <ListBlock title="Populações e situações especiais" items={disease.special_populations} />
        </>
      )}

      {(disease.related_document_slugs.length > 0 || disease.patient_material_slug) && (
        <section className="cartao" style={{ marginTop: "1rem" }}>
          <h2>Conteúdo diretamente relacionado</h2>
          <div className="painel__temas">
            {disease.related_document_slugs.map((documentSlug) => (
              <Link className="painel__tema" key={documentSlug} to={`/biblioteca/${documentSlug}`}>
                {labelOfSlug(documentSlug)}
              </Link>
            ))}
            {disease.patient_material_slug && (
              <Link className="painel__tema" to={`/material-paciente/${disease.patient_material_slug}`}>
                Material ao paciente: {labelOfSlug(disease.patient_material_slug)}
              </Link>
            )}
          </div>
        </section>
      )}

      <GrafoRelacionados entityType="doenca" slug={disease.slug} />

      <section className="cartao" style={{ marginTop: "1rem" }}>
        <h2>Fontes e revisão</h2>
        <ul>{disease.source_refs.map((reference) => <li key={reference}>{reference}</li>)}</ul>
        <div className="painel__temas">
          {disease.source_urls.map((url) => <a key={url} href={url} target="_blank" rel="noopener noreferrer" className="painel__tema">Abrir fonte original</a>)}
        </div>
        <p style={{ fontSize: "0.8rem", color: "var(--texto-secundario)" }}>Status editorial: {disease.review_status}. {disease.review_note}</p>
      </section>
    </>
  );
}
