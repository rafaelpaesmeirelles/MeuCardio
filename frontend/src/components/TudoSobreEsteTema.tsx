import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { carregarRelacoesDoGrafo, chavesVisiveisDoGrafo } from "./GrafoRelacionados";

/**
 * "Tudo sobre este tema no Ecossistema Corvia" — pedido do Rafael, 08/08/2026:
 * a partir de QUALQUER item (documento, evidência, estudo, medicamento, exame,
 * caso clínico, trilha, imagem de galeria, calculadora, protocolo de
 * emergência, checklist ou material do paciente), o médico precisa ver tudo
 * que o ecossistema tem sobre aquele tópico e chegar lá num clique — sem
 * precisar voltar para a busca e refazer o filtro por tema manualmente.
 *
 * Puramente aditivo: some sozinho (`return null`) quando o item não tem tema
 * (`tema` vazio), quando a chamada falha, ou quando não há absolutamente
 * nenhum item relacionado publicado — nunca mostra uma seção vazia. Consome
 * `GET /api/relacionados`, cuja lógica de cruzamento (o que conta como "mesmo
 * tema" em cada uma das doze frentes do ecossistema) vive inteiramente no
 * backend (`app/services/related_content.py`) — este componente só exibe o
 * que a API já decidiu, nunca decide relação por conta própria.
 */

type ItemRelacionado = {
  slug: string;
  titulo: string;
  subtitulo: string | null;
  rota: string;
  relation_type?: string;
  relevance_score?: number;
  confidence?: string;
  provenance_type?: string;
  review_status?: string;
  match_score?: number;
  match_threshold?: number;
};

type Grupo = {
  tipo: string;
  rotulo: string;
  rota_lista: string;
  itens: ItemRelacionado[];
};

type Resposta = {
  tema?: string;
  medicamento?: { slug: string; titulo: string };
  temas?: string[];
  relation_scope?: string;
  relation_method?: string;
  grupos: Grupo[];
  total: number;
};

type Props = {
  /** Tema do item atual — o mesmo valor gravado em `theme`/`tema` no banco. */
  tema?: string | null;
  /**
   * Medicamento que ancora o painel. Diferente do tema genérico
   * "Farmacologia", esta rota atravessa somente indicações clínicas
   * estruturadas do próprio fármaco.
   */
  medicamentoSlug?: string;
  /** Tipo e slug do próprio item, para nunca aparecer na sua própria lista. */
  excluirTipo?: string;
  excluirSlug?: string;
  /** Título da seção — o padrão já é o texto pensado para a maioria das páginas. */
  titulo?: string;
};

const ROTULO_PROVENIENCIA: Record<string, string> = {
  editorial: "curadoria editorial",
  structured_metadata: "metadado estruturado",
  imported: "fonte importada",
  derived: "derivação do grafo",
  ai_suggested: "sugestão de IA",
  clinical_context: "contexto clínico",
};

function detalheDaRelacaoExplicita(item: ItemRelacionado, revisada: boolean): string {
  const estado = revisada ? "e revisado" : "ainda pendente de revisão";
  if (item.provenance_type === "imported") return `Vínculo explícito de fonte importada ${estado}.`;
  if (item.provenance_type === "editorial") return `Vínculo editorial explícito ${estado}.`;
  return `Vínculo explícito ${estado}.`;
}

function explicarCorrespondencia(item: ItemRelacionado, contexto: Resposta): { rotulo: string; detalhe: string; cor: string } {
  if (item.provenance_type === "editorial" || item.confidence === "explicit") {
    const revisada = item.review_status === "revisado";
    return {
      rotulo: revisada ? "Curada e revisada" : "Curada · revisão pendente",
      detalhe: detalheDaRelacaoExplicita(item, revisada),
      cor: revisada ? "#63dfc1" : "#8fdac8",
    };
  }
  if (item.provenance_type && ["structured_metadata", "imported", "derived"].includes(item.provenance_type)) {
    return { rotulo: "Estruturada", detalhe: "Correspondência derivada de metadado ou regra estruturada.", cor: "#76b7ff" };
  }
  if (contexto.relation_scope === "structured_clinical_topic" && contexto.relation_method === "reviewed_drug_indication") {
    return {
      rotulo: "Estruturada e revisada",
      detalhe: "Relação sustentada por indicação clínica estruturada e revisada do medicamento.",
      cor: "#76b7ff",
    };
  }
  return {
    rotulo: "Inferida por contexto",
    detalhe: "Seleção automática por assunto e taxonomia; não equivale a vínculo clínico curado.",
    cor: "#d7a5ff",
  };
}

function metadadosDaCorrespondencia(item: ItemRelacionado, contexto: Resposta): string {
  const partes: string[] = [];
  if (item.provenance_type) partes.push(ROTULO_PROVENIENCIA[item.provenance_type] ?? item.provenance_type.replaceAll("_", " "));
  else if (contexto.relation_method === "reviewed_drug_indication") partes.push("indicação clínica revisada");
  if (item.confidence) partes.push(`confiança ${item.confidence === "explicit" ? "explícita" : item.confidence === "derived" ? "derivada" : "sugerida por IA"}`);
  if (typeof item.relevance_score === "number") partes.push(`pertinência ${Math.round(Math.min(1, Math.max(0, item.relevance_score)) * 100)}%`);
  if (typeof item.match_score === "number" && typeof item.match_threshold === "number") {
    partes.push(`sinal ${item.match_score} · mínimo ${item.match_threshold}`);
  }
  return partes.join(" · ");
}

