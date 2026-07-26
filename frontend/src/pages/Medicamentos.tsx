import { useEffect, useMemo, useState } from "react";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";
import { Carregando, SeloRevisao, Vazio } from "../components/Estado";

type Item = { slug: string; generic_name: string; drug_class: string; review_status: string };
type Detalhe = Record<string, any>;

// A classe salva no banco é bem específica (ex.: "Betabloqueador cardiosseletivo
// (beta-1 seletivo), hidrofílico" — só do Atenolol), então filtrar pelo texto
// exato não agruparia nada. Isto reconhece a classe ampla pela presença de
// palavras-chave. Ordem importa: grupos mais específicos vêm antes dos genéricos.
const GRUPOS_AMPLOS: [string, string[]][] = [
  ["Antagonista mineralocorticoide", ["mineralocorticoide", "poupador de potássio"]],
  ["IECA", ["enzima conversora de angiotensina"]],
  ["BRA", ["receptor de angiotensina ii", "bra/ara"]],
  ["ARNI", ["neprilisina"]],
  ["Betabloqueador", ["betabloqueador"]],
  ["Bloqueador de canal de cálcio", ["canal de cálcio"]],
  ["Diurético", ["diurético", "diuretico"]],
  ["Anticoagulante", ["anticoagulante", "heparina", "hbpm"]],
  ["Antiagregante/antiplaquetário", ["antiagregante", "antiplaquetário"]],
  ["Estatina/hipolipemiante", ["estatina", "hipolipemiante", "pcsk9", "angptl3",
                               "absorção de colesterol"]],
  ["Antiarrítmico", ["antiarrítmico"]],
  ["Nitrato/vasodilatador", ["nitrato", "vasodilatador"]],
  ["Glicosídeo cardíaco", ["glicosídeo cardíaco", "digitálico"]],
  ["iSGLT2/antidiabético", ["cotransportador sódio-glicose", "glp-1", "biguanida"]],
  ["Inotrópico/vasopressor", ["inotrópico", "catecolamina", "vasopressor"]],
  ["Agonista alfa-2 central", ["alfa-2 adrenérgico"]],
];

function classeAmpla(drugClass: string): string {
  const alvo = drugClass.toLowerCase();
  for (const [grupo, chaves] of GRUPOS_AMPLOS) {
    if (chaves.some((c) => alvo.includes(c))) return grupo;
  }
  return "Outros";
}

