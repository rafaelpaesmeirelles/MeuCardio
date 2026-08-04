from __future__ import annotations

from pathlib import Path
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
    return {
        "full_name": user.full_name,
        "professional_title": user.professional_title,
        "profession": user.profession,
        "council_name": user.council_name,
        "council_number": user.council_number,
        "council_state": user.council_state,
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
