"""Métricas agregadas a partir de fatos auditáveis, sem reconstruir passado ausente."""

from datetime import date, datetime, time, timedelta, timezone
from functools import lru_cache
from zoneinfo import ZoneInfo

from redis import Redis
from redis.exceptions import RedisError
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.audit import AuditLog
from app.models.subscription import TIPO_MEUCARDIO
from app.models.user import User
from app.models.user_access import UserAccess

TIMEZONE = "America/Sao_Paulo"
LOCAL_TZ = ZoneInfo(TIMEZONE)
ACTIVE_WINDOW_SECONDS = 90
PRESENCE_KEY = "corvia:admin:visible-users:v1"
TRACKING_ACTION = "activity_subscription_tracking_started"
ACTIVATION_ACTION = "activity_subscription_first_activation"
# Serializa apenas a inicialização/primeira ativação; não altera o esquema.
TRACKING_LOCK = 908202609


@lru_cache(maxsize=1)
def _redis() -> Redis:
    return Redis.from_url(
        settings.redis_url, decode_responses=True,
        socket_connect_timeout=0.5, socket_timeout=0.5,
    )


def heartbeat(user_id: int) -> dict:
    now = datetime.now(timezone.utc)
    try:
        with _redis().pipeline() as pipe:
            pipe.zadd(PRESENCE_KEY, {str(user_id): now.timestamp()})
            pipe.zremrangebyscore(PRESENCE_KEY, "-inf", now.timestamp() - ACTIVE_WINDOW_SECONDS)
            pipe.expire(PRESENCE_KEY, ACTIVE_WINDOW_SECONDS * 2)
            pipe.execute()
        available = True
    except (RedisError, OSError):
        available = False
    return {"available": available, "window_seconds": ACTIVE_WINDOW_SECONDS, "server_time": now.isoformat()}


def active_now() -> dict:
    try:
        threshold = datetime.now(timezone.utc).timestamp() - ACTIVE_WINDOW_SECONDS
        with _redis().pipeline() as pipe:
            pipe.zremrangebyscore(PRESENCE_KEY, "-inf", threshold)
            pipe.zcard(PRESENCE_KEY)
            _, count = pipe.execute()
        return {"count": int(count), "window_seconds": ACTIVE_WINDOW_SECONDS, "available": True}
    except (RedisError, OSError):
        # Redis indisponível não significa que não há pessoas usando o site.
        return {"count": None, "window_seconds": ACTIVE_WINDOW_SECONDS, "available": False}


def tracking_started(db: Session) -> datetime:
    started = db.scalar(select(func.min(AuditLog.created_at)).where(AuditLog.action == TRACKING_ACTION))
    if started is not None:
        return started
    db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": TRACKING_LOCK})
    started = db.scalar(select(func.min(AuditLog.created_at)).where(AuditLog.action == TRACKING_ACTION))
    if started is None:
        started = datetime.now(timezone.utc)
        db.add(AuditLog(
            action=TRACKING_ACTION, entity="activity_metrics", created_at=started,
            detail={"source": "stripe_confirmed_first_activation", "timezone": TIMEZONE},
        ))
        db.flush()
    return started


def record_subscription_activation(
    db: Session, *, subscription, previous_status: str,
    previous_stripe_id: str | None, event_at: datetime,
) -> None:
    """Executada dentro da transação do webhook validado; renovações não contam.

    O estado ativo confirmado pelo Stripe é uma ativação de assinatura, não uma
    comprovação de recebimento de uma fatura. Convidados não passam neste fluxo.
    """
    if subscription.kind != TIPO_MEUCARDIO or subscription.status != "ativo":
        return
    stripe_id = subscription.stripe_subscription_id
    if not stripe_id:
        return
    is_new_contract = previous_stripe_id != stripe_id
    if not is_new_contract and previous_status not in {"inativo", "pendente", "teste"}:
        return
    db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": TRACKING_LOCK})
    exists = db.scalar(select(AuditLog.id).where(
        AuditLog.action == ACTIVATION_ACTION, AuditLog.entity_id == stripe_id,
    ).limit(1))
    if exists is not None:
        return
    started = tracking_started(db)
    if event_at < started:
        # Replay antigo não vira uma nova assinatura nem preenche cobertura ausente.
        return
    db.add(AuditLog(
        user_id=subscription.user_id, action=ACTIVATION_ACTION,
        entity="subscription", entity_id=stripe_id, created_at=event_at,
        detail={"subscription_id": subscription.id, "kind": TIPO_MEUCARDIO,
                "source": "stripe_verified_webhook", "status": "ativo"},
    ))


def period_bounds(period: str, anchor: date) -> tuple[datetime, datetime]:
    if period == "week":
        anchor -= timedelta(days=anchor.weekday())
    elif period == "month":
        anchor = anchor.replace(day=1)
    elif period == "year":
        anchor = anchor.replace(month=1, day=1)
    start = datetime.combine(anchor, time.min, tzinfo=LOCAL_TZ)
    if period == "year":
        end = start.replace(year=start.year + 1)
    elif period == "month":
        end = start.replace(year=start.year + (start.month == 12), month=start.month % 12 + 1)
    else:
        end = start + timedelta(days=7 if period == "week" else 1)
    return start, end


