import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_canonical_brand_assets_exist_and_are_named_explicitly():
    mark = ROOT / "frontend/public/corvia-mark-canonical.svg"
    wordmark = ROOT / "frontend/public/corvia-logo-canonical.svg"
    wordmark_dark = ROOT / "frontend/public/corvia-logo-canonical-dark.svg"
    assert mark.is_file()
    assert wordmark.is_file()
    assert wordmark_dark.is_file()
    assert "CorVIA" in mark.read_text(encoding="utf-8")
    assert "Clinical OS" in wordmark.read_text(encoding="utf-8")


def test_patient_documents_and_welcome_use_canonical_wordmark():
    cabecalho = _read("frontend/src/components/CabecalhoDocumento.tsx")
    boas_vindas = _read("frontend/src/components/BoasVindas.tsx")
    assert "/corvia-logo-canonical.svg" in cabecalho
    assert 'alt="CorVIA Clinical OS"' in cabecalho
    assert "/corvia-logo-canonical.svg" in boas_vindas
    assert "O Caminho do Coração" not in boas_vindas
    assert "O caminho do coração" not in boas_vindas


def test_transactional_email_template_uses_canonical_identity():
    base = _read("backend/app/templates/emails/_base.html")
    transport = _read("backend/app/services/emails.py")
    assert "/corvia-logo-canonical.svg" in base
    assert "CorVIA — Clinical OS" in base
    assert "cid:corvia-logo" not in base
    assert "_normalizar_branding" in transport


def test_appointment_confirmation_uses_canonical_identity():
    notification = _read("backend/app/services/agenda_integrada/notifications.py")
    assert "from app.services.pdf.marca import LOGO, logo_disponivel" in notification
    assert "cid:corvia-logo" in notification
    assert "CorVIA — Clinical OS" in notification
    assert "O caminho do coração" not in notification


def test_server_generated_documents_do_not_depend_on_legacy_logo_asset():
    marca = _read("backend/app/services/pdf/marca.py")
    web = ROOT / "frontend/public/corvia-logo-canonical.png"
    server = ROOT / "backend/app/assets/corvia-logo-canonical.png"
    assert web.is_file()
    assert server.is_file()
    assert hashlib.sha256(web.read_bytes()).digest() == hashlib.sha256(server.read_bytes()).digest()
    assert 'assets" / "corvia-logo-canonical.png' in marca
    assert "/tmp/" not in marca
    assert "_gerar_logo_canonica" not in marca


def test_external_file_generators_share_the_canonical_brand_source():
    generators = {
        "backend/app/services/pdf_documento.py": "app.services.pdf.marca",
        "backend/app/services/receita_controle_especial.py": "app.services.pdf.marca",
        "backend/app/services/apresentacao_pptx.py": "from .pdf.marca import LOGO",
        "backend/app/services/pdf/layout.py": "from .marca import",
    }
    for path, shared_brand_reference in generators.items():
        assert shared_brand_reference in _read(path), path

    for path in (
        "backend/app/services/material_paciente.py",
        "backend/app/services/apresentacao.py",
        "backend/app/services/exportacao_conteudo.py",
    ):
        source = _read(path)
        assert "app.services.pdf" in source or "from .pdf" in source, path


def test_browser_and_pwa_use_canonical_mark_only():
    index = _read("frontend/index.html")
    vite = _read("frontend/vite.config.ts")
    assert 'href="/corvia-mark-canonical.svg"' in index
    assert "corvia-logo-canonical.svg" in index
    assert 'src: "/corvia-mark-canonical.svg"' in vite
    for legacy in ("icon-192.png", "icon-512.png", "icon-maskable.png", "favicon.png", "apple-touch-icon.png"):
        assert legacy not in vite
