"""Gates de segurança do assessment do Guia de Doenças."""

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.specialty_guides import AssessmentPayload, assess_disease


class _Query:
    def __init__(self, item):
        self.item = item

    def filter(self, *_):
        return self

    def first(self):
        return self.item


class _Session:
    def __init__(self, item):
        self.item = item

    def query(self, *_):
        return _Query(self.item)


def _item():
    return SimpleNamespace(
        slug="guia-seguro",
        name="Guia seguro",
        version=1,
        assistant_questions=[{
            "id": "status",
            "label": "Estado",
            "type": "select",
            "required": True,
            "options": [
                {"value": "suspeita", "label": "Suspeita"},
                {"value": "ausente", "label": "Ausente"},
            ],
        }],
        assistant_rules=[{
            "id": "suspeita",
            "priority": 10,
            "when": {"all": [{"field": "status", "op": "eq", "value": "suspeita"}]},
            "add": {"risk": "urgente", "suggested_tests": ["Teste condicional"]},
        }],
        tests=["Teste educacional do verbete"],
        differentials=["Diagnóstico diferencial"],
        ambulatory_flow=["Fluxo educacional ambulatorial"],
        emergency_flow=["Fluxo educacional de emergência"],
        source_refs=[],
        source_urls=[],
    )


def test_assessment_rejeita_resposta_obrigatoria_ausente_antes_do_engine():
    with pytest.raises(HTTPException) as error:
        assess_disease(
            "guia-seguro",
            AssessmentPayload(context="ambulatorio", answers={}),
            db=_Session(_item()),
        )

    assert error.value.status_code == 422
    assert error.value.detail == {
        "erro": "Respostas obrigatórias ausentes.",
        "campos": ["status"],
    }


def test_assessment_nao_rotula_exames_e_fluxos_educacionais_como_sugestao():
    result = assess_disease(
        "guia-seguro",
        AssessmentPayload(context="ambulatorio", answers={"status": "ausente"}),
        db=_Session(_item()),
    )

    assert result["risk"] == "informativo"
    assert result["suggested_tests"] == []
    assert result["ambulatory_flow"] == []
    assert result["emergency_flow"] == []
    assert result["recommended_flow"] == []
    assert result["differentials"] == ["Diagnóstico diferencial"]


def test_assessment_mantem_sugestao_exclusivamente_condicional():
    result = assess_disease(
        "guia-seguro",
        AssessmentPayload(context="ambulatorio", answers={"status": "suspeita"}),
        db=_Session(_item()),
    )

    assert result["risk"] == "urgente"
    assert result["suggested_tests"] == ["Teste condicional"]
    assert result["matched_rules"] == ["suspeita"]
