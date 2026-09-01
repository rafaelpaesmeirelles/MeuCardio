"""Regressões direcionadas da política clínica do grafo universal."""
from __future__ import annotations

import math
from inspect import signature
from types import SimpleNamespace

import pytest
from app.models.knowledge import TIPOS_RELACAO_PERMITIDOS
from app.services import knowledge_graph as kg
from app.services.knowledge_relation_policy import (
    RELATION_TYPE_MATRIX,
    RelacaoClinicaInvalida,
    validar_relacao_clinica,
)


def _validar(
    source_type: str,
    relation_type: str,
    target_type: str,
    *,
    relevance_score: float = 0.8,
    provenance_type: str = "structured_metadata",
    confidence: str = "derived",
    review_status: str = "pendente_revisao",
    evidence_source: str | None = None,
    extra: dict | None = None,
) -> None:
    validar_relacao_clinica(
        source_type=source_type,
        relation_type=relation_type,
        target_type=target_type,
        relevance_score=relevance_score,
        provenance_type=provenance_type,
        confidence=confidence,
        review_status=review_status,
        evidence_source=evidence_source,
        extra=extra,
    )


def test_matriz_cobre_exatamente_o_catalogo_de_relacoes():
    assert set(RELATION_TYPE_MATRIX) == set(TIPOS_RELACAO_PERMITIDOS)
    assert all(RELATION_TYPE_MATRIX.values())


@pytest.mark.parametrize(
    ("source_type", "relation_type", "target_type"),
    [
        ("documento", "supported_by", "evidencia"),
        ("fluxograma", "supported_by", "evidencia"),
        ("evidencia", "supported_by", "estudo"),
        ("material_paciente", "derived_from", "documento"),
        ("checklist", "derived_from", "fluxograma"),
        ("protocolo_emergencia", "derived_from", "documento"),
        ("protocolo_emergencia", "uses_flowchart", "fluxograma"),
        ("protocolo_emergencia", "associated_with", "documento"),
        ("trilha", "contains", "calculadora"),
        ("fluxograma", "mentioned_in", "documento"),
        ("documento", "mentioned_in", "evidencia"),
        ("documento", "mentioned_in", "medicamento"),
        ("doenca", "mentioned_in", "fluxograma"),
        ("material_paciente", "patient_education_for", "doenca"),
        ("doenca", "differential_for", "triagem_sintoma"),
        ("galeria", "belongs_to_topic", "tema"),
        ("triagem_sintoma", "belongs_to_topic", "tema"),
    ],
)
def test_assinaturas_estruturadas_do_backfill_continuam_compativeis(
    source_type, relation_type, target_type,
):
    _validar(source_type, relation_type, target_type)


def test_assinatura_de_study_slug_e_direcional_e_reconciliavel():
    assert kg._ASSINATURAS_AUTOMATICAS_LEGADAS["EvidenceRecord.study_slug"] == (
        "supported_by", {"evidencia"}, {"estudo"},
    )


def test_interacao_curada_do_backfill_continua_compativel():
    _validar(
        "medicamento",
        "interacts_with",
        "medicamento",
        relevance_score=1.0,
        provenance_type="editorial",
        confidence="explicit",
        review_status="revisado",
        evidence_source="medicamentos/interacoes.json#par-curado",
    )


@pytest.mark.parametrize(
    ("source_type", "relation_type", "target_type"),
    [
        ("medicamento", "monitor_with", "exame"),
        ("doenca", "diagnosed_by", "calculadora"),
        ("doenca", "studied_in", "estudo"),
        ("calculadora", "recommended_by", "evidencia"),
        ("medicamento", "used_in_case", "caso_clinico"),
    ],
)
def test_transversais_clinicas_legitimas_nao_sao_bloqueadas(
    source_type, relation_type, target_type,
):
    _validar(source_type, relation_type, target_type)


@pytest.mark.parametrize(
    ("source_type", "relation_type", "target_type"),
    [
        ("estudo", "treats", "calculadora"),
        ("tema", "monitor_with", "medicamento"),
        ("material_paciente", "contraindicated_with", "estudo"),
        ("evidencia", "diagnosed_by", "galeria"),
        ("medicamento", "belongs_to_topic", "documento"),
    ],
)
def test_combinacoes_sem_nexo_sao_rejeitadas(
    source_type, relation_type, target_type,
):
    with pytest.raises(RelacaoClinicaInvalida, match="combinação clínica"):
        _validar(source_type, relation_type, target_type)


@pytest.mark.parametrize(
    "score",
    [-0.01, 1.01, math.nan, math.inf, -math.inf, True, "0.8"],
)
def test_score_deve_ser_numerico_finito_entre_zero_e_um(score):
    with pytest.raises(RelacaoClinicaInvalida, match="relevance_score"):
        _validar("medicamento", "interacts_with", "medicamento", relevance_score=score)


