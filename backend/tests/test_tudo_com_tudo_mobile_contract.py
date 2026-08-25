import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PAINEL = ROOT / "frontend/src/pages/PainelClinicalOS.tsx"
MOBILE_NAV = ROOT / "frontend/src/components/ClinicalMobileNav.tsx"
ROUTE = "/busca?modo=tudo-com-tudo"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _tudo_com_tudo_entries(source: str) -> list[str]:
    return re.findall(r"\{[^{}]*Tudo com Tudo[^{}]*\}", source)


def test_tudo_com_tudo_is_a_visible_quick_action_with_clear_detail():
    painel = _read(PAINEL)
    entries = _tudo_com_tudo_entries(painel)

    assert any(
        ROUTE in entry
        and 'titulo: "Tudo com Tudo"' in entry
        and 'detalhe: "Tema completo, organizado por áreas"' in entry
        for entry in entries
    )


def test_tudo_com_tudo_is_available_in_mobile_tools_for_every_user():
    mobile_nav = _read(MOBILE_NAV)
    entries = _tudo_com_tudo_entries(mobile_nav)

    assert any(ROUTE in entry and 'label: "Tudo com Tudo"' in entry for entry in entries)
    assert all("adminOnly" not in entry for entry in entries)


def test_tudo_com_tudo_route_is_also_exposed_in_panel_tools_without_admin_gate():
    painel = _read(PAINEL)
    entries = _tudo_com_tudo_entries(painel)

    tool_entries = [entry for entry in entries if 'label: "Tudo com Tudo"' in entry]
    assert any(ROUTE in entry for entry in tool_entries)
    assert all("adminOnly" not in entry for entry in tool_entries)
