import abc

import mutwo.converters.abc as converters_abc
from mutwo import events


class EventConverter(converters_abc.Converter):
    """Abstract base class for converters that transform mutwo Events."""

    @abc.abstractmethod
    def convert(self, event_to_convert: events.abc.Event) -> events.abc.Event:
        raise NotImplementedError
