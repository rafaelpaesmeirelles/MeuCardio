"""Vínculos publicados portáveis entre os formatos de exportação."""
import re
from urllib.parse import quote, urljoin, urlsplit
from app.core.config import settings

MARKDOWN_LINK = re.compile(r"(?<!!)\[([^\]]+)\]\(([^\s)]+)\)")


def absolute_link(target: str) -> str | None:
    if target.startswith("/") and not target.startswith("//"):
        target = urljoin(settings.public_url.rstrip("/") + "/", target)
    try:
        parts = urlsplit(target)
    except ValueError:
        return None
    if parts.scheme not in {"http", "https"} or not parts.netloc or parts.username or parts.password:
        return None
    return quote(target, safe="/:?&=#%+@-._~!$'*,;")


def link_runs(text: str) -> list[tuple[str, str | None]]:
    """Texto visível e destino separados; jamais executa um destino do conteúdo."""
    runs = []
    start = 0
    for match in MARKDOWN_LINK.finditer(text):
        if match.start() > start:
            runs.append((text[start:match.start()], None))
        runs.append((match[1], absolute_link(match[2])))
        start = match.end()
    if start < len(text):
        runs.append((text[start:], None))
    return runs


def plain_text(text: str) -> str:
    return "".join(value for value, _ in link_runs(text))


def linked_lines(text: str, wrap):
    """Mantém o destino mesmo quando um rótulo atravessa linhas ou páginas."""
    runs = link_runs(re.sub(r"\s+", " ", text).strip())
    plain = "".join(value for value, _ in runs)
    spans = []
    offset = 0
    for value, url in runs:
        if url:
            spans.append((offset, offset + len(value), url))
        offset += len(value)
    cursor = 0
    for line in wrap(plain):
        start = plain.find(line, cursor)
        if start < 0:
            raise ValueError("A quebra de linha não preservou o texto do vínculo.")
        end = start + len(line)
        yield line, [(max(a, start) - start, min(b, end) - start, url) for a, b, url in spans if a < end and b > start]
        cursor = end


def fragment_linked(text: str, wrap) -> list[str]:
    fragments = []
    for line, spans in linked_lines(text, wrap):
        start = 0
        value = ""
        for a, b, url in spans:
            value += line[start:a] + f"[{line[a:b]}]({url})"
            start = b
        fragments.append(value + line[start:])
    return fragments
