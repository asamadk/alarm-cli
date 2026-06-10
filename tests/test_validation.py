from datetime import datetime

import pytest

from alarm_cli.validation import ValidationError, compute_scheduled_at, parse_time


def test_parse_time_accepts_valid_values() -> None:
    assert parse_time("00:00") == (0, 0)
    assert parse_time("10:30") == (10, 30)
    assert parse_time("23:59") == (23, 59)


@pytest.mark.parametrize(
    "value",
    ["10:60", "24:00", "25:00", "1030", "10-30", "10:30:00"],
)
def test_parse_time_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValidationError):
        parse_time(value)


def test_compute_scheduled_at_uses_today_in_local_timezone() -> None:
    local_tz = datetime.now().astimezone().tzinfo
    now = datetime(2026, 6, 10, 9, 0, tzinfo=local_tz)
    normalized, scheduled_at = compute_scheduled_at("10:30", now=now)

    assert normalized == "10:30"
    assert scheduled_at.hour == 10
    assert scheduled_at.minute == 30
    assert scheduled_at.date() == now.date()


def test_compute_scheduled_at_rejects_past_time() -> None:
    local_tz = datetime.now().astimezone().tzinfo
    now = datetime(2026, 6, 10, 11, 0, tzinfo=local_tz)

    with pytest.raises(ValidationError, match="already passed today"):
        compute_scheduled_at("10:30", now=now)


def test_compute_scheduled_at_rejects_current_minute() -> None:
    local_tz = datetime.now().astimezone().tzinfo
    now = datetime(2026, 6, 10, 10, 30, 15, tzinfo=local_tz)

    with pytest.raises(ValidationError, match="already passed today"):
        compute_scheduled_at("10:30", now=now)
