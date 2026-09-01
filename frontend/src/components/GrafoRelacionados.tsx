import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import DicaContextual from "./DicaContextual";
import { api } from "../lib/api";

/**
 * Painel do Grafo de Conhecimento Clínico (issue #52) — complementar ao
 * `TudoSobreEsteTema` já existente (que cruza por TEMA exato). Este consome
 * `GET /api/grafo/relacionados`, que devolve relações clínicas diretas. A
 * expansão opcional por tema amplo fica desativada nesta superfície para não
 * sugerir que mera vizinhança taxonômica seja relação com o assunto atual.
 *
 * Mesma disciplina do painel de tema: some por inteiro (`return null`)
 * quando não há nada no grafo para este item, quando a chamada falha
 * (rede, 401, 402) ou quando a assinatura não está ativa — nunca mostra
 * seção vazia nem estado de erro ruidoso. Toda a lógica de "o que é
 * relacionado" vive no backend (`app/services/knowledge_graph.py`); este
 * componente só exibe o que a API já decidiu.
 */

type ItemRelacionado = {
  slug: string;
  titulo: string;
  relation_type: string;
  relevance_score: number;
  confidence: string;
  provenance_type: string;
  review_status: string;
  rota: string;
};

type Grupo = {
  tipo: string;
  rota_lista: string;
  total_disponivel: number;
  itens: ItemRelacionado[];
};

type Resposta = {
  entity_type: string;
  slug: string;
  titulo: string | null;
  grupos: Grupo[];
  total: number;
};

type NivelExplicabilidade = "curada" | "estruturada" | "inferida";

type Explicabilidade = {
  nivel: NivelExplicabilidade;
  rotulo: string;
  detalhe: string;
  cor: string;
};

const ROTULO_RELACAO: Record<string, string> = {
  treats: "Tratamento aplicável",
  indicated_for: "Indicação clínica",
  contraindicated_in: "Contraindicação clínica",
  contraindicated_with: "Contraindicação conjunta",
  interacts_with: "Interação relevante",
  monitor_with: "Monitorização necessária",
  diagnosed_by: "Diagnóstico ou investigação",
  supported_by: "Sustentação científica",
  studied_in: "População ou intervenção estudada",
  recommended_by: "Recomendação de diretriz ou evidência",
  associated_with: "Associação clínica",
  causes: "Relação causal",
  may_cause: "Possível efeito ou causalidade",
  alternative_to: "Alternativa clínica",
  belongs_to_class: "Classe estruturada",
  used_in_case: "Aplicação em caso clínico",
  mentioned_in: "Menção explícita",
  patient_education_for: "Educação do paciente",
  differential_for: "Diagnóstico diferencial",
  same_theme: "Tema clínico compartilhado",
  belongs_to_topic: "Taxonomia clínica",
  derived_from: "Derivação editorial",
  uses_flowchart: "Fluxograma utilizado",
  contains: "Composição curada",
};

const ROTULO_PROVENIENCIA: Record<string, string> = {
  editorial: "Curadoria editorial",
  structured_metadata: "Metadado estruturado",
  imported: "Fonte importada",
  derived: "Derivação do grafo",
  ai_suggested: "Sugestão de IA",
  clinical_context: "Contexto clínico",
};

const ROTULO_CONFIANCA: Record<string, string> = {
  explicit: "explícita",
  derived: "derivada",
  ai_suggested: "sugerida por IA",
};

const graphRequests = new Map<string, Promise<Resposta>>();

export function carregarRelacoesDoGrafo(entityType: string, slug: string, limitePorTipo?: number): Promise<Resposta> {
  const params = new URLSearchParams({ entity_type: entityType, slug });
  if (limitePorTipo) params.set("limite_por_tipo", String(limitePorTipo));
  const key = params.toString();
  const existente = graphRequests.get(key);
  if (existente) return existente;
  const request = api.get<Resposta>(`/grafo/relacionados?${key}`);
  graphRequests.set(key, request);
  request.then(
    () => { if (graphRequests.get(key) === request) graphRequests.delete(key); },
    () => { if (graphRequests.get(key) === request) graphRequests.delete(key); },
  );
  return request;
}

