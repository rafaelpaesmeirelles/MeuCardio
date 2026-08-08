from __future__ import annotations

from pathlib import Path
import hashlib
import unicodedata
from typing import Any

from PIL import Image, UnidentifiedImageError

from app.core.config import settings

PROFESSIONAL_TITLES = (
    "", "Sr.", "Sra.", "Dr.", "Dra.", "Prof.", "Profa.",
    "Prof. Dr.", "Profa. Dra.", "Me.", "Ma.", "Esp.",
)

COUNCILS = (
    "CRM", "CRO", "CRBM", "COREN", "CRF", "CREFITO", "CRN", "CRP",
    "CREF", "CRESS", "OUTRO",
)


def normalize_professional_title(value: str | None) -> str | None:
    value = (value or "").strip()
    if not value:
        return None
    if value not in PROFESSIONAL_TITLES:
        raise ValueError("Forma de tratamento inválida.")
    return value


def normalize_council(value: str | None) -> str | None:
    value = (value or "").strip().upper()
    if not value:
        return None
    if value == "OUTRO":
        return value
    if value not in COUNCILS:
        raise ValueError("Conselho profissional inválido.")
    return value


def council_display(source: Any) -> tuple[str | None, str | None]:
    """(nome do conselho, estado/região) para EXIBIÇÃO — nunca para decisão
    de escopo/permissão (isso continua sendo `user.council_name` literal,
    lido direto por `escopo_profissional.escopo_de()`). Quando
    `council_name == "OUTRO"`, troca pelo texto livre que o médico digitou
    no cadastro (`council_name_other`/`council_state_other`), se houver —
    sem isso, toda prescrição/documento de quem tem conselho "Outro"
    mostraria literalmente a palavra "OUTRO" em vez do conselho real."""
    getter = source.get if isinstance(source, dict) else lambda key, default=None: getattr(source, key, default)
    nome = getter("council_name")
    estado = getter("council_state")
    if (nome or "").strip().upper() == "OUTRO":
        nome = getter("council_name_other") or nome
        estado = getter("council_state_other") or estado
    return nome, estado


def normalize_search_text(value: str | None) -> str:
    """Normaliza busca parcial sem expor ou persistir uma segunda cópia do nome."""
    decomposed = unicodedata.normalize("NFKD", (value or "").strip().casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def professional_name(source: Any) -> str:
    getter = source.get if isinstance(source, dict) else lambda key, default=None: getattr(source, key, default)
    name = (getter("full_name") or "").strip()
    title = (getter("professional_title") or "").strip()
    return f"{title} {name}".strip()


def workplace_lines(source: Any) -> list[str]:
    getter = source.get if isinstance(source, dict) else lambda key, default=None: getattr(source, key, default)
    if not bool(getter("include_workplace_on_documents", False)):
        return []
    lines: list[str] = []
    name = (getter("workplace_name") or "").strip()
    department = (getter("workplace_department") or "").strip()
    role = (getter("workplace_role") or "").strip()
    notes = (getter("workplace_notes") or "").strip()
    if name:
        lines.append(name)
    detail = " · ".join(x for x in (department, role) if x)
    if detail:
        lines.append(detail)
    if notes:
        lines.append(notes)
    return lines


def logo_path(document_logo_url: str | None) -> Path | None:
    if not document_logo_url or not document_logo_url.startswith("/logos/"):
        return None
    name = Path(document_logo_url.removeprefix("/logos/")).name
    path = Path(settings.uploads_dir) / "logos" / name
    return path if path.is_file() else None


def logo_needs_dark_plate_path(path: Path | None) -> bool:
    if path is None:
        return False
    try:
        with Image.open(path) as original:
            image = original.convert("RGBA")
            image.thumbnail((128, 128))
            luminances: list[float] = []
            pixels = image.get_flattened_data() if hasattr(image, "get_flattened_data") else image.getdata()
            for red, green, blue, alpha in pixels:
                if alpha < 32:
                    continue
                luminances.append(0.2126 * red + 0.7152 * green + 0.0722 * blue)
    except (OSError, UnidentifiedImageError):
        return False
    if not luminances:
        return False
    luminances.sort()
    average = sum(luminances) / len(luminances)
    percentile_75 = luminances[int((len(luminances) - 1) * 0.75)]
    return average >= 185 or percentile_75 >= 225


def logo_needs_dark_plate(document_logo_url: str | None) -> bool:
    return logo_needs_dark_plate_path(logo_path(document_logo_url))


def rendered_logo_png(document_logo_url: str | None) -> Path | None:
    """Cria um derivado PNG com placa de contraste, sem alterar o upload original.

    O motor PDF leve usado em apresentações aceita PNG, enquanto o upload
    profissional também permite JPEG e WEBP. O cache é invalidado pelo nome,
    tamanho, mtime e decisão de contraste do arquivo original.
    """
    original = logo_path(document_logo_url)
    if original is None:
        return None
    dark = logo_needs_dark_plate_path(original)
    try:
        stat = original.stat()
        key = hashlib.sha256(
            f"{original.name}:{stat.st_size}:{stat.st_mtime_ns}:{int(dark)}".encode()
        ).hexdigest()[:20]
        cache_dir = original.parent / ".rendered"
        cache_dir.mkdir(parents=True, exist_ok=True)
        output = cache_dir / f"{key}.png"
        if output.is_file():
            return output

        with Image.open(original) as source:
            image = source.convert("RGBA")
            image.thumbnail((512, 256), Image.Resampling.LANCZOS)
            padding = 18
            background = (11, 46, 69, 255) if dark else (255, 255, 255, 255)
            canvas = Image.new(
                "RGBA",
                (max(1, image.width + 2 * padding), max(1, image.height + 2 * padding)),
                background,
            )
            canvas.alpha_composite(image, (padding, padding))
            temporary = output.with_suffix(".tmp.png")
            canvas.save(temporary, format="PNG", optimize=True)
            temporary.replace(output)
        return output
    except (OSError, UnidentifiedImageError):
        return None


def profile_payload(user: Any) -> dict:
    return {
        "professional_title": user.professional_title,
        "workplace_name": user.workplace_name,
        "workplace_department": user.workplace_department,
        "workplace_role": user.workplace_role,
        "workplace_notes": user.workplace_notes,
        "include_workplace_on_documents": user.include_workplace_on_documents,
        "profile_completion_required": user.profile_completion_required,
        "document_logo_dark_background": logo_needs_dark_plate(user.document_logo_url),
    }


def document_identity(user: Any) -> dict:
    nome_conselho, estado_conselho = council_display(user)
    return {
        "full_name": user.full_name,
        "professional_title": user.professional_title,
        "profession": user.profession,
        "council_name": nome_conselho,
        "council_number": user.council_number,
        "council_state": estado_conselho,
        "rqe": user.rqe,
        "specialty": user.specialty,
        "document_logo_url": user.document_logo_url,
        "document_logo_dark_background": logo_needs_dark_plate(user.document_logo_url),
        "workplace_name": user.workplace_name,
        "workplace_department": user.workplace_department,
        "workplace_role": user.workplace_role,
        "workplace_notes": user.workplace_notes,
        "include_workplace_on_documents": user.include_workplace_on_documents,
    }
