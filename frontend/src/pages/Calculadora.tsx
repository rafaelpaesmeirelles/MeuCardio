import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../lib/api";
import { Carregando, Erro } from "../components/Estado";

type Campo = {
  name: string; label: string; type: string; unit: string | null;
  options: { value: string | number; label: string }[];
  min: number | null; max: number | null; help: string | null;
};
type Calc = {
  slug: string; name: string; theme: string; purpose: string;
  reference: string; limitations: string[]; fields: Campo[];
};
type Saida = {
  result: Record<string, unknown>; interpretation: string | null;
  reference: string; limitations: string[];
};

export default function Calculadora() {
  const { slug } = useParams();
  const [calc, setCalc] = useState<Calc | null>(null);
  const [valores, setValores] = useState<Record<string, unknown>>({});
  const [saida, setSaida] = useState<Saida | null>(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api.get<Calc>(`/calculators/${slug}`).then((c) => {
      setCalc(c);
      const iniciais: Record<string, unknown> = {};
      for (const f of c.fields) {
        if (f.type === "boolean") iniciais[f.name] = false;
        if (f.type === "select") iniciais[f.name] = f.options[0]?.value;
      }
      setValores(iniciais);
    });
  }, [slug]);

  async function calcular() {
    setErro("");
    try {
      setSaida(await api.post<Saida>(`/calculators/${slug}/run`, valores));
    } catch (e) {
      setSaida(null);
      setErro(e instanceof Error ? e.message : "Revise os valores informados.");
    }
  }

  if (!calc) return <Carregando />;

  const faltando = calc.fields.some(
    (f) => f.type === "number" && (valores[f.name] === undefined || valores[f.name] === "")
  );

  return (
    <div style={{ maxWidth: 720 }}>
      <Link to="/calculadoras" className="eyebrow">← Calculadoras</Link>
      <p className="eyebrow" style={{ marginTop: "0.8rem" }}>{calc.theme}</p>
      <h1>{calc.name}</h1>
      <p style={{ color: "var(--texto-secundario)" }}>{calc.purpose}</p>

      <div className="cartao cartao--clinico" style={{ marginTop: "1rem" }}>
        {calc.fields.map((f) => (
          <div key={f.name} style={{ marginBottom: "0.9rem" }}>
            {f.type === "boolean" ? (
              <label style={{ display: "flex", gap: 10, alignItems: "flex-start", fontWeight: 400 }}>
                <input
                  type="checkbox"
                  style={{ width: 18, height: 18, marginTop: 2, flex: "0 0 18px" }}
                  checked={Boolean(valores[f.name])}
                  onChange={(e) => setValores({ ...valores, [f.name]: e.target.checked })}
                />
                <span>
                  {f.label}
                  {f.help && (
                    <span style={{ display: "block", fontSize: "0.8rem", color: "var(--texto-secundario)" }}>
                      {f.help}
                    </span>
                  )}
                </span>
              </label>
            ) : f.type === "select" ? (
              <>
                <label htmlFor={f.name}>{f.label}</label>
                <select
                  id={f.name}
                  value={String(valores[f.name] ?? "")}
                  onChange={(e) => {
                    const opt = f.options.find((o) => String(o.value) === e.target.value);
                    setValores({ ...valores, [f.name]: opt?.value });
                  }}
                >
                  {f.options.map((o) => (
                    <option key={String(o.value)} value={String(o.value)}>{o.label}</option>
                  ))}
                </select>
              </>
            ) : (
              <>
                <label htmlFor={f.name}>
                  {f.label} {f.unit && <span className="eyebrow">({f.unit})</span>}
                </label>
                <input
                  id={f.name}
                  type="number"
                  inputMode="decimal"
                  step="any"
                  min={f.min ?? undefined}
                  max={f.max ?? undefined}
                  value={String(valores[f.name] ?? "")}
                  onChange={(e) => setValores({ ...valores, [f.name]: e.target.value })}
                />
              </>
            )}
          </div>
        ))}

        <button className="botao" onClick={calcular} disabled={faltando}>Calcular</button>
      </div>

      {erro && <div style={{ marginTop: "1rem" }}><Erro mensagem={erro} /></div>}

      {saida && (
        <div className="cartao" style={{ marginTop: "1rem", borderLeft: "3px solid var(--acento)" }}>
          <p className="eyebrow">Resultado</p>
          <p className="dado" style={{ fontSize: "2.4rem", margin: "0.2rem 0", color: "var(--acento)" }}>
            {Object.values(saida.result)[0] as string | number}
            <span style={{ fontSize: "1rem", color: "var(--texto-secundario)", marginLeft: 8 }}>
              {(saida.result.max ? `/ ${saida.result.max}` : (saida.result.unidade as string) ?? "")}
            </span>
          </p>
          {saida.interpretation && <p>{saida.interpretation}</p>}
        </div>
      )}

      <div className="aviso">
        <strong>Referência:</strong> {calc.reference}
        {calc.limitations.length > 0 && (
          <ul style={{ margin: "0.5rem 0 0", paddingLeft: "1.1rem" }}>
            {calc.limitations.map((l) => <li key={l}>{l}</li>)}
          </ul>
        )}
      </div>
    </div>
  );
}
