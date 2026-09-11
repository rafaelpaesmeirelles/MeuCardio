"""Resource/protocol regressions; all input is synthetic, no DB or networking.

Linux tests invoke the real child without patching resource or subprocess.
Other tests explicitly simulate protocol failures or inspect synthetic parser
fixtures in-process; these are NOT evidence of OS isolation on macOS.
"""

import asyncio
import io
import subprocess
import sys
import threading
from pathlib import Path

import pytest
from pyhanko.pdf_utils import generic
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.pdf_utils.writer import PageObject, PdfFileWriter

from app.core import pdf_upload_validation as pdf
from app.core import uploads


LINUX_ONLY = pytest.mark.skipif(sys.platform != "linux", reason="Hard RLIMIT_AS requires Linux")


def _written(writer):
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def _writer(content=b""):
    writer = PdfFileWriter(stream_xrefs=False)
    contents = writer.add_object(generic.StreamObject(stream_data=content))
    writer.insert_page(PageObject(contents, (0, 0, 612, 792)))
    return writer


@pytest.mark.parametrize("returncode,stdout,reason", [
    (1, b"active\n", "active"), (1, b"limits\n", "limits"),
    (2, b"unavailable\n", "unavailable"), (-9, b"", "limits"),
    (3, b"private parser detail", "unavailable"),
    (0, b"", "unavailable"), (0, b"ok\nextra", "unavailable"),
])
def test_protocol_falha_fechado_sem_expor_conteudo(monkeypatch, returncode, stdout, reason):
    monkeypatch.setattr(pdf.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, returncode, stdout))
    with pytest.raises(pdf.PdfInspectionError) as rejected:
        pdf.validate_pdf_structure(b"synthetic")
    assert rejected.value.reason == reason


def test_timeout_falha_fechado_e_libera_slot(monkeypatch):
    def timed_out(*args, **kwargs):
        raise subprocess.TimeoutExpired("synthetic-child", pdf.PDF_WALL_SECONDS)
    monkeypatch.setattr(pdf.subprocess, "run", timed_out)
    for _ in range(2):
        with pytest.raises(pdf.PdfInspectionError, match="limits"):
            pdf.validate_pdf_structure(b"synthetic")


def test_falha_de_launch_e_recurso_indisponivel_sao_explicitos(monkeypatch):
    def unavailable(*args, **kwargs):
        raise OSError("synthetic launch failure")
    monkeypatch.setattr(pdf.subprocess, "run", unavailable)
    with pytest.raises(pdf.PdfInspectionError, match="unavailable"):
        pdf.validate_pdf_structure(b"synthetic")
    monkeypatch.setitem(sys.modules, "resource", None)
    with pytest.raises(pdf.PdfInspectionError, match="unavailable"):
        pdf._apply_resource_limits()


def test_child_usa_comando_isolado_e_ambiente_minimo(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "never-inherit-synthetic-secret")
    calls = []
    def completed(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, b"ok\n")
    monkeypatch.setattr(pdf.subprocess, "run", completed)
    pdf.validate_pdf_structure(b"synthetic")
    command, options = calls[0]
    assert command[:5] == [sys.executable, "-I", "-B", "-X", "utf8"]
    assert Path(command[-1]).is_absolute()
    assert set(options["env"]) == {"PATH"}
    assert options["stderr"] is subprocess.DEVNULL
    assert options["timeout"] == 8 and options["close_fds"] is True
    assert "preexec_fn" not in options


