import abc

import mutwo.converters.abc as converters_abc
from mutwo import events


class MutwoEventConverter(converters_abc.InPythonConverter):
    """Abstract base class for converters that return copied modified mutwo Events."""

    @abc.abstractmethod
    def convert(self, event_to_convert: events.abc.Event) -> events.abc.Event:
        raise NotImplementedError
