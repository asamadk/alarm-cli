import asyncio
import shlex

from alarm_cli.commands import HELP_TEXT, AlarmService, CommandError
from alarm_cli.daemon.runner import AlarmDaemon

PROMPT = "alarm-cli> "


def _parse_command(line: str) -> tuple[str, list[str]]:
    parts = shlex.split(line.strip())
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]


def _handle_command(service: AlarmService, line: str) -> bool:
    """Handle one REPL line. Returns False when the session should exit."""
    command, args = _parse_command(line)
    if not command:
        return True

    if command in {"exit", "quit", "q"}:
        return False

    if command == "help":
        print(HELP_TEXT, end="")
        return True

    try:
        if command == "create":
            if not args:
                raise CommandError("Usage: create HH:MM [label]")
            time_str = args[0]
            label = " ".join(args[1:]) if len(args) > 1 else None
            print(service.create(time_str, label))
        elif command == "list":
            print(service.list_alarms())
        elif command == "delete":
            if len(args) != 1:
                raise CommandError("Usage: delete <id>")
            print(service.delete(int(args[0])))
        else:
            print(f"Unknown command: {command}. Type 'help' for available commands.")
    except CommandError as exc:
        print(f"Error: {exc}")
    except ValueError:
        print("Error: delete requires a numeric alarm ID.")

    return True


async def _read_line(prompt: str) -> str | None:
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(None, lambda: input(prompt))
    except EOFError:
        return None


async def run_repl() -> None:
    service = AlarmService()
    daemon = AlarmDaemon(store=service.store)
    daemon_task = asyncio.create_task(daemon.run())

    print("alarm-cli — one-time alarms (24-hour clock, local timezone)")
    print("Alarms fire in this session. Type 'help' for commands.\n")

    alarm_count = len(service.store.list_alarms())
    if alarm_count:
        print(f"Loaded {alarm_count} scheduled alarm(s).\n")

    try:
        while True:
            line = await _read_line(PROMPT)
            if line is None:
                break
            if not _handle_command(service, line):
                break
    finally:
        daemon.request_stop()
        await daemon_task
        print("Goodbye.")


def main() -> None:
    try:
        asyncio.run(run_repl())
    except KeyboardInterrupt:
        print("\nGoodbye.")
