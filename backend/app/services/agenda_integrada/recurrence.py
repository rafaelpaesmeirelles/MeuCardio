"""Expansão determinística das recorrências da agenda profissional.

As séries não são materializadas indefinidamente no banco. A API expande uma
janela limitada e aplica exceções por data, o que permite editar apenas uma
ocorrência sem destruir a rotina futura.
"""

from __future__ import annotations

import calendar
from datetime import date, datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo


def _value(source: Any, name: str, default=None):
    return source.get(name, default) if isinstance(source, dict) else getattr(source, name, default)


def occurrence_dates(series: Any, start: date, end: date) -> list[date]:
    """Retorna datas da série dentro da janela inclusiva, sem exceções."""
    starts_on: date = _value(series, "starts_on")
    ends_on: date | None = _value(series, "ends_on")
    recurrence = str(_value(series, "recurrence", "none"))
    interval = max(1, int(_value(series, "recurrence_interval", 1)))
    lower = max(start, starts_on)
    upper = min(end, ends_on) if ends_on else end
    if upper < lower:
        return []
    if recurrence == "none":
        return [starts_on] if lower <= starts_on <= upper else []

    result: list[date] = []
    current = lower
    weekdays = set(_value(series, "weekdays", []) or [starts_on.weekday()])
    month_day = int(_value(series, "month_day", None) or starts_on.day)
    anchor_week = starts_on - timedelta(days=starts_on.weekday())

    while current <= upper:
        elapsed_days = (current - starts_on).days
        include = False
        if recurrence == "daily":
            include = elapsed_days >= 0 and elapsed_days % interval == 0
        elif recurrence == "weekly":
            current_week = current - timedelta(days=current.weekday())
            elapsed_weeks = (current_week - anchor_week).days // 7
            include = elapsed_weeks >= 0 and elapsed_weeks % interval == 0 and current.weekday() in weekdays
        elif recurrence == "monthly":
            elapsed_months = (current.year - starts_on.year) * 12 + current.month - starts_on.month
            valid_day = min(month_day, calendar.monthrange(current.year, current.month)[1])
            include = elapsed_months >= 0 and elapsed_months % interval == 0 and current.day == valid_day
        if include:
            result.append(current)
        current += timedelta(days=1)
    return result


def occurrence_interval(series: Any, occurrence_date: date) -> tuple[datetime, datetime]:
    zone = ZoneInfo(str(_value(series, "timezone", "America/Sao_Paulo")))
    starts_at = datetime.combine(occurrence_date, _value(series, "start_time"), tzinfo=zone)
    ends_at = starts_at + timedelta(minutes=int(_value(series, "duration_minutes", 30)))
    return starts_at.astimezone(timezone.utc), ends_at.astimezone(timezone.utc)
