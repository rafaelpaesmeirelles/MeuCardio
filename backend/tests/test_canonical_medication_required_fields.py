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


def test_ressalvas_comerciais_legadas_permanecem_explicitas_no_baseline_autorizado():
    from hashlib import sha256
    release = _load("editorial-approvals/scoped-corpus-release-20260910.json")
    expected = {"captopril", "clortalidona", "diltiazem-cloridrato", "enalapril-maleato",
                "heparina-nao-fracionada", "lisinopril", "milrinona", "ramipril", "verapamil-cloridrato"}
    found = set()
    for drug in _load("medicamentos/metadados.json"):
        marked = {field for field, value in drug.items() if MARKER in json.dumps(value, ensure_ascii=False)}
        if not marked:
            continue
        assert marked == {"commercial_presentations"}, drug["slug"]
        found.add(drug["slug"])
        proof = release["provenance"]["medicamentos"][drug["slug"]]
        assert proof["basis"] == "baseline_unchanged"
        digest = sha256(json.dumps(drug, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        assert digest == proof["source_sha256"], drug["slug"]
        assert drug["review_status"] == "revisado"
    # Do not erase known limitations or silently introduce new unverified data.
    assert found == expected
    for path in ("checklists/metadados.json", "material-paciente/metadados.json"):
        assert MARKER not in (ROOT / path).read_text(encoding="utf-8"), path
