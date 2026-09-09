"""Geometry regressions: inspect actual PDF glyphs, not source-code strings."""
from datetime import datetime, timezone
from io import BytesIO
from types import SimpleNamespace

import pdfplumber
from PIL import Image

from app.services import pdf_documento as clinical
from app.services import material_paciente

MEDICO = {
    "full_name": "Mariana Aparecida de Albuquerque e Silva",
    "professional_title": "Dra.",
    "council_name": "CRM", "council_state": "SP", "council_number": "123456",
    "rqe": "654321", "profession": "Médica", "specialty": "Cardiologia",
    "include_workplace_on_documents": True,
    "workplace_name": "Instituto de Cardiologia e Medicina Integrada",
    "workplace_department": "Cardiologia clínica", "workplace_role": "Responsável técnica",
}
DATA = datetime(2026, 9, 9, tzinfo=timezone.utc)


def _check_margins(data, margin=clinical.MARGEM):
    with pdfplumber.open(BytesIO(data)) as doc:
        for number, page in enumerate(doc.pages, 1):
            for char in page.chars:
                assert char["x0"] >= margin - 0.5, (number, char)
                assert char["x1"] <= page.width - margin + 0.5, (number, char)
                assert 0 <= char["top"] <= char["bottom"] <= page.height, (number, char)
        return len(doc.pages)


def test_long_document_preserves_body_font_and_paginates_inside_paragraph():
    paragraph = " ".join(f"CONTEXTO{i:04d}" for i in range(1000))
    pdf = clinical.documento_generico(
        "Documento para acompanhamento e orientações de rotina com título extenso " * 2,
        paragraph, MEDICO, DATA,
    )
    assert _check_margins(pdf) > 2
    with pdfplumber.open(BytesIO(pdf)) as doc:
        body = []
        for page in doc.pages:
            words = [w for w in page.extract_words(extra_attrs=["size"]) if w["text"].startswith("CONTEXTO")]
            assert words, "No blank continuation pages"
            assert all(abs(w["size"] - 10.5) < 0.01 for w in words)
            assert all(w["bottom"] < page.height - 62 * clinical.mm for w in words)
            body.extend(w["text"] for w in words)
        assert body == paragraph.split(), "No dropped or duplicated clinical content"


def test_prescription_paginates_long_dosage_and_observations():
    pdf = clinical.receituario_comum(
        {"nome": "Paciente de demonstração " * 8, "endereco": "Endereço de demonstração " * 12},
        [{"descricao": "Item de demonstração " * 12,
          "posologia": "Orientação de teste. " * 700,
          "orientacao": "COMPLEMENTOFINAL " * 100,
          "quantidade": "Quantidade de teste " * 10,
          "uso_continuo": True}],
        MEDICO, DATA, observacoes="OBSFINAL " * 600,
    )
    assert _check_margins(pdf) > 3
    with pdfplumber.open(BytesIO(pdf)) as doc:
        text = " ".join(page.extract_text() for page in doc.pages)
        assert text.count("OBSFINAL") == 600
        assert text.count("Orientação de teste.") == 700
        assert text.count("COMPLEMENTOFINAL") == 100


def test_long_identifier_wraps_without_adding_or_losing_characters():
    token = "IDENTIFICADOR0123456789" * 30
    pdf = clinical.documento_generico("Documento", token, MEDICO, DATA)
    _check_margins(pdf)
    with pdfplumber.open(BytesIO(pdf)) as doc:
        body = "".join(c["text"] for p in doc.pages for c in p.chars if abs(c["size"] - 10.5) < .01)
        assert body == token


def test_personal_logo_is_centered_and_identity_stays_on_right(monkeypatch, tmp_path):
    logo = tmp_path / "logo.png"
    Image.new("RGB", (280, 120), (32, 74, 100)).save(logo)
    monkeypatch.setattr(clinical, "_caminho_logo_pessoal", lambda _url: logo)
    pdf = clinical.documento_generico("Documento", "Corpo de demonstração.", MEDICO, DATA)
    _check_margins(pdf)
    with pdfplumber.open(BytesIO(pdf)) as doc:
        page = doc.pages[0]
        personal = [im for im in page.images if im["srcsize"] == (280, 120)][0]
        assert abs((personal["x0"] + personal["x1"]) / 2 - page.width / 2) < .1
        name = next(w for w in page.extract_words() if w["text"] == "Mariana")
        assert name["x0"] > personal["x1"]


