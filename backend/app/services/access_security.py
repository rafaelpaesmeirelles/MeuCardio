"""Auditoria de login, sessao unica e sinais explicaveis de risco."""
from __future__ import annotations

import ipaddress
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import Request
from sqlalchemy.orm import Session

from app.models.user_access import UserAccess


@dataclass(frozen=True)
class RequestContext:
    ip_address: str | None
    city: str | None
    region: str | None
    country_code: str | None
    operating_system: str
    browser: str
    device_type: str
    user_agent: str


def _clean(value: str | None, limit: int) -> str | None:
    value = (value or "").strip()
    return value[:limit] or None


def _client_ip(request: Request) -> str | None:
    # Em producao o Cloudflare sobrescreve CF-Connecting-IP. X-Forwarded-For
    # e apenas o fallback do proxy/rede de testes; nunca e usado para decidir
    # autorizacao, somente para auditoria e sinalizacao.
    raw = request.headers.get("cf-connecting-ip")
    if not raw:
        forwarded = request.headers.get("x-forwarded-for")
        raw = forwarded.split(",", 1)[0] if forwarded else None
    raw = raw or (request.client.host if request.client else None)
    if not raw:
        return None
    try:
        return str(ipaddress.ip_address(raw.strip()))
    except ValueError:
        return None


def _client_software(user_agent: str) -> tuple[str, str, str]:
    ua = user_agent.lower()
    if "iphone" in ua or "ipad" in ua:
        os_name = "iOS/iPadOS"
    elif "android" in ua:
        os_name = "Android"
    elif "windows" in ua:
        os_name = "Windows"
    elif "cros" in ua:
        os_name = "ChromeOS"
    elif "mac os x" in ua or "macintosh" in ua:
        os_name = "macOS"
    elif "linux" in ua:
        os_name = "Linux"
    else:
        os_name = "Não identificado"

    if "edg/" in ua:
        browser = "Microsoft Edge"
    elif "opr/" in ua or "opera" in ua:
        browser = "Opera"
    elif "firefox/" in ua:
        browser = "Firefox"
    elif "chrome/" in ua or "crios/" in ua:
        browser = "Google Chrome"
    elif "safari/" in ua:
        browser = "Safari"
    elif "python" in ua or "httpx" in ua:
        browser = "Cliente de API"
    else:
        browser = "Não identificado"

    if any(marker in ua for marker in ("mobile", "iphone", "android")):
        device = "Celular/tablet"
    else:
        device = "Computador"
    return os_name, browser, device


def request_context(request: Request) -> RequestContext:
    user_agent = _clean(request.headers.get("user-agent"), 1000) or "Não informado"
    operating_system, browser, device_type = _client_software(user_agent)
    return RequestContext(
        ip_address=_client_ip(request),
        # Estes headers fazem parte do Managed Transform de localizacao do
        # visitante do Cloudflare. Sem o transform, a interface deixa claro
        # que cidade/regiao nao foram informadas; nao inventamos geolocalizacao.
        city=_clean(request.headers.get("cf-ipcity"), 120),
        region=_clean(request.headers.get("cf-region"), 120),
        country_code=_clean(request.headers.get("cf-ipcountry"), 8),
        operating_system=operating_system,
        browser=browser,
        device_type=device_type,
        user_agent=user_agent,
    )


