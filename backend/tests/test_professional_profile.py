from pathlib import Path
from types import SimpleNamespace

from PIL import Image
import pytest

from app.core.config import settings
from app.services.professional_profile import (
    council_display,
    document_identity,
    logo_needs_dark_plate_path,
    normalize_professional_title, normalize_search_text,
    professional_name, rendered_logo_png,
)


def test_titulo_profissional_validado_por_allowlist():
    assert normalize_professional_title("Dra.") == "Dra."
    assert normalize_professional_title("") is None
    with pytest.raises(ValueError):
        normalize_professional_title("Excelentíssimo")


def test_nome_profissional_nao_inventa_doutor():
    assert professional_name({"full_name": "Ana Souza", "professional_title": None}) == "Ana Souza"
    assert professional_name({"full_name": "Ana Souza", "professional_title": "Dra."}) == "Dra. Ana Souza"


def test_logo_branca_transparente_recebe_placa_escura(tmp_path: Path):
    path = tmp_path / "clara.png"
    image = Image.new("RGBA", (40, 20), (0, 0, 0, 0))
    for x in range(5, 35):
        for y in range(5, 15):
            image.putpixel((x, y), (255, 255, 255, 255))
    image.save(path)
    assert logo_needs_dark_plate_path(path) is True


def test_logo_escura_mantem_placa_branca(tmp_path: Path):
    path = tmp_path / "escura.png"
    Image.new("RGBA", (40, 20), (10, 20, 30, 255)).save(path)
    assert logo_needs_dark_plate_path(path) is False


def test_logo_jpeg_e_convertida_para_png_contrastado_sem_alterar_original(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
):
    uploads = tmp_path / "uploads"
    logos = uploads / "logos"
    logos.mkdir(parents=True)
    original = logos / "logo.jpg"
    Image.new("RGB", (80, 30), (245, 245, 245)).save(original, format="JPEG")
    original_bytes = original.read_bytes()
    monkeypatch.setattr(settings, "uploads_dir", str(uploads))

    rendered = rendered_logo_png("/logos/logo.jpg")

    assert rendered is not None
    assert rendered.suffix == ".png"
    assert rendered.is_file()
    assert original.read_bytes() == original_bytes
    with Image.open(rendered) as image:
        assert image.format == "PNG"
        assert image.convert("RGBA").getpixel((0, 0))[:3] == (11, 46, 69)


def test_busca_normaliza_acentos_maiusculas_e_espacos():
    assert normalize_search_text("  JOSÉ da Conceição  ") == "jose da conceicao"
    assert "concei" in normalize_search_text("José da Conceição")


# --- council_display() / document_identity() — conselho "Outro" (08/08/2026) ---

def test_council_display_mantem_conselho_normal_intacto():
    """Fora de 'OUTRO', nunca troca nada — mesmo com os campos _other presentes
    (não deveriam estar, mas não é o council_display que garante isso)."""
    fonte = {
        "council_name": "CRM", "council_state": "SP",
        "council_name_other": "Não devia aparecer", "council_state_other": "Também não",
    }
    assert council_display(fonte) == ("CRM", "SP")


def test_council_display_troca_outro_pelo_texto_livre():
    fonte = {
        "council_name": "OUTRO", "council_state": None,
        "council_name_other": "Ordem dos Farmacêuticos",
        "council_state_other": "Lisboa",
    }
    assert council_display(fonte) == ("Ordem dos Farmacêuticos", "Lisboa")


def test_council_display_outro_sem_texto_livre_mantem_outro_literal():
    """Cadastro antigo, anterior ao campo — cai no valor literal 'OUTRO', não quebra."""
    fonte = {"council_name": "OUTRO", "council_state": None}
    assert council_display(fonte) == ("OUTRO", None)


def test_council_display_aceita_objeto_alem_de_dict():
    class Fake:
        council_name = "OUTRO"
        council_state = None
        council_name_other = "Conselho Regional de Psicologia"
        council_state_other = "Rio de Janeiro"

    assert council_display(Fake()) == ("Conselho Regional de Psicologia", "Rio de Janeiro")


def _usuario_documento(**overrides):
    base = dict(
        full_name="Ana Souza", professional_title="Dra.", profession="Médica",
        council_name="OUTRO", council_number="12345", council_state=None,
        council_name_other="Ordem dos Farmacêuticos", council_state_other="Lisboa",
        rqe=None, specialty="Cardiologia", document_logo_url=None,
        workplace_name=None, workplace_department=None, workplace_role=None,
        workplace_notes=None, include_workplace_on_documents=False,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def test_document_identity_usa_texto_livre_para_outro():
    """Documento/prescrição de um médico com conselho 'Outro' nunca deve
    mostrar a palavra 'OUTRO' — mostra o que ele digitou no cadastro."""
    identidade = document_identity(_usuario_documento())
    assert identidade["council_name"] == "Ordem dos Farmacêuticos"
    assert identidade["council_state"] == "Lisboa"


def test_document_identity_conselho_comum_nao_e_afetado():
    identidade = document_identity(_usuario_documento(
        council_name="CRM", council_state="SP",
        council_name_other=None, council_state_other=None,
    ))
    assert identidade["council_name"] == "CRM"
    assert identidade["council_state"] == "SP"
