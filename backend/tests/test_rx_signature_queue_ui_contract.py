from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_email_signature_uses_canonical_corvia_logo():
    source = (ROOT / "backend" / "app" / "services" / "email_signature.py").read_text(encoding="utf-8")
    assert "corvia-logo-canonical.svg" in source
    assert "corvia-logo-compacta.png" not in source


def test_dedicated_signature_queue_is_routed_and_in_both_navigation_surfaces():
    app = (ROOT / "frontend" / "src" / "App.tsx").read_text(encoding="utf-8")
    desktop = (ROOT / "frontend" / "src" / "components" / "ClinicalDesktopNav.tsx").read_text(encoding="utf-8")
    mobile = (ROOT / "frontend" / "src" / "components" / "ClinicalMobileNav.tsx").read_text(encoding="utf-8")
    page = (ROOT / "frontend" / "src" / "pages" / "ReceitasParaAssinatura.tsx").read_text(encoding="utf-8")

    for source in (app, desktop, mobile):
        assert "receitas-para-assinatura" in source
    assert "queueOnly" in page
    assert "/prescricao-especial/pendentes" in desktop
    assert "/prescricao-especial/pendentes" in mobile
