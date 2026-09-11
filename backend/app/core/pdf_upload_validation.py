"""Bounded, read-only PDF inspection in a disposable child process.

The 40 MiB input ceiling preserves the largest existing route (course
materials); callers retain their smaller 8/15/20/25 MiB upload limits.
Structural inspection is limited to 32 revisions, 50,000 object versions,
500,000 graph nodes and 50 MiB of decoded xref/object streams. Image, font
and page-content streams are not decoded. The process-wide 512 MiB address
space / 4 CPU seconds / 8 wall seconds also bound parser construction and
individual decompression allocations before those structural checks run.
Only one child is admitted per backend process; occupied callers fail with
503 rather than queueing more PDF bytes. Platforms without a genuine hard
address-space limit (including Darwin's RSS alias) fail explicitly with 503.

No network operations, credentials, user files or document-content logging.
This is resource isolation, NOT an OS network sandbox. pyHanko remains the
existing pinned parser; its global classes/decoders are never patched.
"""

from __future__ import annotations

import io
import os
import subprocess
import sys
import threading
from pathlib import Path

MAX_PDF_INPUT_BYTES = 40 * 1024 * 1024
MAX_PDF_STRUCTURAL_BYTES = 50 * 1024 * 1024
MAX_PDF_REVISIONS = 32
MAX_PDF_OBJECTS = 50_000
MAX_PDF_NODES = MAX_PDF_OBJECTS * 10
PDF_MEMORY_BYTES = 512 * 1024 * 1024
PDF_CPU_SECONDS = 4
PDF_WALL_SECONDS = 8
_PDF_SLOTS = threading.BoundedSemaphore(1)

PDF_REJECTIONS = {
    "active": (422, "PDF com scripts ou conteúdo incorporado não é aceito."),
    "encrypted": (422, "PDF protegido por senha ou criptografado não é aceito."),
    "malformed": (422, "O PDF está malformado ou não pôde ser validado com segurança."),
    "limits": (422, "O PDF excede os limites de complexidade ou processamento seguro."),
    "too_large": (413, "O PDF excede o limite máximo de 40 MB."),
    "unavailable": (503, "A validação segura de PDF está indisponível nesta plataforma."),
    "busy": (503, "A validação de PDF está ocupada. Tente novamente em instantes."),
}


class PdfInspectionError(ValueError):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


def validate_pdf_structure(data: bytes) -> None:
    if len(data) > MAX_PDF_INPUT_BYTES:
        raise PdfInspectionError("too_large")
    if not _PDF_SLOTS.acquire(blocking=False):
        raise PdfInspectionError("busy")
    try:
        _run_isolated(data)
    finally:
        # Released by this synchronous worker only AFTER the child has exited.
        _PDF_SLOTS.release()


def _run_isolated(data: bytes) -> None:
    try:
        result = subprocess.run(
            [sys.executable, "-I", "-B", "-X", "utf8", str(Path(__file__).resolve())],
            input=data,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=PDF_WALL_SECONDS,
            check=False,
            close_fds=True,
            env={"PATH": os.defpath},
        )
    except subprocess.TimeoutExpired:
        raise PdfInspectionError("limits") from None
    except (OSError, subprocess.SubprocessError):
        raise PdfInspectionError("unavailable") from None
    if result.returncode == 0 and result.stdout == b"ok\n":
        return
    reason = result.stdout.decode("ascii", errors="replace").strip()
    if result.returncode not in {1, 2} or reason not in PDF_REJECTIONS:
        reason = "limits" if result.returncode < 0 else "unavailable"
    raise PdfInspectionError(reason)


def _apply_resource_limits() -> None:
    # Set limits in the child, never preexec_fn or process-global parent state.
    try:
        import resource

        # Darwin aliases AS to RSS: that is not an address-space hard limit.
        if resource.RLIMIT_AS == getattr(resource, "RLIMIT_RSS", None):
            raise PdfInspectionError("unavailable")
        limits = (
            (resource.RLIMIT_AS, PDF_MEMORY_BYTES),
            (resource.RLIMIT_CPU, PDF_CPU_SECONDS),
            (resource.RLIMIT_FSIZE, 0),
            (resource.RLIMIT_CORE, 0),
        )
        for kind, maximum in limits:
            _soft, hard = resource.getrlimit(kind)
            if hard != resource.RLIM_INFINITY:
                maximum = min(maximum, hard)
            resource.setrlimit(kind, (maximum, maximum))
    except (ImportError, AttributeError, OSError, ValueError):
        raise PdfInspectionError("unavailable") from None