export function chavesVisiveisDoGrafo(resposta: Resposta): Set<string> {
  const chaves = new Set<string>();
  for (const grupo of resposta.grupos) {
    for (const item of grupo.itens) {
      chaves.add(`${grupo.tipo}:${item.slug}`);
      if (item.rota) chaves.add(`rota:${item.rota}`);
    }
  }
  return chaves;
}

function explicarRelacao(item: ItemRelacionado): Explicabilidade {
  const curada = item.provenance_type === "editorial" || item.confidence === "explicit";
  if (curada) {
    const revisada = item.review_status === "revisado";
    const detalhe = item.provenance_type === "imported"
      ? `Vínculo explícito de fonte importada ${revisada ? "e revisado" : "ainda pendente de revisão"}.`
      : item.provenance_type === "editorial"
        ? `Vínculo editorial explícito ${revisada ? "e revisado" : "ainda pendente de revisão"}.`
        : `Vínculo explícito ${revisada ? "e revisado" : "ainda pendente de revisão"}.`;
    return {
      nivel: "curada",
      rotulo: revisada ? "Curada e revisada" : "Curada · revisão pendente",
      detalhe,
      cor: "#63dfc1",
    };
  }
  if (["structured_metadata", "imported", "derived"].includes(item.provenance_type) || item.confidence === "derived") {
    return {
      nivel: "estruturada",
      rotulo: item.review_status === "revisado" ? "Estruturada e revisada" : "Estruturada",
      detalhe: "Derivada de metadado ou relação estruturada; consulte o tipo e a pertinência abaixo.",
      cor: "#76b7ff",
    };
  }
  return {
    nivel: "inferida",
    rotulo: "Inferida · não curada",
    detalhe: "Sugestão contextual ou computacional; não equivale a uma relação clínica revisada.",
    cor: "#d7a5ff",
  };
}

function percentual(score: number): string {
  return `${Math.round(Math.min(1, Math.max(0, score)) * 100)}%`;
}

const ROTULO_TIPO: Record<string, string> = {
  documento: "Documentos",
  fluxograma: "Fluxogramas",
  evidencia: "Evidências",
  estudo: "Estudos",
  medicamento: "Medicamentos",
  exame: "Exames",
  caso_clinico: "Casos clínicos",
  trilha: "Trilhas de estudo",
  galeria: "Galeria de imagens",
  checklist: "Checklists de alta",
  material_paciente: "Material do paciente",
  protocolo_emergencia: "Protocolos de emergência",
  calculadora: "Calculadoras",
  doenca: "Doenças",
  triagem_sintoma: "Triagem por sintomas",
};

function rotuloTipo(tipo: string): string {
  return ROTULO_TIPO[tipo] ?? tipo;
}

type Props = {
  /** Tipo do item atual, no vocabulário do grafo (ver ROTULO_TIPO). */
  entityType: string;
  /** Slug do próprio item — o grafo já exclui o item de si mesmo. */
  slug: string | null | undefined;
  /** Máximo de itens por grupo devolvido pela API (padrão do backend: 5). */
  limitePorTipo?: number;
  /** Título da seção — o padrão já é o texto pensado para a maioria das páginas. */
  titulo?: string;
};

