from pathlib import Path


def test_assinatura_externa_exige_prefixo_do_pdf_original():
    source = (Path(__file__).resolve().parents[1] / "app" / "api" / "prescricao_especial.py").read_text(encoding="utf-8")
    assert "conteudo.startswith(pdf_original)" in source
    assert "não corresponde à receita emitida pela CorVIA" in source
