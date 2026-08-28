from __future__ import annotations

import hashlib
import logging
import re
import unicodedata
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, urlunsplit

from sqlalchemy.orm import Session

from app.models.guideline import Guideline, GuidelineNotification
from app.models.user import User
from app.services.notificar import tentar_enviar_email

log = logging.getLogger("meucardio.guideline_discovery")

DISCOVERY_START = datetime(2026, 8, 10, tzinfo=timezone.utc)
DISCOVERY_LOOKBACK_DAYS = 45
USER_AGENT = "Corvia-Intelligence/2.0 (+https://corvia.med.br)"

GUIDANCE_KEYWORDS = (
    "guideline", "guidelines", "diretriz", "diretrizes", "focused update",
    "consensus", "statement", "posicionamento", "recommendation",
    "recomendacao", "recomendação", "universal definition", "definition",
    "position paper", "core curriculum", "curriculum",
)

ARTICLE_PATH_MARKERS = (
    "/article/", "/advance-article/doi/", "/article-lookup/doi/",
)

DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.IGNORECASE)


@dataclass(frozen=True)
class Source:
    org: str
    index_url: str
    allowed_hosts: tuple[str, ...]
    keywords: tuple[str, ...] = GUIDANCE_KEYWORDS
    accept_all_articles: bool = False
    max_details: int = 80