export default function TudoSobreEsteTema({ tema, medicamentoSlug, excluirTipo, excluirSlug, titulo }: Props) {
  const [resposta, setResposta] = useState<Resposta | null>(null);
  const [chavesDoGrafo, setChavesDoGrafo] = useState<Set<string> | null>(null);

  useEffect(() => {
    setResposta(null);
    setChavesDoGrafo(null);
    const t = (tema ?? "").trim();
    if (!t && !medicamentoSlug) return;
    let ativo = true;
    const params = new URLSearchParams({ tema: t });
    if (excluirTipo) params.set("excluir_tipo", excluirTipo);
    if (excluirSlug) {
      params.set("excluir_slug", excluirSlug);
      params.set("assunto", excluirSlug);
    }
    const endpoint = medicamentoSlug
      ? `/relacionados/medicamento/${encodeURIComponent(medicamentoSlug)}`
      : `/relacionados?${params.toString()}`;
    api
      .get<Resposta>(endpoint)
      .then((dados) => { if (ativo) setResposta(dados); })
      .catch(() => {
        // Silencioso de propósito: este painel é um complemento da página, não
        // o conteúdo principal — uma falha aqui não pode quebrar a leitura do
        // item que o médico já abriu.
      });
    if (excluirTipo && excluirSlug) {
      carregarRelacoesDoGrafo(excluirTipo, excluirSlug)
        .then((dados) => { if (ativo) setChavesDoGrafo(chavesVisiveisDoGrafo(dados)); })
        .catch(() => { if (ativo) setChavesDoGrafo(new Set()); });
    } else {
      setChavesDoGrafo(new Set());
    }
    return () => { ativo = false; };
  }, [tema, medicamentoSlug, excluirTipo, excluirSlug]);

  if (!resposta || resposta.total === 0 || chavesDoGrafo === null) return null;
  const grupos = resposta.grupos
    .map((grupo) => ({
      ...grupo,
      itens: grupo.itens.filter((item) => !chavesDoGrafo.has(`${grupo.tipo}:${item.slug}`) && !chavesDoGrafo.has(`rota:${item.rota}`)),
    }))
    .filter((grupo) => grupo.itens.length > 0);
  if (grupos.length === 0) return null;
  const totalContextual = grupos.reduce((total, grupo) => total + grupo.itens.length, 0);

  return (
    <section className="cartao" style={{ marginTop: "1.2rem" }} data-relationship-surface="contextual-inference">
      <p className="eyebrow">{titulo ?? "Tudo com Tudo · contexto"}</p>
      <p style={{ fontSize: "0.86rem", color: "var(--texto-secundario)", marginTop: "-0.2rem" }}>
        {totalContextual} {totalContextual === 1 ? "correspondência contextual" : "correspondências contextuais"} para{" "}
        <strong>{resposta.medicamento?.titulo ?? resposta.tema}</strong>. Esta seleção automática usa assunto e taxonomia;
        não transforma semelhança textual em vínculo clínico. Relações já exibidas no grafo foram removidas daqui.
      </p>

      {!!resposta.temas?.length && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", marginTop: "0.65rem" }} aria-label="Contextos clínicos relacionados">
          {resposta.temas.map((temaRelacionado) => <span className="chip" key={temaRelacionado}>{temaRelacionado}</span>)}
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: "0.9rem", marginTop: "0.8rem" }}>
        {grupos.map((g) => (
          <div key={g.tipo}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
              <p style={{ fontWeight: 600, fontSize: "0.88rem", margin: "0 0 0.35rem" }}>{g.rotulo}</p>
              <Link to={g.rota_lista} style={{ fontSize: "0.78rem" }}>
                ver todos »
              </Link>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 16rem), 1fr))", gap: "0.45rem" }}>
              {g.itens.map((item) => {
                const explicacao = explicarCorrespondencia(item, resposta);
                const metadados = metadadosDaCorrespondencia(item, resposta);
                return <Link
                  key={item.slug}
                  to={item.rota}
                  className="chip"
                  data-relation-level={explicacao.rotulo.startsWith("Curada") ? "curada" : explicacao.rotulo.startsWith("Estruturada") ? "estruturada" : "inferida"}
                  title={explicacao.detalhe}
                  style={{ display: "grid", gap: "0.25rem", alignContent: "start", maxWidth: "none", minHeight: "5.6rem", padding: "0.66rem", textDecoration: "none", whiteSpace: "normal", background: "rgba(5, 21, 36, .72)", borderColor: "rgba(var(--space-rgb), .14)" }}
                >
                  <small style={{ color: explicacao.cor, fontWeight: 750 }}>{explicacao.rotulo}</small>
                  <strong style={{ color: "var(--space-text, #eaf4f7)", lineHeight: 1.3 }}>{item.titulo}</strong>
                  {item.subtitulo && <small style={{ color: "var(--texto-secundario)", lineHeight: 1.35 }}>{item.subtitulo}</small>}
                  {metadados && <small style={{ color: "var(--texto-secundario)", opacity: 0.78 }}>{metadados}</small>}
                </Link>;
              })}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
