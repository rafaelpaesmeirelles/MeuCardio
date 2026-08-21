import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MARKER = "VERIFICAÇÃO HUMANA NECESSÁRIA"


def _load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_canonical_medications_have_required_identity_fields():
    drugs = _load("medicamentos/metadados.json")
    slugs = []
    for drug in drugs:
        slug = drug.get("slug")
        slugs.append(slug)
        assert isinstance(slug, str) and slug.strip()
        assert isinstance(drug.get("generic_name"), str) and drug["generic_name"].strip(), slug
        assert isinstance(drug.get("drug_class"), str) and drug["drug_class"].strip(), slug
    assert len(slugs) == len(set(slugs))


def test_canonical_publishable_manifests_have_no_human_verification_marker():
    for path in (
        "medicamentos/metadados.json",
        "checklists/metadados.json",
        "material-paciente/metadados.json",
    ):
        assert MARKER not in (ROOT / path).read_text(encoding="utf-8"), path
