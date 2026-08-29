from datetime import datetime, timezone

from app.services.guideline_radar_schedule import (
    SURGE_THRESHOLD,
    active_high_frequency_window,
    evaluate_schedule,
)


def test_esc_congress_window_runs_hourly():
    now = datetime(2026, 8, 29, 9, 17, tzinfo=timezone.utc)
    window = active_high_frequency_window(now)
    assert window is not None
    assert window.name == "ESC Congress 2026"
    decision = evaluate_schedule(now=now)
    assert decision["run"] is True
    assert decision["reason"] == "high_frequency_window"


def test_normal_day_runs_every_four_hours():
    due = evaluate_schedule(now=datetime(2026, 9, 2, 8, 17, tzinfo=timezone.utc))
    waiting = evaluate_schedule(now=datetime(2026, 9, 2, 9, 17, tzinfo=timezone.utc))
    assert due["run"] is True
    assert due["reason"] == "normal_4h_cycle"
    assert waiting["run"] is False
    assert waiting["reason"] == "normal_interval_wait"


def test_recent_publication_surge_temporarily_switches_to_hourly():
    decision = evaluate_schedule(
        now=datetime(2026, 9, 2, 9, 17, tzinfo=timezone.utc),
        recent_trusted_count=SURGE_THRESHOLD,
    )
    assert decision["run"] is True
    assert decision["reason"] == "publication_surge"


def test_manual_force_always_runs():
    decision = evaluate_schedule(
        now=datetime(2026, 9, 2, 9, 17, tzinfo=timezone.utc),
        force=True,
    )
    assert decision["run"] is True
    assert decision["reason"] == "manual_force"
