import abc
import typing

import mutwo.converters.abc as converters_abc
from mutwo import events


class EventConverter(converters_abc.Converter):
    """Abstract base class for converters that transform mutwo Events."""

    @abc.abstractmethod
    def convert(self, event_to_convert: events.abc.Event) -> events.abc.Event:
        raise NotImplementedError


class FileConverter(EventConverter):
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


class InPythonConverter(EventConverter):
    """Abstract base class for converters that return Python objects."""

    @abc.abstractmethod
    def convert(self, event_to_convert: events.abc.Event) -> typing.Any:
        raise NotImplementedError


class ParameterConverter(converters_abc.Converter):
    """Abstract base class for converters that translate mutwo parameters to different formats."""

    @abc.abstractmethod
    def convert(self, parameter_to_convert: typing.Any) -> typing.Any:
        raise NotImplementedError