def _risk(
    db: Session,
    *,
    user_id: int,
    surface: str,
    context: RequestContext,
    successful: bool,
    replaced_recent_session: bool = False,
) -> tuple[str, list[dict[str, str]]]:
    now = datetime.now(timezone.utc)
    reasons: list[dict[str, str]] = []
    level = "normal"

    def add(code: str, message: str, severity: str) -> None:
        nonlocal level
        reasons.append({"code": code, "message": message, "severity": severity})
        if severity == "alto" or (severity == "medio" and level == "normal"):
            level = severity

    history = (
        db.query(UserAccess)
        .filter(
            UserAccess.user_id == user_id,
            UserAccess.surface == surface,
            UserAccess.successful.is_(True),
        )
        .order_by(UserAccess.started_at.desc())
        .limit(50)
        .all()
    )
    last = history[0] if history else None
    if replaced_recent_session:
        add(
            "sessao_ativa_substituida",
            "Um novo login substituiu outra sessão que ainda estava ativa.",
            "medio",
        )
    if last:
        elapsed = now - last.started_at
        if (
            elapsed <= timedelta(hours=12)
            and context.country_code and last.country_code
            and context.country_code != last.country_code
        ):
            add(
                "pais_diferente_em_curto_periodo",
                f"Acesso em {context.country_code} pouco depois de um acesso em {last.country_code}.",
                "alto",
            )
        elif (
            elapsed <= timedelta(hours=2)
            and context.city and last.city
            and context.city.casefold() != last.city.casefold()
        ):
            add(
                "cidade_diferente_em_curto_periodo",
                f"Mudança rápida de cidade: {last.city} → {context.city}.",
                "medio",
            )
        if (
            elapsed <= timedelta(minutes=30)
            and context.ip_address and last.ip_address
            and context.ip_address != last.ip_address
            and (context.operating_system != last.operating_system or context.browser != last.browser)
        ):
            add(
                "ip_e_dispositivo_alterados",
                "IP e características do dispositivo mudaram em menos de 30 minutos.",
                "alto",
            )

    if successful and len(history) >= 5:
        known_os = {item.operating_system for item in history if item.operating_system}
        known_countries = {item.country_code for item in history if item.country_code}
        if context.operating_system not in known_os:
            add("sistema_operacional_novo", f"Primeiro acesso observado com {context.operating_system}.", "medio")
        known_browsers = {item.browser for item in history if item.browser}
        if context.browser not in known_browsers:
            add("navegador_novo", f"Primeiro acesso observado com {context.browser}.", "medio")
        if context.country_code and known_countries and context.country_code not in known_countries:
            add("pais_novo", f"Primeiro acesso observado no país {context.country_code}.", "medio")

    if not successful:
        failures = (
            db.query(UserAccess)
            .filter(
                UserAccess.user_id == user_id,
                UserAccess.surface == surface,
                UserAccess.successful.is_(False),
                UserAccess.started_at >= now - timedelta(minutes=15),
            )
            .count()
        ) + 1
        if failures >= 3:
            add(
                "tentativas_repetidas",
                f"{failures} tentativas de login sem sucesso em até 15 minutos.",
                "alto",
            )
    return level, reasons


def _event(
    db: Session,
    *,
    user_id: int,
    surface: str,
    request: Request,
    successful: bool,
    session_id: str | None,
    replaced_recent_session: bool = False,
    end_reason: str | None = None,
) -> UserAccess:
    now = datetime.now(timezone.utc)
    context = request_context(request)
    level, reasons = _risk(
        db,
        user_id=user_id,
        surface=surface,
        context=context,
        successful=successful,
        replaced_recent_session=replaced_recent_session,
    )
    access = UserAccess(
        user_id=user_id,
        surface=surface,
        successful=successful,
        session_id=session_id,
        end_reason=end_reason,
        started_at=now,
        last_seen_at=now if successful else None,
        ip_address=context.ip_address,
        city=context.city,
        region=context.region,
        country_code=context.country_code,
        operating_system=context.operating_system,
        browser=context.browser,
        device_type=context.device_type,
        user_agent=context.user_agent,
        risk_level=level,
        risk_reasons=reasons,
    )
    db.add(access)
    return access


def start_session(db: Session, *, subject, user_id: int, surface: str, request: Request) -> tuple[str, UserAccess]:
    """Substitui atomicamente a sessao anterior e registra o novo acesso."""
    now = datetime.now(timezone.utc)
    active = (
        db.query(UserAccess)
        .filter(
            UserAccess.user_id == user_id,
            UserAccess.surface == surface,
            UserAccess.successful.is_(True),
            UserAccess.ended_at.is_(None),
        )
        .with_for_update()
        .all()
    )
    replaced_recent = any(
        now - (item.last_seen_at or item.started_at) <= timedelta(minutes=30)
        for item in active
    )
    for item in active:
        item.ended_at = now
        item.end_reason = "substituida_por_novo_login"

    session_id = secrets.token_urlsafe(32)
    subject.active_session_id = session_id
    access = _event(
        db,
        user_id=user_id,
        surface=surface,
        request=request,
        successful=True,
        session_id=session_id,
        replaced_recent_session=replaced_recent,
    )
    db.commit()
    db.refresh(access)
    return session_id, access


def record_failed_login(
    db: Session, *, user_id: int, surface: str, request: Request,
    reason: str = "invalid_credentials",
) -> UserAccess:
    access = _event(
        db, user_id=user_id, surface=surface, request=request,
        successful=False, session_id=None, end_reason=reason,
    )
    db.commit()
    db.refresh(access)
    return access


def touch_session(db: Session, *, user_id: int, surface: str, session_id: str, now: datetime) -> None:
    access = (
        db.query(UserAccess)
        .filter(
            UserAccess.user_id == user_id,
            UserAccess.surface == surface,
            UserAccess.session_id == session_id,
            UserAccess.ended_at.is_(None),
        )
        .first()
    )
    if access:
        access.last_seen_at = now


def end_session(db: Session, *, user_id: int, surface: str, session_id: str | None, reason: str) -> None:
    if not session_id:
        return
    access = (
        db.query(UserAccess)
        .filter(
            UserAccess.user_id == user_id,
            UserAccess.surface == surface,
            UserAccess.session_id == session_id,
            UserAccess.ended_at.is_(None),
        )
        .first()
    )
    if access:
        access.ended_at = datetime.now(timezone.utc)
        access.end_reason = reason
