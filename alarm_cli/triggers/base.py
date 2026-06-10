from abc import ABC, abstractmethod

from alarm_cli.models.alarm import Alarm


class TriggerHandler(ABC):
    @abstractmethod
    def trigger(self, alarm: Alarm) -> None:
        raise NotImplementedError
