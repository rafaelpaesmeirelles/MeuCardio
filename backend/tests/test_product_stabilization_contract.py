from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_prescription_email_does_not_block_mail360_for_profile_smime_preference():
    source = text("backend/app/services/envio_documento_email.py")
    assert "if assinar_smime:" in source
    assert "if assinatura_obrigatoria:\n            return ResultadoEnvio(\n                False, conta.provider" not in source


def test_public_validation_surface_is_wired_and_non_download():
    source = text("backend/app/api/documentos_publicos.py")
    assert '@router.get("/validar/{codigo}")' in source
    assert "validacao_publica.validar(registro)" in source
    assert "sha256" in source


def test_a1_visible_stamp_has_validation_address_and_code():
    source = text("backend/app/services/assinatura/pdf_signer.py")
    assert "Validar:" in source
    assert "Codigo:" in source
    assert "codigo_validacao" in source


def test_saved_locations_are_geocoded_and_have_retry_endpoint():
    source = text("backend/app/api/agenda_integrada.py")
    assert "_try_geocode_calendar_location" in source
    assert '@router.post("/locations/geocode-pending")' in source
    assert '@router.post("/locations/{location_id}/geocode")' in source
