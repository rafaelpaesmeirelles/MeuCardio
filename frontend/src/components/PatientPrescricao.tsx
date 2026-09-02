import CabecalhoDocumento from "./CabecalhoDocumento";
import { lazy, Suspense, useEffect, useState } from "react";
import { api, PaginaDe } from "../lib/api";
import { useAuth } from "../lib/auth";

const PrescricaoLivreEspecial = lazy(() => import("./PrescricaoLivreEspecial"));

type ItemDrug = {
  drug_name: string; presentation: string; posology: string; orientation: string;
  // Tarefa B (CLAUDE.md, 02/08/2026) — escolha de marca via CMED, sempre
  // opcional: o genérico (sem estes seis campos) continua sendo o padrão.
  brand_name?: string; manufacturer?: string; ggrem?: string;
  pmc_snapshot?: number; uf?: string; cmed_version?: string;
};
type Prescricao = { id: number; items: ItemDrug[]; notes: string | null; created_at: string };
// GET /drugs/{slug}/apresentacoes?uf=XX (Tarefa A/B) — marca, laboratório,
// apresentação e PMC (teto CMED) pra escolha explícita durante a digitação.
// Mesma forma usada em Receituario.tsx — não é o `commercial_presentations`
// estático de `Drug` (esse é curado por admin à parte, e quase sempre vazio).
type PrecoCmed = { valor: number | null; rotulo: string };
type ApresentacaoCmed = {
  produto: string; laboratorio: string; apresentacao: string; ggrem: string;
  restricao_hospitalar: boolean; preco: PrecoCmed;
};
type RespostaApresentacoes = {
  uf: string | null; cmed_publicado_em: string | null;
  apresentacoes: ApresentacaoCmed[]; aviso: string | null;
};
type SugestaoFarmaco = { slug: string; generic_name: string };

