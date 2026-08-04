#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    (ROOT / path).write_text(content, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    source = read(path)
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: esperado 1 trecho, encontrado {count}: {old[:100]!r}")
    write(path, source.replace(old, new, 1))


# Render derivado PNG para o motor PDF stdlib, que aceita PNG mas não JPEG/WEBP.
replace_once(
    "backend/app/services/professional_profile.py",
    '''from pathlib import Path
import unicodedata
''',
    '''from pathlib import Path
import hashlib
import unicodedata
''',
)
replace_once(
    "backend/app/services/professional_profile.py",
    '''def logo_needs_dark_plate(document_logo_url: str | None) -> bool:
    return logo_needs_dark_plate_path(logo_path(document_logo_url))


def profile_payload(user: Any) -> dict:
''',
    '''def logo_needs_dark_plate(document_logo_url: str | None) -> bool:
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
''',
)

# A capa da apresentação aceita a logo profissional já normalizada como PNG.
replace_once(
    "backend/app/services/pdf/layout.py",
    '''    def capa(self, titulo: str, subtitulo: str, autor: str, registro: str) -> None:
        self.pdf.nova_pagina()
''',
    '''    def capa(
        self, titulo: str, subtitulo: str, autor: str, registro: str,
        logo_profissional: str | None = None,
    ) -> None:
        self.pdf.nova_pagina()
''',
)
replace_once(
    "backend/app/services/pdf/layout.py",
    '''        self._logo(self.margem, self.altura - 58, 160)

        y = self.altura - 230
''',
    '''        self._logo(self.margem, self.altura - 58, 160)
        if logo_profissional:
            try:
                nome_logo = "LogoProfissional"
                self.pdf.imagem(nome_logo, logo_profissional, 0, 0, 0, 0)
                self.pdf.atual.pop()
                imagem = self.pdf.imagens[nome_logo]
                largura_logo = 132.0
                altura_logo = largura_logo * imagem["altura"] / max(1, imagem["largura"])
                if altura_logo > 82.0:
                    altura_logo = 82.0
                    largura_logo = altura_logo * imagem["largura"] / max(1, imagem["altura"])
                self.pdf.imagem(
                    nome_logo, logo_profissional,
                    self.largura - self.margem - largura_logo,
                    self.altura - 48 - altura_logo,
                    largura_logo, altura_logo,
                )
            except (OSError, ValueError):
                pass

        y = self.altura - 230
''',
)

# Identidade centralizada na apresentação.
replace_once(
    "backend/app/services/apresentacao.py",
    '''from app.models.content import Document

from .pdf import Apresentacao
''',
    '''from app.models.content import Document
from app.services.professional_profile import (
    professional_name, rendered_logo_png, workplace_lines,
)

from .pdf import Apresentacao
''',
)
replace_once(
    "backend/app/services/apresentacao.py",
    '''    nome = (medico.get("full_name") or "").strip()
    registro = " · ".join(
        p for p in (
            " ".join(x for x in (medico.get("council_name"), medico.get("council_number")) if x),
            f"RQE {medico['rqe']}" if medico.get("rqe") else "",
        ) if p
    )
''',
    '''    nome = professional_name(medico)
    conselho = " ".join(
        x for x in (
            medico.get("council_name"), medico.get("council_number"),
            medico.get("council_state"),
        ) if x
    )
    registro = " · ".join(
        p for p in (
            conselho,
            f"RQE {medico['rqe']}" if medico.get("rqe") else "",
            *workplace_lines(medico),
        ) if p
    )
    logo_profissional = rendered_logo_png(medico.get("document_logo_url"))
''',
)
replace_once(
    "backend/app/services/apresentacao.py",
    '''    a.capa(doc.title, doc.summary or "", nome, registro)
''',
    '''    a.capa(
        doc.title, doc.summary or "", nome, registro,
        logo_profissional=str(logo_profissional) if logo_profissional else None,
    )
''',
)

# Amplia o gate de auditoria para o exportador de apresentações.
replace_once(
    "backend/tests/test_identidade_documentos_audit.py",
    '''        "app/services/receita_controle_especial.py": ("logo_path", "logo_needs_dark_plate_path"),
''',
    '''        "app/services/receita_controle_especial.py": ("logo_path", "logo_needs_dark_plate_path"),
        "app/services/apresentacao.py": ("rendered_logo_png", "professional_name"),
''',
)

Path(__file__).unlink()
print("Identidade e logo profissional aplicadas ao modo apresentação.")
