import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { Carregando, Vazio } from "../components/Estado";
import PatientPrescricao from "../components/PatientPrescricao";
import PatientDocumentos from "../components/PatientDocumentos";
import PatientTimeline from "../components/PatientTimeline";

type Problema = { id: number; label: string; status: string };
type Sugestao = {
  id: number; created_at: string; model: string;
  differential_diagnosis: string; suggested_workup: string;
  treatment_considerations: string;
  // `rota`/`entity_type` vêm de montar_contexto() (app/services/rag.py) desde
  // 03/09/2026 — analisar_caso() só repassa o que recuperar()/montar_contexto()
  // já produzem, sem montar URL própria. Opcionais para tolerar resposta em
  // cache de sessão anterior a essa correção.
  sources: { slug: string; titulo: string; rota?: string | null; entity_type?: string | null }[];
  sources_pubmed: { pmid: string; titulo: string; autores: string; revista: string; ano: string; url: string }[];
};
type Paciente = {
  id: number; record_number: string; initials: string; bed: string | null;
  unit: string | null; plan: string | null; pending: string[];
  medications: string[]; problems: Problema[]; labs: Record<string, string | number>;
  chief_complaint: string | null; anamnesis: string | null; physical_exam: string | null;
  cardiac_exam: Record<string, string | boolean>;
  vital_signs: Record<string, string | number>; imaging: string | null;
  diagnostic_hypothesis: string[];
};

