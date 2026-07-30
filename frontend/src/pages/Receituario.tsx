import { useEffect, useState } from "react";
import { api, ApiError } from "../lib/api";
import { Carregando, Erro } from "../components/Estado";

type Farmaco = { slug: string; nome: string };
type Item = { drug_slug?: string; descricao: string; apresentacao: string; posologia: string; orientacao: string };

type DocumentoClassificado = {
  tipo: string; tipo_nome: string | null; tipo_ativo: boolean;
  itens: string[]; pendencias: string[];
};
type Previa = {
  versao_listas: string | null; exige_revisao: boolean;
  documentos: DocumentoClassificado[];
  recusados: { item: string; motivo: string }[];
};

type Documento = {
  id: number; tipo: string; tipo_nome: string | null; cor: string | null;
  vias: number | null; exige_retencao: boolean | null; tipo_ativo: boolean;
  numeracao: string | null; status: string; itens: any[]; pendencias: string[];
  classificacao_corrigida_de: string | null; motivo_correcao: string | null;
  fonte_versao_listas: string | null;
};
type ReceituarioCriado = { prescricao_id: number; exige_revisao: boolean; documentos: Documento[] };

const STATUS_RÓTULO: Record<string, string> = {
  rascunho: "Rascunho", revisado: "Revisado", emitido: "Emitido",
};

function baixarBlob(blob: Blob, nomeArquivo: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = nomeArquivo;
  a.click();
  URL.revokeObjectURL(url);
}

/** Um documento já criado (PrescriptionDocument): revisar, emitir, enviar
 * por e-mail. Emissão só funciona para tipo COMUM hoje — os demais (NRA,
 * RCE etc.) esperam o SNCR e a assinatura digital, e a própria rota recusa
 * com explicação em vez de simular. */
