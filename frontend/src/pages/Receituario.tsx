import { useEffect, useState } from "react";
import { api, ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";
import { Carregando, Erro, Vazio } from "../components/Estado";

type Farmaco = { slug: string; nome: string };
type Item = {
  drug_slug?: string; descricao: string; apresentacao: string;
  quantidade: string; quantidade_extenso: string; posologia: string; orientacao: string;
  // Tarefa B (CLAUDE.md, 02/08/2026) — escolha de marca via CMED, sempre
  // opcional: o genérico (sem estes seis campos) continua sendo o padrão.
  brand_name?: string; manufacturer?: string; ggrem?: string;
  pmc_snapshot?: number; uf?: string; cmed_version?: string;
};

// GET /drugs/{slug}/apresentacoes?uf=XX (Tarefa A/B) — marca, laboratório,
// apresentação e PMC (teto CMED) pra escolha explícita durante a digitação.
type PrecoCmed = { valor: number | null; rotulo: string };
type ApresentacaoCmed = {
  produto: string; laboratorio: string; apresentacao: string; ggrem: string;
  restricao_hospitalar: boolean; preco: PrecoCmed;
};
type RespostaApresentacoes = {
  uf: string | null; cmed_publicado_em: string | null;
  apresentacoes: ApresentacaoCmed[]; aviso: string | null;
};

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
  fonte_versao_listas: string | null; cid: string | null;
};
type ReceituarioCriado = { prescricao_id: number; exige_revisao: boolean; documentos: Documento[] };

// Arquivo/histórico (Tarefa 4, pedido do Rafael de 02/08/2026) — GET
// /receituario (lista) e GET /receituario/{id} (detalhe, usado tanto pra
// "Abrir" quanto pra "Recriar baseado nesta").
type HistoricoDocResumo = { tipo: string; tipo_nome: string | null; status: string };
type HistoricoItem = {
  prescricao_id: number; criado_em: string; paciente_nome: string | null;
  documentos: HistoricoDocResumo[];
};
type ItemOriginal = {
  drug_slug: string | null; descricao: string; apresentacao: string;
  quantidade: string; quantidade_extenso: string; posologia: string; orientacao: string;
};
type PrescricaoDetalhe = {
  prescricao_id: number;
  destinatario: { nome: string | null; endereco: string | null; documento: string | null };
  observacoes: string | null;
  itens_originais: ItemOriginal[];
  documentos: Documento[];
};

// Catálogo de métodos de assinatura (Tarefa 4) — GET /assinatura/provedores.
// "MANUAL" é o único com disponivel=true hoje; os demais aparecem desabilitados
// com o motivo, no mesmo espírito de "recusa e explica" que o tipo_ativo já usa.
type Provedor = { codigo: string; nome: string; nivel: string; familia: string; disponivel: boolean; motivo: string | null };

// GET /receituario/tipos — usado pra deixar o médico escolher/corrigir o
// tipo do documento na revisão (comum ou controle especial), em vez de só
// aceitar a classificação automática.
type TipoReceituario = { codigo: string; nome: string; ativo: boolean };

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
 * RCE etc.) esperam o SNCR e o layout oficial, e a própria rota recusa
 * com explicação em vez de simular. */
