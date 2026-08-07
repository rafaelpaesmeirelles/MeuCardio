import { useEffect, useMemo, useState } from "react";
import { api, ApiError } from "../lib/api";

type Opcao = { value: string | number; label: string };
type Campo = { name: string; label: string; type: "boolean" | "number" | "select"; unit?: string | null; options?: Opcao[]; min?: number | null; max?: number | null; help?: string | null };
type Definicao = { slug: string; name: string; purpose: string; status: string; reference: string; limitations: string[]; fields: Campo[] };
type ResultadoApi = { result: Record<string, unknown>; interpretation: string };
export type MetodoAvancado = { selecionado: boolean; payload: Record<string, unknown>; result: Record<string, unknown> | null; interpretation: string };
export type AvancadosState = Record<string, MetodoAvancado>;
type Props = { idade: string; onChange: (state: AvancadosState) => void };
const SLUGS = ["gscri", "sort", "s-mpm"] as const;

function payloadInicial(def: Definicao, idade: string) {
  const p: Record<string, unknown> = {};
  for (const f of def.fields) {
    if (f.type === "boolean") p[f.name] = false;
    else if (f.type === "select") p[f.name] = f.options?.[0]?.value ?? "";
    else if (f.name === "idade" && idade) p[f.name] = Number(idade);
    else p[f.name] = "";
  }
  return p;
}
function valorResultado(v: unknown) { if (v == null) return "—"; if (typeof v === "boolean") return v ? "sim" : "não"; return String(v); }

export default function CalculadorasPreOperatoriasAvancadas({ idade, onChange }: Props) {
  const [defs, setDefs] = useState<Record<string, Definicao>>({});
  const [state, setState] = useState<AvancadosState>({});
  const [carregando, setCarregando] = useState(true); const [erro, setErro] = useState(""); const [calculando, setCalculando] = useState<string | null>(null);

  useEffect(() => {
    let ativo = true;
    Promise.all(SLUGS.map((slug) => api.get<Definicao>(`/calculators/${slug}`))).then((lista) => {
      if (!ativo) return; const d: Record<string, Definicao> = {}; const s: AvancadosState = {};
      for (const def of lista) { d[def.slug] = def; s[def.slug] = { selecionado: false, payload: payloadInicial(def, idade), result: null, interpretation: "" }; }
      setDefs(d); setState(s);
    }).catch(() => ativo && setErro("Não foi possível carregar as calculadoras avançadas.")).finally(() => ativo && setCarregando(false));
    return () => { ativo = false; };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => { onChange(state); }, [state, onChange]);
  useEffect(() => {
    if (!idade) return;
    setState((atual) => {
      let mudou = false; const novo: AvancadosState = { ...atual };
      for (const slug of SLUGS) {
        const m = atual[slug]; if (!m || !defs[slug]?.fields.some((f) => f.name === "idade")) continue;
        if (m.payload.idade === "" || m.payload.idade === undefined) { novo[slug] = { ...m, payload: { ...m.payload, idade: Number(idade) } }; mudou = true; }
      }
      return mudou ? novo : atual;
    });
  }, [idade, defs]);

  const ordenados = useMemo(() => SLUGS.map((s) => defs[s]).filter(Boolean), [defs]);
  function alterar(slug: string, campo: Campo, valor: string | boolean) {
    setState((atual) => {
      const m = atual[slug]; if (!m) return atual; let normalizado: unknown = valor;
      if (campo.type === "number") normalizado = valor === "" ? "" : Number(valor);
      if (campo.type === "select") normalizado = campo.options?.find((o) => String(o.value) === String(valor))?.value ?? valor;
      return { ...atual, [slug]: { ...m, payload: { ...m.payload, [campo.name]: normalizado }, result: null, interpretation: "" } };
    });
  }
  function selecionar(slug: string, selecionado: boolean) { setState((atual) => { const m = atual[slug]; if (!m) return atual; return { ...atual, [slug]: { ...m, selecionado, result: selecionado ? m.result : null, interpretation: selecionado ? m.interpretation : "" } }; }); }
  async function calcular(slug: string) {
    const m = state[slug]; if (!m) return; setCalculando(slug); setErro("");
    try { const r = await api.post<ResultadoApi>(`/calculators/${slug}/run`, m.payload); setState((atual) => ({ ...atual, [slug]: { ...atual[slug], result: r.result, interpretation: r.interpretation } })); }
    catch (e) { setErro(e instanceof ApiError ? e.message : `Não foi possível calcular ${slug}.`); } finally { setCalculando(null); }
  }
  if (carregando) return <div className="cartao" style={{ marginTop: "1rem" }}>Carregando metodologias avançadas…</div>;
  return <>{ordenados.map((def) => { const m = state[def.slug]; if (!m) return null; return <div className="cartao" style={{ marginTop: "1rem" }} key={def.slug}>
    <label style={{ display: "flex", gap: 8, alignItems: "center", fontWeight: 700 }}><input type="checkbox" checked={m.selecionado} onChange={(e) => selecionar(def.slug, e.target.checked)} />{def.name}</label>
    <p style={{ color: "var(--texto-secundario)", fontSize: "0.86rem" }}>{def.purpose}</p>
    {m.selecionado && <><div className="grade grade--2">{def.fields.map((f) => <div key={f.name}>{f.type === "boolean" ? <label style={{ display: "flex", gap: 8, alignItems: "flex-start", fontWeight: 400 }}><input type="checkbox" checked={Boolean(m.payload[f.name])} onChange={(e) => alterar(def.slug, f, e.target.checked)} /><span>{f.label}</span></label> : <><label>{f.label}{f.unit ? ` (${f.unit})` : ""}</label>{f.type === "select" ? <select value={String(m.payload[f.name] ?? "")} onChange={(e) => alterar(def.slug, f, e.target.value)}>{(f.options ?? []).map((o) => <option key={String(o.value)} value={String(o.value)}>{o.label}</option>)}</select> : <input type="number" min={f.min ?? undefined} max={f.max ?? undefined} value={String(m.payload[f.name] ?? "")} onChange={(e) => alterar(def.slug, f, e.target.value)} />}{f.help && <small style={{ color: "var(--texto-secundario)" }}>{f.help}</small>}</>}</div>)}</div>
    <button className="botao" style={{ marginTop: "0.7rem" }} onClick={() => calcular(def.slug)} disabled={calculando === def.slug}>{calculando === def.slug ? "Calculando…" : `Calcular ${def.name.split(" — ")[0]}`}</button>
    {m.result && <div style={{ marginTop: "0.7rem", borderLeft: "3px solid var(--acento)", paddingLeft: "0.75rem" }}><strong>Resultado</strong><p style={{ margin: "0.3rem 0" }}>{Object.entries(m.result).map(([k,v]) => `${k.split("_").join(" ")}: ${valorResultado(v)}`).join(" · ")}</p><p style={{ color: "var(--texto-secundario)", fontSize: "0.86rem" }}>{m.interpretation}</p></div>}
    <p style={{ color: "var(--texto-secundario)", fontSize: "0.78rem", marginBottom: 0 }}><strong>Referência:</strong> {def.reference}</p></>}
  </div>; })}{erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}</>;
}