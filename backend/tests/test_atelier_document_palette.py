"""Isolated visual contracts: no database, clinical records, signing or delivery.

Office functions are compiled unchanged from their source AST with only their
rendering dependencies, so these checks do not bootstrap the application/ORM.
All sample content is a neutral visual-test fixture, held in memory.
"""

import ast
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
import re
from types import SimpleNamespace
from unittest.mock import patch
from zipfile import ZipFile

from docx import Document as WordDocument
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches as DocxInches, Pt as DocxPt, RGBColor as DocxRGBColor
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

from app.services.pdf import marca
from app.services.pdf.layout import Apresentacao, Documento

ROOT = Path(__file__).resolve().parents[2]
SERVICES = ROOT / "backend/app/services"


def _luminance(color):
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in color]
    return sum(c * weight for c, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


def _contrast(first, second):
    low, high = sorted((_luminance(first), _luminance(second)))
    return (high + 0.05) / (low + 0.05)


def _render_namespace(filename, functions, extra=None):
    """Load only genuine pure rendering functions, not unrelated application imports."""
    tree = ast.parse((SERVICES / filename).read_text(encoding="utf-8"))
    wanted = set(functions)
    found = {node.name for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted}
    assert found == wanted
    nodes = [ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)]
    nodes.extend(node for node in tree.body if (
        isinstance(node, ast.Assign)
        and all(isinstance(target, ast.Name) and target.id.isupper() for target in node.targets)
    ) or (isinstance(node, ast.FunctionDef) and node.name in wanted))
    namespace = {
        "marca": marca, "LOGO": marca.LOGO, "logo_disponivel": marca.logo_disponivel,
        "RGBColor": RGBColor, "Presentation": Presentation, "Inches": Inches, "Pt": Pt,
        "WordDocument": WordDocument, "DocxRGBColor": DocxRGBColor,
        "DocxInches": DocxInches, "DocxPt": DocxPt,
        "WD_ALIGN_PARAGRAPH": WD_ALIGN_PARAGRAPH, "OxmlElement": OxmlElement, "qn": qn,
        "datetime": datetime, "timezone": timezone, "BytesIO": BytesIO,
    }
    namespace.update(extra or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), str(SERVICES / filename), "exec"), namespace)
    return namespace


def test_document_palette_matches_approved_atelier_tokens():
    expected = {
        "NAVY": "24343A", "NAVY_ESCURO": "18282D", "TINTA": "18282D",
        "TEAL": "16776D", "COBRE": "B66D48", "COBRE_CLARO": "D39770",
        "OFF_WHITE": "FFFDFA", "TINTA_TEAL": "F6F3EB",
    }
    for token, value in expected.items():
        assert marca.cor_hex(getattr(marca, token)) == value
        assert tuple(int(value[i:i + 2], 16) for i in (0, 2, 4)) == marca.rgb8(getattr(marca, token))


def test_clinical_red_and_green_tokens_are_not_rebranded():
    for token, value in {
        "VERMELHO": "D5001D", "TINTA_VERMELHA": "FDEEF0",
        "VERDE_CONDUTA": "EEF6EF", "VERDE_TRACO": "2F7A4F",
    }.items():
        assert marca.cor_hex(getattr(marca, token)) == value
    assert marca.COBRE != marca.VERMELHO
    patient_source = (SERVICES / "material_paciente.py").read_text(encoding="utf-8")
    assert "cor_fundo=TINTA_VERMELHA" in patient_source
    assert "cor_barra=VERMELHO" in patient_source
    regulated_source = (SERVICES / "receita_controle_especial.py").read_text(encoding="utf-8")
    assert "COBRE" not in regulated_source


def test_all_small_text_pairings_keep_at_least_aa_contrast():
    for foreground in (marca.NAVY, marca.TINTA, marca.NEUTRO, marca.TEAL):
        for background in (marca.BRANCO, marca.OFF_WHITE, marca.TINTA_TEAL):
            assert _contrast(foreground, background) >= 4.5
    assert _contrast(marca.BRANCO, marca.NAVY) >= 7
    assert _contrast(marca.COBRE_CLARO, marca.NAVY) >= 4.5
    assert _contrast(marca.VERMELHO, marca.TINTA_VERMELHA) >= 4.5
    # This intentionally fails AA on paper: do not reuse the light copper for body text.
    assert _contrast(marca.COBRE_CLARO, marca.OFF_WHITE) < 4.5