def test_educational_material_repeats_centered_header_without_clipping(monkeypatch, tmp_path):
    logo = tmp_path / "logo.png"
    Image.new("RGB", (280, 120), (32, 74, 100)).save(logo)
    monkeypatch.setattr(material_paciente, "rendered_logo_png", lambda _url: logo)
    material = SimpleNamespace(
        titulo="Material de demonstração", subtitulo="Prévia de diagramação",
        secoes=[{"titulo": "Seção de teste", "paragrafos": ["Conteúdo de exemplo. " * 500], "itens": []}],
        sinais_de_alerta=[], perguntas=[], fontes=[],
    )
    pdf = material_paciente.gerar(material, MEDICO)
    assert _check_margins(pdf, 61) > 1
    with pdfplumber.open(BytesIO(pdf)) as doc:
        for page in doc.pages:
            personal = [im for im in page.images if im["srcsize"] == (280, 120)][0]
            assert abs((personal["x0"] + personal["x1"]) / 2 - page.width / 2) < .1
            assert "Mariana" in page.extract_text()


def test_controlled_prescription_splits_a_single_long_item_and_retains_both_copies():
    from app.services.receita_controle_especial import receita_controle_especial, MARGEM_X

    pdf = receita_controle_especial(
        destinatario={"nome": "Paciente de demonstração", "documento": "00000000000",
                      "endereco": "Rua de demonstração, 1 - Centro - Cidade/SP - CEP 00000-000"},
        itens=[{"descricao": "Item de demonstração", "lista": "C1",
                "quantidade": "10 unidades (dez unidades)",
                "posologia": "DOSETESTE " * 400, "orientacao": "ORIENTACAOTESTE " * 300}],
        observacoes="OBSERVACAOTESTE " * 180,
        medico=MEDICO, data_emissao=DATA,
        endereco_profissional={"logradouro": "Rua Teste", "numero": "1", "cidade": "Cidade", "uf": "SP"},
    )
    assert _check_margins(pdf, MARGEM_X) > 2
    with pdfplumber.open(BytesIO(pdf)) as doc:
        assert len(doc.pages) % 2 == 0
        textos = [page.extract_text() for page in doc.pages]
        for marcador, quantidade in [("DOSETESTE", 400), ("ORIENTACAOTESTE", 300), ("OBSERVACAOTESTE", 180)]:
            assert " ".join(textos[:len(textos)//2]).count(marcador) == quantidade
            assert " ".join(textos[len(textos)//2:]).count(marcador) == quantidade
        for page in doc.pages:
            words = [w for w in page.extract_words() if w["text"].endswith("TESTE")]
            assert all(w["bottom"] < page.height - 100 * clinical.mm for w in words)


def test_long_educational_alert_flows_across_pages_without_losing_text():
    material = SimpleNamespace(
        titulo="Material de demonstração", subtitulo="Prévia de diagramação",
        secoes=[], sinais_de_alerta=["ALERTATESTEFIM " * 500], perguntas=[], fontes=[],
    )
    pdf = material_paciente.gerar(material, MEDICO)
    assert _check_margins(pdf, 61) > 1
    with pdfplumber.open(BytesIO(pdf)) as doc:
        assert " ".join(p.extract_text() for p in doc.pages).count("ALERTATESTEFIM") == 500
        for page in doc.pages:
            alerts = [w for w in page.extract_words() if w["text"] == "ALERTATESTEFIM"]
            assert all(w["bottom"] < page.height - 76 for w in alerts)


def test_long_professional_footer_wraps_above_digital_stamp():
    medico = {**MEDICO, "full_name": "Profissional de demonstração " * 8}
    pdf = clinical.documento_generico("Documento", "CORPOTESTE " * 700, medico, DATA, metodo_assinatura="A1_ARQUIVO")
    _check_margins(pdf)
    with pdfplumber.open(BytesIO(pdf)) as doc:
        page = doc.pages[-1]
        footer = [c for c in page.chars if c["top"] > page.height - 100 * clinical.mm]
        assert all(c["bottom"] < page.height - 88 for c in footer)
