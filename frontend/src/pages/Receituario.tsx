import { useEffect, useRef, useState } from "react";
import { api, ApiError, todasAsPaginas } from "../lib/api";
import { useAuth } from "../lib/auth";
import { Carregando, Erro, Vazio } from "../components/Estado";
import Icone from "../components/Icone";
import AssinaturaExternaITI from "../components/AssinaturaExternaITI";
import OfertaEnvioEmailPaciente from "../components/OfertaEnvioEmailPaciente";
import PrescricaoLivreEspecial from "../components/PrescricaoLivreEspecial";

type PrecoCmedSugestao = { valor: number | null; rotulo: string; fonte_icms?: string };
type EnderecoCep = {
  cep: string; logradouro: string; complemento: string; bairro: string; cidade: string; uf: string;
};
type Farmaco = {
  // `slug` nulo = candidato só do catálogo prescritivo amplo (CMED), sem
  // página clínica aprofundada — `tem_conteudo_clinico` é o sinal explícito.
  slug: string | null; nome: string; marca?: string | null; fabricante?: string | null;
  fonte?: string; tem_conteudo_clinico?: boolean;
  cmed_apresentacao_id?: number | null;
  apresentacao?: string | null; apresentacao_cmed?: string | null;
  ggrem?: string | null; registro?: string | null; substancia?: string | null;
  preco?: PrecoCmedSugestao | null;
  cmed_publicado_em?: string | null;
  price_source?: "kairos" | "cmed" | null;
  price_min?: number | null; price_max?: number | null;
  price_reference?: string | null; source_page?: number | null;
};
type Item = {
  drug_slug?: string; cmed_apresentacao_id?: number;
  descricao: string; apresentacao: string;
  quantidade: string; quantidade_extenso: string; posologia: string; orientacao: string;
  uso_continuo: boolean;
  brand_name?: string; manufacturer?: string; ggrem?: string;
  pmc_snapshot?: number; uf?: string; cmed_version?: string;
  price_source?: "kairos" | "cmed";
  price_label?: string; price_min?: number; price_max?: number;
  price_reference?: string; price_source_page?: number;
};

type PrecoCmed = { valor: number | null; rotulo: string; fonte_icms?: string };
type ApresentacaoCmed = {
  produto: string; laboratorio: string; apresentacao: string; ggrem: string;
  apresentacao_cmed?: string;
  restricao_hospitalar: boolean; preco: PrecoCmed;
};
type RespostaApresentacoes = {
  uf: string | null; cmed_publicado_em: string | null;
  apresentacoes: ApresentacaoCmed[]; aviso: string | null;
  kairos?: {
    fonte: "K@iros"; tipo_fonte: "inteligencia_de_mercado";
    edicao: number | null; competencia: string | null;
    opcoes: {
      produto: string; laboratorio: string; apresentacao: string;
      preco_minimo: number; preco_maximo: number;
      precos_por_icms: Record<string, number>; pagina_fonte: number | null;
    }[];
  };
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
  pode_enviar_email: boolean;
  aguardando_assinatura_externa: boolean;
  metodo_emitido: string | null;
};

// Trabalho 14 (06/08/2026) — os métodos sem API própria: assinatura
// acontece de verdade fora da Corvia, no Assinador ITI (assinador.iti.br).
// Mesmo conjunto de `provedor._MANUAL_EXTERNO` no backend.
const METODOS_MANUAL_EXTERNO = new Set(["GOVBR", "VIDAAS", "BIRDID", "SAFEID", "NEOID", "REMOTEID", "A3_TOKEN"]);
type ReceituarioCriado = { prescricao_id: number; exige_revisao: boolean; documentos: Documento[] };

type HistoricoDocResumo = { tipo: string; tipo_nome: string | null; status: string };
type HistoricoItem = {
  prescricao_id: number; criado_em: string; paciente_nome: string | null;
  documentos: HistoricoDocResumo[];
};
type HistoricoResposta = {
  items: HistoricoItem[]; page: number; page_size: number; has_more: boolean; total: number;
};
type ItemOriginal = {
  drug_slug: string | null; cmed_apresentacao_id?: number | null;
  descricao: string; apresentacao: string;
  quantidade: string; quantidade_extenso: string; posologia: string; orientacao: string;
  uso_continuo?: boolean;
  brand_name?: string | null; manufacturer?: string | null; ggrem?: string | null;
  pmc_snapshot?: number | null; uf?: string | null; cmed_version?: string | null;
};
type PrescricaoDetalhe = {
  prescricao_id: number;
  destinatario: { nome: string | null; endereco: string | null; documento: string | null };
  observacoes: string | null;
  itens_originais: ItemOriginal[];
  documentos: Documento[];
};

type Provedor = { codigo: string; nome: string; nivel: string; familia: string; disponivel: boolean; motivo: string | null };
type TipoReceituario = { codigo: string; nome: string; ativo: boolean };

const STATUS_RÓTULO: Record<string, string> = {
  rascunho: "Rascunho", revisado: "Revisado", emitido: "Emitido",
};