function CartaoDocumento({ doc, provedores, tipos, onAtualizado }: {
  doc: Documento; provedores: Provedor[] | null; tipos: TipoReceituario[] | null;
  onAtualizado: (d: Documento) => void;
}) {
  const { usuario } = useAuth();
  const [revisando, setRevisando] = useState(false);
  const [emitindo, setEmitindo] = useState(false);
  const [endereco, setEndereco] = useState<"" | "residencial" | "profissional">("");
  const [metodo, setMetodo] = useState(usuario?.assinatura_metodo_preferido ?? "MANUAL");
  // Correção de tipo na revisão (comum ↔ controle especial): o médico não
  // é obrigado a aceitar a classificação automática. `corrigirPara` começa
  // igual a `doc.tipo` (sem correção) e só exige `motivo` quando muda.
  const [corrigirPara, setCorrigirPara] = useState(doc.tipo);
  const [motivoCorrecao, setMotivoCorrecao] = useState("");
  const [erro, setErro] = useState("");
  const [email, setEmail] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [resultadoEnvio, setResultadoEnvio] = useState<{ enviado: boolean; link: string | null } | null>(null);
  const temC5 = doc.itens.some((item) => String(item.lista ?? "").toUpperCase() === "C5");

  async function revisar() {
    setRevisando(true);
    setErro("");
    try {
      const corrigindo = corrigirPara !== doc.tipo;
      const atualizado = await api.post<Documento>(`/receituario/documentos/${doc.id}/revisar`, {
        confirmar: true,
        ...(corrigindo ? { corrigir_para: corrigirPara, motivo: motivoCorrecao } : {}),
      });
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
      const blob = await api.blob(`/receituario/documentos/${doc.id}/emitir`, {
        method: "POST",
        body: JSON.stringify({ endereco: endereco || null, metodo }),
      });
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

      {/* Sem isto, um item digitado manualmente (sem drug_slug — ver
         "Busque na base ou digite livremente" no formulário) já ia pro
         documento, mas o médico não tinha como conferir aqui que a
         digitação foi capturada antes de revisar e emitir. */}
      {doc.itens.length > 0 && (
        <ul style={{ fontSize: "0.86rem", marginTop: "0.5rem", paddingLeft: "1.1rem" }}>
          {doc.itens.map((it, i) => (
            <li key={i}>
              <strong>{it.descricao}</strong>
              {it.apresentacao && ` — ${it.apresentacao}`}
              {it.posologia && <span style={{ color: "var(--texto-secundario)" }}> · {it.posologia}</span>}
            </li>
          ))}
        </ul>
      )}

      {!doc.tipo_ativo && (
        <p style={{ fontSize: "0.86rem", marginTop: "0.4rem" }}>
          Este modelo exige numeração oficial ou integração SNCR. O sistema não simula número,
          talonário ou autorização; a emissão permanece bloqueada até o requisito existir.
        </p>
      )}
      {doc.tipo === "RCE" && (
        <p style={{ fontSize: "0.86rem", marginTop: "0.4rem" }}>
          Modelo físico Anvisa V2: serão geradas duas vias, cada uma com frente e verso,
          para impressão e assinatura manual.
        </p>
      )}
      {temC5 && (
        <p style={{ color: "var(--alerta)", fontSize: "0.84rem", marginTop: "0.4rem" }}>
          Lista C5: emissão somente por CRM/CRO e com CPF do prescritor, endereço e telefone
          profissionais, endereço do paciente e CID preenchidos.
        </p>
      )}

      {doc.pendencias.length > 0 && (
        <ul style={{ fontSize: "0.84rem", color: "var(--alerta)", marginTop: "0.4rem" }}>
          {doc.pendencias.map((p, i) => <li key={i}>{p}</li>)}
        </ul>
      )}

      {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}

      {doc.status === "revisado" && doc.tipo_ativo && (
        <div style={{ marginTop: "0.6rem" }}>
          {doc.tipo === "RCE" ? (
            <p className="eyebrow" style={{ margin: "0.3rem 0" }}>
              A RCE usa automaticamente o endereço profissional cadastrado. Para Lista C5,
              endereço e telefone profissionais são obrigatórios.
            </p>
          ) : (
            <>
              <label>Endereço no cabeçalho/rodapé (opcional)</label>
              <select value={endereco} onChange={(e) => setEndereco(e.target.value as typeof endereco)}>
                <option value="">Nenhum</option>
                <option value="profissional">Profissional (consultório)</option>
                <option value="residencial">Residencial</option>
              </select>
              <p className="eyebrow" style={{ margin: "0.3rem 0 0" }}>
                Preencha em Minha Conta antes, se ainda não tiver cadastrado.
              </p>
            </>
          )}

          <label style={{ marginTop: "0.5rem" }}>Método de assinatura</label>
          <select value={metodo} onChange={(e) => setMetodo(e.target.value)}>
            {(provedores ?? []).map((p) => (
              <option key={p.codigo} value={p.codigo} disabled={!p.disponivel}>
                {p.nome}{!p.disponivel ? " — indisponível" : ""}
              </option>
            ))}
          </select>
          {(() => {
            const escolhido = provedores?.find((p) => p.codigo === metodo);
            if (!escolhido) return null;
            if (!escolhido.disponivel) {
              return <p style={{ color: "var(--alerta)", fontSize: "0.82rem", margin: "0.3rem 0 0" }}>{escolhido.motivo}</p>;
            }
            if (escolhido.nivel !== "qualificada" && escolhido.codigo !== "MANUAL") {
              return (
                <p style={{ color: "var(--alerta)", fontSize: "0.82rem", margin: "0.3rem 0 0" }}>
                  Assinatura {escolhido.nivel === "avancada" ? "avançada" : escolhido.nivel} — sem presunção
                  ICP-Brasil; a farmácia pode recusar receita assinada assim.
                </p>
              );
            }
            return null;
          })()}
        </div>
      )}

      {doc.status === "rascunho" && (
        <div style={{ marginTop: "0.6rem" }}>
          <label>Tipo de receita</label>
          <select value={corrigirPara} onChange={(e) => setCorrigirPara(e.target.value)}>
            {(tipos ?? []).map((t) => (
              <option key={t.codigo} value={t.codigo}>{t.nome}{!t.ativo ? " (indisponível hoje)" : ""}</option>
            ))}
          </select>
          {corrigirPara !== doc.tipo && (
            <>
              <label style={{ marginTop: "0.4rem" }}>Motivo da correção</label>
              <input value={motivoCorrecao} onChange={(e) => setMotivoCorrecao(e.target.value)}
                     placeholder="Por que este tipo é o correto, não o classificado automaticamente" />
            </>
          )}
        </div>
      )}

      <div style={{ display: "flex", gap: 8, marginTop: "0.6rem", flexWrap: "wrap" }}>
        {doc.status === "rascunho" && (
          <button className="botao" onClick={revisar}
                  disabled={revisando || (corrigirPara !== doc.tipo && !motivoCorrecao.trim())}>
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

/** Arquivo de receituários já criados (Tarefa 4) — "Abrir" retoma um
 * rascunho pra continuar revisando/emitindo; "Recriar baseado nesta"
 * pré-preenche o formulário de uma receita NOVA com os dados desta, pro
 * médico editar em vez de montar tudo de novo (retorno de paciente, refil). */
function HistoricoReceituario({ onAbrir, onRecriar }: {
  onAbrir: (d: PrescricaoDetalhe) => void; onRecriar: (d: PrescricaoDetalhe) => void;
}) {
  const [itens, setItens] = useState<HistoricoItem[] | null>(null);
  const [erro, setErro] = useState("");
  const [carregandoId, setCarregandoId] = useState<number | null>(null);
  const [nome, setNome] = useState("");
  const [tipo, setTipo] = useState("");

  useEffect(() => {
    setItens(null);
    const params = new URLSearchParams();
    if (nome.trim()) params.set("nome", nome.trim());
    if (tipo) params.set("tipo", tipo);
    const suffix = params.toString() ? `?${params}` : "";
    api.get<HistoricoItem[]>(`/receituario${suffix}`)
      .then(setItens)
      .catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível carregar o histórico."));
  }, [nome, tipo]);

  async function abrir(id: number, acao: (d: PrescricaoDetalhe) => void) {
    setCarregandoId(id); setErro("");
    try { acao(await api.get<PrescricaoDetalhe>(`/receituario/${id}`)); }
    catch (e) { setErro(e instanceof ApiError ? e.message : "Não foi possível abrir esta receita."); }
    finally { setCarregandoId(null); }
  }

  const tiposDisponiveis = Array.from(new Map((itens ?? []).flatMap((i) => i.documentos).map((d) => [d.tipo, d.tipo_nome ?? d.tipo])).entries());
  const grupos = new Map<string, HistoricoItem[]>();
  for (const item of itens ?? []) {
    const chave = item.paciente_nome ?? "Paciente não informado";
    grupos.set(chave, [...(grupos.get(chave) ?? []), item]);
  }

  return (
    <div style={{ maxWidth: "76ch" }}>
      <div className="grade grade--2" style={{ marginBottom: "0.8rem" }}>
        <div><label>Procurar pelo nome do paciente</label><input value={nome} onChange={(e) => setNome(e.target.value)} placeholder="Nome completo ou parte do nome" /></div>
        <div><label>Tipo de receita</label><select value={tipo} onChange={(e) => setTipo(e.target.value)}><option value="">Todos</option>{tiposDisponiveis.map(([codigo, rotulo]) => <option key={codigo} value={codigo}>{rotulo}</option>)}</select></div>
      </div>
      {erro && <Erro mensagem={erro} />}
      {!itens ? <Carregando /> : itens.length === 0 ? <Vazio titulo="Nenhuma receita encontrada" /> : (
        [...grupos.entries()].sort(([a], [b]) => a.localeCompare(b, "pt-BR")).map(([paciente, receitas]) => (
          <section key={paciente} style={{ marginBottom: "1rem" }}>
            <h3 style={{ marginBottom: "0.45rem" }}>{paciente}</h3>
            {receitas.map((it) => (
              <div key={it.prescricao_id} className="cartao" style={{ marginBottom: "0.5rem" }}>
                <span className="eyebrow">{new Date(it.criado_em).toLocaleString("pt-BR")}</span>
                <p style={{ fontSize: "0.86rem", margin: "0.3rem 0", color: "var(--texto-secundario)" }}>{it.documentos.map((d, i) => <span key={i}>{i > 0 && " · "}{d.tipo_nome ?? d.tipo} ({STATUS_RÓTULO[d.status] ?? d.status})</span>)}</p>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  <button className="botao botao--secundario" disabled={carregandoId === it.prescricao_id} onClick={() => abrir(it.prescricao_id, onAbrir)}>{carregandoId === it.prescricao_id ? "Abrindo…" : "Abrir"}</button>
                  <button className="botao botao--secundario" disabled={carregandoId === it.prescricao_id} onClick={() => abrir(it.prescricao_id, onRecriar)}>Recriar baseado nesta</button>
                </div>
              </div>
            ))}
          </section>
        ))
      )}
    </div>
  );
}

const ITEM_VAZIO: Item = {
  descricao: "", apresentacao: "", quantidade: "", quantidade_extenso: "",
  posologia: "", orientacao: "",
};

export default function Receituario() {
  const [aba, setAba] = useState<"nova" | "historico">("nova");
  const [farmacos, setFarmacos] = useState<Farmaco[] | null>(null);
  const [provedores, setProvedores] = useState<Provedor[] | null>(null);
  const [tipos, setTipos] = useState<TipoReceituario[] | null>(null);
  const [erroCarregar, setErroCarregar] = useState("");

  const [nome, setNome] = useState("");
  const [endereco, setEndereco] = useState("");
  const [documento, setDocumento] = useState("");
  const [cid, setCid] = useState("");
  const [observacoes, setObservacoes] = useState("");
  const [itens, setItens] = useState<Item[]>([{ ...ITEM_VAZIO }]);
  const [buscaFarmaco, setBuscaFarmaco] = useState<string[]>([""]);
  // Uma entrada por índice de item — null enquanto não escolheu fármaco
  // nenhum, undefined enquanto a busca de apresentações está em voo.
  const [apresentacoes, setApresentacoes] = useState<(RespostaApresentacoes | null | undefined)[]>([null]);
  const { usuario } = useAuth();

  const [previa, setPrevia] = useState<Previa | null>(null);
  const [classificando, setClassificando] = useState(false);
  const [criando, setCriando] = useState(false);
  const [erro, setErro] = useState("");
  const [criado, setCriado] = useState<ReceituarioCriado | null>(null);

  useEffect(() => {
    api.get<{ slug: string; generic_name: string }[]>("/drugs")
      .then((l) => setFarmacos(l.map((d) => ({ slug: d.slug, nome: d.generic_name }))))
      .catch((e) => setErroCarregar(e instanceof ApiError ? e.message : "Não foi possível carregar os medicamentos."));
    // Falha em carregar o catálogo não impede a tela — CartaoDocumento cai
    // para o `<select>` vazio e o default "MANUAL", que é o método que
    // sempre funciona.
    api.get<Provedor[]>("/assinatura/provedores").then(setProvedores).catch(() => {});
    api.get<TipoReceituario[]>("/receituario/tipos").then(setTipos).catch(() => {});
  }, []);

  function atualizarItem(i: number, campo: keyof Item, valor: string) {
    setPrevia(null);
    setItens((lista) => lista.map((it, idx) => idx === i ? { ...it, [campo]: valor } : it));
  }

  function escolherFarmaco(i: number, f: Farmaco) {
    setPrevia(null);
    setItens((lista) => lista.map((it, idx) => idx === i
      ? { drug_slug: f.slug, descricao: f.nome, apresentacao: "",
          quantidade: it.quantidade, quantidade_extenso: it.quantidade_extenso,
          posologia: it.posologia, orientacao: it.orientacao }
      : it));
    setBuscaFarmaco((b) => b.map((v, idx) => idx === i ? f.nome : v));
    // Marca é escolha explícita do médico, nunca automática (Tarefa B,
    // CLAUDE.md) — a busca só traz o que existe pra ele escolher; o genérico
    // (sem marca) continua valendo até ele decidir trocar.
    setApresentacoes((a) => a.map((v, idx) => idx === i ? undefined : v));
    api.get<RespostaApresentacoes>(`/drugs/${f.slug}/apresentacoes${usuario?.council_state ? `?uf=${usuario.council_state}` : ""}`)
      .then((r) => setApresentacoes((a) => a.map((v, idx) => idx === i ? r : v)))
      .catch(() => setApresentacoes((a) => a.map((v, idx) => idx === i ? null : v)));
  }

  function escolherApresentacao(i: number, ap: ApresentacaoCmed, resp: RespostaApresentacoes) {
    setPrevia(null);
    setItens((lista) => lista.map((it, idx) => idx === i ? {
      ...it,
      apresentacao: it.apresentacao || ap.apresentacao,
      brand_name: ap.produto, manufacturer: ap.laboratorio, ggrem: ap.ggrem,
      pmc_snapshot: ap.preco.valor ?? undefined,
      uf: resp.uf ?? undefined, cmed_version: resp.cmed_publicado_em ?? undefined,
    } : it));
  }

  function voltarParaGenerico(i: number) {
    setPrevia(null);
    setItens((lista) => lista.map((it, idx) => idx === i ? {
      ...it, brand_name: undefined, manufacturer: undefined, ggrem: undefined,
      pmc_snapshot: undefined, uf: undefined, cmed_version: undefined,
    } : it));
  }

  function adicionarItem() {
    setItens((l) => [...l, { ...ITEM_VAZIO }]);
    setBuscaFarmaco((b) => [...b, ""]);
    setApresentacoes((a) => [...a, null]);
  }

  function removerItem(i: number) {
    setItens((l) => l.filter((_, idx) => idx !== i));
    setBuscaFarmaco((b) => b.filter((_, idx) => idx !== i));
    setApresentacoes((a) => a.filter((_, idx) => idx !== i));
    setPrevia(null);
  }

  const itensValidos = itens.filter((it) => it.descricao.trim() || it.drug_slug);
  const pedido = {
    destinatario: { nome, endereco: endereco || undefined, documento: documento || undefined },
    itens: itensValidos.map((it) => ({
      drug_slug: it.drug_slug, descricao: it.descricao, apresentacao: it.apresentacao,
      quantidade: it.quantidade, quantidade_extenso: it.quantidade_extenso,
      posologia: it.posologia, orientacao: it.orientacao,
      brand_name: it.brand_name, manufacturer: it.manufacturer, ggrem: it.ggrem,
      pmc_snapshot: it.pmc_snapshot, uf: it.uf, cmed_version: it.cmed_version,
    })),
    observacoes,
    cid: cid.trim() || undefined,
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

  // "Abrir" (histórico) — retoma uma receita já criada, pro médico continuar
  // revisando/emitindo/baixando exatamente como se tivesse acabado de criar.
  function abrirDoHistorico(d: PrescricaoDetalhe) {
    setCriado({
      prescricao_id: d.prescricao_id,
      exige_revisao: d.documentos.some((doc) => doc.pendencias.length > 0),
      documentos: d.documentos,
    });
    setAba("nova");
  }

  // "Recriar baseado nesta" (histórico) — pré-preenche o FORMULÁRIO de uma
  // receita nova com os dados desta. Não reabre nada: o médico edita e
  // clica "Criar receituário" como sempre, virando uma Prescription nova,
  // independente da que serviu de base.
  function recriarDoHistorico(d: PrescricaoDetalhe) {
    setCriado(null);
    setErro("");
    setPrevia(null);
    setNome(d.destinatario.nome ?? "");
    setEndereco(d.destinatario.endereco ?? "");
    setDocumento(d.destinatario.documento ?? "");
    setCid(d.documentos.find((doc) => doc.cid)?.cid ?? "");
    setObservacoes(d.observacoes ?? "");
    // Marca/preço NÃO são carregados daqui de propósito: pmc_snapshot é o
    // preço no momento em que a receita ORIGINAL foi feita, e a lista da
    // CMED muda todo mês — reaproveitar seria mostrar preço velho como se
    // fosse atual. Recriar sempre volta pro genérico; o médico escolhe marca
    // de novo se quiser, com o preço de agora.
    const novosItens: Item[] = d.itens_originais.length > 0
      ? d.itens_originais.map((i) => ({
          drug_slug: i.drug_slug ?? undefined, descricao: i.descricao,
          apresentacao: i.apresentacao ?? "", quantidade: i.quantidade ?? "",
          quantidade_extenso: i.quantidade_extenso ?? "", posologia: i.posologia ?? "",
          orientacao: i.orientacao ?? "",
        }))
      : [{ ...ITEM_VAZIO }];
    setItens(novosItens);
    setBuscaFarmaco(novosItens.map((i) => i.descricao));
    setApresentacoes(novosItens.map(() => null));
    setAba("nova");
  }

  if (erroCarregar) return <Erro mensagem={erroCarregar} />;
  if (!farmacos) return <Carregando />;

  return (
    <>
      <p className="eyebrow">Documentos</p>
      <h1>Prescrição Eletrônica</h1>

      <div style={{ display: "flex", gap: 8, marginBottom: "1rem" }}>
        <button className={aba === "nova" ? "botao" : "botao botao--secundario"} onClick={() => setAba("nova")}>
          Nova receita
        </button>
        <button className={aba === "historico" ? "botao" : "botao botao--secundario"} onClick={() => setAba("historico")}>
          Histórico
        </button>
      </div>

      {aba === "historico" ? (
        <HistoricoReceituario onAbrir={abrirDoHistorico} onRecriar={recriarDoHistorico} />
      ) : !criado ? (
        <div className="cartao" style={{ maxWidth: "72ch" }}>
          <p className="eyebrow" style={{ margin: 0 }}>Paciente</p>
          <label>Nome</label>
          <input value={nome} onChange={(e) => setNome(e.target.value)} />
          <label style={{ marginTop: "0.5rem" }}>Endereço completo (obrigatório para controle especial)</label>
          <input value={endereco} onChange={(e) => setEndereco(e.target.value)} />
          <label style={{ marginTop: "0.5rem" }}>CPF ou passaporte do paciente</label>
          <input value={documento} onChange={(e) => setDocumento(e.target.value)} />
          <label style={{ marginTop: "0.5rem" }}>CID (obrigatório para anabolizantes/Lista C5)</label>
          <input value={cid} onChange={(e) => setCid(e.target.value.toUpperCase())}
                 placeholder="Ex.: E29.1" maxLength={10} />
          <p className="eyebrow" style={{ margin: "0.3rem 0 0" }}>
            Para Lista C5, também são obrigatórios endereço do paciente, CPF do prescritor,
            endereço e telefone profissionais. A emissão é restrita a CRM ou CRO.
          </p>

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
                  setApresentacoes((a) => a.map((v, idx) => idx === i ? null : v));
                }}
                placeholder="Busque na base ou digite livremente"
              />
              {(() => {
                if (!buscaFarmaco[i] || it.drug_slug) return null;
                const sugestoes = farmacos
                  .filter((f) => f.nome.toLowerCase().includes(buscaFarmaco[i].toLowerCase()))
                  .slice(0, 8);
                if (sugestoes.length === 0) {
                  // Não achou na base — deixa explícito que digitar segue valendo:
                  // nome, mg e apresentação ficam nos campos abaixo, texto livre.
                  return (
                    <p className="eyebrow" style={{ margin: "0.3rem 0 0" }}>
                      Não consta na base — pode preencher nome, mg e apresentação abaixo por conta própria.
                    </p>
                  );
                }
                return (
                  <div style={{ maxHeight: 140, overflowY: "auto", border: "1px solid var(--linha)", borderRadius: 6, marginTop: 4 }}>
                    {sugestoes.map((f) => (
                      <button key={f.slug} type="button"
                              style={{ display: "block", width: "100%", textAlign: "left", padding: "0.3rem 0.5rem", border: "none", background: "transparent", cursor: "pointer" }}
                              onClick={() => escolherFarmaco(i, f)}>
                        {f.nome}
                      </button>
                    ))}
                  </div>
                );
              })()}
              <label style={{ marginTop: "0.4rem" }}>Apresentação (ex.: 500mg, comprimido)</label>
              <input value={it.apresentacao} onChange={(e) => atualizarItem(i, "apresentacao", e.target.value)} />

              {it.drug_slug && (() => {
                const resp = apresentacoes[i];
                if (it.brand_name) {
                  // Marca já escolhida — mostra o que foi selecionado e a
                  // saída pra voltar ao genérico (marca nunca é obrigatória).
                  return (
                    <div style={{ marginTop: "0.4rem", padding: "0.4rem 0.6rem", border: "1px solid var(--linha)", borderRadius: 6 }}>
                      <p style={{ margin: 0, fontSize: "0.86rem" }}>
                        <strong>{it.brand_name}</strong> — {it.manufacturer}
                        {it.pmc_snapshot != null && (
                          <> · {it.pmc_snapshot.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}</>
                        )}
                      </p>
                      <button type="button" className="botao botao--secundario" style={{ marginTop: "0.3rem", fontSize: "0.82rem" }}
                              onClick={() => voltarParaGenerico(i)}>
                        Usar genérico (sem marca)
                      </button>
                    </div>
                  );
                }
                if (resp === undefined) {
                  return <p className="eyebrow" style={{ margin: "0.3rem 0 0" }}>Buscando marcas e preços…</p>;
                }
                if (!resp || resp.apresentacoes.length === 0) {
                  // Ausência de marca com PMC publicado é informação real na
                  // maioria dos casos (substância fora da CMED, ou só existe
                  // em combinação) — mostra o aviso em vez de sumir calada.
                  return resp?.aviso
                    ? <p className="eyebrow" style={{ margin: "0.3rem 0 0" }}>{resp.aviso}</p>
                    : null;
                }
                return (
                  <div style={{ marginTop: "0.3rem" }}>
                    <label style={{ margin: 0 }}>Marca (opcional — genérico já está selecionado)</label>
                    <div style={{ maxHeight: 180, overflowY: "auto", border: "1px solid var(--linha)", borderRadius: 6 }}>
                      {resp.apresentacoes.map((ap, ai) => (
                        <button key={ai} type="button"
                                style={{ display: "block", width: "100%", textAlign: "left", padding: "0.3rem 0.5rem", border: "none", borderBottom: "1px solid var(--linha)", background: "transparent", cursor: "pointer", fontSize: "0.86rem" }}
                                onClick={() => escolherApresentacao(i, ap, resp)}>
                        <strong>{ap.produto}</strong> — {ap.laboratorio}
                          <br />
                          <span style={{ color: "var(--texto-secundario, #666)" }}>
                            {ap.apresentacao} · {ap.preco.valor != null
                              ? ap.preco.valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })
                              : "sem preço publicado"}
                          </span>
                        </button>
                      ))}
                    </div>
                    {resp.uf && (
                      <p className="eyebrow" style={{ margin: "0.2rem 0 0" }}>
                        Preço de referência para {resp.uf} — teto CMED (PMC), lista {resp.cmed_publicado_em}.
                        Nunca é o preço final de farmácia, que costuma ser menor.
                      </p>
                    )}
                  </div>
                );
              })()}

              <div className="grade grade--2" style={{ marginTop: "0.4rem" }}>
                <div>
                  <label>Quantidade em algarismos</label>
                  <input value={it.quantidade} onChange={(e) => atualizarItem(i, "quantidade", e.target.value)}
                         placeholder="Ex.: 60 comprimidos" />
                </div>
                <div>
                  <label>Quantidade por extenso</label>
                  <input value={it.quantidade_extenso}
                         onChange={(e) => atualizarItem(i, "quantidade_extenso", e.target.value)}
                         placeholder="Ex.: sessenta comprimidos" />
                </div>
              </div>
              <p className="eyebrow" style={{ margin: "0.2rem 0 0" }}>
                Os dois campos são obrigatórios para Receita de Controle Especial. A RCE aceita
                no máximo três substâncias C1 e, em regra, quantidade para até 60 dias de tratamento.
              </p>
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
          <p style={{ color: "var(--sucesso)" }}>Receituário nº {criado.prescricao_id}.</p>
          {criado.documentos.map((d) => (
            <CartaoDocumento key={d.id} doc={d} provedores={provedores} tipos={tipos} onAtualizado={atualizarDocumento} />
          ))}
          <button className="botao botao--secundario" style={{ marginTop: "1rem" }}
                  onClick={() => { setCriado(null); setItens([{ ...ITEM_VAZIO }]); setBuscaFarmaco([""]); setNome(""); setEndereco(""); setDocumento(""); setCid(""); setPrevia(null); }}>
            Criar outra receita
          </button>
        </div>
      )}
    </>
  );
}