export default function Round() {
  const [lista, setLista] = useState<Paciente[] | null>(null);
  const [aberto, setAberto] = useState<number | null>(null);
  const [novo, setNovo] = useState({ record_number: "", initials: "", bed: "", unit: "" });
  const [resumo, setResumo] = useState<string | null>(null);
  const [form, setForm] = useState({
    chief_complaint: "", anamnesis: "", physical_exam: "", imaging: "",
    pa_sistolica: "", pa_diastolica: "", fc: "", fr: "", temperatura: "", spo2: "",
    labs_texto: "", hipoteses_texto: "",
    ritmo: "regular", bulhas: "normofoneticas", b3: false, b4: false,
    sopro: false, sopro_detalhes: "", ictus: "", turgencia_jugular: "ausente",
    edema_mmii: "ausente", pulsos_perifericos: "", perfusao_periferica: "",
  });
  const [salvando, setSalvando] = useState(false);
  const [sugestoes, setSugestoes] = useState<Sugestao[] | null>(null);
  const [gerando, setGerando] = useState(false);
  const [erroIA, setErroIA] = useState("");

  const recarregar = () => api.get<Paciente[]>("/round/patients").then(setLista);
  useEffect(() => { recarregar(); }, []);

  function abrir(p: Paciente) {
    if (aberto === p.id) { setAberto(null); return; }
    setAberto(p.id);
    setForm({
      chief_complaint: p.chief_complaint ?? "", anamnesis: p.anamnesis ?? "",
      physical_exam: p.physical_exam ?? "", imaging: p.imaging ?? "",
      pa_sistolica: String(p.vital_signs?.pa_sistolica ?? ""),
      pa_diastolica: String(p.vital_signs?.pa_diastolica ?? ""),
      fc: String(p.vital_signs?.fc ?? ""), fr: String(p.vital_signs?.fr ?? ""),
      temperatura: String(p.vital_signs?.temperatura ?? ""), spo2: String(p.vital_signs?.spo2 ?? ""),
      labs_texto: Object.entries(p.labs ?? {}).map(([k, v]) => `${k}: ${v}`).join("\n"),
      hipoteses_texto: (p.diagnostic_hypothesis ?? []).join("\n"),
      ritmo: String(p.cardiac_exam?.ritmo ?? "regular"),
      bulhas: String(p.cardiac_exam?.bulhas ?? "normofoneticas"),
      b3: Boolean(p.cardiac_exam?.b3), b4: Boolean(p.cardiac_exam?.b4),
      sopro: Boolean(p.cardiac_exam?.sopro),
      sopro_detalhes: String(p.cardiac_exam?.sopro_detalhes ?? ""),
      ictus: String(p.cardiac_exam?.ictus ?? ""),
      turgencia_jugular: String(p.cardiac_exam?.turgencia_jugular ?? "ausente"),
      edema_mmii: String(p.cardiac_exam?.edema_mmii ?? "ausente"),
      pulsos_perifericos: String(p.cardiac_exam?.pulsos_perifericos ?? ""),
      perfusao_periferica: String(p.cardiac_exam?.perfusao_periferica ?? ""),
    });
    setSugestoes(null);
    setErroIA("");
    api.get<Sugestao[]>(`/round/patients/${p.id}/ai-assist`).then(setSugestoes).catch(() => setSugestoes([]));
  }

  async function salvarClinico(id: number) {
    setSalvando(true);
    const vital_signs: Record<string, number> = {};
    for (const campo of ["pa_sistolica", "pa_diastolica", "fc", "fr", "temperatura", "spo2"] as const) {
      const valor = form[campo];
      if (valor.trim()) vital_signs[campo] = Number(valor);
    }
    try {
      const labs: Record<string, string> = {};
      form.labs_texto.split("\n").forEach((linha) => {
        const [nome, ...resto] = linha.split(":");
        if (nome?.trim() && resto.length) labs[nome.trim()] = resto.join(":").trim();
      });
      const diagnostic_hypothesis = form.hipoteses_texto.split("\n").map((h) => h.trim()).filter(Boolean);
      const cardiac_exam = {
        ritmo: form.ritmo, bulhas: form.bulhas, b3: form.b3, b4: form.b4,
        sopro: form.sopro, sopro_detalhes: form.sopro ? form.sopro_detalhes : "",
        ictus: form.ictus, turgencia_jugular: form.turgencia_jugular,
        edema_mmii: form.edema_mmii, pulsos_perifericos: form.pulsos_perifericos,
        perfusao_periferica: form.perfusao_periferica,
      };

      await api.patch(`/round/patients/${id}`, {
        chief_complaint: form.chief_complaint || null,
        anamnesis: form.anamnesis || null,
        physical_exam: form.physical_exam || null,
        cardiac_exam,
        imaging: form.imaging || null,
        vital_signs,
        labs,
        diagnostic_hypothesis,
      });
      recarregar();
    } finally {
      setSalvando(false);
    }
  }

  async function pedirAuxilioIA(id: number) {
    setGerando(true);
    setErroIA("");
    try {
      const nova = await api.post<Sugestao>(`/round/patients/${id}/ai-assist`, {});
      setSugestoes((s) => [nova, ...(s ?? [])]);
    } catch (e) {
      setErroIA(e instanceof Error ? e.message : "Não foi possível gerar o auxílio de IA agora.");
    } finally {
      setGerando(false);
    }
  }

  async function adicionar() {
    await api.post("/round/patients", {
      record_number: novo.record_number.trim(),
      initials: novo.initials.trim().toUpperCase(),
      bed: novo.bed || null,
      unit: novo.unit || null,
    });
    setNovo({ record_number: "", initials: "", bed: "", unit: "" });
    recarregar();
  }

  async function gerarResumo(id: number) {
    const r = await api.get<{ text: string }>(`/round/patients/${id}/summary`);
    setResumo(r.text);
  }

  if (!lista) return <Carregando />;

  return (
    <>
      <p className="eyebrow">Round hospitalar</p>
      <h1>Pacientes internados</h1>
      <p className="aviso" style={{ borderTop: "none", marginTop: 0 }}>
        Registre apenas iniciais e número de prontuário. Nome completo não é armazenado.
      </p>

      <div className="cartao" style={{ marginTop: "1rem" }}>
        <p className="eyebrow">Adicionar paciente</p>
        <div className="grade grade--2" style={{ marginTop: "0.6rem" }}>
          <div>
            <label htmlFor="pront">Prontuário</label>
            <input id="pront" value={novo.record_number}
                   onChange={(e) => setNovo({ ...novo, record_number: e.target.value })} />
          </div>
          <div>
            <label htmlFor="ini">Iniciais</label>
            <input id="ini" value={novo.initials}
                   onChange={(e) => setNovo({ ...novo, initials: e.target.value })} />
          </div>
          <div>
            <label htmlFor="unid">Unidade</label>
            <input id="unid" placeholder="UTI, enfermaria, coronariana" value={novo.unit}
                   onChange={(e) => setNovo({ ...novo, unit: e.target.value })} />
          </div>
          <div>
            <label htmlFor="leito">Leito</label>
            <input id="leito" value={novo.bed}
                   onChange={(e) => setNovo({ ...novo, bed: e.target.value })} />
          </div>
        </div>
        <button className="botao" style={{ marginTop: "0.9rem" }} onClick={adicionar}
                disabled={!novo.record_number || !novo.initials}>
          Adicionar
        </button>
      </div>

      {lista.length === 0 ? (
        <div style={{ marginTop: "1.2rem" }}>
          <Vazio titulo="Nenhum paciente no round" acao="Adicione o primeiro paciente acima." />
        </div>
      ) : (
        <div className="grade" style={{ marginTop: "1.2rem" }}>
          {lista.map((p) => (
            <div key={p.id} className="cartao cartao--clinico">
              <div style={{ display: "flex", gap: 10, alignItems: "baseline" }}>
                <strong className="dado">{p.bed ?? "—"}</strong>
                <strong>{p.initials}</strong>
                <span className="eyebrow">prontuário {p.record_number}</span>
                <button className="botao botao--secundario"
                        style={{ marginLeft: "auto", padding: "0.3rem 0.7rem", fontSize: "0.8rem" }}
                        onClick={() => abrir(p)}>
                  {aberto === p.id ? "Fechar" : "Abrir"}
                </button>
              </div>

              {p.problems.length > 0 && (
                <ul style={{ margin: "0.6rem 0 0", paddingLeft: "1.1rem", fontSize: "0.9rem" }}>
                  {p.problems.filter((x) => x.status === "ativo").map((x) => (
                    <li key={x.id}>{x.label}</li>
                  ))}
                </ul>
              )}

              {aberto === p.id && (
                <div style={{ marginTop: "0.9rem", display: "flex", flexDirection: "column", gap: "0.7rem" }}>
                  <p style={{ fontSize: "0.9rem", margin: 0 }}>
                    <strong>Plano:</strong> {p.plan ?? "não registrado"}
                  </p>

                  <div>
                    <label htmlFor={`qp-${p.id}`}>Queixa principal</label>
                    <input id={`qp-${p.id}`} value={form.chief_complaint}
                           onChange={(e) => setForm({ ...form, chief_complaint: e.target.value })} />
                  </div>

                  <div className="grade" style={{ gridTemplateColumns: "repeat(3, 1fr)", gap: "0.5rem" }}>
                    <div>
                      <label htmlFor={`pas-${p.id}`}>PA sist.</label>
                      <input id={`pas-${p.id}`} inputMode="numeric" value={form.pa_sistolica}
                             onChange={(e) => setForm({ ...form, pa_sistolica: e.target.value })} />
                    </div>
                    <div>
                      <label htmlFor={`pad-${p.id}`}>PA diast.</label>
                      <input id={`pad-${p.id}`} inputMode="numeric" value={form.pa_diastolica}
                             onChange={(e) => setForm({ ...form, pa_diastolica: e.target.value })} />
                    </div>
                    <div>
                      <label htmlFor={`fc-${p.id}`}>FC</label>
                      <input id={`fc-${p.id}`} inputMode="numeric" value={form.fc}
                             onChange={(e) => setForm({ ...form, fc: e.target.value })} />
                    </div>
                    <div>
                      <label htmlFor={`fr-${p.id}`}>FR</label>
                      <input id={`fr-${p.id}`} inputMode="numeric" value={form.fr}
                             onChange={(e) => setForm({ ...form, fr: e.target.value })} />
                    </div>
                    <div>
                      <label htmlFor={`tax-${p.id}`}>Tax (°C)</label>
                      <input id={`tax-${p.id}`} inputMode="decimal" value={form.temperatura}
                             onChange={(e) => setForm({ ...form, temperatura: e.target.value })} />
                    </div>
                    <div>
                      <label htmlFor={`spo2-${p.id}`}>SpO₂ (%)</label>
                      <input id={`spo2-${p.id}`} inputMode="numeric" value={form.spo2}
                             onChange={(e) => setForm({ ...form, spo2: e.target.value })} />
                    </div>
                  </div>

                  <div>
                    <label htmlFor={`anam-${p.id}`}>Anamnese</label>
                    <textarea id={`anam-${p.id}`} rows={3} value={form.anamnesis}
                              onChange={(e) => setForm({ ...form, anamnesis: e.target.value })} />
                  </div>
                  <div>
                    <label htmlFor={`ef-${p.id}`}>Exame físico geral</label>
                    <textarea id={`ef-${p.id}`} rows={2} value={form.physical_exam}
                              placeholder="Achados fora do foco cardiológico — pele, respiratório, abdome…"
                              onChange={(e) => setForm({ ...form, physical_exam: e.target.value })} />
                  </div>

                  <div className="cartao" style={{ background: "var(--fundo)" }}>
                    <p className="eyebrow" style={{ margin: 0 }}>Exame físico cardiológico</p>
                    <div className="grade grade--2" style={{ marginTop: "0.5rem", gap: "0.5rem" }}>
                      <div>
                        <label htmlFor={`ritmo-${p.id}`}>Ritmo</label>
                        <select id={`ritmo-${p.id}`} value={form.ritmo}
                                onChange={(e) => setForm({ ...form, ritmo: e.target.value })}>
                          <option value="regular">Regular</option>
                          <option value="irregular">Irregular</option>
                        </select>
                      </div>
                      <div>
                        <label htmlFor={`bulhas-${p.id}`}>Bulhas</label>
                        <select id={`bulhas-${p.id}`} value={form.bulhas}
                                onChange={(e) => setForm({ ...form, bulhas: e.target.value })}>
                          <option value="normofoneticas">Normofonéticas</option>
                          <option value="hipofoneticas">Hipofonéticas</option>
                          <option value="hiperfoneticas">Hiperfonéticas</option>
                        </select>
                      </div>
                    </div>

                    <div style={{ display: "flex", gap: 16, marginTop: "0.6rem" }}>
                      <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.88rem" }}>
                        <input type="checkbox" checked={form.b3}
                               onChange={(e) => setForm({ ...form, b3: e.target.checked })} />
                        B3
                      </label>
                      <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.88rem" }}>
                        <input type="checkbox" checked={form.b4}
                               onChange={(e) => setForm({ ...form, b4: e.target.checked })} />
                        B4
                      </label>
                      <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.88rem" }}>
                        <input type="checkbox" checked={form.sopro}
                               onChange={(e) => setForm({ ...form, sopro: e.target.checked })} />
                        Sopro
                      </label>
                    </div>

                    {form.sopro && (
                      <div style={{ marginTop: "0.5rem" }}>
                        <label htmlFor={`sopro-${p.id}`}>
                          Detalhes do sopro <span className="eyebrow">(foco, intensidade, timing, irradiação)</span>
                        </label>
                        <input id={`sopro-${p.id}`} value={form.sopro_detalhes}
                               placeholder="Ex.: sistólico, foco mitral, 3+/6, irradia para axila"
                               onChange={(e) => setForm({ ...form, sopro_detalhes: e.target.value })} />
                      </div>
                    )}

                    <div style={{ marginTop: "0.5rem" }}>
                      <label htmlFor={`ictus-${p.id}`}>Ictus cordis</label>
                      <input id={`ictus-${p.id}`} value={form.ictus}
                             placeholder="Ex.: normolocalizado, normodinâmico"
                             onChange={(e) => setForm({ ...form, ictus: e.target.value })} />
                    </div>

                    <div className="grade grade--2" style={{ marginTop: "0.5rem", gap: "0.5rem" }}>
                      <div>
                        <label htmlFor={`tj-${p.id}`}>Turgência jugular</label>
                        <select id={`tj-${p.id}`} value={form.turgencia_jugular}
                                onChange={(e) => setForm({ ...form, turgencia_jugular: e.target.value })}>
                          <option value="ausente">Ausente</option>
                          <option value="presente 45°">Presente a 45°</option>
                          <option value="presente 90°">Presente a 90°</option>
                        </select>
                      </div>
                      <div>
                        <label htmlFor={`edema-${p.id}`}>Edema de MMII</label>
                        <select id={`edema-${p.id}`} value={form.edema_mmii}
                                onChange={(e) => setForm({ ...form, edema_mmii: e.target.value })}>
                          <option value="ausente">Ausente</option>
                          <option value="+1/4">+1/4</option>
                          <option value="+2/4">+2/4</option>
                          <option value="+3/4">+3/4</option>
                          <option value="+4/4">+4/4</option>
                        </select>
                      </div>
                    </div>

                    <div style={{ marginTop: "0.5rem" }}>
                      <label htmlFor={`pulsos-${p.id}`}>Pulsos periféricos</label>
                      <input id={`pulsos-${p.id}`} value={form.pulsos_perifericos}
                             placeholder="Ex.: cheios e simétricos em quatro membros"
                             onChange={(e) => setForm({ ...form, pulsos_perifericos: e.target.value })} />
                    </div>
                    <div style={{ marginTop: "0.5rem" }}>
                      <label htmlFor={`perfusao-${p.id}`}>Perfusão periférica</label>
                      <input id={`perfusao-${p.id}`} value={form.perfusao_periferica}
                             placeholder="Ex.: TEC < 2s, extremidades quentes"
                             onChange={(e) => setForm({ ...form, perfusao_periferica: e.target.value })} />
                    </div>
                  </div>
                  <div>
                    <label htmlFor={`img-${p.id}`}>Achados de imagem</label>
                    <textarea id={`img-${p.id}`} rows={2} value={form.imaging}
                              onChange={(e) => setForm({ ...form, imaging: e.target.value })} />
                  </div>
                  <div>
                    <label htmlFor={`labs-${p.id}`}>
                      Exames laboratoriais <span className="eyebrow">(um por linha, "nome: valor")</span>
                    </label>
                    <textarea id={`labs-${p.id}`} rows={3} placeholder={"Troponina: 0,8 ng/mL\nCreatinina: 1,1 mg/dL"}
                              value={form.labs_texto}
                              onChange={(e) => setForm({ ...form, labs_texto: e.target.value })} />
                  </div>
                  <div>
                    <label htmlFor={`hip-${p.id}`}>
                      Hipóteses já aventadas pela equipe <span className="eyebrow">(uma por linha, opcional)</span>
                    </label>
                    <textarea id={`hip-${p.id}`} rows={2}
                              value={form.hipoteses_texto}
                              onChange={(e) => setForm({ ...form, hipoteses_texto: e.target.value })} />
                  </div>

                  <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                    <button className="botao botao--secundario" onClick={() => salvarClinico(p.id)}
                            disabled={salvando}>
                      {salvando ? "Salvando…" : "Salvar dados clínicos"}
                    </button>
                    <button className="botao botao--secundario" onClick={() => gerarResumo(p.id)}>
                      Gerar resumo
                    </button>
                  </div>

                  <div className="cartao" style={{ background: "var(--fundo)" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <p className="eyebrow" style={{ margin: 0 }}>Auxílio de IA</p>
                      <button className="botao" style={{ padding: "0.35rem 0.75rem", fontSize: "0.82rem" }}
                              onClick={() => pedirAuxilioIA(p.id)} disabled={gerando}>
                        {gerando ? "Analisando…" : "Gerar sugestão"}
                      </button>
                    </div>
                    <p className="aviso" style={{ borderTop: "none", margin: "0.4rem 0 0", padding: 0 }}>
                      Sugestão de IA para sua avaliação — nunca substitui julgamento clínico.
                      Dados enviados não incluem nome, iniciais, prontuário, leito ou data de nascimento.
                    </p>
                    {erroIA && <p style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erroIA}</p>}

                    {sugestoes === null ? (
                      <p style={{ fontSize: "0.86rem", color: "var(--texto-secundario)" }}>Carregando…</p>
                    ) : sugestoes.length === 0 ? (
                      <p style={{ fontSize: "0.86rem", color: "var(--texto-secundario)" }}>
                        Nenhuma sugestão gerada ainda para este paciente.
                      </p>
                    ) : (
                      sugestoes.map((s) => (
                        <div key={s.id} style={{ marginTop: "0.8rem", borderTop: "1px solid var(--borda)", paddingTop: "0.6rem" }}>
                          <p className="eyebrow" style={{ margin: 0 }}>
                            {new Date(s.created_at).toLocaleString("pt-BR")} · {s.model}
                          </p>
                          <p style={{ fontSize: "0.88rem", margin: "0.4rem 0 0" }}><strong>Hipóteses diagnósticas</strong></p>
                          <p style={{ fontSize: "0.88rem", whiteSpace: "pre-wrap" }}>{s.differential_diagnosis}</p>
                          <p style={{ fontSize: "0.88rem", margin: "0.4rem 0 0" }}><strong>Investigação sugerida</strong></p>
                          <p style={{ fontSize: "0.88rem", whiteSpace: "pre-wrap" }}>{s.suggested_workup}</p>
                          <p style={{ fontSize: "0.88rem", margin: "0.4rem 0 0" }}><strong>Considerações terapêuticas</strong></p>
                          <p style={{ fontSize: "0.88rem", whiteSpace: "pre-wrap" }}>{s.treatment_considerations}</p>
                          {s.sources.length > 0 && (
                            <p style={{ fontSize: "0.78rem", color: "var(--texto-secundario)" }}>
                              Fontes:{" "}
                              {s.sources.map((f, i) => {
                                const href = f.rota && f.rota.startsWith("/") ? f.rota : `/biblioteca/${f.slug}`;
                                return (
                                  <span key={`${f.entity_type ?? "documento"}-${f.slug}`}>
                                    {i > 0 && ", "}
                                    <Link to={href}>{f.titulo}</Link>
                                  </span>
                                );
                              })}
                            </p>
                          )}
                          {s.sources_pubmed && s.sources_pubmed.length > 0 && (
                            <p style={{ fontSize: "0.78rem", color: "var(--texto-secundario)" }}>
                              Literatura pública (PubMed): {s.sources_pubmed.map((f) => (
                                <a key={f.pmid} href={f.url} target="_blank" rel="noopener noreferrer" style={{ marginRight: 6 }}>
                                  {f.titulo} ({f.ano})
                                </a>
                              ))}
                            </p>
                          )}
                        </div>
                      ))
                    )}
                  </div>

                  <PatientPrescricao patientId={p.id} />
                  <PatientDocumentos patientId={p.id} />
                  <PatientTimeline patientId={p.id} />
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {resumo && (
        <div className="cartao" style={{ marginTop: "1.2rem" }}>
          <p className="eyebrow">Resumo</p>
          <pre style={{ whiteSpace: "pre-wrap", fontFamily: "var(--fonte-dados)", fontSize: "0.84rem" }}>
            {resumo}
          </pre>
          <button className="botao botao--secundario"
                  onClick={() => navigator.clipboard.writeText(resumo)}>
            Copiar
          </button>
        </div>
      )}
    </>
  );
}
