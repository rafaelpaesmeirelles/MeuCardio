import CabecalhoDocumento, { type OperadoraDocumento } from "./CabecalhoDocumento";
import { lazy, Suspense, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { api, PaginaDe } from "../lib/api";
import { incompletePrescription } from "../lib/clinicalInput";
import { useAuth } from "../lib/auth";
import { Link } from "react-router-dom";

const PrescricaoLivreEspecial = lazy(() => import("./PrescricaoLivreEspecial"));

type ItemDrug = {
  drug_name: string; presentation: string; posology: string; orientation: string;
  // Tarefa B (CLAUDE.md, 02/08/2026) — escolha de marca via CMED, sempre
  // opcional: o genérico (sem estes seis campos) continua sendo o padrão.
  brand_name?: string; manufacturer?: string; ggrem?: string;
  pmc_snapshot?: number; uf?: string; cmed_version?: string;
};
type Prescricao = { id: number; items: ItemDrug[]; notes: string | null; created_at: string };
type DadosImpressaoPrescricao = {
  medico: any; paciente: any; prescricao: Prescricao; operadora?: OperadoraDocumento;
};
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
  const [erroImpressao, setErroImpressao] = useState("");
  const [preparandoImpressao, setPreparandoImpressao] = useState(false);
  const consultaImpressao = useRef(0);
  const [escolhendo, setEscolhendo] = useState<{ nome: string; resp: RespostaApresentacoes } | null>(null);
  const [erro, setErro] = useState("");
  const [erroHistorico, setErroHistorico] = useState("");
  const contexto = useRef(0), consultaBusca = useRef(0), consultaHistorico = useRef(0), consultaApresentacao = useRef(0);
  const salvandoRef = useRef(false);

  const { usuario } = useAuth();
  async function recarregar() {
    const token = contexto.current, consulta = ++consultaHistorico.current;
    setErroHistorico("");
    try { const rows = await api.get<Prescricao[]>(`/prescriptions/patient/${patientId}`); if(token===contexto.current&&consulta===consultaHistorico.current)setHistorico(rows); }
    catch(e){if(token===contexto.current&&consulta===consultaHistorico.current)setErroHistorico(e instanceof Error?e.message:"Não foi possível carregar as prescrições.");}
  }
  useEffect(() => {
    contexto.current++; setHistorico(null); setItens([]); setNotas(""); setBusca(""); setSugestoes([]); setEscolhendo(null); setErro("");setSalvando(false);salvandoRef.current=false;
    void recarregar();
    return()=>{contexto.current++;consultaBusca.current++;consultaApresentacao.current++;};
  }, [patientId]);
  useEffect(() => {
    consultaImpressao.current += 1;
    setImpressao(null);
    setErroImpressao("");
    setPreparandoImpressao(false);
    return () => { consultaImpressao.current += 1; };
  }, [patientId]);

  useEffect(() => {
    const consulta = ++consultaBusca.current;
    let ativo = true;
    if (busca.trim().length < 2) { setSugestoes([]); return; }
    const atraso = setTimeout(() => {
      api.get<PaginaDe<SugestaoFarmaco>>(`/drugs?q=${encodeURIComponent(busca)}`)
        .then((r) => {if(ativo&&consulta===consultaBusca.current)setSugestoes(r.items.slice(0, 6));})
        .catch(e=>{if(ativo&&consulta===consultaBusca.current){setSugestoes([]);setErro(e instanceof Error?e.message:"Não foi possível buscar medicamentos.");}});
    }, 250);
    return () => {ativo=false;clearTimeout(atraso);};
  }, [busca]);

  async function escolherMedicamento(slug: string, nome: string) {
    if(salvandoRef.current)return;
    const consulta=++consultaApresentacao.current,token=contexto.current;
    setBusca("");
    setSugestoes([]);
    const uf = usuario?.council_state;
    setErro("");
    try {
    const resp = await api.get<RespostaApresentacoes>(`/drugs/${slug}/apresentacoes${uf ? `?uf=${uf}` : ""}`);
    if(token!==contexto.current||consulta!==consultaApresentacao.current||salvandoRef.current)return;
    if (resp.apresentacoes.length > 0) {
      setEscolhendo({ nome, resp });
    } else {
      adicionarItem(nome);
    }
    } catch(e){if(token===contexto.current&&consulta===consultaApresentacao.current)setErro(e instanceof Error?e.message:"Não foi possível carregar as apresentações. Tente selecionar o medicamento novamente.");}
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
    if (salvandoRef.current) return;
    if (incompletePrescription(itens)) { setErro("Preencha medicamento, apresentação e posologia de todos os itens antes de salvar."); return; }
    salvandoRef.current=true;
    const token=contexto.current;
    setSalvando(true);
    setErro("");
    try {
      await api.post(`/prescriptions`, { patient_id: patientId, items: itens, notes: notas });
      if(token!==contexto.current)return;
      setItens([]);
      setNotas("");
      await recarregar();
    } catch(e){if(token===contexto.current)setErro(e instanceof Error?e.message:"Não foi possível salvar a prescrição. Seus itens foram preservados.");
    } finally {
      if(token===contexto.current){salvandoRef.current=false;setSalvando(false);}
    }
  }

  async function abrirImpressao(id: number) {
    const consulta = ++consultaImpressao.current;
    setPreparandoImpressao(true);
    setErroImpressao("");
    setImpressao(null);
    try {
      const dados = await api.get<DadosImpressaoPrescricao>(`/prescriptions/${id}/imprimir`);
      if (consulta !== consultaImpressao.current) return;
      if (incompletePrescription(dados.prescricao.items)) throw new Error("Prescrição incompleta. Revise medicamento, apresentação e posologia antes de imprimir.");
      const campos = ["razao_social", "cnpj", "logradouro", "numero", "bairro", "cidade", "uf", "cep"] as const;
      if (!dados.operadora || campos.some((campo) => !dados.operadora?.[campo]?.trim())) {
        throw new Error("A identificação institucional está incompleta. A impressão não foi aberta; tente novamente após atualizar a página.");
      }
      setImpressao(dados);
      // Wait for the committed header and its real assets, not an arbitrary delay.
      await new Promise<void>((resolve) => requestAnimationFrame(() => requestAnimationFrame(() => resolve())));
      await document.fonts.ready;
      await Promise.all(Array.from(document.querySelectorAll<HTMLImageElement>(".folha-impressao img"))
        .map((img) => img.complete ? Promise.resolve() : img.decode().catch(() => undefined)));
      if (consulta !== consultaImpressao.current) return;
      window.print();
    } catch (error) {
      if (consulta !== consultaImpressao.current) return;
      setImpressao(null);
      setErroImpressao(error instanceof Error ? error.message : "Não foi possível preparar a impressão. Tente novamente.");
    } finally {
      if (consulta === consultaImpressao.current) setPreparandoImpressao(false);
    }
  }

  return (
    <>
      <Suspense fallback={null}><PrescricaoLivreEspecial /></Suspense>
      <div className="cartao" style={{ background: "var(--fundo)" }}>
        <p className="eyebrow patient-round-heading" style={{ margin: 0 }}>Prescrição</p>
        {erro&&<p role="alert">{erro}</p>}
        <fieldset disabled={salvando} style={{border:0,padding:0,margin:0,minWidth:0}} aria-label="Itens da prescrição hospitalar">

        <div style={{ position: "relative", marginTop: "0.5rem" }}>
          <input
            aria-label="Buscar medicamento para prescrição hospitalar"
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
            placeholder="Buscar medicamento pra adicionar…"
          />
          {sugestoes.length > 0 && (
            <div className="cartao" style={{ position: "absolute", zIndex: 5, width: "100%", padding: "0.3rem" }}>
              {sugestoes.map((s) => (
                <button type="button" key={s.slug} onClick={() => escolherMedicamento(s.slug, s.generic_name)}
                     style={{ display:"block",width:"100%",textAlign:"left",border:0,background:"transparent",padding: "0.4rem", cursor: "pointer", fontSize: "0.88rem" }}>
                  {s.generic_name}
                </button>
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
            <input aria-label={`Apresentação do item ${i+1}`} required placeholder="Apresentação (ex.: comp. 40mg)" value={item.presentation}
                   onChange={(e) => atualizarItem(i, "presentation", e.target.value)}
                   style={{ marginTop: "0.3rem" }} />
            <input aria-label={`Posologia do item ${i+1}`} required placeholder="Posologia (ex.: 1 comprimido, 1x ao dia)" value={item.posology}
                   onChange={(e) => atualizarItem(i, "posology", e.target.value)}
                   style={{ marginTop: "0.3rem" }} />
            <input aria-label={`Orientação do item ${i+1}`} placeholder="Orientação (opcional)" value={item.orientation}
                   onChange={(e) => atualizarItem(i, "orientation", e.target.value)}
                   style={{ marginTop: "0.3rem" }} />
          </div>
        ))}

        {itens.length > 0 && (
          <>
            <textarea aria-label="Observações gerais da prescrição" placeholder="Observações gerais (opcional)" rows={2} value={notas}
                      onChange={(e) => setNotas(e.target.value)} style={{ marginTop: "0.6rem" }} />
            <button className="botao" style={{ marginTop: "0.5rem" }} onClick={salvar} disabled={salvando}>
              {salvando ? "Salvando…" : "Salvar prescrição"}
            </button>
          </>
        )}

        </fieldset>
        {erroHistorico&&<div role="alert"><p>{erroHistorico}</p><button className="botao botao--secundario" onClick={()=>void recarregar()}>Recarregar prescrições</button></div>}
        {historico && historico.length > 0 && (
          <div style={{ marginTop: "0.8rem" }}>
            <p className="eyebrow">Histórico</p>
            {historico.map((p) => (
              <div key={p.id} className="patient-prescription-history" style={{ display: "flex", flexWrap: "wrap", alignItems: "flex-start", gap: "0.6rem", padding: "0.3rem 0", fontSize: "0.86rem" }}>
                <span style={{ flex: "1 1 16rem", minWidth: 0, overflowWrap: "anywhere" }}>{new Date(p.created_at).toLocaleDateString("pt-BR")} — {p.items.map((i) => i.drug_name).join(", ")}</span>
                <div className="patient-prescription-history__actions" style={{ display: "flex", flex: "1 1 22rem", flexWrap: "wrap", gap: "0.5rem", minWidth: 0 }}>
                  <button className="botao botao--secundario" style={{ flex: "1 1 11rem", minWidth: 0, minHeight: 44, padding: "0.5rem", whiteSpace: "normal", overflowWrap: "anywhere" }} disabled={preparandoImpressao} onClick={() => abrirImpressao(p.id)}>
                    Imprimir para assinatura manual
                  </button>
                  <Link className="botao botao--secundario" style={{ flex: "1 1 11rem", minWidth: 0, minHeight: 44, padding: "0.5rem", whiteSpace: "normal", overflowWrap: "anywhere" }} to="/receituario" state={{ prescricaoLegadaId: p.id }}>
                    Revisar e assinar digitalmente
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}

        {erroImpressao && <p role="alert">{erroImpressao}</p>}

        {impressao && createPortal(
          <div className="folha-impressao">
            <CabecalhoDocumento medico={impressao.medico} operadora={impressao.operadora} />
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
          </div>, document.body,
        )}
      </div>
    </>
  );
}
