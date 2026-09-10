from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

from app.models.guideline import Guideline
from app.services.guideline_source_trust import is_trusted_official_guideline

NORMAL_INTERVAL_HOURS = 4
SURGE_LOOKBACK_HOURS = 6
SURGE_THRESHOLD = 8


@dataclass(frozen=True)
class HighFrequencyWindow:
    name: str
    start: date
    end: date


# Janelas ampliadas em 1 dia nas bordas quando há press day/embargo/publicações
# simultâneas, para capturar os artigos liberados imediatamente antes/depois.
# Manter esta lista curta e centrada em congressos cardiovasculares de alto sinal.
HIGH_FREQUENCY_WINDOWS = (
    HighFrequencyWindow("ESC Congress 2026", date(2026, 8, 27), date(2026, 9, 1)),
    HighFrequencyWindow("HRS HRX Live 2026", date(2026, 9, 17), date(2026, 9, 21)),
    HighFrequencyWindow("Hypertension Scientific Sessions 2026", date(2026, 10, 6), date(2026, 10, 12)),
    HighFrequencyWindow("TCT 2026", date(2026, 10, 30), date(2026, 11, 4)),
    HighFrequencyWindow("AHA Scientific Sessions 2026", date(2026, 11, 5), date(2026, 11, 10)),
)


def _utc(now: datetime | None = None) -> datetime:
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return current.astimezone(timezone.utc)


def active_high_frequency_window(now: datetime | None = None) -> HighFrequencyWindow | None:
    today = _utc(now).date()
    return next((window for window in HIGH_FREQUENCY_WINDOWS if window.start <= today <= window.end), None)


def evaluate_schedule(
    *,
    now: datetime | None = None,
    recent_trusted_count: int = 0,
    force: bool = False,
    last_started_at: datetime | None = None,
) -> dict:
    current = _utc(now)
    window = active_high_frequency_window(current)
    interval = 1 if window or recent_trusted_count >= SURGE_THRESHOLD else NORMAL_INTERVAL_HOURS
    reason = "high_frequency_window" if window else (
        "publication_surge" if recent_trusted_count >= SURGE_THRESHOLD else "normal_4h_cycle"
    )
    # Decidir pelo tempo decorrido, nunca pela hora de chegada do scheduler.
    # GitHub pode atrasar/despachar o cron fora da hora nominal.
    due_at = _utc(last_started_at) + timedelta(hours=interval) if last_started_at else current
    return {
        "run": force or current >= due_at,
        "reason": "manual_force" if force else reason,
        "window": window.name if window else None,
        "recent_trusted_count": recent_trusted_count,
        "interval_hours": interval,
        "next_run_at": due_at.isoformat(),
    }


def recent_trusted_publications(db, *, now: datetime | None = None) -> int:
    current = _utc(now)
    cutoff = current - timedelta(hours=SURGE_LOOKBACK_HOURS)
    candidates = db.query(Guideline).filter(
        Guideline.discovered_at >= cutoff,
        Guideline.published_at.isnot(None),
    ).all()
    return sum(1 for item in candidates if is_trusted_official_guideline(item))


def decide_radar_run(
    db, *, now: datetime | None = None, force: bool = False,
    last_started_at: datetime | None = None,
) -> dict:
    current = _utc(now)
    recent_count = recent_trusted_publications(db, now=current)
    return evaluate_schedule(
        now=current, recent_trusted_count=recent_count, force=force,
        last_started_at=last_started_at,
    )
