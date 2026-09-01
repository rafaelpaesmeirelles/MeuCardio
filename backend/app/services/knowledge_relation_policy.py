"""Política clínica de admissão de arestas no Grafo de Conhecimento.

O catálogo de verbos, sozinho, não é suficiente: ``treats`` é um verbo
válido, mas ``estudo -[treats]-> calculadora`` não é uma afirmação coerente.
Este módulo mantém a matriz fechada ``origem x verbo x destino`` e valida os
metadados que determinam se uma aresta é curada, derivada ou apenas sugerida.

A política decide se a aresta pode ser *persistida*. Publicação continua
separada: sugestões/derivações clínicas pendentes podem ser guardadas para
revisão, mas ``knowledge_graph.relacionados_de`` não as promove a fato.
"""
from __future__ import annotations

import math
from collections.abc import Mapping
from datetime import datetime
from numbers import Real


class RelacaoClinicaInvalida(ValueError):
    """A aresta viola a matriz clínica ou o contrato de proveniência."""


_CONTEUDO = frozenset({
    "documento",
    "fluxograma",
    "evidencia",
    "estudo",
    "medicamento",
    "exame",
    "caso_clinico",
    "trilha",
    "galeria",
    "checklist",
    "material_paciente",
    "protocolo_emergencia",
    "calculadora",
    "doenca",
    "triagem_sintoma",
})
_ENTIDADES = _CONTEUDO | {"tema"}
_REFERENCIAS = frozenset({"documento", "fluxograma", "evidencia", "estudo"})
_CONDICOES = frozenset({"doenca", "documento", "caso_clinico", "triagem_sintoma"})


def _pares(origens: frozenset[str], destinos: frozenset[str]) -> frozenset[tuple[str, str]]:
    return frozenset((origem, destino) for origem in origens for destino in destinos)


def _mesmo_tipo(tipos: frozenset[str]) -> frozenset[tuple[str, str]]:
    return frozenset((tipo, tipo) for tipo in tipos)


# Matriz fechada. Relações estruturais mantêm as assinaturas do backfill
# atual; relações clínicas permitem travessias justificáveis, sem tornar um
# verbo forte universal entre quaisquer duas categorias.
RELATION_TYPE_MATRIX: dict[str, frozenset[tuple[str, str]]] = {
    "treats": _pares(
        frozenset({"medicamento", "protocolo_emergencia"}),
        _CONDICOES,
    ),
    "indicated_for": _pares(
        frozenset({"medicamento", "exame", "calculadora", "protocolo_emergencia"}),
        _CONDICOES,
    ),
    "contraindicated_in": _pares(
        frozenset({"medicamento", "exame", "calculadora", "protocolo_emergencia"}),
        frozenset({"doenca", "documento", "caso_clinico"}),
    ),
    "contraindicated_with": frozenset({("medicamento", "medicamento")}),
    "interacts_with": frozenset({("medicamento", "medicamento")}),
    "monitor_with": _pares(
        frozenset({"medicamento", "doenca", "protocolo_emergencia"}),
        frozenset({"exame", "calculadora"}),
    ),
    "diagnosed_by": _pares(
        frozenset({"doenca", "triagem_sintoma"}),
        frozenset({"exame", "calculadora", "fluxograma"}),
    ),
    "supported_by": _pares(_CONTEUDO, _REFERENCIAS),
    "studied_in": _pares(
        frozenset({
            "doenca", "medicamento", "exame", "calculadora",
            "protocolo_emergencia", "caso_clinico",
        }),
        frozenset({"estudo", "evidencia"}),
    ),
    "recommended_by": _pares(
        frozenset({
            "medicamento", "exame", "calculadora", "protocolo_emergencia",
            "checklist", "fluxograma", "documento", "caso_clinico",
        }),
        _REFERENCIAS,
    ),
    # Uma associação genérica só é publicável mediante curadoria explícita
    # (validada abaixo). Isso preserva transversais reais sem transformar
    # similaridade genérica em afirmação clínica.
    "associated_with": _pares(_CONTEUDO, _CONTEUDO),
    "causes": _pares(
        frozenset({"doenca", "medicamento"}),
        frozenset({"doenca", "triagem_sintoma", "caso_clinico"}),
    ),
    "may_cause": _pares(
        frozenset({"doenca", "medicamento"}),
        frozenset({"doenca", "triagem_sintoma", "caso_clinico"}),
    ),
    "alternative_to": _mesmo_tipo(frozenset({
        "medicamento", "exame", "calculadora", "protocolo_emergencia",
        "fluxograma", "checklist", "documento",
    })),
    "belongs_to_class": _mesmo_tipo(frozenset({
        "medicamento", "exame", "doenca", "estudo", "documento",
    })),
    "used_in_case": _pares(_CONTEUDO - {"caso_clinico"}, frozenset({"caso_clinico"})),
    "mentioned_in": _pares(
        _CONTEUDO,
        frozenset({
            "documento", "fluxograma", "evidencia", "estudo", "medicamento",
            "caso_clinico", "material_paciente",
        }),
    ),
    "patient_education_for": frozenset({("material_paciente", "doenca")}),
    "differential_for": frozenset({("doenca", "triagem_sintoma")}),
    "same_theme": _pares(_CONTEUDO, _CONTEUDO),
    "belongs_to_topic": _pares(_CONTEUDO, frozenset({"tema"})),
    "derived_from": _pares(
        frozenset({
            "documento", "fluxograma", "evidencia", "estudo", "caso_clinico",
            "trilha", "galeria", "checklist", "material_paciente",
            "protocolo_emergencia",
        }),
        _REFERENCIAS,
    ),
    "uses_flowchart": _pares(
        frozenset({
            "protocolo_emergencia", "checklist", "doenca", "triagem_sintoma",
            "caso_clinico", "documento",
        }),
        # Instalações legadas classificaram alguns fluxos como documento.
        frozenset({"fluxograma", "documento"}),
    ),
    "contains": _pares(
        frozenset({"trilha"}),
        frozenset({
            "documento", "fluxograma", "estudo", "medicamento", "checklist",
            "caso_clinico", "evidencia", "calculadora",
        }),
    ),
}