function CartaoDocumento({ doc, onAtualizado }: { doc: Documento; onAtualizado: (d: Documento) => void }) {
  const [revisando, setRevisando] = useState(false);
  const [emitindo, setEmitindo] = useState(false);
  const [erro, setErro] = useState("");
  const [email, setEmail] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [resultadoEnvio, setResultadoEnvio] = useState<{ enviado: boolean; link: string | null } | null>(null);

  async function revisar() {
    setRevisando(true);
    setErro("");
    try {
      const atualizado = await api.post<Documento>(`/receituario/documentos/${doc.id}/revisar`, { confirmar: true });
      onAtualizado(atualizado);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível revisar.");
    } finally {
      setRevisando(false);
    }
  }

  async function emitir() {
    setEmitindo(true);
    setErro("");
    try {
      const blob = await api.blob(`/receituario/documentos/${doc.id}/emitir`);
      baixarBlob(blob, `receituario-${doc.id}.pdf`);
      onAtualizado({ ...doc, status: "emitido" });
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível emitir.");
    } finally {
      setEmitindo(false);
    }
  }

  async function enviar() {
    setEnviando(true);
    setErro("");
    try {
      const r = await api.post<{ enviado: boolean; link: string | null }>(
        `/receituario/documentos/${doc.id}/enviar-email`, { email },
      );
      setResultadoEnvio(r);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível enviar.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="cartao" style={{ marginTop: "0.8rem", borderLeft: `3px solid ${doc.cor === "amarela" ? "#c9a227" : doc.cor === "azul" ? "#1c7293" : "var(--linha)"}` }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <strong>{doc.tipo_nome ?? doc.tipo}</strong>
        <span className="eyebrow" style={{ margin: 0 }}>{STATUS_RÓTULO[doc.status] ?? doc.status}</span>
      </div>

      {!doc.tipo_ativo && (
        <p style={{ fontSize: "0.86rem", marginTop: "0.4rem" }}>
          Este tipo depende da integração com o SNCR (Anvisa, previsto até 30/09/2026) e da assinatura
          digital — ainda não pode ser emitido.
        </p>
      )}

      {doc.pendencias.length > 0 && (
        <ul style={{ fontSize: "0.84rem", color: "var(--alerta)", marginTop: "0.4rem" }}>
          {doc.pendencias.map((p, i) => <li key={i}>{p}</li>)}
        </ul>
      )}

      {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}

      <div style={{ display: "flex", gap: 8, marginTop: "0.6rem", flexWrap: "wrap" }}>
        {doc.status === "rascunho" && (
          <button className="botao" onClick={revisar} disabled={revisando}>
            {revisando ? "Revisando…" : "Confirmar revisão"}
          </button>
        )}
        {doc.status === "revisado" && doc.tipo_ativo && (
          <button className="botao" onClick={emitir} disabled={emitindo}>
            {emitindo ? "Emitindo…" : "Emitir e baixar PDF"}
          </button>
        )}
      </div>

      {doc.status === "emitido" && (
        <div style={{ marginTop: "0.8rem" }}>
          <label>Enviar por e-mail ao paciente (link seguro, válido por 7 dias)</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                 placeholder="paciente@exemplo.com" />
          <button className="botao" style={{ marginTop: "0.4rem" }} onClick={enviar} disabled={enviando || !email}>
            {enviando ? "Enviando…" : "Enviar por e-mail"}
          </button>
          {resultadoEnvio && (
            resultadoEnvio.enviado ? (
              <p style={{ color: "var(--sucesso)", fontSize: "0.86rem" }}>E-mail enviado.</p>
            ) : (
              <p style={{ fontSize: "0.86rem" }}>
                O envio automático não está disponível agora. Copie o link e envie manualmente:{" "}
                <code style={{ wordBreak: "break-all" }}>{resultadoEnvio.link}</code>
              </p>
            )
          )}
        </div>
      )}
    </div>
  );
}

const ITEM_VAZIO: Item = { descricao: "", apresentacao: "", posologia: "", orientacao: "" };

export default function Receituario() {
  const [farmacos, setFarmacos] = useState<Farmaco[] | null>(null);
  const [erroCarregar, setErroCarregar] = useState("");

  const [nome, setNome] = useState("");
  const [endereco, setEndereco] = useState("");
  const [documento, setDocumento] = useState("");
  const [observacoes, setObservacoes] = useState("");
  const [itens, setItens] = useState<Item[]>([{ ...ITEM_VAZIO }]);
  const [buscaFarmaco, setBuscaFarmaco] = useState<string[]>([""]);

  const [previa, setPrevia] = useState<Previa | null>(null);
  const [classificando, setClassificando] = useState(false);
  const [criando, setCriando] = useState(false);
  const [erro, setErro] = useState("");
  const [criado, setCriado] = useState<ReceituarioCriado | null>(null);

  useEffect(() => {
    api.get<{ slug: string; generic_name: string }[]>("/drugs")
      .then((l) => setFarmacos(l.map((d) => ({ slug: d.slug, nome: d.generic_name }))))
      .catch((e) => setErroCarregar(e instanceof ApiError ? e.message : "Não foi possível carregar os medicamentos."));
  }, []);

  function atualizarItem(i: number, campo: keyof Item, valor: string) {
    setPrevia(null);
    setItens((lista) => lista.map((it, idx) => idx === i ? { ...it, [campo]: valor } : it));
  }

  function escolherFarmaco(i: number, f: Farmaco) {
    atualizarItem(i, "drug_slug", f.slug);
    atualizarItem(i, "descricao", f.nome);
    setBuscaFarmaco((b) => b.map((v, idx) => idx === i ? f.nome : v));
  }

  function adicionarItem() {
    setItens((l) => [...l, { ...ITEM_VAZIO }]);
    setBuscaFarmaco((b) => [...b, ""]);
  }

  function removerItem(i: number) {
    setItens((l) => l.filter((_, idx) => idx !== i));
    setBuscaFarmaco((b) => b.filter((_, idx) => idx !== i));
    setPrevia(null);
  }

  const itensValidos = itens.filter((it) => it.descricao.trim() || it.drug_slug);
  const pedido = {
    destinatario: { nome, endereco: endereco || undefined, documento: documento || undefined },
    itens: itensValidos.map((it) => ({
      drug_slug: it.drug_slug, descricao: it.descricao, apresentacao: it.apresentacao,
      posologia: it.posologia, orientacao: it.orientacao,
    })),
    observacoes,
  };
  const podeEnviar = nome.trim().length >= 3 && itensValidos.length > 0;

  async function verPrevia() {
    setClassificando(true);
    setErro("");
    try {
      setPrevia(await api.post<Previa>("/receituario/classificar", pedido));
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível classificar.");
    } finally {
      setClassificando(false);
    }
  }

  async function criar() {
    setCriando(true);
    setErro("");
    try {
      const resultado = await api.post<ReceituarioCriado>("/receituario", pedido);
      setCriado(resultado);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível criar o receituário.");
    } finally {
      setCriando(false);
    }
  }

  function atualizarDocumento(d: Documento) {
    setCriado((c) => c ? { ...c, documentos: c.documentos.map((x) => x.id === d.id ? d : x) } : c);
  }

  if (erroCarregar) return <Erro mensagem={erroCarregar} />;
  if (!farmacos) return <Carregando />;

  return (
    <>
      <p className="eyebrow">Documentos</p>
      <h1>Emitir receita</h1>

      {!criado ? (
        <div className="cartao" style={{ maxWidth: "72ch" }}>
          <p className="eyebrow" style={{ margin: 0 }}>Paciente</p>
          <label>Nome</label>
          <input value={nome} onChange={(e) => setNome(e.target.value)} />
          <label style={{ marginTop: "0.5rem" }}>Endereço (opcional)</label>
          <input value={endereco} onChange={(e) => setEndereco(e.target.value)} />
          <label style={{ marginTop: "0.5rem" }}>Documento — RG/CPF (opcional)</label>
          <input value={documento} onChange={(e) => setDocumento(e.target.value)} />

          <p className="eyebrow" style={{ margin: "1rem 0 0" }}>Itens da receita</p>
          {itens.map((it, i) => (
            <div key={i} style={{ borderTop: "1px solid var(--linha)", paddingTop: "0.6rem", marginTop: "0.6rem" }}>
              <label>Medicamento</label>
              <input
                value={buscaFarmaco[i] ?? ""}
                onChange={(e) => {
                  setBuscaFarmaco((b) => b.map((v, idx) => idx === i ? e.target.value : v));
                  atualizarItem(i, "drug_slug", "");
                  atualizarItem(i, "descricao", e.target.value);
                }}
                placeholder="Busque na base ou digite livremente"
              />
              {buscaFarmaco[i] && !it.drug_slug && (
                <div style={{ maxHeight: 140, overflowY: "auto", border: "1px solid var(--linha)", borderRadius: 6, marginTop: 4 }}>
                  {farmacos
                    .filter((f) => f.nome.toLowerCase().includes(buscaFarmaco[i].toLowerCase()))
                    .slice(0, 8)
                    .map((f) => (
                      <button key={f.slug} type="button"
                              style={{ display: "block", width: "100%", textAlign: "left", padding: "0.3rem 0.5rem", border: "none", background: "transparent", cursor: "pointer" }}
                              onClick={() => escolherFarmaco(i, f)}>
                        {f.nome}
                      </button>
                    ))}
                </div>
              )}
              <label style={{ marginTop: "0.4rem" }}>Apresentação</label>
              <input value={it.apresentacao} onChange={(e) => atualizarItem(i, "apresentacao", e.target.value)} />
              <label style={{ marginTop: "0.4rem" }}>Posologia</label>
              <input value={it.posologia} onChange={(e) => atualizarItem(i, "posologia", e.target.value)} />
              <label style={{ marginTop: "0.4rem" }}>Orientação (opcional)</label>
              <input value={it.orientacao} onChange={(e) => atualizarItem(i, "orientacao", e.target.value)} />
              {itens.length > 1 && (
                <button type="button" className="botao botao--secundario" style={{ marginTop: "0.4rem" }}
                        onClick={() => removerItem(i)}>Remover item</button>
              )}
            </div>
          ))}
          <button type="button" className="botao botao--secundario" style={{ marginTop: "0.6rem" }} onClick={adicionarItem}>
            + Adicionar item
          </button>

          <label style={{ marginTop: "0.8rem" }}>Observações (opcional)</label>
          <textarea rows={3} value={observacoes} onChange={(e) => setObservacoes(e.target.value)} />

          {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}

          <div style={{ display: "flex", gap: 8, marginTop: "1rem" }}>
            <button className="botao botao--secundario" onClick={verPrevia} disabled={classificando || !podeEnviar}>
              {classificando ? "Classificando…" : "Ver prévia"}
            </button>
            <button className="botao" onClick={criar} disabled={criando || !podeEnviar}>
              {criando ? "Criando…" : "Criar receituário"}
            </button>
          </div>

          {previa && (
            <div style={{ marginTop: "0.8rem", fontSize: "0.88rem" }}>
              <p>
                {previa.documentos.length} documento(s) será(ão) gerado(s)
                {previa.exige_revisao && " — exige revisão manual antes de emitir"}.
              </p>
              <ul>
                {previa.documentos.map((d, i) => (
                  <li key={i}>
                    <strong>{d.tipo_nome ?? d.tipo}</strong> — {d.itens.join(", ")}
                    {d.pendencias.length > 0 && (
                      <span style={{ color: "var(--alerta)" }}> ({d.pendencias.join("; ")})</span>
                    )}
                  </li>
                ))}
              </ul>
              {previa.recusados.length > 0 && (
                <p style={{ color: "var(--alerta)" }}>
                  Recusado(s): {previa.recusados.map((r) => `${r.item} — ${r.motivo}`).join("; ")}
                </p>
              )}
            </div>
          )}
        </div>
      ) : (
        <div style={{ maxWidth: "72ch" }}>
          <p style={{ color: "var(--sucesso)" }}>Receituário nº {criado.prescricao_id} criado.</p>
          {criado.documentos.map((d) => (
            <CartaoDocumento key={d.id} doc={d} onAtualizado={atualizarDocumento} />
          ))}
          <button className="botao botao--secundario" style={{ marginTop: "1rem" }}
                  onClick={() => { setCriado(null); setItens([{ ...ITEM_VAZIO }]); setBuscaFarmaco([""]); setNome(""); setPrevia(null); }}>
            Nova receita
          </button>
        </div>
      )}
    </>
  );
}
