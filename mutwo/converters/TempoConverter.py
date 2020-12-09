import copy
import typing

import expenvelope

from mutwo import converters
from mutwo import events


TempoEvents = typing.Iterable[events.basic.TempoEvent]


class TempoConverter(converters.abc.Converter):
    def __init__(self, tempo_events: TempoEvents):
        self.tempo_events = tempo_events

    @staticmethod
    def make_envelope_from_tempo_events(
        tempo_events: TempoEvents,
    ) -> expenvelope.Envelope:
        pass

    @property
    def tempo_events(self) -> events.basic.SequentialEvent:
        return self._tempo_events

    @tempo_events.setter
    def tempo_events(self, tempo_events: TempoEvents):
        self._tempo_events = events.basic.SequentialEvent(tempo_events)
        self._envelope = self.make_envelope_from_tempo_events(self.tempo_events)

    @property
    def envelope(self) -> expenvelope.Envelope:
        return self._envelope

    def _convert_sequential_event(
        self, sequential_event: events.basic.SequentialEvent
    ) -> events.basic.SequentialEvent:
        # copy event before applying tempo curve
        sequential_event = copy.deepcopy(sequential_event)
        return sequential_event

    def _convert_simple_event(
        self, simple_event: events.basic.SequentialEvent
    ) -> events.basic.SimpleEvent:
        raise NotImplementedError

    def _convert_simultaneous_event(
        self, simultaneous_event: events.basic.SimultaneousEvent
    ) -> events.basic.SimultaneousEvent:
        raise NotImplementedError

    def _convert(self, event: events.abc.Event) -> events.abc.Event:
        if isinstance(event, events.basic.SequentialEvent):
            converted_event = self._convert_sequential_event(event)

        elif isinstance(event, events.basic.SimultaneousEvent,):
            converted_event = self._convert_simultaneous_event(event)

        elif isinstance(event, events.basic.SimpleEvent,):
            converted_event = self._convert_simple_event(event)

        else:
            msg = "Can't apply tempo curve on object '{}' of type '{}'.".format(
                event, type(event)
            )
            raise TypeError(msg)

        return converted_event