RELACOES_CLINICAS_FORTES = frozenset({
    "treats",
    "indicated_for",
    "contraindicated_in",
    "contraindicated_with",
    "interacts_with",
    "monitor_with",
    "diagnosed_by",
    "supported_by",
    "studied_in",
    "recommended_by",
    "causes",
    "may_cause",
    "alternative_to",
})

_PROVENIENCIAS_EXPLICITAS = frozenset({"editorial", "imported"})
_PROVENIENCIAS_DERIVADAS = frozenset({
    "structured_metadata", "imported", "derived", "clinical_context",
})
_PROVENIENCIAS = _PROVENIENCIAS_EXPLICITAS | _PROVENIENCIAS_DERIVADAS | {
    "ai_suggested",
}
_CONFIANCAS = frozenset({"explicit", "derived", "ai_suggested"})
_STATUS_REVISAO = frozenset({"revisado", "pendente_revisao", "rejeitado"})
_RELACOES_COM_REFERENCIA_NO_DESTINO = frozenset({
    "supported_by", "studied_in", "recommended_by",
})


def _tem_excecao_auditavel(extra: Mapping[str, object] | None) -> bool:
    """Exige decisão humana identificável para fugir da matriz fechada."""
    if not isinstance(extra, Mapping):
        return False
    excecao = extra.get("policy_exception")
    if not isinstance(excecao, Mapping):
        return False
    campos_presentes = all(
        isinstance(excecao.get(campo), str) and bool(str(excecao[campo]).strip())
        for campo in ("reason", "reviewed_by", "reviewed_at")
    )
    if not campos_presentes:
        return False
    try:
        instante = datetime.fromisoformat(
            str(excecao["reviewed_at"]).replace("Z", "+00:00")
        )
    except ValueError:
        return False
    return instante.tzinfo is not None


