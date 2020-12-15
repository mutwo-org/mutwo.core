import abc

import mutwo.converters.abc as converters_abc
from mutwo import events


class FileConverter(converters_abc.EventConverter):
    """Abstract base class for converters that generate new files."""

    def __init__(self, path: str):
        self.path = path

    @abc.abstractmethod
    def convert(self, event_to_convert: events.abc.Event) -> None:
        raise NotImplementedError
