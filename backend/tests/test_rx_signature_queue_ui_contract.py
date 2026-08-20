from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_email_signature_uses_canonical_corvia_logo():
    source = (ROOT / "backend" / "app" / "services" / "email_signature.py").read_text(encoding="utf-8")
    assert "corvia-logo-canonical.png" in source
    assert "corvia-logo-compacta.png" not in source
    png = ROOT / "frontend" / "public" / "corvia-logo-canonical.png"
    assert png.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_dedicated_signature_queue_is_routed_and_in_both_navigation_surfaces():
    app = (ROOT / "frontend" / "src" / "App.tsx").read_text(encoding="utf-8")
    desktop = (ROOT / "frontend" / "src" / "components" / "ClinicalDesktopNav.tsx").read_text(encoding="utf-8")
    mobile = (ROOT / "frontend" / "src" / "components" / "ClinicalMobileNav.tsx").read_text(encoding="utf-8")
    badge = (ROOT / "frontend" / "src" / "hooks" / "usePrescriptionQueueBadge.ts").read_text(encoding="utf-8")
    queue = (ROOT / "frontend" / "src" / "components" / "PrescricaoLivreEspecial.tsx").read_text(encoding="utf-8")

    for source in (app, desktop, mobile):
        assert "receitas-para-assinatura" in source
    assert "queueOnly" in queue
    assert "usePrescriptionQueueBadge" in desktop
    assert "usePrescriptionQueueBadge" in mobile
    assert "/prescricao-especial/pendentes" in badge
    assert "setInterval" in badge


def test_authorized_users_free_text_prescription_is_exposed_in_global_receituario():
    receituario = (ROOT / "frontend" / "src" / "pages" / "Receituario.tsx").read_text(encoding="utf-8")
    composer = (ROOT / "frontend" / "src" / "components" / "PrescricaoLivreEspecial.tsx").read_text(encoding="utf-8")

    assert 'import PrescricaoLivreEspecial from "../components/PrescricaoLivreEspecial"' in receituario
    assert "if(queueOnly&&x.rafael_signer)" in composer
    assert "<PrescricaoLivreEspecial />" in receituario
    assert 'placeholder="Digite a prescrição, posologia e orientações…"' in composer
    assert '<option value="propria">Emitir com minhas credenciais</option>' in composer
    assert "Emissão somente pelo Dr. Rafael." in composer


def test_medication_suggestions_have_explicit_dark_theme_contrast_and_focus():
    css = (ROOT / "frontend" / "src" / "styles" / "clinical-work-v2.css").read_text(encoding="utf-8")
    assert ".clinical-os .prescricao-sugestoes{" in css
    assert "background:#0b2331!important" in css
    assert ".clinical-os .prescricao-sugestoes button strong{color:#f3fbfc!important}" in css
    assert ".clinical-os .prescricao-sugestoes button small{color:#91adb5!important}" in css
    assert ".clinical-os .prescricao-sugestoes button:focus-visible" in css
