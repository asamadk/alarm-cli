from alarm_cli.models.alarm import Alarm
from alarm_cli.storage.alarm_store import AlarmNotFoundError, AlarmStore
from alarm_cli.validation import ValidationError, compute_scheduled_at


class CommandError(Exception):
    pass


class AlarmService:
    def __init__(self, store: AlarmStore | None = None) -> None:
        self._store = store or AlarmStore()

    @property
    def store(self) -> AlarmStore:
        return self._store

    def create(self, time: str, label: str | None = None) -> str:
        try:
            normalized_time, scheduled_at = compute_scheduled_at(time)
        except ValidationError as exc:
            raise CommandError(str(exc)) from exc

        alarm = Alarm(
            id=0,
            label=label,
            time=normalized_time,
            scheduled_at=scheduled_at,
        )
        created = self._store.add_alarm(alarm)
        label_text = f' "{created.label}"' if created.label else ""
        fires_at = created.scheduled_at.strftime("%Y-%m-%d %H:%M")
        return (
            f"Created alarm {created.id} at {created.time}{label_text} "
            f"(fires at {fires_at})."
        )

    def list_alarms(self) -> str:
        alarms = self._store.list_alarms()
        if not alarms:
            return "No alarms scheduled."

        lines = [f"{'ID':<4}{'Label':<18}{'Time':<8}{'Fires at'}"]
        for alarm in alarms:
            label = alarm.label or "(none)"
            fires_at = alarm.scheduled_at.strftime("%Y-%m-%d %H:%M")
            lines.append(f"{alarm.id:<4}{label:<18}{alarm.time:<8}{fires_at}")
        return "\n".join(lines)

    def delete(self, alarm_id: int) -> str:
        try:
            self._store.delete_alarm(alarm_id)
        except AlarmNotFoundError as exc:
            raise CommandError(str(exc)) from exc
        return f"Deleted alarm {alarm_id}."


HELP_TEXT = """\
Commands:
  create HH:MM [label]  Create a one-time alarm for today
  list                  List scheduled alarms
  delete <id>           Delete an alarm by ID
  help                  Show this help
  exit                  Quit (also: quit, q)
"""
