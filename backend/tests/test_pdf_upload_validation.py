"""PDF upload regressions: synthetic bytes only, no DB or external services."""

import io
import sys

import pytest
from pyhanko.pdf_utils import generic
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.pdf_utils.writer import PageObject, PdfFileWriter
from reportlab.pdfgen.canvas import Canvas

from app.core.uploads import UploadRejected, validate_file
from app.services.pdf.marca import LOGO
from app.core import pdf_upload_validation as inspection


@pytest.fixture(autouse=True, params=[
    "parser-unit",
    pytest.param("isolated-child", marks=pytest.mark.skipif(
        sys.platform != "linux", reason="Hard RLIMIT_AS requires the Linux backend platform",
    )),
])
def inspection_execution(request, monkeypatch):
    """Unit semantics on every host; real resource-limited child additionally on Linux.

    This fixture never changes the production worker or its resource limits.
    Synthetic unit PDFs are deliberately parsed in-process and labelled as such.
    """
    if request.param == "parser-unit":
        def inspect_synthetic(data):
            try:
                inspection._inspect_pdf_structure(data)
            except inspection.PdfInspectionError:
                raise
            except Exception:
                raise inspection.PdfInspectionError("malformed") from None
        monkeypatch.setattr(inspection, "validate_pdf_structure", inspect_synthetic)


