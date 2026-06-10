import os
from pathlib import Path

import pytest


@pytest.fixture
def data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    alarm_dir = tmp_path / "alarm-cli-data"
    alarm_dir.mkdir()
    monkeypatch.setenv("ALARM_CLI_DATA_DIR", str(alarm_dir))
    return alarm_dir
