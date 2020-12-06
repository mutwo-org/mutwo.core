import abc

from mutwo import events


class Converter(abc.ABC):
    @abc.abstractmethod
    def convert(self, events_to_convert: events.abc.Event):
        raise NotImplementedError