function normalizarBusca(valor: string | null | undefined) {
  return (valor ?? "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("pt-BR").trim();
}

function formatarPreco(valor: number | null | undefined) {
  if (valor == null) return "Preço não publicado";
  return valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function formatarFaixaPreco(minimo: number | null | undefined, maximo: number | null | undefined) {
  if (minimo == null || maximo == null) return "Preço não publicado";
  if (minimo === maximo) return formatarPreco(minimo);
  return `${formatarPreco(minimo)} a ${formatarPreco(maximo)}`;
}

function precoCmedExibivel(preco: PrecoCmedSugestao | null | undefined) {
  if (!preco || preco.fonte_icms === "media_nacional_nao_verificada" || /verifica[cç][aã]o humana/i.test(preco.rotulo)) {
    return { valor: null, rotulo: "Preço não disponível para esta UF" };
  }
  return { valor: preco.valor, rotulo: formatarPreco(preco.valor) };
}

function formatarCep(valor: string) {
  const digitos = valor.replace(/\D/g, "").slice(0, 8);
  return digitos.length > 5 ? `${digitos.slice(0, 5)}-${digitos.slice(5)}` : digitos;
}

function montarEnderecoCompleto(campos: {
  cep: string; logradouro: string; numero: string; complemento: string;
  bairro: string; cidade: string; uf: string;
}) {
  const primeira = [campos.logradouro.trim(), campos.numero.trim()].filter(Boolean).join(", ");
  return [
    [primeira, campos.complemento.trim()].filter(Boolean).join(" - "),
    campos.bairro.trim(),
    campos.cidade.trim() && campos.uf.trim() ? `${campos.cidade.trim()}/${campos.uf.trim().toUpperCase()}` : campos.cidade.trim() || campos.uf.trim().toUpperCase(),
    campos.cep.trim() ? `CEP ${formatarCep(campos.cep)}` : "",
  ].filter(Boolean).join(" - ");
}

function rotuloPrecoItem(item: Item) {
  return item.price_label ?? formatarPreco(item.pmc_snapshot);
}

function baixarBlob(blob: Blob, nomeArquivo: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = nomeArquivo;
  a.click();
  URL.revokeObjectURL(url);
}

function CartaoDocumento({ doc, provedores, tipos, onAtualizado }: {
  doc: Documento; provedores: Provedor[] | null; tipos: TipoReceituario[] | null;
  onAtualizado: (d: Documento) => void;
}) {
  const { usuario } = useAuth();
  const [revisando, setRevisando] = useState(false);
  const [emitindo, setEmitindo] = useState(false);
  const [endereco, setEndereco] = useState<"" | "residencial" | "profissional">("");
  const [metodo, setMetodo] = useState(usuario?.assinatura_metodo_preferido ?? "MANUAL");
  const [corrigirPara, setCorrigirPara] = useState(doc.tipo);
  const [motivoCorrecao, setMotivoCorrecao] = useState("");
  const [erro, setErro] = useState("");
  const [email, setEmail] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [resultadoEnvio, setResultadoEnvio] = useState<{ enviado: boolean; link: string | null } | null>(null);
  const [assinadoExternoAgora, setAssinadoExternoAgora] = useState(false);
  const temC5 = doc.itens.some((item) => String(item.lista ?? "").toUpperCase() === "C5");

  // `usuario` pode chegar depois do primeiro render. Sem esta sincronizacao,
  // o estado ficava preso em MANUAL mesmo quando Minha Conta definia A1.
  useEffect(() => {
    if (usuario?.assinatura_metodo_preferido) {
      setMetodo(usuario.assinatura_metodo_preferido);
    }
  }, [usuario?.assinatura_metodo_preferido]);

  useEffect(() => {
    if (doc.tipo !== "RCE" || !provedores?.length) return;
    setMetodo((atual) => {
      const selecionado = provedores.find((p) => p.codigo === atual);
      if (selecionado && (selecionado.codigo === "MANUAL" || selecionado.nivel === "qualificada")) {
        return atual;
      }
      return provedores.find((p) => p.disponivel && p.nivel === "qualificada")?.codigo
        ?? provedores.find((p) => p.codigo === "MANUAL")?.codigo
        ?? "MANUAL";
    });
  }, [doc.tipo, provedores]);

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
      const prefixo = doc.tipo === "RCE" ? "receita-controle-especial" : "receituario";
      const sufixo = metodo === "A1_ARQUIVO" ? "-assinado" : "";
      baixarBlob(blob, `${prefixo}-${doc.id}${sufixo}.pdf`);
      const externo = METODOS_MANUAL_EXTERNO.has(metodo);
      const provedor = provedores?.find((item) => item.codigo === metodo);
      onAtualizado({
        ...doc,
        status: "emitido",
        // Método manual-externo (Trabalho 14) nunca assina em `/emitir` — o
        // PDF baixado agora está SEM assinatura, `pode_enviar_email`
        // continua false até o médico voltar do Assinador ITI. Os demais
        // (MANUAL, A1_ARQUIVO) seguem a lógica anterior: assinam de
        // verdade na própria chamada, quando o nível é qualificada.
        pode_enviar_email: externo ? false : Boolean(
          metodo !== "MANUAL" && provedor?.disponivel && provedor.nivel === "qualificada",
        ),
        aguardando_assinatura_externa: externo,
        metodo_emitido: metodo,
      });
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
        <>
          <p style={{ fontSize: "0.86rem", marginTop: "0.4rem" }}>
            Modelo Anvisa V2: duas vias. O verso opcional de preenchimento da farmácia não é impresso.
          </p>
        </>
      )}
      {temC5 && (
        <p style={{ color: "var(--alerta)", fontSize: "0.84rem", marginTop: "0.4rem" }}>
          Lista C5: exige CRM/CRO, CPF, endereço e telefone profissionais, endereço do paciente e CID.
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
              Usa o endereço profissional cadastrado; na Lista C5, endereço e telefone são obrigatórios.
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
            {(provedores ?? []).map((p) => {
              const invalidoParaRce = doc.tipo === "RCE" && p.codigo !== "MANUAL" && p.nivel !== "qualificada";
              return (
              <option key={p.codigo} value={p.codigo} disabled={!p.disponivel || invalidoParaRce}>
                {p.nome}{!p.disponivel ? " — indisponível" : invalidoParaRce ? " — não válido para RCE" : ""}
              </option>
              );
            })}
          </select>
          {(() => {
            const escolhido = provedores?.find((p) => p.codigo === metodo);
            if (!escolhido) return null;
            if (!escolhido.disponivel) {
              return <p style={{ color: "var(--alerta)", fontSize: "0.82rem", margin: "0.3rem 0 0" }}>{escolhido.motivo}</p>;
            }
            if (doc.tipo === "RCE" && escolhido.nivel !== "qualificada" && escolhido.codigo !== "MANUAL") {
              return (
                <p style={{ color: "var(--alerta)", fontSize: "0.82rem", margin: "0.3rem 0 0" }}>
                  Receita de controle especial exige assinatura qualificada ICP-Brasil. A assinatura gov.br comum
                  é avançada e não pode ser usada neste documento.
                </p>
              );
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

      {doc.status === "emitido" && doc.aguardando_assinatura_externa && doc.metodo_emitido && (
        <AssinaturaExternaITI
          metodo={doc.metodo_emitido}
          nomeProvedor={provedores?.find((p) => p.codigo === doc.metodo_emitido)?.nome ?? doc.metodo_emitido}
          enviarUrl={`/receituario/documentos/${doc.id}/assinatura-externa`}
          onConcluido={() => {
            const provedor = provedores?.find((p) => p.codigo === doc.metodo_emitido);
            setAssinadoExternoAgora(true);
            onAtualizado({
              ...doc,
              aguardando_assinatura_externa: false,
              pode_enviar_email: provedor?.nivel === "qualificada",
            });
          }}
        />
      )}
      {assinadoExternoAgora && !doc.aguardando_assinatura_externa && (
        <p style={{ color: "var(--sucesso)", fontSize: "0.86rem", marginTop: "0.4rem" }}>
          Assinatura conferida com sucesso — o documento já está assinado.
        </p>
      )}

      {doc.status === "emitido" && (
        <OfertaEnvioEmailPaciente
          endpointBase={`/receituario/documentos/${doc.id}`}
          habilitado={doc.pode_enviar_email}
        />
      )}

      {doc.status === "emitido" && doc.pode_enviar_email && (
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
      {doc.status === "emitido" && !doc.pode_enviar_email && (
        <p className="eyebrow" style={{ marginTop: "0.8rem" }}>
          O envio por e-mail será liberado quando esta receita tiver assinatura digital
          qualificada ICP-Brasil. Documento com assinatura manual não é enviado como receita digital.
        </p>
      )}
    </div>
  );
}

function HistoricoReceituario({ onAbrir, onRecriar }: {
  onAbrir: (d: PrescricaoDetalhe) => void; onRecriar: (d: PrescricaoDetalhe) => void;
}) {
  const [itens, setItens] = useState<HistoricoItem[] | null>(null);
  const [erro, setErro] = useState("");
  const [carregandoId, setCarregandoId] = useState<number | null>(null);
  const [carregandoMais, setCarregandoMais] = useState(false);
  const [nome, setNome] = useState("");
  const [tipo, setTipo] = useState("");
  const [pagina, setPagina] = useState(1);
  const [temMais, setTemMais] = useState(false);

  function caminhoHistorico(paginaAlvo: number) {
    const params = new URLSearchParams({ page: String(paginaAlvo), page_size: "20" });
    if (nome.trim()) params.set("nome", nome.trim());
    if (tipo) params.set("tipo", tipo);
    return `/receituario?${params}`;
  }

  useEffect(() => {
    let ativo = true;
    setItens(null);
    setErro("");
    setPagina(1);
    api.get<HistoricoResposta>(caminhoHistorico(1))
      .then((r) => {
        if (!ativo) return;
        setItens(r.items);
        setTemMais(r.has_more);
      })
      .catch((e) => ativo && setErro(e instanceof ApiError ? e.message : "Não foi possível carregar o histórico."));
    return () => { ativo = false; };
  }, [nome, tipo]);

  async function carregarMais() {
    const proxima = pagina + 1;
    setCarregandoMais(true);
    setErro("");
    try {
      const r = await api.get<HistoricoResposta>(caminhoHistorico(proxima));
      setItens((atuais) => [...(atuais ?? []), ...r.items]);
      setPagina(r.page);
      setTemMais(r.has_more);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível carregar mais receitas.");
    } finally {
      setCarregandoMais(false);
    }
  }

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
        <>
          {[...grupos.entries()].sort(([a], [b]) => a.localeCompare(b, "pt-BR")).map(([paciente, receitas]) => (
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
          ))}
          {temMais && (
            <button className="botao botao--secundario" onClick={carregarMais} disabled={carregandoMais}>
              {carregandoMais ? "Carregando…" : "Carregar mais"}
            </button>
          )}
        </>
      )}
    </div>
  );
}

const ITEM_VAZIO: Item = {
  descricao: "", apresentacao: "", quantidade: "", quantidade_extenso: "",
  posologia: "", orientacao: "", uso_continuo: false,
};

export default function Receituario() {
  const [aba, setAba] = useState<"nova" | "historico">("nova");
  const [farmacos, setFarmacos] = useState<Farmaco[] | null>(null);
  const [provedores, setProvedores] = useState<Provedor[] | null>(null);
  const [tipos, setTipos] = useState<TipoReceituario[] | null>(null);
  const [erroCarregar, setErroCarregar] = useState("");

  const [nome, setNome] = useState("");
  const [cep, setCep] = useState("");
  const [logradouro, setLogradouro] = useState("");
  const [numero, setNumero] = useState("");
  const [complemento, setComplemento] = useState("");
  const [bairro, setBairro] = useState("");
  const [cidade, setCidade] = useState("");
  const [uf, setUf] = useState("");
  const [consultandoCep, setConsultandoCep] = useState(false);
  const [erroCep, setErroCep] = useState("");
  const sequenciaCep = useRef(0);
  const [documento, setDocumento] = useState("");
  const [cid, setCid] = useState("");
  const [observacoes, setObservacoes] = useState("");
  const [itens, setItens] = useState<Item[]>([{ ...ITEM_VAZIO }]);
  const [buscaFarmaco, setBuscaFarmaco] = useState<string[]>([""]);
  const [sugestoesFarmaco, setSugestoesFarmaco] = useState<(Farmaco[] | undefined)[]>([[]]);
  const [marcaConsultada, setMarcaConsultada] = useState<(string | null)[]>([null]);
  const [apresentacoes, setApresentacoes] = useState<(RespostaApresentacoes | null | undefined)[]>([null]);
  const temporizadoresBusca = useRef<(number | undefined)[]>([]);
  const sequenciasBusca = useRef<number[]>([0]);
  const { usuario } = useAuth();

  const [previa, setPrevia] = useState<Previa | null>(null);
  const [classificando, setClassificando] = useState(false);
  const [criando, setCriando] = useState(false);
  const [erro, setErro] = useState("");
  const [criado, setCriado] = useState<ReceituarioCriado | null>(null);

  useEffect(() => {
    todasAsPaginas<{ slug: string; generic_name: string }>("/drugs")
      .then((l) => setFarmacos(l.map((d) => ({ slug: d.slug, nome: d.generic_name }))))
      .catch((e) => setErroCarregar(e instanceof ApiError ? e.message : "Não foi possível carregar os medicamentos."));
    api.get<Provedor[]>("/assinatura/provedores").then(setProvedores).catch(() => {});
    api.get<TipoReceituario[]>("/receituario/tipos").then(setTipos).catch(() => {});
    return () => temporizadoresBusca.current.forEach((timer) => timer && window.clearTimeout(timer));
  }, []);

  function atualizarItem(i: number, campo: keyof Item, valor: string | boolean | undefined) {
    setPrevia(null);
    setItens((lista) => lista.map((it, idx) => idx === i ? { ...it, [campo]: valor } : it));
  }

  function buscarMedicamentos(i: number, valor: string) {
    setBuscaFarmaco((atuais) => atuais.map((item, indice) => indice === i ? valor : item));
    setMarcaConsultada((atuais) => atuais.map((item, indice) => indice === i ? null : item));
    atualizarItem(i, "drug_slug", undefined);
    // Some o cartão de confirmação "só CMED" (`it.cmed_apresentacao_id && !it.drug_slug`)
    // assim que o médico volta a digitar — sem isto, ele ficava preso na
    // tela mesmo depois de o texto de busca já não corresponder mais à
    // apresentação escolhida antes.
    atualizarItem(i, "cmed_apresentacao_id", undefined);
    atualizarItem(i, "descricao", valor);
    setApresentacoes((atuais) => atuais.map((item, indice) => indice === i ? null : item));

    const sequencia = (sequenciasBusca.current[i] ?? 0) + 1;
    sequenciasBusca.current[i] = sequencia;
    if (temporizadoresBusca.current[i]) window.clearTimeout(temporizadoresBusca.current[i]);
    if (valor.trim().length < 2) {
      setSugestoesFarmaco((atuais) => atuais.map((item, indice) => indice === i ? [] : item));
      return;
    }
    setSugestoesFarmaco((atuais) => atuais.map((item, indice) => indice === i ? undefined : item));
    temporizadoresBusca.current[i] = window.setTimeout(() => {
      api.get<{
        slug: string | null; generic_name: string; brand_name: string | null;
        manufacturer: string | null; source: string; tem_conteudo_clinico?: boolean;
        cmed_apresentacao_id?: number | null;
        apresentacao?: string | null; apresentacao_cmed?: string | null;
        ggrem?: string | null; registro?: string | null; substancia?: string | null;
        preco?: PrecoCmedSugestao | null;
        cmed_publicado_em?: string | null;
        price_source?: "kairos" | "cmed" | null;
        price_min?: number | null; price_max?: number | null;
        price_reference?: string | null; source_page?: number | null;
      }[]>(`/drugs/sugestoes?q=${encodeURIComponent(valor.trim())}`)
        .then((resultado) => {
          if (sequenciasBusca.current[i] !== sequencia) return;
          setSugestoesFarmaco((atuais) => atuais.map((item, indice) => indice === i
            ? resultado.map((s) => ({
                slug: s.slug, nome: s.generic_name, marca: s.brand_name,
                fabricante: s.manufacturer, fonte: s.source,
                tem_conteudo_clinico: s.tem_conteudo_clinico,
                cmed_apresentacao_id: s.cmed_apresentacao_id,
                apresentacao: s.apresentacao, apresentacao_cmed: s.apresentacao_cmed,
                ggrem: s.ggrem, registro: s.registro, substancia: s.substancia,
                preco: s.preco,
                cmed_publicado_em: s.cmed_publicado_em,
                price_source: s.price_source,
                price_min: s.price_min, price_max: s.price_max,
                price_reference: s.price_reference, source_page: s.source_page,
              }))
            : item));
        })
        .catch(() => {
          if (sequenciasBusca.current[i] === sequencia) {
            setSugestoesFarmaco((atuais) => atuais.map((item, indice) => indice === i ? [] : item));
          }
        });
    }, 180);
  }

  function escolherFarmaco(i: number, f: Farmaco) {
    setPrevia(null);
    if (f.slug) {
      const precoCmed = precoCmedExibivel(f.preco);
      // Catálogo clínico: fluxo em 2 passos, como já era — escolhe o
      // genérico aqui, e a apresentação comercial específica logo abaixo
      // (`escolherApresentacao`, via `/drugs/{slug}/apresentacoes`).
      setItens((lista) => lista.map((it, idx) => idx === i
        ? { drug_slug: f.slug ?? undefined, cmed_apresentacao_id: undefined,
            descricao: f.marca ?? f.nome, apresentacao: f.apresentacao ?? "",
            quantidade: it.quantidade, quantidade_extenso: it.quantidade_extenso,
            posologia: it.posologia, orientacao: it.orientacao, uso_continuo: it.uso_continuo,
            brand_name: f.marca ?? undefined, manufacturer: f.fabricante ?? undefined,
            cmed_version: f.price_source === "kairos" ? undefined : f.cmed_publicado_em ?? undefined,
            price_source: f.price_source ?? (f.preco ? "cmed" : undefined),
            price_label: f.price_source === "kairos" ? f.preco?.rotulo : precoCmed.rotulo,
            price_min: f.price_min ?? precoCmed.valor ?? undefined,
            price_max: f.price_max ?? precoCmed.valor ?? undefined,
            price_reference: f.price_reference ?? f.cmed_publicado_em ?? undefined,
            price_source_page: f.source_page ?? undefined }
        : it));
      setBuscaFarmaco((b) => b.map((v, idx) => idx === i ? (f.marca ?? f.nome) : v));
      setMarcaConsultada((atuais) => atuais.map((valor, indice) => indice === i ? (f.marca ?? null) : valor));
      setSugestoesFarmaco((atuais) => atuais.map((valor, indice) => indice === i ? [] : valor));
      setApresentacoes((a) => a.map((v, idx) => idx === i ? undefined : v));
      api.get<RespostaApresentacoes>(`/drugs/${f.slug}/apresentacoes${usuario?.council_state ? `?uf=${usuario.council_state}` : ""}`)
        .then((r) => setApresentacoes((a) => a.map((v, idx) => idx === i ? r : v)))
        .catch(() => setApresentacoes((a) => a.map((v, idx) => idx === i ? null : v)));
      return;
    }

    // Só catálogo prescritivo amplo (CMED, sem página clínica): a sugestão
    // já É a apresentação comercial específica — não existe segundo passo
    // pra desdobrar (não há `/apresentacoes` sem `slug`), então tudo é
    // preenchido de uma vez, incluindo marca/laboratório/preço já
    // conhecidos da própria sugestão.
    const precoCmed = precoCmedExibivel(f.preco);
    setItens((lista) => lista.map((it, idx) => idx === i
      ? {
          drug_slug: undefined, cmed_apresentacao_id: f.cmed_apresentacao_id ?? undefined,
          descricao: f.marca ?? f.nome, apresentacao: f.apresentacao ?? "",
          quantidade: it.quantidade, quantidade_extenso: it.quantidade_extenso,
          posologia: it.posologia, orientacao: it.orientacao, uso_continuo: it.uso_continuo,
          brand_name: f.marca ?? undefined, manufacturer: f.fabricante ?? undefined,
          ggrem: f.ggrem ?? undefined, pmc_snapshot: precoCmed.valor ?? undefined,
          uf: usuario?.council_state ?? undefined,
          cmed_version: f.cmed_publicado_em ?? undefined,
          price_source: "cmed", price_label: precoCmed.rotulo,
          price_min: precoCmed.valor ?? undefined, price_max: precoCmed.valor ?? undefined,
          price_reference: f.cmed_publicado_em ?? undefined,
        }
      : it));
    setBuscaFarmaco((b) => b.map((v, idx) => idx === i ? (f.marca ?? f.nome) : v));
    setMarcaConsultada((atuais) => atuais.map((valor, indice) => indice === i ? (f.marca ?? null) : valor));
    setSugestoesFarmaco((atuais) => atuais.map((valor, indice) => indice === i ? [] : valor));
    setApresentacoes((a) => a.map((v, idx) => idx === i ? null : v));
  }

  function escolherApresentacao(i: number, ap: ApresentacaoCmed, resp: RespostaApresentacoes) {
    const precoCmed = precoCmedExibivel(ap.preco);
    setPrevia(null);
    setItens((lista) => lista.map((it, idx) => idx === i ? {
      ...it,
      descricao: ap.produto,
      apresentacao: ap.apresentacao,
      brand_name: ap.produto, manufacturer: ap.laboratorio, ggrem: ap.ggrem,
      pmc_snapshot: precoCmed.valor ?? undefined,
      uf: resp.uf ?? undefined, cmed_version: resp.cmed_publicado_em ?? undefined,
      price_source: "cmed", price_label: precoCmed.rotulo,
      price_min: precoCmed.valor ?? undefined, price_max: precoCmed.valor ?? undefined,
      price_reference: resp.cmed_publicado_em ?? undefined,
    } : it));
  }

  function escolherApresentacaoKairos(
    i: number,
    ap: NonNullable<RespostaApresentacoes["kairos"]>["opcoes"][number],
    fonte: NonNullable<RespostaApresentacoes["kairos"]>,
  ) {
    setPrevia(null);
    setItens((lista) => lista.map((it, idx) => idx === i ? {
      ...it,
      descricao: ap.produto,
      apresentacao: ap.apresentacao,
      brand_name: ap.produto,
      manufacturer: ap.laboratorio,
      pmc_snapshot: undefined,
      uf: undefined,
      cmed_version: undefined,
      price_source: "kairos",
      price_label: formatarFaixaPreco(ap.preco_minimo, ap.preco_maximo),
      price_min: ap.preco_minimo,
      price_max: ap.preco_maximo,
      price_reference: `edição ${fonte.edicao} · competência ${fonte.competencia}`,
      price_source_page: ap.pagina_fonte ?? undefined,
    } : it));
  }

  function voltarParaGenerico(i: number) {
    setPrevia(null);
    setItens((lista) => lista.map((it, idx) => {
      if (idx !== i) return it;
      const generico = farmacos?.find((f) => f.slug === it.drug_slug)?.nome ?? buscaFarmaco[i] ?? it.descricao;
      setBuscaFarmaco((atuais) => atuais.map((valor, indice) => indice === i ? generico : valor));
      return {
        ...it,
        descricao: generico,
        apresentacao: "",
        brand_name: undefined, manufacturer: undefined, ggrem: undefined,
        pmc_snapshot: undefined, uf: undefined, cmed_version: undefined,
        price_source: undefined, price_label: undefined,
        price_min: undefined, price_max: undefined,
        price_reference: undefined, price_source_page: undefined,
      };
    }));
    setMarcaConsultada((atuais) => atuais.map((valor, indice) => indice === i ? null : valor));
  }

  function trocarMedicamento(i: number) {
    // Só para item resolvido pelo catálogo prescritivo amplo (CMED, sem
    // `Drug` clínico) — não existe "genérico sem marca" pra voltar (a
    // sugestão já É a apresentação específica), então a única saída é
    // limpar o item por completo e deixar o médico buscar de novo.
    setPrevia(null);
    setItens((lista) => lista.map((it, idx) => idx === i
      ? {
          drug_slug: undefined, cmed_apresentacao_id: undefined,
          descricao: "", apresentacao: "",
          quantidade: it.quantidade, quantidade_extenso: it.quantidade_extenso,
          posologia: it.posologia, orientacao: it.orientacao, uso_continuo: it.uso_continuo,
        }
      : it));
    setBuscaFarmaco((b) => b.map((v, idx) => idx === i ? "" : v));
    setMarcaConsultada((atuais) => atuais.map((valor, indice) => indice === i ? null : valor));
    setSugestoesFarmaco((atuais) => atuais.map((valor, indice) => indice === i ? [] : valor));
    setApresentacoes((a) => a.map((v, idx) => idx === i ? null : v));
  }

  function adicionarItem() {
    setItens((l) => [...l, { ...ITEM_VAZIO }]);
    setBuscaFarmaco((b) => [...b, ""]);
    setSugestoesFarmaco((b) => [...b, []]);
    setMarcaConsultada((b) => [...b, null]);
    sequenciasBusca.current.push(0);
    setApresentacoes((a) => [...a, null]);
  }

  function removerItem(i: number) {
    setItens((l) => l.filter((_, idx) => idx !== i));
    setBuscaFarmaco((b) => b.filter((_, idx) => idx !== i));
    setSugestoesFarmaco((b) => b.filter((_, idx) => idx !== i));
    setMarcaConsultada((b) => b.filter((_, idx) => idx !== i));
    setApresentacoes((a) => a.filter((_, idx) => idx !== i));
    setPrevia(null);
  }

  async function atualizarCep(valor: string) {
    const formatado = formatarCep(valor);
    setCep(formatado);
    setErroCep("");
    const digitos = formatado.replace(/\D/g, "");
    const sequencia = ++sequenciaCep.current;
    if (digitos.length !== 8) {
      setConsultandoCep(false);
      return;
    }
    setConsultandoCep(true);
    try {
      const resposta = await api.get<EnderecoCep>(`/receituario/enderecos/cep/${digitos}`);
      if (sequencia !== sequenciaCep.current) return;
      setCep(formatarCep(resposta.cep));
      setLogradouro(resposta.logradouro);
      setComplemento(resposta.complemento);
      setBairro(resposta.bairro);
      setCidade(resposta.cidade);
      setUf(resposta.uf);
    } catch (e) {
      if (sequencia !== sequenciaCep.current) return;
      setErroCep(e instanceof ApiError ? e.message : "Não foi possível consultar o CEP. Preencha manualmente.");
    } finally {
      if (sequencia === sequenciaCep.current) setConsultandoCep(false);
    }
  }

  const itensValidos = itens.filter((it) => it.descricao.trim() || it.drug_slug || it.cmed_apresentacao_id);
  const itensComPreco = itensValidos.filter((it) => it.price_min != null || it.pmc_snapshot != null);
  const somaPrecosMinimos = itensComPreco.reduce((total, it) => total + (it.price_min ?? it.pmc_snapshot ?? 0), 0);
  const somaPrecosMaximos = itensComPreco.reduce((total, it) => total + (it.price_max ?? it.pmc_snapshot ?? 0), 0);
  const somaPrecosParcial = itensComPreco.length > 0 && itensComPreco.length < itensValidos.length;
  const enderecoCompleto = montarEnderecoCompleto({
    cep, logradouro, numero, complemento, bairro, cidade, uf,
  });
  const pedido = {
    destinatario: {
      nome,
      endereco: enderecoCompleto || undefined,
      documento: documento || undefined,
      cep: cep || undefined,
      logradouro: logradouro || undefined,
      numero: numero || undefined,
      complemento: complemento || undefined,
      bairro: bairro || undefined,
      cidade: cidade || undefined,
      uf: uf || undefined,
    },
    itens: itensValidos.map((it) => ({
      drug_slug: it.drug_slug, cmed_apresentacao_id: it.cmed_apresentacao_id,
      descricao: it.descricao, apresentacao: it.apresentacao,
      quantidade: it.quantidade, quantidade_extenso: it.quantidade_extenso,
      posologia: it.posologia, orientacao: it.orientacao, uso_continuo: it.uso_continuo,
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

  function abrirDoHistorico(d: PrescricaoDetalhe) {
    setCriado({
      prescricao_id: d.prescricao_id,
      exige_revisao: d.documentos.some((doc) => doc.pendencias.length > 0),
      documentos: d.documentos,
    });
    setAba("nova");
  }

  function recriarDoHistorico(d: PrescricaoDetalhe) {
    setCriado(null);
    setErro("");
    setPrevia(null);
    setNome(d.destinatario.nome ?? "");
    setCep("");
    setLogradouro(d.destinatario.endereco ?? "");
    setNumero("");
    setComplemento("");
    setBairro("");
    setCidade("");
    setUf("");
    setDocumento(d.destinatario.documento ?? "");
    setCid(d.documentos.find((doc) => doc.cid)?.cid ?? "");
    setObservacoes(d.observacoes ?? "");
    const novosItens: Item[] = d.itens_originais.length > 0
      ? d.itens_originais.map((i) => ({
          drug_slug: i.drug_slug ?? undefined,
          cmed_apresentacao_id: i.cmed_apresentacao_id ?? undefined,
          descricao: i.brand_name ?? i.descricao,
          apresentacao: i.apresentacao ?? "",
          quantidade: i.quantidade ?? "",
          quantidade_extenso: i.quantidade_extenso ?? "",
          posologia: i.posologia ?? "",
          orientacao: i.orientacao ?? "",
          uso_continuo: Boolean(i.uso_continuo),
          brand_name: i.brand_name ?? undefined,
          manufacturer: i.manufacturer ?? undefined,
          ggrem: i.ggrem ?? undefined,
          pmc_snapshot: i.pmc_snapshot ?? undefined,
          uf: i.uf ?? undefined,
          cmed_version: i.cmed_version ?? undefined,
        }))
      : [{ ...ITEM_VAZIO }];
    setItens(novosItens);
    setBuscaFarmaco(novosItens.map((item) =>
      farmacos?.find((f) => f.slug === item.drug_slug)?.nome ?? item.descricao,
    ));
    setApresentacoes(novosItens.map(() => null));
    setSugestoesFarmaco(novosItens.map(() => []));
    setMarcaConsultada(novosItens.map((item) => item.brand_name ?? null));
    setAba("nova");
  }

  if (erroCarregar) return <Erro mensagem={erroCarregar} />;
  if (!farmacos) return <Carregando />;

  return (
    <div className="prescricao">
      <header className="prescricao__cabecalho">
        <div>
          <p className="eyebrow">Documentos clínicos</p>
          <h1>Prescrição Eletrônica</h1>
          <p>Prepare, revise e emita a receita com rastreabilidade do medicamento à assinatura.</p>
        </div>
        <div className="prescricao__seguranca">
          <Icone nome="check" />
          <span><strong>Fluxo seguro</strong><small>Revisão obrigatória antes da emissão</small></span>
        </div>
      </header>

      <div className="prescricao__abas" role="tablist" aria-label="Seções da prescrição">
        <button role="tab" aria-selected={aba === "nova"} className={aba === "nova" ? "ativo" : ""} onClick={() => setAba("nova")}>
          Nova receita
        </button>
        <button role="tab" aria-selected={aba === "historico"} className={aba === "historico" ? "ativo" : ""} onClick={() => setAba("historico")}>
          Histórico
        </button>
      </div>

      {aba === "nova" && !criado && <PrescricaoLivreEspecial />}

      {aba === "historico" ? (
        <HistoricoReceituario onAbrir={abrirDoHistorico} onRecriar={recriarDoHistorico} />
      ) : !criado ? (
        <div className="prescricao-workspace">
        <div className="cartao prescricao__formulario">
          <section className="prescricao-bloco">
            <div className="prescricao-bloco__titulo">
              <span>1</span><div><p className="eyebrow">Destinatário</p><h2>Dados do paciente</h2></div>
            </div>
            <div className="prescricao-paciente__grade">
              <div className="prescricao-campo prescricao-campo--largo">
                <label>Nome completo</label>
                <input value={nome} onChange={(e) => setNome(e.target.value)} autoComplete="name" />
              </div>
              <div className="prescricao-campo">
                <label>CPF do Paciente</label>
                <input value={documento} onChange={(e) => setDocumento(e.target.value)} />
              </div>
              <div className="prescricao-campo">
                <label>CID <small>Obrigatório para anabolizantes/Lista C5</small></label>
                <input value={cid} onChange={(e) => setCid(e.target.value.toUpperCase())}
                       placeholder="Ex.: E29.1" maxLength={10} />
              </div>
              <div className="prescricao-campo">
                <label>CEP <small>Preenche o endereço automaticamente</small></label>
                <input value={cep} onChange={(e) => void atualizarCep(e.target.value)}
                       inputMode="numeric" autoComplete="postal-code" placeholder="00000-000" />
                {consultandoCep && <small className="prescricao-campo__estado">Consultando CEP…</small>}
                {erroCep && <small className="prescricao-campo__erro">{erroCep}</small>}
              </div>
              <div className="prescricao-campo prescricao-campo--largo">
                <label>Logradouro <small>Obrigatório para controle especial</small></label>
                <input value={logradouro} onChange={(e) => setLogradouro(e.target.value)} autoComplete="address-line1" />
              </div>
              <div className="prescricao-campo">
                <label>Número <small>Obrigatório para controle especial</small></label>
                <input value={numero} onChange={(e) => setNumero(e.target.value)} autoComplete="address-line2" />
              </div>
              <div className="prescricao-campo">
                <label>Complemento <small>Opcional</small></label>
                <input value={complemento} onChange={(e) => setComplemento(e.target.value)} autoComplete="address-line3" />
              </div>
              <div className="prescricao-campo">
                <label>Bairro <small>Obrigatório para controle especial</small></label>
                <input value={bairro} onChange={(e) => setBairro(e.target.value)} />
              </div>
              <div className="prescricao-campo">
                <label>Cidade <small>Obrigatório para controle especial</small></label>
                <input value={cidade} onChange={(e) => setCidade(e.target.value)} autoComplete="address-level2" />
              </div>
              <div className="prescricao-campo">
                <label>Estado (UF) <small>Obrigatório para controle especial</small></label>
                <input value={uf} onChange={(e) => setUf(e.target.value.replace(/[^a-z]/gi, "").slice(0, 2).toUpperCase())}
                       autoComplete="address-level1" maxLength={2} placeholder="SP" />
              </div>
            </div>
          <p className="prescricao__nota-legal">
            Para Lista C5, também são obrigatórios endereço do paciente, CPF do prescritor,
            endereço e telefone profissionais. A emissão é restrita a CRM ou CRO.
          </p>
          </section>

          <section className="prescricao-bloco">
            <div className="prescricao-bloco__titulo">
              <span>2</span><div><p className="eyebrow">Medicamentos</p><h2>Itens da receita</h2></div>
            </div>
          {itens.map((it, i) => (
            <article key={i} className="prescricao-item">
              <div className="prescricao-item__topo">
                <span>Item {String(i + 1).padStart(2, "0")}</span>
                {itens.length > 1 && (
                  <button type="button" className="prescricao-item__remover" onClick={() => removerItem(i)}>Remover</button>
                )}
              </div>
              <label>Medicamento <small>nome genérico ou comercial</small></label>
              <input
                value={buscaFarmaco[i] ?? ""}
                onChange={(e) => buscarMedicamentos(i, e.target.value)}
                placeholder="Digite o nome genérico ou comercial"
                autoComplete="off"
              />
              {(() => {
                // Some por inteiro assim que o item já tem substância
                // resolvida — catálogo clínico (`drug_slug`) OU catálogo
                // prescritivo amplo (`cmed_apresentacao_id`). Sem essa
                // segunda condição, escolher uma sugestão só-CMED reabria a
                // mesma lista de sugestões (ela só some quando `drug_slug`
                // existe) e ainda por cima mostrava "não consta na base"
                // logo depois de o item ter sido resolvido com sucesso.
                if (!buscaFarmaco[i] || it.drug_slug || it.cmed_apresentacao_id) return null;
                if (buscaFarmaco[i].trim().length < 2) {
                  return <p className="eyebrow" style={{ margin: "0.3rem 0 0" }}>Digite ao menos 2 caracteres.</p>;
                }
                const sugestoes = sugestoesFarmaco[i];
                if (sugestoes === undefined) {
                  return <p className="eyebrow" style={{ margin: "0.3rem 0 0" }}>Buscando genéricos e marcas na lista CMED…</p>;
                }
                if (sugestoes.length === 0) {
                  return (
                    <p className="eyebrow" style={{ margin: "0.3rem 0 0" }}>
                      Não consta na base — pode preencher nome, mg e apresentação abaixo por conta própria.
                    </p>
                  );
                }
                return (
                  <div className="prescricao-sugestoes" role="listbox" aria-label="Sugestões de medicamentos">
                    <div className="prescricao-sugestoes__cabecalho" aria-hidden="true">
                      <span>Medicamento e apresentação</span>
                      <span>Fabricante e fonte</span>
                      <span>Preço de referência</span>
                    </div>
                    {sugestoes.map((f) => {
                      const rotuloPrincipal = f.marca ?? f.nome;
                      const generico = f.marca && normalizarBusca(f.marca) !== normalizarBusca(f.nome) ? f.nome : null;
                      return (
                        <button
                          key={`${f.slug ?? "cmed"}:${f.cmed_apresentacao_id ?? ""}:${f.marca ?? ""}:${f.fabricante ?? ""}`}
                          type="button"
                          onClick={() => escolherFarmaco(i, f)}>
                          <span className="prescricao-sugestao__principal">
                            <strong>{rotuloPrincipal}</strong>
                            {generico && <small>Princípio ativo: {generico}</small>}
                            {f.apresentacao && <small>{f.apresentacao}</small>}
                          </span>
                          <span className="prescricao-sugestao__meta">
                            <small className="prescricao-sugestao__rotulo">Fabricante e fonte</small>
                            <small>
                              {[
                                f.fabricante,
                                f.fonte,
                              ].filter(Boolean).join(" · ")}
                            </small>
                          </span>
                          <span className="prescricao-sugestao__preco">
                            <small className="prescricao-sugestao__rotulo">Preço de referência</small>
                            <strong>{f.preco
                              ? f.price_source === "kairos"
                                ? f.preco.rotulo
                                : precoCmedExibivel(f.preco).rotulo
                              : "Consultar apresentação"}</strong>
                            {f.preco && (
                              <small>
                                {f.fonte ?? "CMED"}
                                {f.price_source !== "kairos" && usuario?.council_state ? ` · ${usuario.council_state}` : ""}
                              </small>
                            )}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                );
              })()}
              <label style={{ marginTop: "0.4rem" }}>Apresentação (ex.: 500mg, comprimido)</label>
              <input value={it.apresentacao} onChange={(e) => atualizarItem(i, "apresentacao", e.target.value)} />

              {it.drug_slug && (() => {
                const resp = apresentacoes[i];
                if (it.brand_name) {
                  return (
                    <div className="prescricao-selecao">
                      <p>
                        <span><strong>{it.brand_name}</strong> — {it.manufacturer}</span>
                        <strong className="prescricao-selecao__preco">{rotuloPrecoItem(it)}</strong>
                      </p>
                      <p className="eyebrow" style={{ margin: "0.2rem 0 0" }}>{it.apresentacao}</p>
                      <small className="prescricao-selecao__fonte">
                        Fonte {it.price_source === "kairos" ? "K@iros" : "CMED"}
                        {it.uf ? ` · ${it.uf}` : ""}
                        {it.price_reference ? ` · ${it.price_reference}` : it.cmed_version ? ` · referência ${it.cmed_version}` : ""}
                        {it.price_source_page ? ` · pág. ${it.price_source_page}` : ""}
                      </small>
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
                if (!resp || (resp.apresentacoes.length === 0 && (resp.kairos?.opcoes.length ?? 0) === 0)) {
                  return resp?.aviso
                    ? <p className="eyebrow" style={{ margin: "0.3rem 0 0" }}>{resp.aviso}</p>
                    : null;
                }
                const marcaAlvo = normalizarBusca(marcaConsultada[i]);
                const opcoes = marcaAlvo
                  ? resp.apresentacoes.filter((ap) => normalizarBusca(ap.produto) === marcaAlvo)
                  : resp.apresentacoes;
                const opcoesKairos = marcaAlvo
                  ? (resp.kairos?.opcoes ?? []).filter((ap) => normalizarBusca(ap.produto) === marcaAlvo)
                  : (resp.kairos?.opcoes ?? []);
                if (marcaAlvo && opcoes.length === 0 && opcoesKairos.length === 0) {
                  return (
                    <p className="eyebrow" style={{ margin: "0.3rem 0 0" }}>
                      A marca foi localizada no catálogo, mas não há apresentação vinculada a este
                      princípio ativo na versão CMED carregada. Se necessário, selecione o genérico.
                    </p>
                  );
                }
                return (
                  <div className="prescricao-apresentacoes">
                    <label style={{ margin: 0 }}>Marca (opcional — genérico já está selecionado)</label>
                    {opcoesKairos.length > 0 && resp.kairos && (
                      <section className="prescricao-apresentacoes__fonte prescricao-apresentacoes__fonte--kairos">
                        <header>
                          <strong>K@iros · edição {resp.kairos.edicao}</strong>
                          <small>Competência {resp.kairos.competencia} · fonte mais recente disponível</small>
                        </header>
                        <div className="prescricao-apresentacoes__lista">
                          {opcoesKairos.map((ap, ai) => (
                            <button key={`kairos:${ai}`} type="button"
                                    onClick={() => escolherApresentacaoKairos(i, ap, resp.kairos!)}>
                              <span>
                                <strong>{ap.produto}</strong>
                                <small>{ap.laboratorio} · {ap.apresentacao}</small>
                              </span>
                              <strong className="prescricao-apresentacoes__preco">
                                {formatarFaixaPreco(ap.preco_minimo, ap.preco_maximo)}
                              </strong>
                            </button>
                          ))}
                        </div>
                        <p>Faixa literal dos PMC publicados por alíquota de ICMS; nenhuma UF é presumida.</p>
                      </section>
                    )}
                    {opcoes.length > 0 && (
                      <section className="prescricao-apresentacoes__fonte">
                        <header>
                          <strong>CMED/ANVISA</strong>
                          <small>Referência regulatória oficial · {resp.cmed_publicado_em}</small>
                        </header>
                        <div className="prescricao-apresentacoes__lista">
                          {opcoes.map((ap, ai) => (
                            <button key={`cmed:${ai}`} type="button"
                                    onClick={() => escolherApresentacao(i, ap, resp)}>
                              <span>
                                <strong>{ap.produto}</strong>
                                <small>{ap.laboratorio} · {ap.apresentacao}</small>
                              </span>
                              <strong className="prescricao-apresentacoes__preco">
                                {precoCmedExibivel(ap.preco).rotulo}
                              </strong>
                            </button>
                          ))}
                        </div>
                      </section>
                    )}
                    {resp.uf && (
                      <p className="eyebrow" style={{ margin: "0.2rem 0 0" }}>
                        Teto CMED (PMC), lista {resp.cmed_publicado_em}. Quando não houver alíquota
                        auditável para {resp.uf}, o preço permanece indisponível; nunca é estimado.
                      </p>
                    )}
                  </div>
                );
              })()}

              {it.cmed_apresentacao_id && !it.drug_slug && (
                <div className="prescricao-selecao">
                  <p>
                    <span><strong>{it.brand_name ?? it.descricao}</strong>{it.manufacturer && <> — {it.manufacturer}</>}</span>
                <strong className="prescricao-selecao__preco">{rotuloPrecoItem(it)}</strong>
                  </p>
                  <p className="eyebrow" style={{ margin: "0.2rem 0 0" }}>{it.apresentacao}</p>
                  <small className="prescricao-selecao__fonte">
                    Fonte CMED{it.uf ? ` · ${it.uf}` : ""}{it.price_reference ? ` · ${it.price_reference}` : it.cmed_version ? ` · referência ${it.cmed_version}` : ""}
                  </small>
                  <button type="button" className="botao botao--secundario" style={{ marginTop: "0.3rem", fontSize: "0.82rem" }}
                          onClick={() => trocarMedicamento(i)}>
                    Trocar medicamento
                  </button>
                </div>
              )}

              <div className="grade grade--2" style={{ marginTop: "0.4rem" }}>
                <div>
                  <label>Quantidade em algarismos</label>
                  <input value={it.quantidade} disabled={it.uso_continuo}
                         onChange={(e) => atualizarItem(i, "quantidade", e.target.value)}
                         placeholder="Ex.: 60 comprimidos" />
                </div>
                <div>
                  <label>Quantidade por extenso</label>
                  <input value={it.quantidade_extenso} disabled={it.uso_continuo}
                         onChange={(e) => atualizarItem(i, "quantidade_extenso", e.target.value)}
                         placeholder="Ex.: sessenta comprimidos" />
                </div>
              </div>
              <label className="prescricao-continuo">
                <input
                  type="checkbox"
                  checked={it.uso_continuo}
                  onChange={(e) => {
                    const marcado = e.target.checked;
                    setPrevia(null);
                    setItens((atuais) => atuais.map((item, indice) => indice === i
                      ? {
                          ...item,
                          uso_continuo: marcado,
                          quantidade: marcado ? "" : item.quantidade,
                          quantidade_extenso: marcado ? "" : item.quantidade_extenso,
                        }
                      : item));
                  }}
                  style={{ width: "auto", marginTop: 2 }}
                />
                <span>
                  <strong>Uso contínuo / tempo indeterminado</strong><br />
                  <small style={{ color: "var(--texto-secundario)" }}>
                    Na receita comum, substitui a quantidade pela orientação de dispensar o máximo
                    permitido pela legislação aplicável. Não elimina limites de controlados,
                    antimicrobianos ou outras categorias especiais.
                  </small>
                </span>
              </label>
              <p className="eyebrow" style={{ margin: "0.2rem 0 0" }}>
                Os dois campos são obrigatórios para Receita de Controle Especial. A RCE aceita
                no máximo três substâncias C1 e, em regra, quantidade para até 60 dias de tratamento.
              </p>
              <label style={{ marginTop: "0.4rem" }}>Posologia</label>
              <input value={it.posologia} onChange={(e) => atualizarItem(i, "posologia", e.target.value)} />
              <label style={{ marginTop: "0.4rem" }}>Orientação (opcional)</label>
              <input value={it.orientacao} onChange={(e) => atualizarItem(i, "orientacao", e.target.value)} />
            </article>
          ))}
          <button type="button" className="botao botao--secundario" style={{ marginTop: "0.6rem" }} onClick={adicionarItem}>
            + Adicionar item
          </button>
          </section>

          <section className="prescricao-bloco">
            <div className="prescricao-bloco__titulo">
              <span>3</span><div><p className="eyebrow">Finalização</p><h2>Revisar e gerar</h2></div>
            </div>
            <label>Observações <small>Opcional</small></label>
            <textarea rows={3} value={observacoes} onChange={(e) => setObservacoes(e.target.value)} />

          {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}

          <div className="prescricao__acoes">
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
          </section>
        </div>
        <aside className="prescricao-resumo" aria-label="Resumo da prescrição">
          <div className="prescricao-resumo__topo">
            <div>
              <p className="eyebrow">Resumo da prescrição</p>
              <h2>{itensValidos.length || 0} {itensValidos.length === 1 ? "item selecionado" : "itens selecionados"}</h2>
            </div>
            <span className={previa ? "prescricao-resumo__status pronto" : "prescricao-resumo__status"}>
              {previa ? "Prévia pronta" : "Em edição"}
            </span>
          </div>

          <div className="prescricao-resumo__itens">
            {itensValidos.length === 0 ? (
              <p className="prescricao-resumo__vazio">Pesquise por princípio ativo ou marca para incluir o primeiro medicamento.</p>
            ) : itensValidos.map((item, indice) => (
              <article key={`${item.drug_slug ?? item.cmed_apresentacao_id ?? indice}:${indice}`}>
                <span>{String(indice + 1).padStart(2, "0")}</span>
                <div>
                  <strong>{item.brand_name ?? item.descricao}</strong>
                  <small>{item.apresentacao || "Apresentação ainda não informada"}</small>
                  {item.posologia && <small>{item.posologia}</small>}
                </div>
                <strong className="prescricao-resumo__preco">{rotuloPrecoItem(item)}</strong>
              </article>
            ))}
          </div>

          <dl className="prescricao-resumo__dados">
            <div>
              <dt>Classificação</dt>
              <dd>{previa ? previa.documentos.map((doc) => doc.tipo_nome ?? doc.tipo).join(" · ") : "Aguardando prévia"}</dd>
            </div>
            <div>
              <dt>Assinatura</dt>
              <dd>Escolhida após revisão</dd>
            </div>
          </dl>

          <div className="prescricao-resumo__total">
            <span>
              <small>Soma de referência das apresentações{somaPrecosParcial ? " (parcial)" : ""}</small>
              <strong>{itensComPreco.length > 0 ? formatarFaixaPreco(somaPrecosMinimos, somaPrecosMaximos) : "Indisponível"}</strong>
            </span>
            <small>
              K@iros é exibida como inteligência de mercado por edição; CMED/ANVISA permanece a referência regulatória oficial. Os valores não representam o preço final praticado pela farmácia.
            </small>
          </div>

          <ul className="prescricao-resumo__checklist" aria-label="Conferência antes de gerar">
            <li className={nome.trim().length >= 3 ? "ok" : ""}><Icone nome="check" /> Paciente identificado</li>
            <li className={itensValidos.length > 0 ? "ok" : ""}><Icone nome="check" /> Medicamento informado</li>
            <li className={previa ? "ok" : ""}><Icone nome="check" /> Classificação revisada</li>
          </ul>

          <div className="prescricao-resumo__acoes">
            <button className="botao botao--secundario" onClick={verPrevia} disabled={classificando || !podeEnviar}>
              {classificando ? "Classificando…" : "Ver prévia"}
            </button>
            <button className="botao" onClick={criar} disabled={criando || !podeEnviar}>
              {criando ? "Criando…" : "Criar receituário"}
            </button>
          </div>
        </aside>
        </div>
      ) : (
        <div style={{ maxWidth: "72ch" }}>
          <p style={{ color: "var(--sucesso)" }}>Receituário nº {criado.prescricao_id}.</p>
          {criado.documentos.map((d) => (
            <CartaoDocumento key={d.id} doc={d} provedores={provedores} tipos={tipos} onAtualizado={atualizarDocumento} />
          ))}
          <button className="botao botao--secundario" style={{ marginTop: "1rem" }}
                  onClick={() => {
                    setCriado(null); setItens([{ ...ITEM_VAZIO }]); setBuscaFarmaco([""]); setNome("");
                    setCep(""); setLogradouro(""); setNumero(""); setComplemento("");
                    setBairro(""); setCidade(""); setUf(""); setDocumento(""); setCid(""); setPrevia(null);
                  }}>
            Criar outra receita
          </button>
        </div>
      )}
    </div>
  );
}