export default function GrafoRelacionados({ entityType, slug, limitePorTipo, titulo }: Props) {
  const [resposta, setResposta] = useState<Resposta | null>(null);

  useEffect(() => {
    setResposta(null);
    const s = (slug ?? "").trim();
    if (!entityType || !s) return;
    let ativo = true;
    carregarRelacoesDoGrafo(entityType, s, limitePorTipo)
      .then((dados) => { if (ativo) setResposta(dados); })
      .catch(() => {
        // Silencioso de propósito, mesmo padrão de TudoSobreEsteTema: este
        // painel é um complemento da página, nunca o conteúdo principal —
        // falha de rede, 401 (sessão) ou 402 (assinatura) não podem quebrar
        // a leitura do item que o médico já abriu.
      });
    return () => { ativo = false; };
  }, [entityType, slug, limitePorTipo]);

  if (!resposta || resposta.total === 0) return null;
  const grupos = resposta.grupos.filter((g) => g.itens.length > 0);
  if (grupos.length === 0) return null;

  return (
    <section className="cartao" style={{ marginTop: "1.2rem" }} data-relationship-surface="knowledge-graph">
      <p className="eyebrow">{titulo ?? "Relações no Grafo de Conhecimento"}</p>
      <p style={{ fontSize: "0.86rem", color: "var(--texto-secundario)", marginTop: "-0.2rem" }}>
        {resposta.total} {resposta.total === 1 ? "item relacionado" : "itens relacionados"} a{" "}
        <strong>{resposta.titulo ?? "este item"}</strong> com tipo, proveniência, confiança e pertinência auditáveis.
      </p>

      <div style={{ marginTop: "0.7rem" }}>
        <DicaContextual id="grafo-relacionados" titulo="Como interpretar estas relações">
          Curada identifica vínculo editorial explícito; estruturada indica metadado ou regra determinística;
          inferida sinaliza sugestão ainda não equivalente a curadoria clínica. A pertinência ordena, mas não
          substitui a revisão humana.
        </DicaContextual>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "0.9rem", marginTop: "0.8rem" }}>
        {grupos.map((g) => (
          <div key={g.tipo}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
              <p style={{ fontWeight: 600, fontSize: "0.88rem", margin: "0 0 0.35rem" }}>
                {rotuloTipo(g.tipo)}
                {g.total_disponivel > g.itens.length && (
                  <small style={{ marginLeft: "0.35rem", opacity: 0.72 }}>
                    exibindo {g.itens.length} de {g.total_disponivel}
                  </small>
                )}
              </p>
              {g.rota_lista && (
                <Link to={g.rota_lista} style={{ fontSize: "0.78rem" }}>
                  ver todos »
                </Link>
              )}
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 17rem), 1fr))", gap: "0.5rem" }}>
              {g.itens.map((item) => {
                const explicacao = explicarRelacao(item);
                const proveniencia = ROTULO_PROVENIENCIA[item.provenance_type] ?? item.provenance_type;
                const confianca = ROTULO_CONFIANCA[item.confidence] ?? item.confidence;
                const relacao = ROTULO_RELACAO[item.relation_type] ?? item.relation_type.replaceAll("_", " ");
                return (
                  <Link
                    key={item.slug}
                    to={item.rota}
                    className="chip"
                    data-relation-level={explicacao.nivel}
                    title={explicacao.detalhe}
                    style={{ display: "grid", alignContent: "start", gap: "0.3rem", maxWidth: "none", minHeight: "6.7rem", padding: "0.72rem", textDecoration: "none", whiteSpace: "normal", background: "linear-gradient(145deg, rgba(6,24,39,.92), rgba(3,16,28,.96))", borderColor: "rgba(var(--space-rgb),.18)" }}
                  >
                    <span style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "0.35rem" }}>
                      <small style={{ color: explicacao.cor, fontWeight: 750, letterSpacing: ".035em" }}>{explicacao.rotulo}</small>
                      {item.review_status === "pendente_revisao" && <small style={{ color: "#f1c36f" }}>Revisão pendente</small>}
                    </span>
                    <strong style={{ color: "var(--space-text, #eaf4f7)", lineHeight: 1.3 }}>{item.titulo}</strong>
                    <small style={{ color: "var(--texto-secundario)", lineHeight: 1.35 }}>{relacao}</small>
                    <small style={{ color: "var(--texto-secundario)", opacity: 0.82, lineHeight: 1.35 }}>
                      {proveniencia} · confiança {confianca} · pertinência {percentual(item.relevance_score)}
                    </small>
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
