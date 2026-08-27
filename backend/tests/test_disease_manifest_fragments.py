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


def test_rejeita_slug_duplicado_entre_base_e_fragmento(tmp_path):
    base = tmp_path / "doencas" / "metadados.json"
    _write(base, [{"slug": "duplicado", "name": "Base", "summary": "Base"}])
    _write(
        base.parent / "fragmentos" / "novo.json",
        [{"slug": "duplicado", "name": "Novo", "summary": "Novo"}],
    )

    with pytest.raises(ValueError, match="slugs duplicados"):
        load_disease_records(base)


def test_rejeita_fragmento_que_nao_seja_lista_json(tmp_path):
    base = tmp_path / "doencas" / "metadados.json"
    _write(base, [{"slug": "base", "name": "Base", "summary": "Base"}])
    _write(base.parent / "fragmentos" / "invalido.json", {"slug": "x"})

    with pytest.raises(ValueError, match="lista JSON"):
        load_disease_records(base)
