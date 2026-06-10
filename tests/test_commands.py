from datetime import datetime, timedelta

import pytest

from alarm_cli.commands import AlarmService, CommandError
from alarm_cli.repl import _handle_command


def _future_time_str(offset_minutes: int = 30) -> str:
    now = datetime.now().astimezone()
    scheduled_at = (now + timedelta(minutes=offset_minutes)).replace(
        second=0, microsecond=0
    )
    if scheduled_at <= now:
        scheduled_at += timedelta(minutes=1)
    if scheduled_at.date() != now.date():
        end_of_day = now.replace(hour=23, minute=59, second=0, microsecond=0)
        if end_of_day <= now:
            pytest.skip("No remaining time today for alarm test")
        scheduled_at = end_of_day
    return scheduled_at.strftime("%H:%M")


def test_create_and_list(data_dir, capsys) -> None:
    service = AlarmService()
    time_str = _future_time_str()

    assert _handle_command(service, f"create {time_str} standup")
    assert "Created alarm 1" in capsys.readouterr().out

    assert _handle_command(service, "list")
    output = capsys.readouterr().out
    assert "standup" in output
    assert time_str in output


def test_create_rejects_past_time(data_dir, capsys) -> None:
    service = AlarmService()
    now = datetime.now().astimezone()
    past = (now - timedelta(hours=1)).strftime("%H:%M")

    assert _handle_command(service, f"create {past}")
    assert "already passed today" in capsys.readouterr().out


def test_delete_alarm(data_dir, capsys) -> None:
    service = AlarmService()
    _handle_command(service, f"create {_future_time_str(45)}")
    capsys.readouterr()

    assert _handle_command(service, "delete 1")
    assert "Deleted alarm 1" in capsys.readouterr().out

    assert _handle_command(service, "list")
    assert "No alarms scheduled." in capsys.readouterr().out


def test_delete_missing_alarm(data_dir, capsys) -> None:
    service = AlarmService()

    assert _handle_command(service, "delete 1")
    assert "not found" in capsys.readouterr().out


def test_exit_command() -> None:
    service = AlarmService()
    assert _handle_command(service, "exit") is False
    assert _handle_command(service, "quit") is False


def test_create_with_quoted_label(data_dir, capsys) -> None:
    service = AlarmService()
    time_str = _future_time_str()

    assert _handle_command(service, f'create {time_str} "morning standup"')
    assert "morning standup" in capsys.readouterr().out


def test_service_create_raises(data_dir) -> None:
    service = AlarmService()
    now = datetime.now().astimezone()
    past = (now - timedelta(hours=1)).strftime("%H:%M")

    with pytest.raises(CommandError, match="already passed today"):
        service.create(past)
