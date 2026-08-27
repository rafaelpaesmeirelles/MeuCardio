"""Gates do primeiro lote profundo de condições cardiovasculares do adulto."""

from __future__ import annotations

import json
from pathlib import Path
import re
import unicodedata

from app.services.clinical_rule_engine import (
    validate_question_definitions,
    validate_rule_definitions,
)


ROOT = Path(__file__).resolve().parents[2]
DISEASES = ROOT / "doencas/metadados.json"
TRIAGE = ROOT / "triagem-sintomas/metadados.json"
PATIENT_MATERIALS = ROOT / "material-paciente/metadados.json"
DETAIL_PAGE = ROOT / "frontend/src/pages/GuiaDoenca.tsx"
CATALOG_PAGE = ROOT / "frontend/src/pages/GuiaDoencas.tsx"

LOT_SLUGS = {
    "hipertensao-arterial-sistemica",
    "fibrilacao-atrial",
    "insuficiencia-cardiaca",
    "sindrome-coronariana-cronica",
}
REQUIRED_LISTS = {
    "presentation": 4,
    "differentials": 5,
    "tests": 5,
    "red_flags": 4,
    "ambulatory_flow": 4,
    "emergency_flow": 4,
    "monitoring": 4,
    "special_populations": 4,
    "assistant_questions": 4,
    "assistant_rules": 4,
    "source_refs": 1,
    "source_urls": 1,
    "related_document_slugs": 2,
}


def _records(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    return data


def _normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", value.casefold()).strip()


def _document_slugs() -> set[str]:
    slugs: set[str] = set()
    for path in (ROOT / "content").rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^slug:\s*['\"]?([^'\"\n]+)", text, re.MULTILINE)
        if match:
            slugs.add(match.group(1).strip())
    return slugs


def test_lote_adulto_tem_profundidade_clinica_e_decisao_humana_preservada():
    diseases = {item["slug"]: item for item in _records(DISEASES)}
    assert LOT_SLUGS <= set(diseases)

    for slug in LOT_SLUGS:
        disease = diseases[slug]
        assert disease["area"] == "geral"
        assert disease["completeness"] == "completo"
        assert disease["review_status"] == "revisado"
        assert disease["fonte_producao"] == "chatgpt"
        assert disease["review_note"]
        assert len(disease["summary"]) >= 180
        assert len(disease["epidemiology"]) >= 120
        assert len(disease["treatment_summary"]) >= 300
        assert isinstance(disease["diagnostic_approach"], dict)
        assert len(disease["diagnostic_approach"]) >= 3
        for field, minimum in REQUIRED_LISTS.items():
            assert len(disease[field]) >= minimum, f"{slug}:{field}"

        question_errors, question_ids = validate_question_definitions(
            slug, disease["assistant_questions"]
        )
        rule_errors = validate_rule_definitions(
            slug, disease["assistant_rules"], question_ids
        )
        assert question_errors == []
        assert rule_errors == []


def test_relacoes_explicitas_resolvem_sem_fabricar_malha_de_triagem():
    diseases = {
        item["slug"]: item
        for item in _records(DISEASES)
        if item["slug"] in LOT_SLUGS
    }
    document_slugs = _document_slugs()
    material_slugs = {item["slug"] for item in _records(PATIENT_MATERIALS)}

    for disease in diseases.values():
        assert set(disease["related_document_slugs"]) <= document_slugs
        assert disease["patient_material_slug"] in material_slugs

    # O grafo só liga triagem↔doença por casamento exato de nome/alias.
    # No lote, apenas IC já possui vínculos diretos no corpus; não criamos
    # aliases artificiais para aproximar HAS, FA ou SCC de diferenciais amplos.
    names: dict[str, str] = {}
    for disease in diseases.values():
        for name in [disease["name"], *disease["aliases"]]:
            names[_normalize(name)] = disease["slug"]
    direct_matches = {
        (names[key], triage["slug"])
        for triage in _records(TRIAGE)
        for differential in triage.get("differentials", [])
        if (key := _normalize(str(differential))) in names
    }
    assert direct_matches == {
        ("insuficiencia-cardiaca", "dispneia"),
        ("insuficiencia-cardiaca", "edema"),
        ("insuficiencia-cardiaca", "fadiga-e-intolerancia-ao-esforco"),
        ("insuficiencia-cardiaca", "queda-ou-delirium-no-idoso-cardiopata"),
        ("insuficiencia-cardiaca", "sintomas-cardiovasculares-no-paciente-oncologico"),
    }


def test_tela_exibe_diagnostico_conexoes_e_filtro_adulto():
    detail = DETAIL_PAGE.read_text(encoding="utf-8")
    catalog = CATALOG_PAGE.read_text(encoding="utf-8")

    assert 'title="Abordagem diagnóstica"' in detail
    assert "Conteúdo diretamente relacionado" in detail
    assert "related_document_slugs.map" in detail
    assert "patient_material_slug" in detail
    assert '["geral", "Cardiologia do adulto"]' in catalog
