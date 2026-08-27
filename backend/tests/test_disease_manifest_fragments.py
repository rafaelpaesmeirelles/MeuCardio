import json
from pathlib import Path

import pytest

from app.services.disease_manifest import load_disease_records


def _write(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_combina_manifesto_base_e_fragmentos_em_ordem_deterministica(tmp_path):
    base = tmp_path / "doencas" / "metadados.json"
    _write(base, [{"slug": "base", "name": "Base", "summary": "Base"}])
    _write(base.parent / "fragmentos" / "b.json", [{"slug": "b", "name": "B", "summary": "B"}])
    _write(base.parent / "fragmentos" / "a.json", [{"slug": "a", "name": "A", "summary": "A"}])

    records = load_disease_records(base)

    assert [item["slug"] for item in records] == ["base", "a", "b"]


def test_snapshot_pode_repetir_registro_base_se_for_identico(tmp_path):
    base = tmp_path / "doencas" / "metadados.json"
    record = {"slug": "base", "name": "Base", "summary": "Base"}
    _write(base, [record])
    _write(base.parent / "fragmentos" / "snapshot.json", [record, {"slug": "novo", "name": "Novo", "summary": "Novo"}])

    records = load_disease_records(base)

    assert [item["slug"] for item in records] == ["base", "novo"]


def test_rejeita_snapshot_que_diverge_do_registro_base(tmp_path):
    base = tmp_path / "doencas" / "metadados.json"
    _write(base, [{"slug": "duplicado", "name": "Base", "summary": "Base"}])
    _write(
        base.parent / "fragmentos" / "novo.json",
        [{"slug": "duplicado", "name": "Novo", "summary": "Novo"}],
    )

    with pytest.raises(ValueError, match="diverge de registro já composto"):
        load_disease_records(base)


def test_rejeita_fragmento_que_nao_seja_lista_json(tmp_path):
    base = tmp_path / "doencas" / "metadados.json"
    _write(base, [{"slug": "base", "name": "Base", "summary": "Base"}])
    _write(base.parent / "fragmentos" / "invalido.json", {"slug": "x"})

    with pytest.raises(ValueError, match="lista JSON"):
        load_disease_records(base)


def test_overlay_corrige_campos_texto_e_regra_por_id(tmp_path):
    base = tmp_path / "doencas" / "metadados.json"
    _write(base, [{
        "slug": "x",
        "name": "X",
        "summary": "texto antigo",
        "review_status": "pendente_revisao",
        "assistant_questions": [{"id": "q1", "label": "Q", "type": "boolean"}],
        "assistant_rules": [{"id": "r1", "priority": 1, "when": {"all": []}, "add": {"messages": ["antigo"]}}],
    }])
    _write(base.parent / "correcoes" / "x.json", [{
        "slug": "x",
        "set": {"review_status": "revisado"},
        "replace": [{"old": "texto antigo", "new": "texto corrigido"}],
        "assistant_rules": {"r1": {"priority": 90}},
        "assistant_questions": {"q1": {"required": True}},
    }])

    record = load_disease_records(base)[0]

    assert record["summary"] == "texto corrigido"
    assert record["review_status"] == "revisado"
    assert record["assistant_rules"][0]["priority"] == 90
    assert record["assistant_questions"][0]["required"] is True


def test_overlay_adiciona_perguntas_e_regras_sem_id_duplicado(tmp_path):
    base = tmp_path / "doencas" / "metadados.json"
    _write(base, [{
        "slug": "x",
        "name": "X",
        "summary": "X",
        "assistant_questions": [{"id": "q1", "label": "Q1", "type": "boolean"}],
        "assistant_rules": [{"id": "r1", "priority": 1, "when": {"all": []}, "add": {}}],
    }])
    _write(base.parent / "correcoes" / "x.json", [{
        "slug": "x",
        "assistant_questions_add": [{"id": "q2", "label": "Q2", "type": "boolean"}],
        "assistant_rules_add": [{"id": "r2", "priority": 2, "when": {"all": []}, "add": {}}],
    }])

    record = load_disease_records(base)[0]
    assert [item["id"] for item in record["assistant_questions"]] == ["q1", "q2"]
    assert [item["id"] for item in record["assistant_rules"]] == ["r1", "r2"]

    _write(base.parent / "correcoes" / "x.json", [{
        "slug": "x",
        "assistant_questions_add": [{"id": "q1", "label": "duplicada", "type": "boolean"}],
    }])
    with pytest.raises(ValueError, match="id duplicado"):
        load_disease_records(base)
