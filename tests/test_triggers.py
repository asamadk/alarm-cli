from datetime import datetime

from alarm_cli.models.alarm import Alarm
from alarm_cli.triggers.console import ConsoleTrigger


def test_console_trigger_without_label(capsys) -> None:
    alarm = Alarm(
        id=1,
        label=None,
        time="10:30",
        scheduled_at=datetime(2026, 6, 10, 10, 30).astimezone(),
    )

    ConsoleTrigger().trigger(alarm)

    captured = capsys.readouterr()
    assert captured.out.strip() == "ALARM TRIGGERED [10:30]"


def test_console_trigger_with_label(capsys) -> None:
    alarm = Alarm(
        id=1,
        label="standup",
        time="10:30",
        scheduled_at=datetime(2026, 6, 10, 10, 30).astimezone(),
    )

    ConsoleTrigger().trigger(alarm)

    captured = capsys.readouterr()
    assert captured.out.strip() == 'ALARM TRIGGERED [10:30] (standup)'
