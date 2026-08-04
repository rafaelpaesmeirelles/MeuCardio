from pathlib import Path

from PIL import Image
import pytest

from app.services.professional_profile import (
    logo_needs_dark_plate_path,
    normalize_professional_title, normalize_search_text,
    professional_name,
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


def test_busca_normaliza_acentos_maiusculas_e_espacos():
    assert normalize_search_text("  JOSÉ da Conceição  ") == "jose da conceicao"
    assert "concei" in normalize_search_text("José da Conceição")