def test_pdf_decorations_are_copper_but_alerts_stay_red():
    document = Documento("Verificação visual", "CorVIA", "Paleta", "Contrato visual")
    with patch.object(document.pdf, "retangulo", wraps=document.pdf.retangulo) as rectangles:
        document.capa_simples("Verificação visual", "Subtítulo de teste")
        document.paragrafo("Texto neutro de verificação visual.")
        document.destaque("Aviso de teste", cor_fundo=marca.TINTA_VERMELHA, cor_barra=marca.VERMELHO)
        fills = [call.args[4] for call in rectangles.call_args_list]
        assert marca.OFF_WHITE in fills
        assert marca.COBRE in fills
        assert marca.VERMELHO in fills
        assert marca.TINTA_VERMELHA in fills
    assert document.salvar_bytes().startswith(b"%PDF-")

    slides = Apresentacao("Verificação", "CorVIA", "Paleta", "Contrato visual")
    with patch.object(slides.pdf, "texto", wraps=slides.pdf.texto) as text:
        slides.capa("Verificação visual", "Subtítulo", "Identidade de teste", "Registro de teste")
        copper_text = [call.args for call in text.call_args_list if call.args[4] == marca.COBRE_CLARO]
        assert len(copper_text) == 1
        assert copper_text[0][2] == "Registro de teste"
    assert slides.salvar_bytes().startswith(b"%PDF-")


def test_both_powerpoint_renderers_serialize_shared_palette():
    configurations = (
        ("exportacao_office.py", ("_slide_vazio", "_caixa", "_rodape_slide", "_capa_pptx", "_slide_conteudo")),
        ("apresentacao_pptx.py", ("_slide_em_branco", "_caixa_texto", "_logo_corvia", "_rodape", "_titulo_slide", "_corpo_com_marcadores", "_capa")),
    )
    for filename, functions in configurations:
        render = _render_namespace(filename, functions)
        presentation = Presentation()
        presentation.slide_width, presentation.slide_height = render["LARGURA"], render["ALTURA"]
        if filename == "exportacao_office.py":
            render["_capa_pptx"](presentation, "Verificação", "Subtítulo", "Identidade de teste", [])
            render["_slide_conteudo"](presentation, "Seção", [("paragrafo", "Texto de teste")], "Rodapé")
        else:
            render["_capa"](presentation, "Verificação", "", "Identidade de teste", "Registro de teste")
            slide = render["_slide_em_branco"](presentation)
            render["_titulo_slide"](slide, "Seção")
            render["_corpo_com_marcadores"](slide, [("paragrafo", "Texto de teste")])
            render["_rodape"](slide, "Rodapé")
        stream = BytesIO()
        presentation.save(stream)
        with ZipFile(stream) as archive:
            cover = archive.read("ppt/slides/slide1.xml").decode()
            body = archive.read("ppt/slides/slide2.xml").decode()
        for color in ("24343A", "D39770", "FFFFFF"):
            assert f'val="{color}"' in cover
        for color in ("24343A", "18282D", "FFFDFA"):
            assert f'val="{color}"' in body
        assert 'val="D39770"' not in body
        assert 'val="0B2E45"' not in cover + body


def test_word_generator_serializes_paper_copper_border_and_dark_text():
    content_tree = ast.parse((SERVICES / "exportacao_conteudo.py").read_text(encoding="utf-8"))
    selected = [node for node in content_tree.body if (
        isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "ROTULOS_TIPO" for target in node.targets)
    ) or (isinstance(node, ast.FunctionDef) and node.name == "_sem_markdown")]
    content = {"re": re}
    exec(compile(ast.Module(body=selected, type_ignores=[]), "isolated_content_formatting", "exec"), content)
    render = _render_namespace("exportacao_office.py", (
        "_titulo_exportacao", "_identificacao", "_cabecalho_docx", "_definir_borda_inferior", "gerar_docx",
    ), content)
    section = SimpleNamespace(titulo="Seção de teste", destaque="Realce visual", paragrafos=["Texto de verificação visual."], itens=["Item de teste"])
    item = SimpleNamespace(tipo="documento", titulo="Verificação visual", tema="Paleta", subtitulo=None, secoes=[section])
    payload = render["gerar_docx"]([item], user=None, incluir_dados_assinante=False)
    restored = WordDocument(BytesIO(payload))
    for style, color in {"Normal": "18282D", "Title": "24343A", "Heading 1": "24343A", "Heading 2": "16776D"}.items():
        assert str(restored.styles[style].font.color.rgb) == color
    with ZipFile(BytesIO(payload)) as archive:
        xml = archive.read("word/document.xml").decode()
    assert '<w:background w:color="FFFDFA"' in xml
    assert 'w:color="B66D48"' in xml
    assert "Texto de verificação visual." in xml
    assert 'w:color="D39770"' not in xml
    assert 'w:color="0B2E45"' not in xml
