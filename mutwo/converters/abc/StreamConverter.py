import abc

import mutwo.converters.abc as converters_abc
from mutwo import events


class StreamConverter(converters_abc.EventConverter):
    """Abstract base class for converters that return a Stream for live playing."""

    @abc.abstractmethod
    def convert(self, event_to_convert: events.abc.Event):
        raise NotImplementedError
