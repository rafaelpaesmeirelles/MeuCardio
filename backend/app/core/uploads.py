"""Validação central de uploads antes dos routers FastAPI.

A aplicação recebe uploads com perfis de risco distintos: imagem de perfil,
exames clínicos, documentos científicos privados, anexos de e-mail e materiais
de fluxos especializados. Esta camada limita o body antes que um endpoint faça
``await arquivo.read()``, valida o conteúdo real e reproduz o mesmo body para o
parser multipart da rota.

Não é antivírus. A defesa é reduzir a superfície permitida: imagens realmente
decodificáveis, PDF sem recursos ativos conhecidos e documentos Office Open
XML sem macros/objetos incorporados.
"""

from __future__ import annotations

import io
import os
import re
import tempfile
import unicodedata
import warnings
import zipfile
from dataclasses import dataclass
from email import policy
from email.parser import BytesParser
from hashlib import sha256
from pathlib import Path
from typing import Awaitable, Callable

from PIL import Image, UnidentifiedImageError
from redis.asyncio import Redis
from redis.exceptions import RedisError
from starlette.datastructures import Headers
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.config import settings
from app.core.runtime import ambiente_atual

_CHUNK_OVERHEAD = 512 * 1024
_MAX_IMAGE_PIXELS = 25_000_000
_UPLOAD_LIMIT = 20
_UPLOAD_WINDOW_SECONDS = 600

