from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from app.services.disease_manifest import load_disease_records


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "doencas" / "metadados.json"
CANONICAL_DISEASE_COUNT = 172


def _load_script(name: str, path: Path):
    spec = spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_catalogo_canonico_tem_172_doencas_incluindo_fragmentos():
    records = load_disease_records(BASE)
    assert len(records) == CANONICAL_DISEASE_COUNT
    slugs = {item["slug"] for item in records}
    assert len(slugs) == CANONICAL_DISEASE_COUNT
    for expected in (
        "doenca-da-aorta",
        "choque-cardiogenico",
        "insuficiencia-cardiaca-avancada",
        "cardiopatia-congenita-do-adulto",
        "hipertensao-resistente-e-refrataria",
        "dispositivos-cardiacos-implantaveis",
        "cardiomiopatia-hipertrofica",
        "cardiomiopatias",
    ):
        assert expected in slugs


def test_auditoria_carrega_catalogo_canonico_e_nao_so_manifesto_base():
    audit_module = _load_script("audit_tudo_com_tudo_rc605", ROOT / "scripts" / "audit_tudo_com_tudo.py")
    records = audit_module._load("doencas")
    assert len(records) == CANONICAL_DISEASE_COUNT


def test_inventario_conta_catalogo_canonico_com_fragmentos():
    inventory_module = _load_script("content_inventory_rc605", ROOT / "scripts" / "content_inventory.py")
    result = inventory_module.inventory()
    assert result["fronts"]["doencas_especializadas"]["records"] == CANONICAL_DISEASE_COUNT
    assert result["fronts"]["doencas_especializadas"]["duplicate_keys"] == []
