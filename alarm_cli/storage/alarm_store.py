import json
import os
from pathlib import Path

from alarm_cli.models.alarm import Alarm
from alarm_cli.paths import get_data_dir


class AlarmNotFoundError(LookupError):
    pass


class AlarmStore:
    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or get_data_dir()
        self._alarms_file = self._data_dir / "alarms.json"

    @property
    def alarms_file(self) -> Path:
        return self._alarms_file

    def _ensure_data_dir(self) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)

    def _load_state(self) -> dict:
        if not self._alarms_file.exists():
            return {"next_id": 1, "alarms": []}

        with self._alarms_file.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _save_state(self, state: dict) -> None:
        self._ensure_data_dir()
        temp_path = self._alarms_file.with_suffix(".json.tmp")
        with temp_path.open("w", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        temp_path.replace(self._alarms_file)

    def list_alarms(self) -> list[Alarm]:
        state = self._load_state()
        alarms = [Alarm.from_dict(item) for item in state["alarms"]]
        return sorted(alarms, key=lambda alarm: (alarm.scheduled_at, alarm.id))

    def add_alarm(self, alarm: Alarm) -> Alarm:
        state = self._load_state()
        alarm.id = state["next_id"]
        state["next_id"] += 1
        state["alarms"].append(alarm.to_dict())
        self._save_state(state)
        return alarm

    def delete_alarm(self, alarm_id: int) -> None:
        state = self._load_state()
        alarms = state["alarms"]
        remaining = [item for item in alarms if item["id"] != alarm_id]
        if len(remaining) == len(alarms):
            raise AlarmNotFoundError(f"Alarm with ID {alarm_id} not found.")
        state["alarms"] = remaining
        self._save_state(state)

    def remove_alarms(self, alarm_ids: list[int]) -> None:
        if not alarm_ids:
            return
        state = self._load_state()
        ids = set(alarm_ids)
        state["alarms"] = [item for item in state["alarms"] if item["id"] not in ids]
        self._save_state(state)

    def get_due_alarms(self, now) -> list[Alarm]:
        return [
            alarm
            for alarm in self.list_alarms()
            if alarm.scheduled_at <= now
        ]