def _access_filter():
    return (UserAccess.successful.is_(True), UserAccess.surface == "corvia_os")


def _totals(db: Session, start: datetime, end: datetime) -> dict:
    registrations = db.scalar(select(func.count(User.id)).where(User.created_at >= start, User.created_at < end))
    accesses, unique = db.execute(select(
        func.count(UserAccess.id), func.count(func.distinct(UserAccess.user_id)),
    ).where(*_access_filter(), UserAccess.started_at >= start, UserAccess.started_at < end)).one()
    subscriptions = db.scalar(select(func.count(AuditLog.id)).where(
        AuditLog.action == ACTIVATION_ACTION, AuditLog.created_at >= start, AuditLog.created_at < end,
    ))
    return {"registrations": registrations, "subscriptions": subscriptions, "accesses": accesses, "unique_users": unique}


def _coverage(values: dict, start: datetime, end: datetime, *, accesses_since, subscriptions_since, now) -> dict:
    for metric, since in (("accesses", accesses_since), ("subscriptions", subscriptions_since)):
        values[f"{metric}_partial"] = since is None or start < since
        if since is None or end <= since or start > now:
            values[metric] = None
            if metric == "accesses":
                values["unique_users"] = None
    if start > now:
        values["registrations"] = None
    return values


def activity_report(db: Session, period: str, anchor: date | None = None) -> dict:
    now = datetime.now(timezone.utc)
    subscriptions_since = tracking_started(db)
    db.commit()
    accesses_since = db.scalar(select(func.min(UserAccess.started_at)).where(*_access_filter()))
    start, end = period_bounds(period, anchor or now.astimezone(LOCAL_TZ).date())
    granularity = "hour" if period == "day" else "month" if period == "year" else "day"
    registration_bucket = func.date_trunc(granularity, func.timezone(TIMEZONE, User.created_at))
    access_bucket = func.date_trunc(granularity, func.timezone(TIMEZONE, UserAccess.started_at))
    subscription_bucket = func.date_trunc(granularity, func.timezone(TIMEZONE, AuditLog.created_at))

    registrations = dict(db.execute(select(registration_bucket, func.count(User.id)).where(
        User.created_at >= start, User.created_at < end,
    ).group_by(registration_bucket)).all())
    access_rows = db.execute(select(
        access_bucket, func.count(UserAccess.id), func.count(func.distinct(UserAccess.user_id)),
    ).where(*_access_filter(), UserAccess.started_at >= start, UserAccess.started_at < end)
      .group_by(access_bucket)).all()
    accesses = {row[0]: (row[1], row[2]) for row in access_rows}
    subscriptions = dict(db.execute(select(subscription_bucket, func.count(AuditLog.id)).where(
        AuditLog.action == ACTIVATION_ACTION, AuditLog.created_at >= start, AuditLog.created_at < end,
    ).group_by(subscription_bucket)).all())

    def cover(values, left, right):
        return _coverage(values, left, right, accesses_since=accesses_since,
                         subscriptions_since=subscriptions_since, now=now)

    series = []
    cursor = start
    while cursor < end:
        if granularity == "month":
            following = cursor.replace(year=cursor.year + (cursor.month == 12), month=cursor.month % 12 + 1)
        else:
            following = cursor + (timedelta(hours=1) if granularity == "hour" else timedelta(days=1))
        key = cursor.replace(tzinfo=None)
        count, unique = accesses.get(key, (0, 0))
        series.append({"date": cursor.isoformat(), **cover({
            "registrations": registrations.get(key, 0), "subscriptions": subscriptions.get(key, 0),
            "accesses": count, "unique_users": unique,
        }, cursor, following)})
        cursor = following
    current = {}
    for name in ("day", "week", "month", "year"):
        left, right = period_bounds(name, now.astimezone(LOCAL_TZ).date())
        current[name] = cover(_totals(db, left, right), left, right)
    return {
        "timezone": TIMEZONE, "generated_at": now.isoformat(), "period": period,
        "granularity": granularity, "start": start.isoformat(), "end": end.isoformat(),
        "totals": cover(_totals(db, start, end), start, end), "series": series,
        "current": current, "active_now": active_now(),
        "coverage": {
            "accesses_since": accesses_since.isoformat() if accesses_since else None,
            "subscriptions_since": subscriptions_since.isoformat(),
            "subscriptions_note": "Primeiras ativações da assinatura CorVIA confirmadas pelo Stripe desde o início da coleta; não inclui checkout, convidados, períodos de teste nem renovações. Não é total de pagamentos. Períodos anteriores têm cobertura parcial ou indisponível.",
            "accesses_note": "Acessos são logins bem-sucedidos no CorVIA, não visualizações de páginas. Contagem disponível desde o primeiro registro de sessão; o passado anterior não foi reconstruído. Usuários únicos são deduplicados no período.",
            "registrations_note": "Cadastros pela data de criação das contas existentes; contas excluídas não são reconstruídas.",
        },
    }
