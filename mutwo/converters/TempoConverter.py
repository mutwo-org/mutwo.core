import copy
import numbers
import typing

import expenvelope

from mutwo import converters
from mutwo import events


TempoEvents = typing.Iterable[events.basic.TempoEvent]


class TempoConverter(converters.abc.MutwoEventConverter):
    def __init__(self, tempo_events: TempoEvents):
        self.tempo_events = tempo_events

    @staticmethod
    def beats_per_minute_to_seconds_per_beat(beats_per_minute: numbers.Number) -> float:
        return 60 / beats_per_minute

    @staticmethod
    def make_envelope_from_tempo_events(
        tempo_events: TempoEvents,
    ) -> expenvelope.Envelope:
        """Convert a list of TempoEvents to an Envelope."""

        levels = []
        durations = []
        curve_shapes = []
        is_first = True
        for tempo_event in tempo_events:
            if is_first:
                is_first = False
            else:
                durations.append(1e-100)
                curve_shapes.append(0)

            beat_length_at_start_and_end = tuple(
                TempoConverter.beats_per_minute_to_seconds_per_beat(
                    getattr(tempo_event, tempo)
                )
                * tempo_event.reference
                for tempo in ("tempo_start", "tempo_end")
            )
            levels.extend(beat_length_at_start_and_end)
            durations.append(tempo_event.duration - 1e-100)
            curve_shapes.append(tempo_event.curve_shape)

        return expenvelope.Envelope.from_levels_and_durations(
            levels, durations, curve_shapes
        )

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
        start_and_end_time_per_event = sequential_event.start_and_end_time_per_event
        for event_index, start_and_end_time in enumerate(start_and_end_time_per_event):
            sequential_event[event_index].duration = self.envelope.integrate_interval(
                *start_and_end_time
            )

        return sequential_event

    def _convert_simple_event(
        self, simple_event: events.basic.SequentialEvent
    ) -> events.basic.SimpleEvent:
        # copy event before applying tempo curve
        simple_event = copy.deepcopy(simple_event)
        simple_event.duration = self.envelope.integrate_interval(
            0, simple_event.duration
        )
        return simple_event

    def _convert_simultaneous_event(
        self, simultaneous_event: events.basic.SimultaneousEvent
    ) -> events.basic.SimultaneousEvent:
        # TODO(write conversion function for simultaneous events..
        # shall we just apply the same method that has been used in
        # the _convert_simple_event method?)
        raise NotImplementedError

    def convert(self, event_to_convert: events.abc.Event) -> events.abc.Event:
        if isinstance(event_to_convert, events.basic.SequentialEvent):
            converted_event = self._convert_sequential_event(event_to_convert)

        elif isinstance(event_to_convert, events.basic.SimultaneousEvent,):
            converted_event = self._convert_simultaneous_event(event_to_convert)

        elif isinstance(event_to_convert, events.basic.SimpleEvent,):
            converted_event = self._convert_simple_event(event_to_convert)

        else:
            msg = "Can't apply tempo curve on object '{}' of type '{}'.".format(
                event_to_convert, type(event_to_convert)
            )
            raise TypeError(msg)

        return converted_event
