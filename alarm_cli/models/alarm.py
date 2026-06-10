from dataclasses import dataclass
from datetime import datetime


@dataclass
class Alarm:
    id: int
    label: str | None
    time: str
    scheduled_at: datetime

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "time": self.time,
            "scheduled_at": self.scheduled_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Alarm":
        return cls(
            id=data["id"],
            label=data.get("label"),
            time=data["time"],
            scheduled_at=datetime.fromisoformat(data["scheduled_at"]),
        )