function GraficoMeiaVida({ drogas, admin, aoSalvar }: {
  drogas: Detalhe[]; admin: boolean; aoSalvar: () => void;
}) {
  const comDado = drogas.filter((d) => typeof d.half_life_hours === "number");
  const max = Math.max(1, ...comDado.map((d) => d.half_life_hours as number));
  const [editando, setEditando] = useState<string | null>(null);
  const [valor, setValor] = useState("");

  async function salvar(slug: string) {
    const numero = valor.trim() ? Number(valor.replace(",", ".")) : null;
    await api.patch(`/drugs/${slug}/meia-vida`, { half_life_hours: numero });
    setEditando(null);
    aoSalvar();
  }

  return (
    <div className="cartao" style={{ marginTop: "1rem" }}>
      <p className="eyebrow">Meia-vida de eliminação</p>
      <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: "0.6rem" }}>
        {drogas.map((d) => {
          const valorAtual = d.half_life_hours as number | null;
          const pct = valorAtual ? Math.max(4, (valorAtual / max) * 100) : 0;
          return (
            <div key={d.slug}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.86rem" }}>
                <span>{d.generic_name}</span>
                <span className="dado" style={{ color: "var(--cinza-texto)" }}>
                  {valorAtual ? `${valorAtual} h` : "sem dado"}
                </span>
              </div>
              <div style={{
                background: "var(--cinza-fundo)", borderRadius: 5, height: 18, marginTop: 4,
                border: "1px solid var(--cinza-borda)", overflow: "hidden",
              }}>
                {valorAtual !== null && (
                  <div style={{
                    width: `${pct}%`, height: "100%", background: "var(--bordo)",
                    borderRadius: 4, transition: "width 0.3s",
                  }} />
                )}
              </div>
              {admin && (
                editando === d.slug ? (
                  <div style={{ display: "flex", gap: 6, marginTop: 4 }}>
                    <input
                      autoFocus type="text" inputMode="decimal" placeholder="horas, ex.: 8.5"
                      value={valor} onChange={(e) => setValor(e.target.value)}
                      style={{ maxWidth: 120, padding: "0.2rem 0.4rem", fontSize: "0.82rem" }}
                    />
                    <button className="botao" style={{ padding: "0.2rem 0.6rem", fontSize: "0.8rem" }}
                            onClick={() => salvar(d.slug)}>Salvar</button>
                    <button className="botao botao--secundario" style={{ padding: "0.2rem 0.6rem", fontSize: "0.8rem" }}
                            onClick={() => setEditando(null)}>Cancelar</button>
                  </div>
                ) : (
                  <button
                    className="botao botao--secundario"
                    style={{ padding: "0.1rem 0.5rem", fontSize: "0.76rem", marginTop: 4 }}
                    onClick={() => { setEditando(d.slug); setValor(valorAtual ? String(valorAtual) : ""); }}
                  >
                    {valorAtual ? "Editar" : "Preencher"}
                  </button>
                )
              )}
            </div>
          );
        })}
      </div>
      {comDado.length === 0 && (
        <p style={{ color: "var(--cinza-texto)", fontSize: "0.9rem", marginTop: "0.5rem" }}>
          Nenhum dos medicamentos selecionados tem meia-vida cadastrada ainda.
          {admin ? " Use os botões abaixo pra preencher." : " Peça a um administrador para preencher."}
        </p>
      )}
      {comDado.length < drogas.length && comDado.length > 0 && (
        <p className="aviso">
          Valor por medicamento, a partir da bula ou referência farmacocinética — não extraído
          automaticamente. {admin ? "Preencha acima." : "Peça a um administrador para preencher."}
        </p>
      )}
    </div>
  );
}

function BarraComparativa({ rotulo, valor, unidade, max, cor }: {
  rotulo: string; valor: number | null; unidade: string; max: number; cor: string;
}) {
  const pct = valor !== null ? Math.max(6, (valor / max) * 100) : 0;
  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.86rem" }}>
        <span>{rotulo}</span>
        <span className="dado" style={{ color: "var(--cinza-texto)" }}>
          {valor !== null ? `${valor} ${unidade}` : "sem dado"}
        </span>
      </div>
      <div style={{
        background: "var(--cinza-fundo)", borderRadius: 5, height: 18, marginTop: 4,
        border: "1px solid var(--cinza-borda)", overflow: "hidden",
      }}>
        {valor !== null && (
          <div style={{
            width: `${pct}%`, height: "100%", background: cor,
            borderRadius: 4, transition: "width 0.3s",
          }} />
        )}
      </div>
    </div>
  );
}