_RATE_SCRIPT = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then redis.call('EXPIRE', KEYS[1], ARGV[1]) end
local ttl = redis.call('TTL', KEYS[1])
return {current, ttl}
"""


@dataclass(frozen=True)
class UploadPolicy:
    name: str
    max_file_bytes: int
    kind: str
    max_files: int = 1
    max_total_file_bytes: int | None = None
    min_files: int = 1


_IMAGE_POLICY = UploadPolicy("imagem-perfil", 3 * 1024 * 1024, "image")
_EXAM_POLICY = UploadPolicy("exame", 20 * 1024 * 1024, "exam")
_CARDIOVASCULAR_EXAM_POLICY = UploadPolicy(
    "exame-cardiovascular",
    20 * 1024 * 1024,
    "clinical_exam",
    max_files=5,
    max_total_file_bytes=40 * 1024 * 1024,
    min_files=0,
)
_PATIENT_MULTIMODAL_EXAM_POLICY = UploadPolicy(
    "exame-prontuario-multimodal",
    20 * 1024 * 1024,
    "clinical_exam",
)
_SCIENTIFIC_DOCUMENT_POLICY = UploadPolicy(
    "documento-cientifico-privado",
    25 * 1024 * 1024,
    "email",
)
_HEART_TEAM_POLICY = UploadPolicy(
    "heart-team",
    20 * 1024 * 1024,
    "clinical_exam",
    max_files=5,
    max_total_file_bytes=40 * 1024 * 1024,
)
_EMAIL_POLICY = UploadPolicy("anexo-email", 15 * 1024 * 1024, "email")


class UploadRejected(ValueError):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def policy_for(method: str, path: str) -> UploadPolicy | None:
    if method != "POST":
        return None
    if path in {"/api/auth/me/foto", "/api/auth/me/logo"}:
        return _IMAGE_POLICY
    if re.fullmatch(r"/api/pedidos/\d+/exame", path):
        return _EXAM_POLICY
    if re.fullmatch(r"/api/pacientes/\d+/ecgs", path) or path == "/api/ecg-ia/analisar":
        return _EXAM_POLICY
    if re.fullmatch(r"/api/pacientes/\d+/exames-multimodais", path):
        return _PATIENT_MULTIMODAL_EXAM_POLICY
    if path == "/api/exames-ia/analisar":
        return _CARDIOVASCULAR_EXAM_POLICY
    if path == "/api/documentos-cientificos-ia":
        return _SCIENTIFIC_DOCUMENT_POLICY
    if re.fullmatch(r"/api/heart-team/cases/\d+/attachments", path):
        return _HEART_TEAM_POLICY
    if path == "/api/email/mensagens/anexos" or re.fullmatch(
        r"/api/email/externas/corvia-\d+/mensagens/anexos(?:/verificar-assinatura)?",
        path,
    ):
        return _EMAIL_POLICY
    return None


def safe_filename(value: str | None, fallback: str = "arquivo") -> str:
    """Nome de exibição sem caminhos, controles ou metacaracteres de header."""
    raw = unicodedata.normalize("NFKC", value or "").strip()
    if not raw:
        return fallback
    if any(ord(char) < 32 or ord(char) == 127 for char in raw):
        raise UploadRejected(422, "Nome do arquivo contém caracteres de controle.")
    if any(char in raw for char in ('/', '\\', '"', "\x00")):
        raise UploadRejected(422, "Nome do arquivo contém caracteres não permitidos.")

    # Limita por caracteres, preservando acentos usuais e a extensão.
    raw = re.sub(r"\s+", " ", raw).strip(" .")
    if not raw:
        return fallback
    if len(raw) > 180:
        stem = Path(raw).stem[:140].rstrip(" .") or fallback
        suffix = Path(raw).suffix[:20]
        raw = f"{stem}{suffix}"
    return raw


def _verify_image(data: bytes, filename: str) -> str:
    signatures = {
        "JPEG": (b"\xff\xd8\xff", {".jpg", ".jpeg"}),
        "PNG": (b"\x89PNG\r\n\x1a\n", {".png"}),
        "WEBP": (b"RIFF", {".webp"}),
    }
    suffix = Path(filename).suffix.lower()

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            Image.MAX_IMAGE_PIXELS = _MAX_IMAGE_PIXELS
            with Image.open(io.BytesIO(data)) as image:
                image.verify()
            with Image.open(io.BytesIO(data)) as image:
                fmt = image.format
                width, height = image.size
                frames = getattr(image, "n_frames", 1)
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise UploadRejected(422, "A imagem está corrompida ou não é um formato aceito.") from None

    if fmt not in signatures:
        raise UploadRejected(422, "Envie uma imagem JPEG, PNG ou WEBP.")
    signature, suffixes = signatures[fmt]
    if not data.startswith(signature) or (fmt == "WEBP" and data[8:12] != b"WEBP"):
        raise UploadRejected(422, "A assinatura do arquivo não corresponde à imagem.")
    if suffix and suffix not in suffixes:
        raise UploadRejected(422, "A extensão não corresponde ao conteúdo da imagem.")
    if width <= 0 or height <= 0 or width * height > _MAX_IMAGE_PIXELS:
        raise UploadRejected(422, "A imagem excede o limite de 25 megapixels.")
    if frames != 1:
        raise UploadRejected(422, "Imagens animadas não são aceitas.")
    return {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}[fmt]


def _verify_pdf(data: bytes, filename: str) -> str:
    if not data.startswith(b"%PDF-") or b"%%EOF" not in data[-4096:]:
        raise UploadRejected(422, "O PDF está incompleto ou possui assinatura inválida.")
    if Path(filename).suffix.lower() not in {"", ".pdf"}:
        raise UploadRejected(422, "A extensão não corresponde ao conteúdo PDF.")

    # Recursos ativos não são necessários para ECG, Holter, MAPA ou documentos
    # anexados e ampliam desnecessariamente o risco no visualizador do usuário.
    active_markers = (b"/JavaScript", b"/JS", b"/Launch", b"/EmbeddedFile", b"/RichMedia")
    if any(marker in data for marker in active_markers):
        raise UploadRejected(422, "PDF com scripts ou conteúdo incorporado não é aceito.")
    return "application/pdf"


def _verify_ooxml(data: bytes, filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    expected_root = {".docx": "word/", ".xlsx": "xl/", ".pptx": "ppt/"}.get(suffix)
    if expected_root is None:
        raise UploadRejected(422, "Formato de documento não permitido.")
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            infos = archive.infolist()
            names = {info.filename for info in infos}
            if "[Content_Types].xml" not in names or not any(name.startswith(expected_root) for name in names):
                raise UploadRejected(422, "Documento Office inválido ou com extensão divergente.")
            if len(infos) > 2000:
                raise UploadRejected(422, "Documento compactado contém arquivos demais.")

            total_uncompressed = 0
            for info in infos:
                name = info.filename.replace("\\", "/")
                if name.startswith("/") or "../" in f"/{name}":
                    raise UploadRejected(422, "Documento compactado contém caminho inseguro.")
                if info.flag_bits & 0x1:
                    raise UploadRejected(422, "Documento Office protegido por senha não é aceito.")
                lower = name.lower()
                if lower.endswith("vbaproject.bin") or "/activex/" in lower or "/embeddings/" in lower:
                    raise UploadRejected(422, "Documento Office com macro ou objeto incorporado não é aceito.")
                total_uncompressed += info.file_size
                if total_uncompressed > 100 * 1024 * 1024:
                    raise UploadRejected(422, "Documento compactado expande além do limite seguro.")
                if info.compress_size and info.file_size / info.compress_size > 200:
                    raise UploadRejected(422, "Documento possui taxa de compactação suspeita.")
    except zipfile.BadZipFile:
        raise UploadRejected(422, "Documento Office corrompido.") from None

    return {
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }[suffix]


def _verify_text(data: bytes, filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in {".txt", ".csv"}:
        raise UploadRejected(422, "Formato de texto não permitido.")
    if b"\x00" in data:
        raise UploadRejected(422, "Arquivo de texto contém conteúdo binário.")
    try:
        data.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise UploadRejected(422, "Arquivo de texto precisa estar em UTF-8.") from None
    return "text/csv" if suffix == ".csv" else "text/plain"


def validate_file(data: bytes, filename: str, kind: str) -> str:
    if not data:
        raise UploadRejected(422, "Arquivo vazio.")
    filename = safe_filename(filename)

    if kind == "image":
        return _verify_image(data, filename)
    if kind == "exam":
        return _verify_pdf(data, filename) if data.startswith(b"%PDF-") else _verify_image(data, filename)
    if kind == "clinical_exam":
        suffix = Path(filename).suffix.lower()
        if data.startswith(b"%PDF-"):
            return _verify_pdf(data, filename)
        if data.startswith((b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"RIFF")):
            return _verify_image(data, filename)
        if suffix in {".txt", ".csv"}:
            return _verify_text(data, filename)
        raise UploadRejected(
            422,
            "Anexe PDF, JPEG, PNG, WEBP, TXT ou CSV. DICOM, vídeo, DOCX e XLSX ainda não são aceitos.",
        )
    if kind != "email":
        raise UploadRejected(500, "Política de upload desconhecida.")

    suffix = Path(filename).suffix.lower()
    if data.startswith(b"%PDF-"):
        return _verify_pdf(data, filename)
    if data.startswith((b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"RIFF")):
        return _verify_image(data, filename)
    if data.startswith(b"PK\x03\x04"):
        return _verify_ooxml(data, filename)
    if suffix in {".txt", ".csv"}:
        return _verify_text(data, filename)
    raise UploadRejected(422, "Anexe PDF, JPEG, PNG, WEBP, DOCX, XLSX, PPTX, TXT ou CSV.")


def _parse_files(body: bytes, content_type: str) -> list[tuple[str, bytes]]:
    message = BytesParser(policy=policy.default).parsebytes(
        b"Content-Type: " + content_type.encode("latin-1") + b"\r\nMIME-Version: 1.0\r\n\r\n" + body
    )
    files: list[tuple[str, bytes]] = []
    if not message.is_multipart():
        raise UploadRejected(422, "Corpo multipart inválido.")
    for part in message.iter_parts():
        if part.get_content_disposition() != "form-data" or part.get_filename() is None:
            continue
        payload = part.get_payload(decode=True)
        files.append((safe_filename(part.get_filename()), payload or b""))
    return files


def _parse_single_file(body: bytes, content_type: str) -> tuple[str, bytes]:
    """Preserva o contrato dos fluxos legados que aceitam um único anexo."""
    files = _parse_files(body, content_type)
    if len(files) != 1:
        raise UploadRejected(422, "Envie exatamente um arquivo por requisição.")
    return files[0]


def _client_key(scope: Scope, headers: Headers, policy_name: str) -> str:
    forwarded = headers.get("x-forwarded-for")
    if forwarded:
        ip = forwarded.split(",")[-1].strip()
    else:
        client = scope.get("client")
        ip = str(client[0]) if client else "desconhecido"
    digest = sha256(ip.encode("utf-8")).hexdigest()[:24]
    return f"corvia:upload:{policy_name}:{digest}"


async def _read_and_validate(scope: Scope, receive: Receive, headers: Headers, upload_policy: UploadPolicy) -> Receive:
    content_type = headers.get("content-type", "")
    if not content_type.lower().startswith("multipart/form-data;"):
        raise UploadRejected(415, "O upload precisa usar multipart/form-data.")

    max_total = upload_policy.max_total_file_bytes or upload_policy.max_file_bytes
    max_body = max_total + _CHUNK_OVERHEAD
    raw_length = headers.get("content-length")
    if raw_length:
        try:
            if int(raw_length) > max_body:
                raise UploadRejected(413, f"Os arquivos excedem o limite total de {max_total // 1048576} MB.")
        except ValueError:
            raise UploadRejected(400, "Content-Length inválido.") from None

    chunks: list[bytes] = []
    total = 0
    while True:
        message = await receive()
        if message["type"] == "http.disconnect":
            raise UploadRejected(400, "Upload interrompido pelo cliente.")
        if message["type"] != "http.request":
            continue
        chunk = message.get("body", b"")
        total += len(chunk)
        if total > max_body:
            raise UploadRejected(413, f"Os arquivos excedem o limite total de {max_total // 1048576} MB.")
        chunks.append(chunk)
        if not message.get("more_body", False):
            break

    body = b"".join(chunks)
    files = _parse_files(body, content_type)
    if len(files) < upload_policy.min_files:
        raise UploadRejected(422, "Envie ao menos um arquivo por requisição.")
    if len(files) > upload_policy.max_files:
        raise UploadRejected(422, f"Envie no máximo {upload_policy.max_files} arquivos por requisição.")
    if sum(len(file_data) for _, file_data in files) > max_total:
        raise UploadRejected(413, f"Os arquivos excedem o limite total de {max_total // 1048576} MB.")
    for filename, file_data in files:
        if len(file_data) > upload_policy.max_file_bytes:
            raise UploadRejected(
                413,
                f"Cada arquivo precisa ter no máximo {upload_policy.max_file_bytes // 1048576} MB.",
            )
        validate_file(file_data, filename, upload_policy.kind)

    delivered = False

    async def replay() -> Message:
        nonlocal delivered
        if delivered:
            return {"type": "http.request", "body": b"", "more_body": False}
        delivered = True
        return {"type": "http.request", "body": body, "more_body": False}

    return replay


class UploadSecurityMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        *,
        force_enabled: bool | None = None,
        redis_client: Redis | None = None,
    ) -> None:
        self.app = app
        self.force_enabled = force_enabled
        self.redis = redis_client or Redis.from_url(settings.redis_url, decode_responses=True)

    @property
    def enabled(self) -> bool:
        return self.force_enabled if self.force_enabled is not None else ambiente_atual() == "production"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not self.enabled:
            await self.app(scope, receive, send)
            return

        method = str(scope.get("method", "GET")).upper()
        path = str(scope.get("path", ""))
        upload_policy = policy_for(method, path)
        if upload_policy is None:
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        key = _client_key(scope, headers, upload_policy.name)
        try:
            current, ttl = await self.redis.eval(_RATE_SCRIPT, 1, key, _UPLOAD_WINDOW_SECONDS)
            current, ttl = int(current), max(int(ttl), 1)
        except (RedisError, OSError, TypeError, ValueError):
            response = JSONResponse(
                {"detail": "Proteção de upload temporariamente indisponível."},
                status_code=503,
                headers={"Retry-After": "5"},
            )
            await response(scope, receive, send)
            return
        if current > _UPLOAD_LIMIT:
            response = JSONResponse(
                {"detail": "Muitos uploads. Aguarde antes de tentar novamente."},
                status_code=429,
                headers={"Retry-After": str(ttl)},
            )
            await response(scope, receive, send)
            return

        try:
            replay = await _read_and_validate(scope, receive, headers, upload_policy)
        except UploadRejected as error:
            response = JSONResponse({"detail": error.detail}, status_code=error.status_code)
            await response(scope, receive, send)
            return

        await self.app(scope, replay, send)


def atomic_write_bytes(directory: Path, filename: str, data: bytes, mode: int = 0o600) -> Path:
    """Grava no mesmo filesystem, sincroniza e publica com ``os.replace``."""
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / filename
    if destination.resolve().parent != directory.resolve():
        raise ValueError("Destino de arquivo fora do diretório permitido.")

    fd, temporary = tempfile.mkstemp(prefix=".upload-", suffix=".tmp", dir=directory)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
        os.chmod(destination, mode)
        return destination
    except Exception:
        try:
            os.close(fd)
        except OSError:
            pass
        Path(temporary).unlink(missing_ok=True)
        raise
