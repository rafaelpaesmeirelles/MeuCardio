from __future__ import annotations

import hashlib
import json
import logging
import re
import unicodedata
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, urlunsplit

from sqlalchemy.orm import Session

from app.models.guideline import Guideline, GuidelineNotification
from app.models.user import User
from app.services.notificar import tentar_enviar_email

log = logging.getLogger("meucardio.guideline_discovery")

CUTOFF = datetime(2026, 8, 10, tzinfo=timezone.utc)
USER_AGENT = "Corvia-Guideline-Monitor/1.0 (+https://corvia.med.br)"


@dataclass(frozen=True)
class Source:
    org: str
    index_url: str
    allowed_hosts: tuple[str, ...]


SOURCES = (
    Source(
        "ESC",
        "https://www.escardio.org/guidelines/clinical-practice-guidelines/all-esc-practice-guidelines/",
        ("escardio.org", "www.escardio.org"),
    ),
    Source(
        "ACC",
        "https://www.acc.org/guidelines",
        ("acc.org", "www.acc.org"),
    ),
    Source(
        "AHA",
        "https://professional.heart.org/en/guidelines-statements",
        ("professional.heart.org", "heart.org", "www.heart.org"),
    ),
    Source(
        "SBC",
        "https://www.portal.cardiol.br/diretrizes",
        ("portal.cardiol.br", "www.portal.cardiol.br", "abccardiol.org"),
    ),
)

KEYWORDS = (
    "guideline", "guidelines", "diretriz", "diretrizes", "focused update",
    "consensus", "statement", "posicionamento", "recommendation",
    "recomendacao", "recomendação",
)


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.anchors: list[tuple[str, str]] = []
        self.meta: dict[str, str] = {}
        self.times: list[str] = []
        self.title = ""
        self._href: str | None = None
        self._anchor_text: list[str] = []
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): (value or "") for key, value in attrs}
        if tag.lower() == "a" and values.get("href"):
            self._href = values["href"]
            self._anchor_text = []
        elif tag.lower() == "meta":
            key = (values.get("property") or values.get("name") or values.get("itemprop") or "").lower()
            content = values.get("content", "").strip()
            if key and content:
                self.meta[key] = content
        elif tag.lower() == "time" and values.get("datetime"):
            self.times.append(values["datetime"].strip())
        elif tag.lower() == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href:
            text = re.sub(r"\s+", " ", " ".join(self._anchor_text)).strip()
            if text:
                self.anchors.append((self._href, text))
            self._href = None
            self._anchor_text = []
        elif tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._href:
            self._anchor_text.append(data)
        if self._in_title:
            self.title += data


def _fetch(url: str, timeout: int = 35) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
            raise ValueError(f"Conteúdo não HTML em {url}")
        return response.read(3_000_000).decode("utf-8", errors="replace")


def _canonical(url: str) -> str | None:
    try:
        parsed = urlsplit(url)
    except ValueError:
        return None
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    if parsed.username or parsed.password:
        return None
    path = re.sub(r"/+", "/", parsed.path or "/")
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), path, "", ""))


def _candidate(source: Source, href: str, text: str) -> str | None:
    full = _canonical(urljoin(source.index_url, href))
    if not full:
        return None
    host = urlsplit(full).hostname or ""
    if host not in source.allowed_hosts:
        return None
    normalized = f"{text} {full}".casefold()
    if not any(keyword in normalized for keyword in KEYWORDS):
        return None
    if len(text.strip()) < 12:
        return None
    return full


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    value = value.strip()
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        pass
    for pattern in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(value, pattern).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def _date_published(html: str, parser: PageParser) -> datetime | None:
    for key in (
        "article:published_time", "datepublished", "date", "dc.date",
        "dc.date.issued", "publication_date", "publish-date",
    ):
        parsed = _parse_datetime(parser.meta.get(key))
        if parsed:
            return parsed
    for value in parser.times:
        parsed = _parse_datetime(value)
        if parsed:
            return parsed
    for match in re.finditer(r'"datePublished"\s*:\s*"([^"]+)"', html, flags=re.I):
        parsed = _parse_datetime(match.group(1))
        if parsed:
            return parsed
    return None


def _page_title(parser: PageParser, fallback: str) -> str:
    title = (
        parser.meta.get("og:title")
        or parser.meta.get("twitter:title")
        or parser.title
        or fallback
    )
    return re.sub(r"\s+", " ", title).strip()[:300]


def _slug(org: str, title: str, date: datetime) -> str:
    decomposed = unicodedata.normalize("NFKD", title.casefold())
    cleaned = "".join(char for char in decomposed if not unicodedata.combining(char))
    cleaned = re.sub(r"[^a-z0-9]+", "-", cleaned).strip("-")[:110]
    digest = hashlib.sha256(f"{org}:{title}:{date.date().isoformat()}".encode()).hexdigest()[:10]
    return f"{org.casefold()}-{date.year}-{cleaned}-{digest}"[:160]


def _fingerprint(org: str, url: str, title: str, published_at: datetime) -> str:
    canonical = f"{org}|{url}|{title}|{published_at.date().isoformat()}"
    return hashlib.sha256(canonical.encode()).hexdigest()


