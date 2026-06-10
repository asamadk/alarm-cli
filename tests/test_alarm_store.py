from datetime import datetime, timedelta, timezone

import pytest

from alarm_cli.models.alarm import Alarm
from alarm_cli.storage.alarm_store import AlarmNotFoundError, AlarmStore


def _future_alarm(label: str | None = None, offset_minutes: int = 30) -> Alarm:
    now = datetime.now().astimezone()
    scheduled_at = (now + timedelta(minutes=offset_minutes)).replace(
        second=0, microsecond=0
    )
    if scheduled_at <= now:
        scheduled_at += timedelta(minutes=1)
    if scheduled_at.date() != now.date():
        scheduled_at = now.replace(hour=23, minute=59, second=0, microsecond=0)
        if scheduled_at <= now:
            scheduled_at = now + timedelta(minutes=1)
    return Alarm(
        id=0,
        label=label,
        time=scheduled_at.strftime("%H:%M"),
        scheduled_at=scheduled_at,
    )


def test_add_and_list_alarms(data_dir) -> None:
    store = AlarmStore(data_dir=data_dir)
    first = store.add_alarm(_future_alarm("morning"))
    second = store.add_alarm(_future_alarm())

    assert first.id == 1
    assert second.id == 2
    assert len(store.list_alarms()) == 2


def test_delete_alarm(data_dir) -> None:
    store = AlarmStore(data_dir=data_dir)
    created = store.add_alarm(_future_alarm())

    store.delete_alarm(created.id)

    assert store.list_alarms() == []


def test_delete_missing_alarm_raises(data_dir) -> None:
    store = AlarmStore(data_dir=data_dir)

    with pytest.raises(AlarmNotFoundError):
        store.delete_alarm(99)


def test_remove_alarms(data_dir) -> None:
    store = AlarmStore(data_dir=data_dir)
    first = store.add_alarm(_future_alarm())
    second = store.add_alarm(_future_alarm(offset_minutes=45))

    store.remove_alarms([first.id])

    remaining = store.list_alarms()
    assert len(remaining) == 1
    assert remaining[0].id == second.id


def test_get_due_alarms(data_dir) -> None:
    store = AlarmStore(data_dir=data_dir)
    now = datetime.now().astimezone()
    due = Alarm(
        id=0,
        label=None,
        time=now.strftime("%H:%M"),
        scheduled_at=now - timedelta(minutes=1),
    )
    store.add_alarm(due)

    due_alarms = store.get_due_alarms(now)

    assert len(due_alarms) == 1
    assert due_alarms[0].id == 1
