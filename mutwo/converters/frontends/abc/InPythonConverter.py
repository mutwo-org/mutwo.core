import abc
import typing

import mutwo.converters.frontends.abc as converters_abc
from mutwo import events


class InPythonConverter(converters_abc.EventConverter):
    """Abstract base class for converters that return Python objects."""

    @abc.abstractmethod
    def convert(self, event_to_convert: events.abc.Event) -> typing.Any:
        raise NotImplementedError
