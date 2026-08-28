from pathlib import Path
import json

import frontmatter

from app.services.disease_manifest import load_disease_records


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "doencas/metadados.json"


def _document_slugs() -> set[str]:
    slugs: set[str] = set()
    for path in (ROOT / "content").rglob("*.md"):
        post = frontmatter.load(path)
        slugs.add(str(post.metadata.get("slug") or path.stem))
    return slugs


def _patient_material_slugs() -> set[str]:
    payload = json.loads((ROOT / "material-paciente/metadados.json").read_text(encoding="utf-8"))
    return {str(item["slug"]) for item in payload}


def test_catalogo_combinado_tem_slugs_unicos_e_status_editorial_explicito():
    records = load_disease_records(BASE)
    slugs = [str(item["slug"]) for item in records]
    assert len(slugs) == len(set(slugs))
    assert all(item.get("review_status") == "revisado" for item in records)


def test_todos_os_vinculos_das_doencas_combinadas_resolvem():
    documents = _document_slugs()
    materials = _patient_material_slugs()
    broken: list[str] = []
    for disease in load_disease_records(BASE):
        slug = str(disease["slug"])
        for target in disease.get("related_document_slugs") or []:
            if target not in documents:
                broken.append(f"{slug}:documento:{target}")
        material = disease.get("patient_material_slug")
        if material and material not in materials:
            broken.append(f"{slug}:material_paciente:{material}")
    assert broken == []


def test_fragmentos_nao_podem_marcar_registro_nao_revisado_como_publicado():
    conflitos = [
        str(item["slug"])
        for item in load_disease_records(BASE)
        if item.get("review_status") != "revisado" and item.get("published") is True
    ]
    assert conflitos == []
