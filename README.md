# alarm-cli

CLI for **one-time alarms** at absolute clock times in your machine's local timezone (24-hour format).

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quick start

```bash
alarm-cli
```

This starts an interactive session. The alarm scheduler runs in the background while you type commands:

```text
alarm-cli — one-time alarms (24-hour clock, local timezone)
Alarms fire in this session. Type 'help' for commands.

alarm-cli> create 10:30 "morning standup"
Created alarm 1 at 10:30 "morning standup" (fires at 2026-06-10 10:30).

alarm-cli> list
ID  Label            Time    Fires at
1   morning standup  10:30   2026-06-10 10:30

alarm-cli> delete 1
Deleted alarm 1.

alarm-cli> exit
```

When an alarm fires, output appears directly in the session:

```text
ALARM TRIGGERED [10:30] (morning standup)
```

## Commands

| Command | Description |
|---------|-------------|
| `create HH:MM [label]` | Create a one-time alarm for today |
| `list` | List all scheduled alarms |
| `delete <id>` | Delete an alarm by ID |
| `help` | Show available commands |
| `exit` | Quit the session (`quit` or `q` also work) |

## Behavior

- Alarms use your **system timezone** and **24-hour** clock (`00:00`–`23:59`).
- Each alarm fires **once today** at the given time, then is removed automatically.
- If the time has **already passed today**, `create` is rejected.
- Labels are optional. Use quotes for labels with spaces: `create 10:30 "morning standup"`.
- The session must stay open for alarms to fire — there is no separate background daemon.
- Data is stored in `~/.alarm-cli/alarms.json` and persists across sessions.

Override the data directory for testing:

```bash
export ALARM_CLI_DATA_DIR=/tmp/my-alarm-cli
```

## Tests

```bash
pytest
```

## Design

See [design.md](design.md) for the full specification.