def test_fato_clinico_derivado_revisado_exige_evidencia_rastreavel():
    with pytest.raises(RelacaoClinicaInvalida, match="evidência rastreável"):
        _validar(
            "medicamento",
            "treats",
            "doenca",
            review_status="revisado",
        )

    _validar(
        "medicamento",
        "treats",
        "doenca",
        review_status="revisado",
        evidence_source="doi:10.0000/exemplo",
    )


def test_relacao_forte_pendente_pode_ser_guardada_sem_ser_promovida_a_fato():
    _validar("medicamento", "treats", "doenca", review_status="pendente_revisao")
    _validar(
        "medicamento",
        "treats",
        "doenca",
        provenance_type="ai_suggested",
        confidence="ai_suggested",
        review_status="pendente_revisao",
    )
    with pytest.raises(RelacaoClinicaInvalida, match="promovida"):
        _validar(
            "medicamento",
            "treats",
            "doenca",
            provenance_type="ai_suggested",
            confidence="ai_suggested",
            review_status="revisado",
            evidence_source="pmid:123",
        )


def test_relacao_editorial_curada_e_preservada():
    _validar(
        "doenca",
        "associated_with",
        "trilha",
        relevance_score=1.0,
        provenance_type="editorial",
        confidence="explicit",
        review_status="revisado",
        evidence_source="doencas/relacoes-explicitas.json#registro",
    )


def test_excecao_fora_da_matriz_precisa_ser_explicitamente_auditavel():
    metadados = {
        "policy_exception": {
            "reason": "Relação transversal validada pelo comitê científico",
            "reviewed_by": "comite-cientifico",
            "reviewed_at": "2026-09-01T12:00:00Z",
        }
    }
    _validar(
        "estudo",
        "treats",
        "calculadora",
        provenance_type="editorial",
        confidence="explicit",
        review_status="revisado",
        evidence_source="review:ata-42",
        extra=metadados,
    )
    with pytest.raises(RelacaoClinicaInvalida, match="policy_exception"):
        _validar(
            "estudo",
            "treats",
            "calculadora",
            provenance_type="editorial",
            confidence="explicit",
            review_status="revisado",
            extra={"policy_exception": {"reason": "sem auditor identificado"}},
        )
    with pytest.raises(RelacaoClinicaInvalida, match="policy_exception"):
        _validar(
            "estudo",
            "treats",
            "calculadora",
            provenance_type="editorial",
            confidence="explicit",
            review_status="revisado",
            evidence_source="review:ata-42",
            extra={
                "policy_exception": {
                    "reason": "data sem fuso não é auditável",
                    "reviewed_by": "comite-cientifico",
                    "reviewed_at": "2026-09-01T12:00:00",
                }
            },
        )


def test_excecao_nao_pode_burlar_catalogo_ou_allowlist_global():
    metadados = {
        "policy_exception": {
            "reason": "tentativa inválida",
            "reviewed_by": "revisor",
            "reviewed_at": "2026-09-01T12:00:00Z",
        }
    }
    for source_type, relation_type in (
        ("paciente", "treats"),
        ("doenca", "verbo_inventado"),
    ):
        with pytest.raises(RelacaoClinicaInvalida):
            _validar(
                source_type,
                relation_type,
                "doenca",
                provenance_type="editorial",
                confidence="explicit",
                review_status="revisado",
                evidence_source="review:ata-43",
                extra=metadados,
            )


def test_relacionados_de_desativa_expansao_tematica_por_padrao():
    parametro = signature(kg.relacionados_de).parameters["incluir_contexto_tematico"]
    assert parametro.default is False


def test_reconciliacao_quarentena_automatica_invalida_sem_apagar_historico():
    relacao = SimpleNamespace(
        relation_type="treats",
        relevance_score=0.7,
        provenance_type="structured_metadata",
        confidence="derived",
        evidence_source=None,
        review_status="pendente_revisao",
        extra={"_producer": kg._PRODUTOR_BACKFILL},
        source_entity=SimpleNamespace(entity_type="estudo"),
        target_entity=SimpleNamespace(entity_type="calculadora"),
    )
    lote = kg._LoteRelacoes(existentes={(1, 2, "treats"): relacao}, desejadas=set())

    assert kg._rejeitar_relacoes_automaticas_invalidas(lote) == 1
    assert relacao.review_status == "rejeitado"
    assert relacao.extra["_inactive_reason"] == "policy_rejected"
    assert "estudo -[treats]-> calculadora" in relacao.extra["_policy_error"]


