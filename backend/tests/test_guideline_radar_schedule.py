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


def test_normal_day_runs_every_four_hours_even_when_scheduler_is_delayed():
    previous = datetime(2026, 9, 2, 4, 17, tzinfo=timezone.utc)
    due = evaluate_schedule(now=datetime(2026, 9, 2, 9, 8, tzinfo=timezone.utc), last_started_at=previous)
    waiting = evaluate_schedule(now=datetime(2026, 9, 2, 8, 16, tzinfo=timezone.utc), last_started_at=previous)
    assert due["run"] is True
    assert due["reason"] == "normal_4h_cycle"
    assert waiting["run"] is False
    assert due["interval_hours"] == 4


def test_first_run_catches_up_at_any_hour_and_restart_does_not_repeat():
    now = datetime(2026, 9, 2, 9, 17, tzinfo=timezone.utc)
    assert evaluate_schedule(now=now)["run"] is True
    assert evaluate_schedule(now=now, last_started_at=now)["run"] is False


def test_peak_runs_after_one_elapsed_hour_not_on_every_worker_tick():
    previous = datetime(2026, 8, 29, 9, 17, tzinfo=timezone.utc)
    assert evaluate_schedule(now=datetime(2026, 8, 29, 10, 16, tzinfo=timezone.utc), last_started_at=previous)["run"] is False
    assert evaluate_schedule(now=datetime(2026, 8, 29, 10, 18, tzinfo=timezone.utc), last_started_at=previous)["run"] is True


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
