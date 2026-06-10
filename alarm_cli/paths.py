import os
from pathlib import Path


def get_data_dir() -> Path:
    override = os.environ.get("ALARM_CLI_DATA_DIR")
    if override:
        return Path(override)
    return Path.home() / ".alarm-cli"


def get_alarms_file() -> Path:
    return get_data_dir() / "alarms.json"
