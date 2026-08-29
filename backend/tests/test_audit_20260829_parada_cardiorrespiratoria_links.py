from pathlib import Path

from app.services.disease_manifest import load_disease_records


ROOT = Path(__file__).resolve().parents[2]
SLUG = "parada-cardiorrespiratoria-e-morte-subita-abortada"
EXPECTED = {
    "parada-cardiorrespiratoria-no-adulto-suporte-avancado-sbc-2019",
    "fluxograma-parada-cardiorrespiratoria-ritmo-inicial",
    "dea-cadeia-de-sobrevivencia-e-plano-de-emergencia-no-esporte",
    "controle-de-temperatura-pos-parada-cardiorrespiratoria-ttm-e-ttm2",
    "neuroprognostico-multimodal-pos-parada-cardiorrespiratoria-algoritmo-erc-esicm-2021-e-a-atualizacao-aha-2025",
    "coronariografia-imediata-apos-parada-cardiaca-sem-supra-de-st-coact-e-tomahawk",
    "rcp-extracorporea-ecpr-na-parada-refrataria-arrest-e-inception",
}


def _record() -> dict:
    records = load_disease_records(ROOT / "doencas" / "metadados.json")
    return next(item for item in records if item["slug"] == SLUG)


def _document_slugs() -> set[str]:
    slugs: set[str] = set()
    for path in (ROOT / "content").rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        slug = path.stem
        if text.startswith("---"):
            for line in text.split("---", 2)[1].splitlines():
                if line.startswith("slug:"):
                    slug = line.split(":", 1)[1].strip().strip('"\'')
                    break
        slugs.add(slug)
    return slugs


def test_links_pos_parada_sao_exatamente_os_revisados():
    record = _record()
    assert record.get("review_status") == "revisado"
    assert record.get("completeness") == "completo"
    assert record.get("version") == 3
    assert set(record.get("related_document_slugs") or []) == EXPECTED


def test_todos_os_sete_links_resolvem_no_corpus():
    missing = EXPECTED - _document_slugs()
    assert missing == set(), f"links Tudo com Tudo quebrados: {sorted(missing)}"