def test_entrada_acima_40mib_nao_lanca_child(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("oversized input must be rejected before launch")
    monkeypatch.setattr(pdf.subprocess, "run", forbidden)
    with pytest.raises(pdf.PdfInspectionError, match="too_large"):
        pdf.validate_pdf_structure(b" " * (pdf.MAX_PDF_INPUT_BYTES + 1))


@pytest.mark.skipif(sys.platform != "darwin", reason="Darwin aliases address-space and RSS limits")
def test_plataforma_sem_limite_real_falha_explicitamente():
    with pytest.raises(pdf.PdfInspectionError, match="unavailable"):
        pdf.validate_pdf_structure(_written(_writer()))


@pytest.mark.parametrize("limit", ["MAX_PDF_OBJECTS", "MAX_PDF_NODES", "MAX_PDF_REVISIONS", "MAX_PDF_STRUCTURAL_BYTES"])
def test_limites_estruturais_unitarios(monkeypatch, limit):
    writer = _writer()
    if limit == "MAX_PDF_STRUCTURAL_BYTES":
        writer.add_object(generic.StreamObject({
            "/Type": generic.NameObject("/ObjStm"),
            "/N": generic.NumberObject(1), "/First": generic.NumberObject(4),
        }, stream_data=b"9 0 << /Title (inert) >>"))
    monkeypatch.setattr(pdf, limit, 0)
    with pytest.raises(pdf.PdfInspectionError, match="limits"):
        pdf._inspect_pdf_structure(_written(writer))


@LINUX_ONLY
@pytest.mark.parametrize("kind", ["revisions", "objects", "expansion"])
def test_child_real_rejeita_limites_documentados(kind):
    writer = _writer()
    if kind == "objects":
        for _ in range(pdf.MAX_PDF_OBJECTS):
            writer.add_object(generic.DictionaryObject())
    elif kind == "expansion":
        stream = generic.StreamObject({
            "/Type": generic.NameObject("/ObjStm"),
            "/N": generic.NumberObject(1), "/First": generic.NumberObject(4),
        }, stream_data=b"9 0 << >>" + b" " * pdf.MAX_PDF_STRUCTURAL_BYTES)
        stream.compress()
        writer.add_object(stream)
    data = _written(writer)
    if kind == "revisions":
        for index in range(pdf.MAX_PDF_REVISIONS):
            revision = IncrementalPdfFileWriter(io.BytesIO(data))
            revision.root["/Title"] = generic.TextStringObject(str(index))
            revision.update_root()
            data = _written(revision)
    assert len(data) <= pdf.MAX_PDF_INPUT_BYTES
    with pytest.raises(pdf.PdfInspectionError, match="limits"):
        pdf.validate_pdf_structure(data)


@LINUX_ONLY
def test_child_real_preserva_pdf_de_curso_proximo_40mib():
    from app.core.course_uploads import validate_course_file
    data = _written(_writer(b" " * (pdf.MAX_PDF_INPUT_BYTES - 4096)))
    assert 39 * 1024 * 1024 < len(data) <= 40 * 1024 * 1024
    assert validate_course_file(data, "material.pdf") == "application/pdf"


def test_limites_existentes_por_rota_nao_mudam():
    from app.core.course_uploads import _COURSE_MAX_FILE_BYTES
    assert uploads.policy_for("POST", "/api/pacientes/1/exames-multimodais").max_file_bytes == 20 * 1024 * 1024
    assert uploads.policy_for("POST", "/api/documentos-cientificos-ia").max_file_bytes == 25 * 1024 * 1024
    assert _COURSE_MAX_FILE_BYTES == pdf.MAX_PDF_INPUT_BYTES == 40 * 1024 * 1024


def test_cancelamento_nao_libera_slot_nem_bloqueia_event_loop(monkeypatch):
    started, finish = threading.Event(), threading.Event()
    def waiting_child(*args, **kwargs):
        started.set()
        assert finish.wait(3), "synthetic test thread must be released"
        return subprocess.CompletedProcess(args, 0, b"ok\n")
    monkeypatch.setattr(pdf.subprocess, "run", waiting_child)

    async def scenario():
        first = asyncio.create_task(uploads.validate_file_async(_written(_writer()), "sintetico.pdf", "exam"))
        try:
            for _ in range(200):
                if started.is_set():
                    break
                await asyncio.sleep(0.005)
            assert started.is_set(), "loop progressed while inspection waited in its thread"
            first.cancel()
            with pytest.raises(asyncio.CancelledError):
                await first
            with pytest.raises(uploads.UploadRejected) as busy:
                await uploads.validate_file_async(b"x", "x.txt", "email")
            assert busy.value.status_code == 503
            # Synchronous callers also cannot launch a second child.
            with pytest.raises(pdf.PdfInspectionError, match="busy"):
                pdf.validate_pdf_structure(b"synthetic")
        finally:
            finish.set()
    asyncio.run(scenario())
    # asyncio.run drains its executor; both slots must now be reusable.
    assert asyncio.run(uploads.validate_file_async(b"texto", "x.txt", "email")) == "text/plain"