def _pdf(catalog=b"", *, content=b"", extra_objects=()):
    """Real xref offsets, allowing escaped PDF names without writer canonicalisation."""
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R " + catalog + b" >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream",
        *extra_objects,
    ]
    output = io.BytesIO(b"%PDF-1.7\n")
    output.seek(0, io.SEEK_END)
    offsets = []
    for number, obj in enumerate(objects, 1):
        offsets.append(output.tell())
        output.write(f"{number} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = output.tell()
    output.write(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets:
        output.write(f"{offset:010d} 00000 n \n".encode())
    output.write(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return output.getvalue()


def _written(writer):
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


@pytest.mark.parametrize("kind", ["exam", "clinical_exam", "email"])
def test_pdf_da_marca_atelier_com_js_nos_bytes_da_imagem_e_aceito(kind):
    output = io.BytesIO()
    canvas = Canvas(output)
    canvas.drawImage(str(LOGO), 30, 750, width=225, height=60)
    canvas.drawString(30, 700, "Documento sintetico de teste")
    canvas.save()
    data = output.getvalue()
    assert b"/JS" in data, "fixture deve reproduzir a colisão ASCII85 da marca"
    original = bytes(data)
    assert validate_file(data, "documento.pdf", kind) == "application/pdf"
    assert data == original, "validação nunca regrava bytes assináveis"
    assert not PdfFileReader(io.BytesIO(data)).embedded_signatures


@pytest.mark.parametrize("entries", [
    b"/JavaScript (teste)",
    b"/JS (teste)",
    b"/Launch << /F (arquivo) >>",
    b"/EmbeddedFile << >>",
    b"/Names << /EmbeddedFiles << /Names [] >> >>",
    b"/RichMedia << >>",
    b"/AA << /O << /S /JavaScript /JS (teste) >> >>",
    b"/OpenAction [3 0 R /Fit]",
    b"/AcroForm << /XFA [] >>",
    b"/Custom << /Nested [ << /S /JavaScript >> ] >>",
    b"/J#53 (teste)",
    b"/#4AS (teste)",
    b"/Custom << /S /Java#53cript >>",
    b"/Open#41ction [3 0 R /Fit]",
    b"/A#41 << >>",
    b"/AcroForm << /X#46A [] >>",
    b"/Custom << /Type /Embedded#46ile >>",
])
def test_pdf_rejeita_nomes_ativos_inclusive_escapados_e_aninhados(entries):
    with pytest.raises(UploadRejected, match="scripts"):
        validate_file(_pdf(entries), "documento.pdf", "email")


def test_pdf_rejeita_objeto_ativo_fora_do_catalogo():
    with pytest.raises(UploadRejected, match="scripts"):
        validate_file(_pdf(extra_objects=(b"<< /JS (teste) >>",)), "documento.pdf", "email")


def test_pdf_nao_confunde_texto_comentario_hex_ou_stream_com_nome_ativo():
    keywords = b"/JS /JavaScript /Launch /EmbeddedFile /AA /OpenAction /XFA"
    entries = b"/Title (" + keywords + b") /Subject <" + keywords.hex().encode() + b">"
    entries += b" /JSVersion 1 % /JS is only a comment\n"
    assert validate_file(_pdf(entries, content=keywords), "documento.pdf", "email") == "application/pdf"


@pytest.mark.parametrize("active", [False, True])
def test_pdf_inspeciona_objetos_comprimidos_e_referencias_ciclicas(active):
    writer = PdfFileWriter()
    contents = writer.add_object(generic.StreamObject(stream_data=b""))
    writer.insert_page(PageObject(contents, (0, 0, 612, 792)))
    stream = writer.prepare_object_stream()
    dictionary = generic.DictionaryObject({"/Title": generic.TextStringObject("/JS texto inerte")})
    if active:
        dictionary["/JS"] = generic.TextStringObject("teste")
    reference = writer.add_object(dictionary, obj_stream=stream)
    dictionary["/Self"] = reference
    writer.root["/Custom"] = reference
    data = _written(writer)
    assert b"/ObjStm" in data
    assert b"/JS" not in data, "objeto deve estar comprimido, não visível ao filtro antigo"
    if active:
        with pytest.raises(UploadRejected, match="scripts"):
            validate_file(data, "documento.pdf", "email")
    else:
        assert validate_file(data, "documento.pdf", "email") == "application/pdf"


@pytest.mark.parametrize("active_in_first_revision", [False, True])
def test_pdf_inspeciona_revisoes_incrementais_anteriores_e_atuais(active_in_first_revision):
    initial = _pdf(b"/JS (teste)" if active_in_first_revision else b"")
    writer = IncrementalPdfFileWriter(io.BytesIO(initial))
    if active_in_first_revision:
        del writer.root["/JS"]
    else:
        writer.root["/JS"] = generic.TextStringObject("teste")
    writer.update_root()
    data = _written(writer)
    assert PdfFileReader(io.BytesIO(data)).total_revisions == 2
    with pytest.raises(UploadRejected, match="scripts"):
        validate_file(data, "documento.pdf", "email")


def test_pdf_incremental_com_bytes_de_assinatura_nao_e_regravado():
    writer = IncrementalPdfFileWriter(io.BytesIO(_pdf()))
    # Payload sintético, NÃO uma assinatura válida. A validação criptográfica
    # continua obrigatória na rota de assinatura, após a inspeção do upload.
    writer.root["/Custom"] = generic.DictionaryObject({
        "/Contents": generic.ByteStringObject(b"/JS /JavaScript /Launch"),
    })
    writer.update_root()
    data = _written(writer)
    assert validate_file(data, "documento.pdf", "email") == "application/pdf"


@pytest.mark.parametrize("password", ["senha-sintetica", ""])
def test_pdf_criptografado_e_rejeitado_mesmo_sem_senha_de_abertura(password):
    writer = PdfFileWriter()
    contents = writer.add_object(generic.StreamObject(stream_data=b""))
    writer.insert_page(PageObject(contents, (0, 0, 612, 792)))
    writer.encrypt("dono-sintetico", user_pass=password)
    with pytest.raises(UploadRejected, match="criptografado"):
        validate_file(_written(writer), "documento.pdf", "email")


@pytest.mark.parametrize("data", [
    b"%PDF-1.4\nconteudo falso\n%%EOF",
    _pdf()[:-30] + b"\n%%EOF",
    _pdf().replace(b"/Pages 2 0 R", b"/Pages 9 0 R"),
    _pdf().replace(b"/Count 1", b"/Count x"),
    _pdf().replace(b"endobj", b"broken", 1),
    _pdf(b"/Custom 9 0 R"),
])
def test_pdf_malformado_falha_fechado(data):
    with pytest.raises(UploadRejected) as rejected:
        validate_file(data, "documento.pdf", "email")
    assert rejected.value.status_code == 422


def test_pdf_extensao_incorreta_e_arquivo_incompleto_continuam_rejeitados():
    with pytest.raises(UploadRejected, match="extensão"):
        validate_file(_pdf(), "documento.png", "email")
    with pytest.raises(UploadRejected, match="incompleto"):
        validate_file(_pdf().replace(b"%%EOF", b""), "documento.pdf", "email")