def validar_relacao_clinica(
    *,
    source_type: str,
    relation_type: str,
    target_type: str,
    relevance_score: float,
    provenance_type: str,
    confidence: str,
    review_status: str,
    evidence_source: str | None,
    extra: Mapping[str, object] | None = None,
) -> None:
    """Valida uma aresta antes de qualquer INSERT/UPDATE.

    Arestas clínicas derivadas ou sugeridas podem permanecer pendentes para
    revisão. Para uma afirmação forte já revisada, exige-se curadoria
    explícita ou evidência rastreável (inclusive quando o próprio destino é a
    evidência/estudo/diretriz). Sugestão de IA nunca vira fato apenas pela
    troca de ``review_status``.
    """
    if isinstance(relevance_score, bool) or not isinstance(relevance_score, Real):
        raise RelacaoClinicaInvalida("relevance_score deve ser número real entre 0 e 1.")
    score = float(relevance_score)
    if not math.isfinite(score) or not 0.0 <= score <= 1.0:
        raise RelacaoClinicaInvalida("relevance_score deve ser finito e estar entre 0 e 1.")

    if provenance_type not in _PROVENIENCIAS:
        raise RelacaoClinicaInvalida("proveniência fora do catálogo da política clínica.")
    if confidence not in _CONFIANCAS:
        raise RelacaoClinicaInvalida("confiança fora do catálogo da política clínica.")
    if review_status not in _STATUS_REVISAO:
        raise RelacaoClinicaInvalida("status de revisão fora do catálogo da política clínica.")

    if source_type not in _ENTIDADES or target_type not in _ENTIDADES:
        raise RelacaoClinicaInvalida("tipo de entidade fora do allowlist global do grafo.")
    permitidos = RELATION_TYPE_MATRIX.get(relation_type)
    if permitidos is None:
        raise RelacaoClinicaInvalida("tipo de relação fora do catálogo da política clínica.")
    combinacao_permitida = (source_type, target_type) in permitidos
    fonte_rastreavel = isinstance(evidence_source, str) and bool(evidence_source.strip())
    excecao_curada = (
        confidence == "explicit"
        and provenance_type in _PROVENIENCIAS_EXPLICITAS
        and review_status == "revisado"
        and fonte_rastreavel
        and _tem_excecao_auditavel(extra)
    )
    if not combinacao_permitida and not excecao_curada:
        raise RelacaoClinicaInvalida(
            "combinação clínica não permitida: "
            f"{source_type} -[{relation_type}]-> {target_type}; "
            "exceção exige curadoria explícita e policy_exception auditável."
        )

    if confidence == "explicit" and provenance_type not in _PROVENIENCIAS_EXPLICITAS:
        raise RelacaoClinicaInvalida(
            "confidence='explicit' exige proveniência editorial ou importada."
        )
    if confidence == "derived" and provenance_type not in _PROVENIENCIAS_DERIVADAS:
        raise RelacaoClinicaInvalida(
            "confidence='derived' não é coerente com a proveniência informada."
        )
    if confidence == "ai_suggested" and provenance_type != "ai_suggested":
        raise RelacaoClinicaInvalida(
            "confidence='ai_suggested' exige provenance_type='ai_suggested'."
        )
    if provenance_type == "editorial" and confidence != "explicit":
        raise RelacaoClinicaInvalida(
            "proveniência editorial deve permanecer identificada como explícita."
        )
    if provenance_type == "ai_suggested" and confidence != "ai_suggested":
        raise RelacaoClinicaInvalida(
            "proveniência de IA deve permanecer identificada como sugestão de IA."
        )
    if review_status == "revisado" and confidence == "ai_suggested":
        raise RelacaoClinicaInvalida(
            "sugestão de IA revisada deve ser promovida com proveniência humana/rastreável."
        )

    destino_e_referencia = (
        relation_type in _RELACOES_COM_REFERENCIA_NO_DESTINO
        and target_type in _REFERENCIAS
    )
    if (
        relation_type in RELACOES_CLINICAS_FORTES
        and review_status == "revisado"
        and confidence != "explicit"
        and not fonte_rastreavel
        and not destino_e_referencia
    ):
        raise RelacaoClinicaInvalida(
            "relação clínica forte revisada exige curadoria explícita ou evidência rastreável."
        )

    if (
        relation_type == "associated_with"
        and review_status == "revisado"
        and not (
            confidence == "explicit"
            and provenance_type in _PROVENIENCIAS_EXPLICITAS
        )
    ):
        raise RelacaoClinicaInvalida(
            "associated_with revisado exige associação explícita e curada."
        )