SOURCES = (
    Source(
        "ESC",
        "https://www.escardio.org/guidelines/clinical-practice-guidelines/all-esc-practice-guidelines/",
        (
            "escardio.org", "www.escardio.org",
            "corporate-prod.dxc.escardio.org",
        ),
    ),
    # Coleção oficial OUP/ESC: garante captura da publicação primária, DOI e data.
    Source(
        "ESC",
        "https://academic.oup.com/eurheartj/pages/esc_guidelines",
        ("academic.oup.com",),
        max_details=100,
    ),
    # Hub oficial de publicações simultâneas do ESC Congress. É uma coleção
    # editorial curada; por isso artigos do hub são aceitos mesmo sem a palavra
    # "guideline" no título. A página é atualizada ao longo do congresso.
    Source(
        "ESC",
        "https://academic.oup.com/esc/pages/2026-simultaneous-publications",
        ("academic.oup.com",),
        accept_all_articles=True,
        max_details=220,
    ),
    # Advance Articles do EHJ captura statements/curriculum publicados fora do
    # hub simultâneo, mantendo filtro estrito por tipo documental de alto sinal.
    Source(
        "ESC",
        "https://academic.oup.com/eurheartj/advance-articles",
        ("academic.oup.com",),
        max_details=120,
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

# Bootstrap auditável de documentos oficiais já confirmados no momento em que
# o radar foi ampliado. Evita perder lançamentos que já saíram da primeira tela
# de uma coleção dinâmica. Itens subsequentes continuam vindo das fontes acima.
BOOTSTRAP_DOCUMENTS = (
    {
        "org": "ESC",
        "title": "2026 ESC Guidelines for the management of cardiovascular disease and chronic kidney disease",
        "doi": "10.1093/eurheartj/ehag098",
        "url": "https://doi.org/10.1093/eurheartj/ehag098",
        "published_at": datetime(2026, 8, 28, tzinfo=timezone.utc),
    },
    {
        "org": "ESC",
        "title": "2026 ESC Guidelines on cardiac rehabilitation",
        "doi": "10.1093/eurheartj/ehag099",
        "url": "https://doi.org/10.1093/eurheartj/ehag099",
        "published_at": datetime(2026, 8, 28, tzinfo=timezone.utc),
    },
    {
        "org": "ESC",
        "title": "2026 ESC Guidelines for the management of heart failure",
        "doi": "10.1093/eurheartj/ehag100",
        "url": "https://doi.org/10.1093/eurheartj/ehag100",
        "published_at": datetime(2026, 8, 28, tzinfo=timezone.utc),
    },
    {
        "org": "ESC/ACC/AHA/WHF",
        "title": "Fifth Universal Definition of Myocardial Infarction (2026)",
        "doi": "10.1093/eurheartj/ehag101",
        "url": "https://doi.org/10.1093/eurheartj/ehag101",
        "published_at": datetime(2026, 8, 28, tzinfo=timezone.utc),
    },
    {
        "org": "ESC",
        "title": "European Society of Cardiology (ESC) Core Curriculum for the Cardiologist: 2026 update",
        "doi": "10.1093/eurheartj/ehag521",
        "url": "https://doi.org/10.1093/eurheartj/ehag521",
        "published_at": datetime(2026, 8, 27, tzinfo=timezone.utc),
    },
    {
        "org": "ESC",
        "title": "Ventricular free-wall rupture, ventricular pseudoaneurysm, and papillary muscle rupture complicating acute myocardial infarction: a clinical consensus statement",
        "doi": "10.1093/eurheartj/ehag164",
        "url": "https://doi.org/10.1093/eurheartj/ehag164",
        "published_at": datetime(2026, 8, 14, tzinfo=timezone.utc),
    },
    {
        "org": "ESC",
        "title": "Pathophysiology, prevention, and management of coronary microvascular obstruction: a clinical consensus statement",
        "doi": "10.1093/eurheartj/ehag334",
        "url": "https://doi.org/10.1093/eurheartj/ehag334",
        "published_at": datetime(2026, 8, 14, tzinfo=timezone.utc),
    },
    {
        "org": "ESC/EHRA/HFA",
        "title": "Workup and Management of Rhythm Disorders in Myocarditis and Inflammatory Cardiomyopathy: a clinical consensus statement",
        "doi": "10.1093/europace/euag153",
        "url": "https://doi.org/10.1093/europace/euag153",
        "published_at": datetime(2026, 8, 28, tzinfo=timezone.utc),
    },
    {
        "org": "ESC/EHRA/ACNAP",
        "title": "Diagnosis and Management of Very Rare Primary Arrhythmia Syndromes in Children and Adults: a clinical consensus statement",
        "doi": "10.1093/europace/euag184",
        "url": "https://doi.org/10.1093/europace/euag184",
        "published_at": datetime(2026, 8, 28, tzinfo=timezone.utc),
    },
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
        return response.read(4_000_000).decode("utf-8", errors="replace")


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
    if len(text.strip()) < 12:
        return None

    normalized = f"{text} {full}".casefold()
    if source.accept_all_articles:
        if not any(marker in urlsplit(full).path.casefold() for marker in ARTICLE_PATH_MARKERS):
            return None
    elif not any(keyword in normalized for keyword in source.keywords):
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
    for pattern in (
        "%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%b %d, %Y", "%B %d, %Y",
        "%d %b %Y", "%d %B %Y",
    ):
        try:
            return datetime.strptime(value, pattern).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def _date_published(html: str, parser: PageParser) -> datetime | None:
    for key in (
        "article:published_time", "datepublished", "date", "dc.date",
        "dc.date.issued", "publication_date", "publish-date", "citation_publication_date",
        "citation_online_date",
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
        or parser.meta.get("citation_title")
        or parser.title
        or fallback
    )
    return re.sub(r"\s+", " ", title).strip()[:300]


def _clean_doi(value: str | None) -> str | None:
    if not value:
        return None
    candidate = value.strip()
    candidate = re.sub(r"^(?:doi\s*:\s*|https?://(?:dx\.)?doi\.org/)", "", candidate, flags=re.I)
    match = DOI_RE.search(candidate)
    if not match:
        return None
    return match.group(0).rstrip(".,;:)]}").lower()


def _extract_doi(html: str, parser: PageParser) -> str | None:
    for key in (
        "citation_doi", "dc.identifier", "dc.identifier.doi", "doi", "prism.doi",
    ):
        doi = _clean_doi(parser.meta.get(key))
        if doi:
            return doi
    match = DOI_RE.search(html)
    return _clean_doi(match.group(0)) if match else None


def _slug(org: str, title: str, date: datetime) -> str:
    decomposed = unicodedata.normalize("NFKD", title.casefold())
    cleaned = "".join(char for char in decomposed if not unicodedata.combining(char))
    cleaned = re.sub(r"[^a-z0-9]+", "-", cleaned).strip("-")[:110]
    digest = hashlib.sha256(f"{org}:{title}:{date.date().isoformat()}".encode()).hexdigest()[:10]
    return f"{org.casefold().replace('/', '-')}-{date.year}-{cleaned}-{digest}"[:160]


def _title_key(title: str) -> str:
    decomposed = unicodedata.normalize("NFKD", title.casefold())
    cleaned = "".join(char for char in decomposed if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", cleaned).strip()


def _fingerprint(org: str, url: str, title: str, published_at: datetime, doi: str | None = None) -> str:
    normalized_doi = _clean_doi(doi)
    if normalized_doi:
        canonical = f"doi|{normalized_doi}"
    else:
        canonical = f"{org.casefold()}|{_title_key(title)}|{published_at.date().isoformat()}"
    return hashlib.sha256(canonical.encode()).hexdigest()


def _effective_cutoff(now: datetime) -> datetime:
    rolling = now - timedelta(days=DISCOVERY_LOOKBACK_DAYS)
    return max(DISCOVERY_START, rolling)


def _discover_source(
    source: Source,
    *,
    fetch=_fetch,
    cutoff: datetime | None = None,
    now: datetime | None = None,
) -> list[dict]:
    now = now or datetime.now(timezone.utc)
    cutoff = cutoff or _effective_cutoff(now)
    index_html = fetch(source.index_url)
    parser = PageParser()
    parser.feed(index_html)
    candidates: dict[str, str] = {}
    for href, text in parser.anchors:
        url = _candidate(source, href, text)
        if url:
            candidates.setdefault(url, text)

    discovered: list[dict] = []
    for url, fallback_title in list(candidates.items())[:source.max_details]:
        try:
            html = fetch(url)
            detail = PageParser()
            detail.feed(html)
            published_at = _date_published(html, detail)
            # O hub do congresso pode pré-listar artigos de dias seguintes.
            # Só alertar quando a data oficial já tiver sido alcançada.
            if published_at is None or published_at < cutoff or published_at > now:
                continue
            title = _page_title(detail, fallback_title)
            if not source.accept_all_articles and not any(
                keyword in title.casefold() for keyword in source.keywords
            ):
                continue
            discovered.append({
                "org": source.org,
                "title": title,
                "url": url,
                "doi": _extract_doi(html, detail),
                "published_at": published_at,
            })
        except Exception as error:  # uma página não derruba a fonte inteira
            log.warning("Falha ao inspecionar %s: %s", url, type(error).__name__)
    return discovered


def _bootstrap_documents(*, cutoff: datetime, now: datetime) -> list[dict]:
    return [
        dict(item)
        for item in BOOTSTRAP_DOCUMENTS
        if cutoff <= item["published_at"] <= now
    ]


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
            assunto=f"CorVIA Intelligence — nova publicação científica oficial ({guideline.org})",
            corpo=(
                f"O CorVIA Intelligence identificou uma publicação oficial em {guideline.published_at.strftime('%d/%m/%Y')}:\n\n"
                f"{guideline.titulo}\n{guideline.url}\n\n"
                "O achado foi marcado para revisão. Nenhuma recomendação clínica da plataforma foi alterada automaticamente."
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
    now = datetime.now(timezone.utc)
    cutoff = _effective_cutoff(now)
    discovered: list[dict] = _bootstrap_documents(cutoff=cutoff, now=now)
    failures: list[str] = []
    for source in SOURCES:
        try:
            discovered.extend(
                _discover_source(source, fetch=fetch, cutoff=cutoff, now=now)
            )
        except Exception as error:
            log.exception("Falha na fonte %s (%s)", source.org, source.index_url)
            failures.append(f"{source.org}:{source.index_url}:{type(error).__name__}")

    # Deduplicação em memória reduz hits no banco quando a mesma publicação
    # aparece simultaneamente no site ESC, OUP Guidelines e hub do Congresso.
    unique: dict[str, dict] = {}
    for item in discovered:
        fingerprint = _fingerprint(
            item["org"], item["url"], item["title"], item["published_at"], item.get("doi")
        )
        current = unique.get(fingerprint)
        if current is None or (item.get("doi") and not current.get("doi")):
            unique[fingerprint] = item

    created = updated = in_app = emails = 0
    for fingerprint, item in unique.items():
        guideline = None
        doi = _clean_doi(item.get("doi"))
        if doi:
            guideline = db.query(Guideline).filter(Guideline.doi == doi).first()
        if guideline is None:
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
                doi=doi,
                url=item["url"],
                published_at=item["published_at"],
                source_fingerprint=fingerprint,
                detection_status="detected",
            )
            db.add(guideline)
            db.flush()
            created += 1
        else:
            guideline.published_at = guideline.published_at or item["published_at"]
            guideline.source_fingerprint = guideline.source_fingerprint or fingerprint
            guideline.doi = guideline.doi or doi
            guideline.url = guideline.url or item["url"]
            updated += 1

        new_in_app, new_emails = _ensure_notifications(db, guideline)
        in_app += new_in_app
        emails += new_emails

    db.commit()
    return {
        "cutoff": cutoff.date().isoformat(),
        "official_items_seen": len(discovered),
        "unique_official_items": len(unique),
        "created": created,
        "updated": updated,
        "in_app_notifications": in_app,
        "emails_sent": emails,
        "source_failures": failures,
        "clinical_content_changed": False,
    }
