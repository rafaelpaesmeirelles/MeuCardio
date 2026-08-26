import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import DicaContextual from "./DicaContextual";
import { api } from "../lib/api";

/**
 * Painel do Grafo de Conhecimento Clínico (issue #52) — complementar ao
 * `TudoSobreEsteTema` já existente (que cruza por TEMA exato). Este consome
 * `GET /api/grafo/relacionados`, que devolve relações diretas e associações
 * taxonômicas em dois saltos, com pontuação de relevância própria.
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
    const params = new URLSearchParams({ entity_type: entityType, slug: s });
    if (limitePorTipo) params.set("limite_por_tipo", String(limitePorTipo));
    api
      .get<Resposta>(`/grafo/relacionados?${params.toString()}`)
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
    <section className="cartao" style={{ marginTop: "1.2rem" }}>
      <p className="eyebrow">{titulo ?? "Relacionados no Grafo de Conhecimento"}</p>
      <p style={{ fontSize: "0.86rem", color: "var(--texto-secundario)", marginTop: "-0.2rem" }}>
        {resposta.total} {resposta.total === 1 ? "item relacionado" : "itens relacionados"} a{" "}
        <strong>{resposta.titulo ?? "este item"}</strong> no ecossistema.
      </p>

      <div style={{ marginTop: "0.7rem" }}>
        <DicaContextual id="grafo-relacionados" titulo="Tudo na Corvia está conectado">
          Relações diretas aparecem primeiro. Itens marcados como “mesmo tema” são conexões
          taxonômicas mais amplas. Siga por qualquer um deles sem perder o contexto — e volte
          quando quiser.
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
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem" }}>
              {g.itens.map((item) => {
                const mesmoTema = item.relation_type === "belongs_to_topic";
                return (
                  <Link
                    key={item.slug}
                    to={item.rota}
                    className="chip"
                    title={mesmoTema ? "Conexão por tema canônico" : "Relação direta"}
                    style={{ textDecoration: "none", maxWidth: "26rem" }}
                  >
                    {item.titulo}
                    {mesmoTema && (
                      <small style={{ marginLeft: "0.35rem", opacity: 0.72 }}>· mesmo tema</small>
                    )}
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
