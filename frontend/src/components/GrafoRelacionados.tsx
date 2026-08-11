import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import DicaContextual from "./DicaContextual";
import { api } from "../lib/api";

/**
 * Painel do Grafo de Conhecimento Clínico (issue #52) — complementar ao
 * `TudoSobreEsteTema` já existente (que cruza por TEMA exato). Este consome
 * `GET /api/grafo/relacionados`, que devolve relações tipadas entre itens
 * específicos (não por tema), com pontuação de relevância própria.
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
    const params = new URLSearchParams({ entity_type: entityType, slug: s });
    if (limitePorTipo) params.set("limite_por_tipo", String(limitePorTipo));
    api
      .get<Resposta>(`/grafo/relacionados?${params.toString()}`)
      .then(setResposta)
      .catch(() => {
        // Silencioso de propósito, mesmo padrão de TudoSobreEsteTema: este
        // painel é um complemento da página, nunca o conteúdo principal —
        // falha de rede, 401 (sessão) ou 402 (assinatura) não podem quebrar
        // a leitura do item que o médico já abriu.
      });
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

      {/* Onboarding contextual (issue #52): a primeira vez que o médico
          encontra o painel do grafo, uma frase explica o paradigma. Depois
          de fechada, nunca mais aparece — em nenhuma das páginas de detalhe
          que instalam este componente. */}
      <div style={{ marginTop: "0.7rem" }}>
        <DicaContextual id="grafo-relacionados" titulo="Tudo na Corvia está conectado">
          Estes itens não foram buscados por você: são as relações que a Corvia já conhece entre
          este conteúdo e o resto do ecossistema. Siga por qualquer um deles sem perder o
          contexto — e volte quando quiser.
        </DicaContextual>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "0.9rem", marginTop: "0.8rem" }}>
        {grupos.map((g) => (
          <div key={g.tipo}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
              <p style={{ fontWeight: 600, fontSize: "0.88rem", margin: "0 0 0.35rem" }}>
                {rotuloTipo(g.tipo)}
              </p>
              {g.rota_lista && (
                <Link to={g.rota_lista} style={{ fontSize: "0.78rem" }}>
                  ver todos »
                </Link>
              )}
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem" }}>
              {g.itens.map((item) => (
                <Link
                  key={item.slug}
                  to={item.rota}
                  className="chip"
                  style={{ textDecoration: "none", maxWidth: "26rem" }}
                >
                  {item.titulo}
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
