import re
from datetime import datetime

TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


class ValidationError(ValueError):
    pass


def parse_time(time_str: str) -> tuple[int, int]:
    match = TIME_PATTERN.match(time_str.strip())
    if not match:
        raise ValidationError(
            f"Invalid time format '{time_str}'. Expected HH:MM in 24-hour format."
        )
    return int(match.group(1)), int(match.group(2))


def format_time(hour: int, minute: int) -> str:
    return f"{hour:02d}:{minute:02d}"


def compute_scheduled_at(
    time_str: str, now: datetime | None = None
) -> tuple[str, datetime]:
    if now is None:
        now = datetime.now().astimezone()

    hour, minute = parse_time(time_str)
    normalized = format_time(hour, minute)
    scheduled_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if scheduled_at <= now:
        raise ValidationError(f"{normalized} has already passed today.")

    return normalized, scheduled_at
