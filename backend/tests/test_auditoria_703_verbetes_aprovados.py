from pathlib import Path
from app.services.disease_manifest import load_disease_records

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "doencas" / "metadados.json"
APPROVED = {"obesidade-e-coracao","insuficiencia-mitral","bloqueio-atrioventricular","estenose-mitral","cardiomiopatia-dilatada","apneia-do-sono-e-coracao","sindrome-cardiorrenal","cardiomiopatia-chagasica","minoca-e-disseccao-espontanea-arteria-coronaria","cardiomiopatia-de-takotsubo","cardiotoxicidade-por-cocaina-e-estimulantes","amiloidose-cardiaca-cadeia-leve","insuficiencia-tricuspide","emergencia-hipertensiva","cteph","protese-valvar-mecanica","torsades-de-pointes-qt-longo-adquirido","insuficiencia-aortica","estenose-aortica","sarcoidose-cardiaca","cardiomiopatia-arritmogenica"}

def test_703_verbetes_aprovados_estao_unicos_e_revisados():
    records = load_disease_records(MANIFEST)
    by_slug = {item["slug"]: item for item in records}
    assert len(by_slug) == len(records)
    assert APPROVED <= set(by_slug)
    for slug in APPROVED:
        assert by_slug[slug].get("review_status") == "revisado", slug
        assert by_slug[slug].get("source_refs"), slug
        assert by_slug[slug].get("summary"), slug