function GraficoEficaciaPA({ drogas }: { drogas: Detalhe[] }) {
  const comDado = drogas.filter((d) => typeof d.sbp_reduction_mmhg === "number");
  const max = Math.max(1, ...comDado.map((d) => d.sbp_reduction_mmhg as number));

  return (
    <div className="cartao" style={{ marginTop: "1rem" }}>
      <p className="eyebrow">Redução média de pressão arterial (PAS/PAD, mmHg)</p>

      {comDado.length === 0 ? (
        <p style={{ color: "var(--cinza-texto)", fontSize: "0.9rem", marginTop: "0.5rem" }}>
          Nenhum dos medicamentos selecionados tem dado de eficácia anti-hipertensiva
          cadastrado ainda — cobrimos só os principais anti-hipertensivos por classe até agora.
        </p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 14, marginTop: "0.7rem" }}>
          {drogas.map((d) => {
            const sbp = typeof d.sbp_reduction_mmhg === "number" ? d.sbp_reduction_mmhg : null;
            const dbp = typeof d.dbp_reduction_mmhg === "number" ? d.dbp_reduction_mmhg : null;
            return (
              <div key={d.slug}>
                <strong style={{ fontSize: "0.9rem" }}>{d.generic_name}</strong>
                <div style={{ display: "flex", flexDirection: "column", gap: 6, marginTop: 4 }}>
                  <BarraComparativa rotulo="PAS" valor={sbp} unidade="mmHg" max={max} cor="var(--bordo)" />
                  <BarraComparativa rotulo="PAD" valor={dbp} unidade="mmHg" max={max} cor="var(--dourado)" />
                </div>
              </div>
            );
          })}
        </div>
      )}

      <p className="aviso">
        Valores de dose padrão/quase-máxima, de ensaios controlados por placebo — populações e
        desenhos de estudo diferem entre fármacos, então a comparação é aproximada, não uma régua
        única. Fonte de cada valor disponível na tabela de comparação acima.
      </p>
    </div>
  );
}

const LINHAS: [string, string][] = [
  ["drug_class", "Classe"],
  ["mechanism", "Mecanismo"],

  ["dosing", "Doses"],
  ["renal_adjustment", "Ajuste renal"],
  ["hepatic_adjustment", "Ajuste hepático"],
  ["contraindications", "Contraindicações"],
  ["interactions", "Interações"],
  ["monitoring", "Monitorização"],
  ["outcomes", "Desfechos"],
  ["pregnancy", "Gestação"],
  ["lactation", "Lactação"],
  ["references", "Referências"],
];

function celula(v: unknown) {
  if (v === null || v === undefined || (Array.isArray(v) && v.length === 0)) return "—";
  if (Array.isArray(v)) return v.join("; ");
  if (typeof v === "object") {
    return Object.entries(v as object)
      .map(([k, val]) => `${k}: ${val}`)
      .join(" · ");
  }
  return String(v);
}

