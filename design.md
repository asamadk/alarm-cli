# alarm-cli — Design Specification

## Overview

Python CLI for **one-time alarms** at absolute **24-hour clock times** in the machine's local timezone. Alarms persist on disk; an **interactive session** runs the scheduler in-process and fires alarms while the CLI is open.

---

## Functional Requirements

### Interactive session

```bash
alarm-cli
```

- Starts a REPL-style loop that stays open until `exit`.
- The alarm scheduler runs asynchronously in the same process.
- Alarms fire with output shown directly in the terminal.

### Create

```text
alarm-cli> create 10:30 "morning standup"
alarm-cli> create 22:15
```

- **Time:** `HH:MM`, 24-hour format (`00:00`–`23:59`).
- **Label:** optional string; no length or uniqueness validation.
- **ID:** auto-increment integer assigned on create.
- **Scheduling:** fires **once** at that clock time **today only**.
- **Past time:** if the time has already passed when creating → **reject** with a clear error.
- On success: persist to filesystem.

### List

```text
alarm-cli> list
```

Example output:

```text
ID  Label            Time    Fires at
1   morning standup  10:30   2026-06-10 10:30
2   (none)           22:15   2026-06-10 22:15
```

### Delete

```text
alarm-cli> delete 1
```

- Remove alarm by ID from persistence.
- Error if ID does not exist.

### Exit

```text
alarm-cli> exit
```

- Stops the scheduler and closes the session (`quit` or `q` also work).

### Trigger (v1)

- Separate, extensible trigger function/module.
- Default behavior: print `ALARM TRIGGERED [TIME]` (optionally include label if present).

---

## Non-Functional Requirements

| Area | Requirement |
|------|-------------|
| Language | Python |
| Design | Modular OOP — `Alarm`, store, scheduler/daemon, trigger handler, CLI |
| Persistence | Filesystem JSON (no database), e.g. `~/.alarm-cli/alarms.json` |
| Tests | Unit tests (pytest) |
| Docs | README with install and interactive usage |
| CLI framework | Interactive REPL loop |
| Async | In-process asyncio scheduler while session is open |

---

## Validation Rules

| Case | Behavior |
|------|----------|
| Invalid format | `10:30:00`, `10-30`, `1030` → error |
| Invalid clock | `25:00`, `10:60`, `24:00` → error |
| Past time today | Reject, e.g. `"10:30 has already passed today"` |
| Same minute as now | Valid only if current time is **before** that time today; otherwise reject (past time rule) |
| Missing time on create | Error |
| Delete unknown ID | Error |
| Start when already running | N/A (single interactive session) |
| Stop when not running | N/A |
| Create with no alarms file | Create file/store on first write |

---

## Data Model

### `Alarm`

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Auto-increment identifier |
| `label` | `str \| None` | Optional user label |
| `time` | `str` | Normalized `HH:MM` string |
| `scheduled_at` | `datetime` | Today at `HH:MM` in local timezone |

### Persistence File

Location: `~/.alarm-cli/alarms.json`

```json
{
  "next_id": 3,
  "alarms": [
    {
      "id": 1,
      "label": "morning standup",
      "time": "10:30",
      "scheduled_at": "2026-06-10T10:30:00"
    }
  ]
}
```

- `next_id` tracks the next ID to assign.
- `scheduled_at` is ISO datetime in local timezone (simplifies daemon logic and list display).
- On create: compute `scheduled_at` = today + `time`; reject if `scheduled_at <= now`.

---

## Architecture

```
alarm_cli/
  __init__.py
  models/
    alarm.py           # Alarm dataclass
  storage/
    alarm_store.py     # JSON CRUD, ID generation, atomic writes
  triggers/
    base.py            # TriggerHandler protocol/ABC
    console.py         # Default: print ALARM TRIGGERED [TIME]
  daemon/
    runner.py          # asyncio scheduler loop
  commands.py          # create/list/delete business logic
  repl.py              # interactive command loop
  cli.py               # entry point
  validation.py        # Time parsing and business rules
tests/
  test_validation.py
  test_alarm_store.py
  test_daemon.py
  ...
pyproject.toml
README.md
```

### Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| `Alarm` | Data model: id, label, time, scheduled_at |
| `AlarmStore` | Load/save JSON, CRUD, ID generation, atomic writes |
| `AlarmDaemon` | In-process asyncio loop; sleep until next due alarm |
| `TriggerHandler` | Pluggable trigger — default prints to stdout |
| `AlarmService` | Create/list/delete business logic |
| `REPL` | Interactive command loop |

### Runtime Flow

1. User runs `alarm-cli` → REPL starts, scheduler runs in-process.
2. User runs `create` → validate → append to JSON.
3. Scheduler sleeps until earliest `scheduled_at`.
4. Alarm due → trigger → remove from JSON → recalculate next sleep.
5. User runs `exit` → scheduler stops, session closes.

```
┌─────────────────┐     write/read      ┌──────────────────┐
│  REPL commands  │ ◄──────────────────►│  alarms.json     │
│  create/list/   │                     │  (filesystem)    │
│  delete         │                     └────────┬─────────┘
└────────┬────────┘                              │
         │ same process                           │
         ▼                                        │
┌─────────────────┐     read/write               │
│  AlarmDaemon    │ ◄────────────────────────────┘
│  (asyncio loop) │
└────────┬────────┘
         │ due
         ▼
┌─────────────────┐
│  TriggerHandler │ → prints to terminal
└─────────────────┘
```

---

## Edge Cases

- **File locking / atomic writes** when scheduler and REPL both touch JSON.
- **Timezone:** use local timezone consistently (`datetime.now().astimezone()`); document that alarms follow system timezone.
- **Delete while scheduler sleeping:** scheduler reloads store after wake or on periodic check so deleted alarms don't fire.
- **Multiple alarms at same time:** fire all due alarms, remove each, trigger each.
- **Clock skew / sleep:** asyncio sleep until `scheduled_at`; on wake, re-check `now >= scheduled_at`.

---

## README Outline

1. Install (`pip install -e .` or similar)
2. Quick start: run `alarm-cli`, `create`, wait, see trigger, `list` shows alarm gone
3. Commands reference
4. Data directory (`~/.alarm-cli/`)
5. Note: alarms are one-shot, today only; past times rejected; session must stay open
6. Running tests

---

## Out of Scope (v1)

- Daily or recurring alarms
- Relative durations ("in 30 minutes")
- Interactive REPL
- Database
- Sound or desktop notifications (trigger is pluggable for later)
