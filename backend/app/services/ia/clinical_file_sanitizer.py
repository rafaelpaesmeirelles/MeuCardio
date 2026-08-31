"""Sanitização fail-closed de arquivos clínicos antes do processador externo."""
from __future__ import annotations

import io
import re
import shutil
import subprocess

import fitz
from PIL import Image, ImageOps

MAX_PDF_PAGES = 12
MAX_TOTAL_PIXELS = 60_000_000
MAX_SANITIZED_FILE_BYTES = 20 * 1024 * 1024
MAX_SANITIZED_BYTES = 40 * 1024 * 1024

IDENTIFIER_PATTERNS = (
    re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"),
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    re.compile(r"\b(?:\+?55\s*)?(?:\(?\d{2}\)?\s*)?9?\d{4}[-\s]?\d{4}\b"),
    re.compile(r"\b(?:nome|paciente|patient)\s*[:#-]?\s+[A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ'-]+(?:\s+(?:[A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ'-]+|da|de|do|das|dos|e)){1,6}\b", re.I),
    re.compile(r"\b(?:cpf|rg|prontu[aá]rio|registro|endere[cç]o|telefone|celular)\s*[:#]", re.I),
    re.compile(r"\b(?:MRN|CNS|medical\s+record|registro|prontu[aá]rio)\s*[:#-]?\s*\d{4,20}\b", re.I),
    re.compile(r"\b\d{15}\b"),
    re.compile(r"\b[A-ZÀ-ÖØ-Ý]{2,}(?:\s+(?:DA|DE|DO|DAS|DOS|E)\s+[A-ZÀ-ÖØ-Ý]{2,}){1,3}\b"),
    re.compile(r"\b(?:data\s+de\s+nascimento|nasc(?:imento)?\.?|dob)\s*[:#]?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", re.I),
)


class UnsafeClinicalFile(ValueError):
    pass


def contains_identifier(text: str) -> bool:
    return any(pattern.search(text) for pattern in IDENTIFIER_PATTERNS)


def _ocr(image_bytes: bytes) -> str:
    executable = shutil.which("tesseract")
    if not executable:
        raise UnsafeClinicalFile("A verificação local de identificadores em imagens está indisponível.")
    try:
        result = subprocess.run(
            [executable, "stdin", "stdout", "--psm", "11", "-l", "por+eng"],
            input=image_bytes, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            timeout=10, check=True,
        )
    except (subprocess.SubprocessError, OSError) as error:
        raise UnsafeClinicalFile("Não foi possível verificar identificadores visíveis no arquivo.") from error
    return result.stdout.decode("utf-8", errors="replace")[:100_000]


def _sanitize_image(content: bytes, *, run_ocr: bool = True) -> tuple[bytes, str]:
    try:
        with Image.open(io.BytesIO(content)) as source:
            source.load()
            source_format = (source.format or "").upper()
            image = ImageOps.exif_transpose(source).convert("RGB")
            output = io.BytesIO()
            if source_format == "PNG":
                image.save(output, format="PNG", optimize=True)
                media_type = "image/png"
            else:
                image.save(output, format="JPEG", quality=95, subsampling=0, optimize=True)
                media_type = "image/jpeg"
    except (OSError, ValueError) as error:
        raise UnsafeClinicalFile("Imagem clínica inválida.") from error
    sanitized = output.getvalue()
    if len(sanitized) > MAX_SANITIZED_FILE_BYTES:
        raise UnsafeClinicalFile("A imagem sanitizada excede o limite de 20 MB.")
    if run_ocr and contains_identifier(_ocr(sanitized)):
        raise UnsafeClinicalFile("A imagem parece conter identificador visível; recorte ou oculte o cabeçalho.")
    return sanitized, media_type


def _sanitize_pdf(content: bytes) -> bytes:
    try:
        source = fitz.open(stream=content, filetype="pdf")
    except Exception as error:
        raise UnsafeClinicalFile("PDF clínico inválido.") from error
    try:
        if source.page_count < 1 or source.page_count > MAX_PDF_PAGES:
            raise UnsafeClinicalFile(f"O PDF deve ter entre 1 e {MAX_PDF_PAGES} páginas.")
        output = fitz.open()
        total_pixels = 0
        for page in source:
            extracted = page.get_text("text")[:100_000]
            if contains_identifier(extracted):
                raise UnsafeClinicalFile("O PDF parece conter identificador; exporte uma cópia desidentificada.")
            # Aproximadamente 200 dpi: preserva grade/traçado fino de ECG sem
            # manter metadados, camadas, formulários ou anotações do PDF.
            pix = page.get_pixmap(matrix=fitz.Matrix(2.78, 2.78), alpha=False)
            total_pixels += pix.width * pix.height
            if total_pixels > MAX_TOTAL_PIXELS:
                raise UnsafeClinicalFile("O PDF excede o limite seguro de resolução total.")
            page_image = pix.tobytes("png")
            if contains_identifier(_ocr(page_image)):
                raise UnsafeClinicalFile("O PDF parece conter identificador visível; oculte o cabeçalho.")
            target = output.new_page(width=pix.width, height=pix.height)
            target.insert_image(target.rect, stream=page_image)
        sanitized = output.tobytes(garbage=4, deflate=True, clean=True)
        if len(sanitized) > MAX_SANITIZED_BYTES:
            raise UnsafeClinicalFile("O PDF sanitizado excede o limite de 40 MB.")
        return sanitized
    finally:
        source.close()
        if "output" in locals():
            output.close()


def sanitize_clinical_file(content: bytes, media_type: str) -> tuple[bytes, str]:
    if media_type.startswith("image/"):
        return _sanitize_image(content)
    if media_type == "application/pdf":
        return _sanitize_pdf(content), media_type
    if media_type in {"text/plain", "text/csv"}:
        text = content.decode("utf-8-sig")
        if contains_identifier(text):
            raise UnsafeClinicalFile("O arquivo de texto parece conter identificador direto.")
        return text.encode("utf-8"), media_type
    raise UnsafeClinicalFile("Formato clínico não suportado pelo sanitizador.")