def test_reconciliacao_nao_rebaixa_curadoria_editorial_fora_da_matriz():
    relacao = SimpleNamespace(
        relation_type="treats",
        relevance_score=1.0,
        provenance_type="editorial",
        confidence="explicit",
        evidence_source="review:legado",
        review_status="revisado",
        extra={"curadoria": "legado preservado"},
        source_entity=SimpleNamespace(entity_type="estudo"),
        target_entity=SimpleNamespace(entity_type="calculadora"),
    )
    lote = kg._LoteRelacoes(existentes={(1, 2, "treats"): relacao}, desejadas=set())

    assert kg._rejeitar_relacoes_automaticas_invalidas(lote) == 0
    assert relacao.review_status == "revisado"
    assert relacao.extra == {"curadoria": "legado preservado"}


class _ResultadoFake:
    def __init__(self, *, escalar=None, linhas=None):
        self._escalar = escalar
        self._linhas = linhas or []

    def scalar_one_or_none(self):
        return self._escalar

    def all(self):
        return self._linhas


class _DbFake:
    def __init__(self, *resultados):
        self._resultados = iter(resultados)

    def execute(self, _query):
        return next(self._resultados)


def _relacao_fake(**campos):
    padrao = {
        "relation_type": "belongs_to_topic",
        "relevance_score": 0.35,
        "provenance_type": "structured_metadata",
        "confidence": "derived",
        "evidence_source": None,
        "review_status": "pendente_revisao",
        "extra": {"tema": "Cardiologia"},
    }
    return SimpleNamespace(**{**padrao, **campos})


def test_relacionados_de_oculta_aresta_persistida_que_viola_politica():
    origem = SimpleNamespace(
        id=1, entity_type="estudo", slug="ensaio", title="Ensaio",
    )
    alvo = SimpleNamespace(
        id=2, entity_type="calculadora", slug="escore", title="Escore",
    )
    absurda = _relacao_fake(relation_type="treats", relevance_score=0.9)
    db = _DbFake(
        _ResultadoFake(escalar=origem),
        _ResultadoFake(linhas=[(absurda, alvo)]),
        _ResultadoFake(linhas=[]),
    )

    resultado = kg.relacionados_de(db, entity_type="estudo", slug="ensaio")

    assert resultado["grupos"] == []
    assert resultado["total"] == 0


def test_contexto_tematico_opt_in_nao_recebe_score_clinico():
    origem = SimpleNamespace(
        id=1, entity_type="documento", slug="origem", title="Origem",
    )
    tema = SimpleNamespace(
        id=2, entity_type="tema", slug="cardiologia", title="Cardiologia",
    )
    vizinho = SimpleNamespace(
        id=3, entity_type="evidencia", slug="vizinho", title="Vizinho",
    )
    relacao_origem = _relacao_fake()
    relacao_vizinho = _relacao_fake()
    db = _DbFake(
        _ResultadoFake(escalar=origem),
        _ResultadoFake(linhas=[(relacao_origem, tema)]),
        _ResultadoFake(linhas=[]),
        _ResultadoFake(linhas=[(relacao_vizinho, vizinho)]),
    )

    resultado = kg.relacionados_de(
        db,
        entity_type="documento",
        slug="origem",
        incluir_contexto_tematico=True,
    )

    item = resultado["grupos"][0]["itens"][0]
    assert item["relation_type"] == "belongs_to_topic"
    assert item["relevance_score"] is None
    assert item["context_only"] is True


def test_registrar_relacao_aplica_politica_antes_de_consultar_banco():
    class _BancoNaoDeveSerConsultado:
        def execute(self, _query):
            raise AssertionError("a aresta inválida chegou ao banco")

    source = SimpleNamespace(id=1, entity_type="estudo")
    target = SimpleNamespace(id=2, entity_type="calculadora")

    with pytest.raises(RelacaoClinicaInvalida, match="combinação clínica"):
        kg.registrar_relacao(
            _BancoNaoDeveSerConsultado(),
            source=source,
            target=target,
            relation_type="treats",
            provenance_type="structured_metadata",
            confidence="derived",
        )


def test_curadoria_fora_da_matriz_so_reaparece_com_excecao_auditavel():
    origem = SimpleNamespace(
        id=1, entity_type="estudo", slug="ensaio", title="Ensaio",
    )
    alvo = SimpleNamespace(
        id=2, entity_type="calculadora", slug="escore", title="Escore",
    )
    curada = _relacao_fake(
        relation_type="treats",
        relevance_score=1.0,
        provenance_type="editorial",
        confidence="explicit",
        review_status="revisado",
        evidence_source="review:ata-42",
        extra={
            "policy_exception": {
                "reason": "validação transversal excepcional",
                "reviewed_by": "comite-cientifico",
                "reviewed_at": "2026-09-01T12:00:00Z",
            }
        },
    )
    db = _DbFake(
        _ResultadoFake(escalar=origem),
        _ResultadoFake(linhas=[(curada, alvo)]),
        _ResultadoFake(linhas=[]),
    )

    resultado = kg.relacionados_de(db, entity_type="estudo", slug="ensaio")

    assert resultado["total"] == 1
    assert resultado["grupos"][0]["itens"][0]["slug"] == "escore"