export default function Medicamentos() {
  const { usuario } = useAuth();
  const [todos, setTodos] = useState<Item[] | null>(null);
  const [busca, setBusca] = useState("");
  const [classe, setClasse] = useState("");
  const [sel, setSel] = useState<string[]>([]);
  const [comparacao, setComparacao] = useState<Detalhe[] | null>(null);

  useEffect(() => { api.get<Item[]>("/drugs").then(setTodos); }, []);

  const grupos = useMemo(() => {
    if (!todos) return [];
    const contagem = new Map<string, number>();
    for (const d of todos) {
      const g = classeAmpla(d.drug_class);
      contagem.set(g, (contagem.get(g) ?? 0) + 1);
    }
    return [...contagem.entries()].sort((a, b) => b[1] - a[1]);
  }, [todos]);

  const lista = useMemo(() => {
    if (!todos) return null;
    const termo = busca.trim().toLowerCase();
    return todos.filter((d) => {
      const bateBusca = !termo || d.generic_name.toLowerCase().includes(termo);
      const bateClasse = !classe || classeAmpla(d.drug_class) === classe;
      return bateBusca && bateClasse;
    });
  }, [todos, busca, classe]);

  function alternar(slug: string) {
    setComparacao(null);
    setSel((s) => (s.includes(slug) ? s.filter((x) => x !== slug) : s.length < 4 ? [...s, slug] : s));
  }

  async function comparar() {
    const qs = sel.map((s) => `slug=${encodeURIComponent(s)}`).join("&");
    const r = await api.get<{ drugs: Detalhe[] }>(`/drugs/compare?${qs}`);
    setComparacao(r.drugs);
  }

  async function recomparar() {
    const qs = sel.map((s) => `slug=${encodeURIComponent(s)}`).join("&");
    const r = await api.get<{ drugs: Detalhe[] }>(`/drugs/compare?${qs}`);
    setComparacao(r.drugs);
  }

  return (
    <>
      <p className="eyebrow">Farmacologia</p>
      <h1>Medicamentos</h1>

      <input
        value={busca}
        onChange={(e) => setBusca(e.target.value)}
        placeholder="Buscar por nome — ex.: losartana, enalapril, digoxina…"
        aria-label="Buscar medicamento"
        style={{ maxWidth: 420, marginTop: "0.8rem" }}
      />

      {grupos.length > 0 && (
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: "0.7rem" }}>
          <button
            className={`botao ${classe ? "botao--secundario" : ""}`}
            style={{ padding: "0.3rem 0.7rem", fontSize: "0.8rem" }}
            onClick={() => setClasse("")}
          >
            Todas ({todos?.length})
          </button>
          {grupos.map(([g, n]) => (
            <button
              key={g}
              className={`botao ${classe === g ? "" : "botao--secundario"}`}
              style={{ padding: "0.3rem 0.7rem", fontSize: "0.8rem" }}
              onClick={() => setClasse(g)}
            >
              {g} ({n})
            </button>
          ))}
        </div>
      )}

      {lista === null ? (
        <Carregando />
      ) : lista.length === 0 ? (
        <div style={{ marginTop: "1rem" }}>
          <Vazio
            titulo={busca || classe ? "Nenhum medicamento encontrado" : "O banco de medicamentos está vazio"}
            acao={busca || classe ? "Tente outro termo ou outra classe." : "Importe os registros pelo painel de administração."}
          />
        </div>
      ) : (
        <>
          <p style={{ color: "var(--cinza-texto)", marginTop: "0.9rem" }}>
            Selecione um medicamento para ver os detalhes, ou até 4 para comparar lado a lado.
          </p>
          <div className="grade grade--3" style={{ marginTop: "0.8rem" }}>
            {lista.map((d) => (
              <button
                key={d.slug}
                onClick={() => alternar(d.slug)}
                className="cartao"
                style={{
                  textAlign: "left",
                  cursor: "pointer",
                  borderLeft: sel.includes(d.slug) ? "3px solid var(--bordo)" : undefined,
                }}
              >
                <p className="eyebrow">{classeAmpla(d.drug_class)}</p>
                <strong>{d.generic_name}</strong>
                <div style={{ fontSize: "0.78rem", color: "var(--cinza-texto)", marginTop: 2 }}>
                  {d.drug_class}
                </div>
                <div style={{ marginTop: 6 }}><SeloRevisao status={d.review_status} /></div>
              </button>
            ))}
          </div>

          <button
            className="botao"
            style={{ marginTop: "1rem" }}
            onClick={comparar}
            disabled={sel.length < 1}
          >
            {sel.length <= 1 ? "Ver detalhes" : `Comparar (${sel.length})`}
          </button>
        </>
      )}

      {comparacao && (
        <div className="grade grade--2" style={{ marginTop: "1.4rem" }}>
          {comparacao.map((d) => (
            <div key={d.slug} className="cartao cartao--clinico">
              <p className="eyebrow">{classeAmpla(d.drug_class)}</p>
              <h3 style={{ marginBottom: "0.7rem" }}>{d.generic_name}</h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                {LINHAS.map(([campo, rotulo]) => {
                  const valor = celula(d[campo]);
                  if (valor === "—") return null;
                  return (
                    <div key={campo}>
                      <div className="eyebrow" style={{ marginBottom: 2 }}>{rotulo}</div>
                      <div style={{ fontSize: "0.9rem" }}>{valor}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}

      {comparacao && (
        <>
          <GraficoEficaciaPA drogas={comparacao} />
          <GraficoMeiaVida drogas={comparacao} admin={usuario?.role === "admin"} aoSalvar={recomparar} />
        </>
      )}
    </>
  );
}