def _inspect_pdf_structure(data: bytes) -> None:
    from pyhanko.pdf_utils import generic
    from pyhanko.pdf_utils.reader import PdfFileReader

    active_names = {
        "/JavaScript", "/JS", "/Launch", "/EmbeddedFile", "/EmbeddedFiles",
        "/RichMedia", "/RichMediaContent", "/RichMediaSettings",
        "/AA", "/OpenAction", "/XFA",
    }
    reader = PdfFileReader(io.BytesIO(data), strict=True)
    if reader.total_revisions > MAX_PDF_REVISIONS:
        raise PdfInspectionError("limits")
    if "/Encrypt" in reader.trailer_view:
        raise PdfInspectionError("encrypted")
    if reader.root.get("/Type") != "/Catalog":
        raise PdfInspectionError("malformed")
    pages = reader.root["/Pages"]
    if pages.get("/Type") != "/Pages" or int(pages["/Count"]) < 1:
        raise PdfInspectionError("malformed")

    object_count = node_count = structural_bytes = 0
    # Include historical and orphaned objects, not only the current catalog.
    for revision in range(reader.total_revisions):
        resolver = reader.get_historical_resolver(revision)
        if "/Encrypt" in resolver.trailer_view:
            raise PdfInspectionError("encrypted")
        references = resolver.explicit_refs_in_revision() - resolver.refs_freed_in_revision()
        object_count += len(references)
        if object_count > MAX_PDF_OBJECTS:
            raise PdfInspectionError("limits")
        pending = [resolver.trailer_view]
        pending.extend(generic.IndirectObject(ref.idnum, ref.generation, resolver) for ref in references)
        seen_references: set[tuple[int, int]] = set()
        seen_containers: set[int] = set()
        while pending:
            node_count += 1
            if node_count > MAX_PDF_NODES:
                raise PdfInspectionError("limits")
            obj = pending.pop()
            if isinstance(obj, generic.IndirectObject):
                identity = (obj.idnum, obj.generation)
                if identity not in seen_references:
                    seen_references.add(identity)
                    pending.append(resolver.get_object(obj.reference))
            elif isinstance(obj, generic.NameObject):
                if obj in active_names:
                    raise PdfInspectionError("active")
            elif isinstance(obj, (generic.DictionaryObject, generic.ArrayObject)):
                if id(obj) in seen_containers:
                    continue
                seen_containers.add(id(obj))
                if isinstance(obj, generic.StreamObject) and obj.get("/Type") in {"/ObjStm", "/XRef"}:
                    # Hard process limits already protect this allocation.
                    structural_bytes += len(obj.data)
                    if structural_bytes > MAX_PDF_STRUCTURAL_BYTES:
                        raise PdfInspectionError("limits")
                    if obj.get("/Type") == "/ObjStm" and int(obj["/N"]) > MAX_PDF_OBJECTS:
                        raise PdfInspectionError("limits")
                if isinstance(obj, generic.DictionaryObject):
                    pending.extend(obj.keys())
                    pending.extend(obj.values())
                else:
                    pending.extend(obj)


def _worker() -> int:
    try:
        _apply_resource_limits()
        data = sys.stdin.buffer.read(MAX_PDF_INPUT_BYTES + 1)
        if len(data) > MAX_PDF_INPUT_BYTES:
            raise PdfInspectionError("too_large")
        _inspect_pdf_structure(data)
        reason = "ok"
    except PdfInspectionError as error:
        reason = error.reason
    except MemoryError:
        reason = "limits"
    except Exception:
        reason = "malformed"
    # Only an allowlisted code leaves the child, never a parser traceback.
    sys.stdout.write(reason + "\n")
    return 0 if reason == "ok" else 2 if reason == "unavailable" else 1


if __name__ == "__main__":
    raise SystemExit(_worker())
