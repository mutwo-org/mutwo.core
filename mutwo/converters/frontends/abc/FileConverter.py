import abc

import mutwo.converters.frontends.abc as converters_abc
from mutwo import events


class FileConverter(converters_abc.EventConverter):
    """Abstract base class for converters that generate new files."""

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, path: str):
        self._path = path

    @abc.abstractmethod
    def convert(self, event_to_convert: events.abc.Event) -> None:
        raise NotImplementedError
