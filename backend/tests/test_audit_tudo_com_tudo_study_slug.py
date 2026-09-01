"""Contrato puro do auditor para o vínculo evidência -> estudo."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]


def _carregar_auditor():
    spec = importlib.util.spec_from_file_location(
        "audit_tudo_com_tudo_study_slug",
        ROOT / "scripts" / "audit_tudo_com_tudo.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _preparar_auditoria(tmp_path, monkeypatch, *, evidencias, estudos):
    auditor = _carregar_auditor()
    (tmp_path / "content").mkdir()
    (tmp_path / "doencas").mkdir()
    (tmp_path / "medicamentos").mkdir()
    (tmp_path / "backend" / "app" / "services").mkdir(parents=True)
    (tmp_path / "doencas" / "relacoes-explicitas.json").write_text(
        "[]", encoding="utf-8",
    )
    (tmp_path / "medicamentos" / "interacoes.json").write_text(
        "[]", encoding="utf-8",
    )
    manifestos = {
        "evidencias": evidencias,
        "estudos": estudos,
    }
    monkeypatch.setattr(auditor, "ROOT", tmp_path)
    monkeypatch.setattr(
        auditor,
        "_load",
        lambda name: manifestos.get(name, []),
    )
    return auditor, manifestos


def test_auditor_valida_study_slug_exatamente_como_estudo(tmp_path, monkeypatch):
    auditor, manifestos = _preparar_auditoria(
        tmp_path,
        monkeypatch,
        evidencias=[{
            "slug": "evidencia-a",
            "study_slug": "estudo-a",
            "pmid": "12345678",
            "review_status": "revisado",
            "published": True,
        }],
        estudos=[{
            "slug": "estudo-a",
            "pmid": "12345678",
            "review_status": "revisado",
            "published": True,
        }],
    )

    resultado = auditor.audit()

    assert resultado["references"]["EvidenceRecord.study_slug"] == {
        "total": 1,
        "resolved": 1,
    }
    assert resultado["broken_references"] == []

    manifestos["estudos"] = []
    resultado_quebrado = auditor.audit()

    assert resultado_quebrado["references"]["EvidenceRecord.study_slug"] == {
        "total": 1,
        "broken": 1,
    }
    assert resultado_quebrado["broken_references"] == [{
        "field": "EvidenceRecord.study_slug",
        "source": "evidencia-a",
        "target": "estudo-a",
        "reason": "missing_target",
        "allowed_types": ["estudo"],
        "actual_types": [],
    }]


@pytest.mark.parametrize(
    ("study_patch", "reason"),
    [
        ({"pmid": "87654321"}, "pmid_mismatch"),
        ({"pmid": None}, "target_pmid_missing"),
        ({"published": False}, "target_not_published"),
        ({"review_status": "pendente_revisao"}, "target_not_reviewed"),
    ],
)
def test_auditor_bloqueia_estudo_incompativel(
    tmp_path, monkeypatch, study_patch, reason,
):
    study = {
        "slug": "estudo-a",
        "pmid": "12345678",
        "review_status": "revisado",
        "published": True,
        **study_patch,
    }
    auditor, _manifestos = _preparar_auditoria(
        tmp_path,
        monkeypatch,
        evidencias=[{
            "slug": "evidencia-a",
            "study_slug": "estudo-a",
            "pmid": "12345678",
            "review_status": "revisado",
            "published": True,
        }],
        estudos=[study],
    )

    resultado = auditor.audit()

    assert resultado["references"]["EvidenceRecord.study_slug"] == {
        "total": 1,
        "broken": 1,
    }
    expected = {
        "field": "EvidenceRecord.study_slug",
        "source": "evidencia-a",
        "target": "estudo-a",
        "reason": reason,
        "allowed_types": ["estudo"],
        "actual_types": ["estudo"],
    }
    if reason in {"pmid_mismatch", "target_pmid_missing"}:
        expected.update({
            "source_pmid": "12345678",
            "target_pmid": study.get("pmid"),
        })
    assert resultado["broken_references"] == [expected]


def test_auditor_permite_vinculo_sem_pmid_quando_evidencia_nao_o_declara(
    tmp_path, monkeypatch,
):
    auditor, _manifestos = _preparar_auditoria(
        tmp_path,
        monkeypatch,
        evidencias=[{
            "slug": "evidencia-sem-pmid",
            "study_slug": "estudo-sem-pmid",
            "review_status": "revisado",
            "published": True,
        }],
        estudos=[{
            "slug": "estudo-sem-pmid",
            "review_status": "revisado",
            "published": True,
        }],
    )

    resultado = auditor.audit()

    assert resultado["references"]["EvidenceRecord.study_slug"] == {
        "total": 1,
        "resolved": 1,
    }
    assert resultado["broken_references"] == []