def _discover_source(source: Source, *, fetch=_fetch, max_details: int = 80) -> list[dict]:
    index_html = fetch(source.index_url)
    parser = PageParser()
    parser.feed(index_html)
    candidates: dict[str, str] = {}
    for href, text in parser.anchors:
        url = _candidate(source, href, text)
        if url:
            candidates.setdefault(url, text)

    discovered: list[dict] = []
    for url, fallback_title in list(candidates.items())[:max_details]:
        try:
            html = fetch(url)
            detail = PageParser()
            detail.feed(html)
            published_at = _date_published(html, detail)
            if published_at is None or published_at < CUTOFF:
                continue
            title = _page_title(detail, fallback_title)
            if not any(keyword in title.casefold() for keyword in KEYWORDS):
                continue
            discovered.append({
                "org": source.org,
                "title": title,
                "url": url,
                "published_at": published_at,
            })
        except Exception as error:  # coleta externa: uma página não derruba a fonte inteira
            log.warning("Falha ao inspecionar %s: %s", url, type(error).__name__)
    return discovered


def _ensure_notifications(db: Session, guideline: Guideline) -> tuple[int, int]:
    users = db.query(User).filter(User.is_active.is_(True)).all()
    created = emails_sent = 0
    now = datetime.now(timezone.utc)
    for user in users:
        in_app = db.query(GuidelineNotification).filter(
            GuidelineNotification.guideline_id == guideline.id,
            GuidelineNotification.user_id == user.id,
            GuidelineNotification.channel == "in_app",
        ).first()
        if in_app is None:
            db.add(GuidelineNotification(
                guideline_id=guideline.id,
                user_id=user.id,
                channel="in_app",
                status="disponivel",
                sent_at=now,
            ))
            created += 1

        email_delivery = db.query(GuidelineNotification).filter(
            GuidelineNotification.guideline_id == guideline.id,
            GuidelineNotification.user_id == user.id,
            GuidelineNotification.channel == "email",
        ).first()
        if email_delivery is not None:
            continue
        email_delivery = GuidelineNotification(
            guideline_id=guideline.id,
            user_id=user.id,
            channel="email",
            status="pendente",
        )
        db.add(email_delivery)
        db.flush()
        sent = tentar_enviar_email(
            destinatario=user.email,
            assunto=f"Corvia — nova diretriz oficial identificada ({guideline.org})",
            corpo=(
                f"A Corvia identificou uma nova publicação oficial em {guideline.published_at.strftime('%d/%m/%Y')}:\n\n"
                f"{guideline.titulo}\n{guideline.url}\n\n"
                "Este aviso confirma a publicação. O conteúdo clínico da plataforma permanece em revisão e não foi alterado automaticamente."
            ),
        )
        email_delivery.status = "enviado" if sent else "indisponivel"
        email_delivery.sent_at = now if sent else None
        email_delivery.error = None if sent else "Canal de e-mail indisponível."
        emails_sent += int(sent)
    guideline.alerta_enviado_em = now
    return created, emails_sent


def discover_and_publish(db: Session, *, fetch=_fetch) -> dict:
    """Descobre publicações oficiais, cria alertas factuais e não altera conteúdo clínico."""
    discovered: list[dict] = []
    failures: list[str] = []
    for source in SOURCES:
        try:
            discovered.extend(_discover_source(source, fetch=fetch))
        except Exception as error:
            log.exception("Falha na fonte %s", source.org)
            failures.append(f"{source.org}:{type(error).__name__}")

    created = updated = in_app = emails = 0
    for item in discovered:
        fingerprint = _fingerprint(
            item["org"], item["url"], item["title"], item["published_at"]
        )
        guideline = db.query(Guideline).filter(
            Guideline.source_fingerprint == fingerprint
        ).first()
        if guideline is None:
            guideline = db.query(Guideline).filter(Guideline.url == item["url"]).first()
        if guideline is None:
            guideline = Guideline(
                slug=_slug(item["org"], item["title"], item["published_at"]),
                org=item["org"],
                titulo=item["title"],
                ano=item["published_at"].year,
                url=item["url"],
                published_at=item["published_at"],
                source_fingerprint=fingerprint,
                detection_status="aguardando_revisao",
            )
            db.add(guideline)
            db.flush()
            created += 1
        else:
            guideline.published_at = guideline.published_at or item["published_at"]
            guideline.source_fingerprint = guideline.source_fingerprint or fingerprint
            guideline.url = guideline.url or item["url"]
            if guideline.detection_status == "manual":
                guideline.detection_status = "aguardando_revisao"
            updated += 1

        new_in_app, new_emails = _ensure_notifications(db, guideline)
        in_app += new_in_app
        emails += new_emails

    db.commit()
    return {
        "cutoff": CUTOFF.date().isoformat(),
        "candidates_with_official_date": len(discovered),
        "created": created,
        "updated": updated,
        "in_app_notifications": in_app,
        "emails_sent": emails,
        "source_failures": failures,
        "clinical_content_changed": False,
    }
