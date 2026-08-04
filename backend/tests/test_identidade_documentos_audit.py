from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _ler(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_rotas_documentais_usam_identidade_profissional_centralizada():
    for path in (
        "app/api/documents.py",
        "app/api/documentos_publicos.py",
        "app/api/exportacao.py",
        "app/api/receituario.py",
    ):
        source = _ler(path)
        assert "document_identity" in source, path
        assert 'f"Dr. {' not in source, path
        assert 'f"Dr(a). {' not in source, path


def test_todos_os_renderizadores_clinicos_suportam_logo_profissional():
    expected = {
        "app/services/pdf_documento.py": ("logo_path", "logo_needs_dark_plate_path"),
        "app/services/material_paciente.py": ("logo_path", "logo_needs_dark_plate_path"),
        "app/services/receita_controle_especial.py": ("logo_path", "logo_needs_dark_plate_path"),
        "app/services/apresentacao.py": ("rendered_logo_png", "professional_name"),
    }
    for path, symbols in expected.items():
        source = _ler(path)
        for symbol in symbols:
            assert symbol in source, f"{path}: faltou {symbol}"


def test_forma_de_tratamento_nao_e_inferida_pelo_conselho():
    profile = _ler("app/services/professional_profile.py")
    assert "professional_title" in profile
    assert 'return f"{title} {name}".strip()' in profile
