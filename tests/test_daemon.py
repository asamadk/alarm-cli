import asyncio
from datetime import datetime, timedelta

import pytest

from alarm_cli.daemon.runner import AlarmDaemon
from alarm_cli.models.alarm import Alarm
from alarm_cli.storage.alarm_store import AlarmStore
from alarm_cli.triggers.base import TriggerHandler


class CollectingTrigger(TriggerHandler):
    def __init__(self) -> None:
        self.fired: list[Alarm] = []

    def trigger(self, alarm: Alarm) -> None:
        self.fired.append(alarm)


@pytest.mark.asyncio
async def test_daemon_fires_due_alarm_and_removes_it(data_dir) -> None:
    store = AlarmStore(data_dir=data_dir)
    trigger = CollectingTrigger()
    now = datetime.now().astimezone()
    alarm = Alarm(
        id=0,
        label="test",
        time=now.strftime("%H:%M"),
        scheduled_at=now - timedelta(seconds=1),
    )
    store.add_alarm(alarm)

    daemon = AlarmDaemon(store=store, trigger_handler=trigger, idle_poll_seconds=0.01)
    task = asyncio.create_task(daemon.run())
    await asyncio.sleep(0.05)
    daemon.request_stop()
    await asyncio.wait_for(task, timeout=1)

    assert len(trigger.fired) == 1
    assert trigger.fired[0].id == 1
    assert store.list_alarms() == []


@pytest.mark.asyncio
async def test_daemon_waits_for_future_alarm(data_dir) -> None:
    store = AlarmStore(data_dir=data_dir)
    trigger = CollectingTrigger()
    now = datetime.now().astimezone()
    future = now + timedelta(milliseconds=200)
    alarm = Alarm(
        id=0,
        label=None,
        time=future.strftime("%H:%M"),
        scheduled_at=future,
    )
    store.add_alarm(alarm)

    daemon = AlarmDaemon(store=store, trigger_handler=trigger, idle_poll_seconds=0.05)

    task = asyncio.create_task(daemon.run())
    await asyncio.sleep(0.4)
    daemon.request_stop()
    await asyncio.wait_for(task, timeout=1)

    assert len(trigger.fired) == 1
    assert store.list_alarms() == []
