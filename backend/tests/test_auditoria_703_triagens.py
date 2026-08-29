from pathlib import Path

from app.services.carregar_triagem_sintomas import load_triage_records

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "triagem-sintomas" / "metadados.json"


def test_triagens_auditadas_703_compostas_e_revisadas():
    records = load_triage_records(MANIFEST)
    by_slug = {item["slug"]: item for item in records}
    assert len(by_slug) == len(records)
    for slug in ("suspeita-infeccao-dispositivo-cardiaco-implantavel", "complicacao-local-pos-cateterismo-procedimento-vascular"):
        assert slug in by_slug
        assert by_slug[slug]["review_status"] == "revisado"
        assert by_slug[slug].get("source_refs")
        assert by_slug[slug].get("questions")
        assert by_slug[slug].get("rules")
