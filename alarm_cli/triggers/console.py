from alarm_cli.models.alarm import Alarm
from alarm_cli.triggers.base import TriggerHandler


class ConsoleTrigger(TriggerHandler):
    def trigger(self, alarm: Alarm) -> None:
        if alarm.label:
            message = f'ALARM TRIGGERED [{alarm.time}] ({alarm.label})'
        else:
            message = f"ALARM TRIGGERED [{alarm.time}]"
        print(message, flush=True)
