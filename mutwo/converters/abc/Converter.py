import abc

from mutwo import events


class Converter(abc.ABC):
    @abc.abstractmethod
    def _convert(self, event: events.abc.Event):
        raise NotImplementedError

    def convert(self, *events_to_convert) -> tuple:
        return tuple(self._convert(event) for event in events_to_convert)