export default function PatientPrescricao({ patientId }: { patientId: number }) {
  const [historico, setHistorico] = useState<Prescricao[] | null>(null);
  const [itens, setItens] = useState<ItemDrug[]>([]);
  const [busca, setBusca] = useState("");
  const [sugestoes, setSugestoes] = useState<SugestaoFarmaco[]>([]);
  const [notas, setNotas] = useState("");
  const [salvando, setSalvando] = useState(false);
  const [impressao, setImpressao] = useState<any | null>(null);
  const [escolhendo, setEscolhendo] = useState<{ nome: string; resp: RespostaApresentacoes } | null>(null);

  const { usuario } = useAuth();
  const recarregar = () => api.get<Prescricao[]>(`/prescriptions/patient/${patientId}`).then(setHistorico);
  useEffect(() => { recarregar(); }, [patientId]);

  useEffect(() => {
    if (busca.trim().length < 2) { setSugestoes([]); return; }
    const atraso = setTimeout(() => {
      api.get<PaginaDe<SugestaoFarmaco>>(`/drugs?q=${encodeURIComponent(busca)}`).then((r) => setSugestoes(r.items.slice(0, 6)));
    }, 250);
    return () => clearTimeout(atraso);
  }, [busca]);

  async function escolherMedicamento(slug: string, nome: string) {
    setBusca("");
    setSugestoes([]);
    const uf = usuario?.council_state;
    const resp = await api.get<RespostaApresentacoes>(`/drugs/${slug}/apresentacoes${uf ? `?uf=${uf}` : ""}`);
    if (resp.apresentacoes.length > 0) {
      setEscolhendo({ nome, resp });
    } else {
      adicionarItem(nome);
    }
  }

  function adicionarComApresentacao(nome: string, ap: ApresentacaoCmed, resp: RespostaApresentacoes) {
    setItens([...itens, {
      drug_name: nome,
      presentation: `${ap.produto} — ${ap.apresentacao}`,
      posology: "", orientation: "",
      brand_name: ap.produto, manufacturer: ap.laboratorio, ggrem: ap.ggrem,
      pmc_snapshot: ap.preco.valor ?? undefined,
      uf: resp.uf ?? undefined, cmed_version: resp.cmed_publicado_em ?? undefined,
    }]);
    setEscolhendo(null);
  }

  function adicionarItem(nome: string) {
    setItens([...itens, { drug_name: nome, presentation: "", posology: "", orientation: "" }]);
    setBusca("");
    setSugestoes([]);
  }

  function atualizarItem(i: number, campo: keyof ItemDrug, valor: string) {
    const copia = [...itens];
    copia[i] = { ...copia[i], [campo]: valor };
    setItens(copia);
  }

  function removerItem(i: number) {
    setItens(itens.filter((_, idx) => idx !== i));
  }

  async function salvar() {
    if (itens.length === 0) return;
    setSalvando(true);
    try {
      await api.post(`/prescriptions`, { patient_id: patientId, items: itens, notes: notas });
      setItens([]);
      setNotas("");
      recarregar();
    } finally {
      setSalvando(false);
    }
  }

  async function abrirImpressao(id: number) {
    const dados = await api.get(`/prescriptions/${id}/imprimir`);
    setImpressao(dados);
    setTimeout(() => window.print(), 200);
  }

  return (
    <>
      <Suspense fallback={null}><PrescricaoLivreEspecial /></Suspense>
      <div className="cartao" style={{ background: "var(--fundo)" }}>
        <p className="eyebrow" style={{ margin: 0 }}>Prescrição</p>

        <div style={{ position: "relative", marginTop: "0.5rem" }}>
          <input
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
            placeholder="Buscar medicamento pra adicionar…"
          />
          {sugestoes.length > 0 && (
            <div className="cartao" style={{ position: "absolute", zIndex: 5, width: "100%", padding: "0.3rem" }}>
              {sugestoes.map((s) => (
                <div key={s.slug} onClick={() => escolherMedicamento(s.slug, s.generic_name)}
                     style={{ padding: "0.4rem", cursor: "pointer", fontSize: "0.88rem" }}>
                  {s.generic_name}
                </div>
              ))}
            </div>
          )}
        </div>

        {escolhendo && (
          <div className="cartao" style={{ marginTop: "0.5rem" }}>
            <p style={{ margin: 0, fontSize: "0.88rem" }}>
              <strong>{escolhendo.nome}</strong> — escolha a marca (opcional):
            </p>
            <div style={{ maxHeight: 180, overflowY: "auto", marginTop: "0.4rem" }}>
              {escolhendo.resp.apresentacoes.map((ap, i) => (
                <button key={i} type="button"
                        style={{ display: "block", width: "100%", textAlign: "left", padding: "0.3rem 0", border: "none", borderTop: i > 0 ? "1px solid var(--borda)" : "none", background: "transparent", cursor: "pointer" }}
                        onClick={() => adicionarComApresentacao(escolhendo.nome, ap, escolhendo.resp)}>
                  <p style={{ margin: 0, fontSize: "0.86rem" }}>
                    <strong>{ap.produto}</strong> — {ap.laboratorio}
                    <br />
                    <span style={{ color: "var(--texto-secundario, #666)" }}>
                      {ap.apresentacao} · {ap.preco.valor != null
                        ? ap.preco.valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })
                        : "sem preço publicado"}
                    </span>
                  </p>
                </button>
              ))}
            </div>
            {escolhendo.resp.uf && (
              <p className="eyebrow" style={{ margin: "0.2rem 0 0" }}>
                Preço de referência para {escolhendo.resp.uf} — teto CMED (PMC), lista {escolhendo.resp.cmed_publicado_em}.
                Nunca é o preço final de farmácia, que costuma ser menor.
              </p>
            )}
            <button className="botao botao--secundario" style={{ marginTop: "0.6rem", fontSize: "0.82rem" }}
                    onClick={() => { adicionarItem(escolhendo.nome); setEscolhendo(null); }}>
              Usar genérico (sem marca)
            </button>
          </div>
        )}

        {itens.map((item, i) => (
          <div key={i} style={{ marginTop: "0.6rem", borderTop: "1px solid var(--borda)", paddingTop: "0.5rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <strong style={{ fontSize: "0.9rem" }}>{item.drug_name}</strong>
              <button className="botao botao--secundario" style={{ padding: "0.1rem 0.4rem" }} onClick={() => removerItem(i)}>✕</button>
            </div>
            <input placeholder="Apresentação (ex.: comp. 40mg)" value={item.presentation}
                   onChange={(e) => atualizarItem(i, "presentation", e.target.value)}
                   style={{ marginTop: "0.3rem" }} />
            <input placeholder="Posologia (ex.: 1 comprimido, 1x ao dia)" value={item.posology}
                   onChange={(e) => atualizarItem(i, "posology", e.target.value)}
                   style={{ marginTop: "0.3rem" }} />
            <input placeholder="Orientação (opcional)" value={item.orientation}
                   onChange={(e) => atualizarItem(i, "orientation", e.target.value)}
                   style={{ marginTop: "0.3rem" }} />
          </div>
        ))}

        {itens.length > 0 && (
          <>
            <textarea placeholder="Observações gerais (opcional)" rows={2} value={notas}
                      onChange={(e) => setNotas(e.target.value)} style={{ marginTop: "0.6rem" }} />
            <button className="botao" style={{ marginTop: "0.5rem" }} onClick={salvar} disabled={salvando}>
              {salvando ? "Salvando…" : "Salvar prescrição"}
            </button>
          </>
        )}

        {historico && historico.length > 0 && (
          <div style={{ marginTop: "0.8rem" }}>
            <p className="eyebrow">Histórico</p>
            {historico.map((p) => (
              <div key={p.id} style={{ display: "flex", justifyContent: "space-between", padding: "0.3rem 0", fontSize: "0.86rem" }}>
                <span>{new Date(p.created_at).toLocaleDateString("pt-BR")} — {p.items.map((i) => i.drug_name).join(", ")}</span>
                <button className="botao botao--secundario" style={{ padding: "0.15rem 0.5rem" }} onClick={() => abrirImpressao(p.id)}>
                  Imprimir
                </button>
              </div>
            ))}
          </div>
        )}

        {impressao && (
          <div className="folha-impressao">
            <CabecalhoDocumento medico={impressao.medico} />
            <h2>Receituário</h2>
            <hr />
            <p>Paciente: {impressao.paciente.initials} — prontuário {impressao.paciente.record_number}</p>
            <ol>
              {impressao.prescricao.items.map((i: ItemDrug, idx: number) => (
                <li key={idx}>
                  <strong>{i.drug_name}</strong> {i.presentation && `— ${i.presentation}`}<br />
                  {i.posology}
                  {i.orientation && <><br /><em>{i.orientation}</em></>}
                </li>
              ))}
            </ol>
            {impressao.prescricao.notes && <p>{impressao.prescricao.notes}</p>}
          </div>
        )}
      </div>
    </>
  );
}