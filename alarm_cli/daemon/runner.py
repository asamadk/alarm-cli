import asyncio
import signal
from datetime import datetime
from pathlib import Path

from alarm_cli.models.alarm import Alarm
from alarm_cli.storage.alarm_store import AlarmStore
from alarm_cli.triggers.base import TriggerHandler
from alarm_cli.triggers.console import ConsoleTrigger

IDLE_POLL_SECONDS = 5.0


class AlarmDaemon:
    def __init__(
        self,
        store: AlarmStore | None = None,
        trigger_handler: TriggerHandler | None = None,
        idle_poll_seconds: float = IDLE_POLL_SECONDS,
    ) -> None:
        self._store = store or AlarmStore()
        self._trigger = trigger_handler or ConsoleTrigger()
        self._idle_poll_seconds = idle_poll_seconds
        self._stop_requested = False

    def request_stop(self) -> None:
        self._stop_requested = True

    async def run(self) -> None:
        while not self._stop_requested:
            now = datetime.now().astimezone()
            due_alarms = self._store.get_due_alarms(now)
            if due_alarms:
                await self._fire_alarms(due_alarms)
                continue

            alarms = self._store.list_alarms()
            if not alarms:
                await asyncio.sleep(self._idle_poll_seconds)
                continue

            next_alarm = min(alarms, key=lambda alarm: alarm.scheduled_at)
            delay = (next_alarm.scheduled_at - now).total_seconds()
            if delay > 0:
                await self._sleep_interruptibly(delay)
            else:
                await asyncio.sleep(0)

    async def _sleep_interruptibly(self, delay: float) -> None:
        end = asyncio.get_running_loop().time() + delay
        while not self._stop_requested:
            remaining = end - asyncio.get_running_loop().time()
            if remaining <= 0:
                return
            await asyncio.sleep(min(remaining, self._idle_poll_seconds))

    async def _fire_alarms(self, alarms: list[Alarm]) -> None:
        for alarm in alarms:
            self._trigger.trigger(alarm)
        self._store.remove_alarms([alarm.id for alarm in alarms])


def _install_signal_handlers(daemon: AlarmDaemon) -> None:
    loop = asyncio.get_running_loop()

    def _handle_stop() -> None:
        daemon.request_stop()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, _handle_stop)


async def _async_main(data_dir: Path | None = None) -> None:
    store = AlarmStore(data_dir=data_dir) if data_dir else AlarmStore()
    daemon = AlarmDaemon(store=store)
    _install_signal_handlers(daemon)
    await daemon.run()


def main(data_dir: Path | None = None) -> None:
    asyncio.run(_async_main(data_dir=data_dir))


if __name__ == "__main__":
    main()
