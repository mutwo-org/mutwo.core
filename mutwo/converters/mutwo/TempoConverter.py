import numbers
import typing

import expenvelope

from mutwo import converters
from mutwo import events
from mutwo import parameters


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

    def _apply_tempo_envelope_on_event(
        self,
        event_to_process: events.abc.Event,
        absolute_entry_delay: parameters.durations.abc.DurationType,
    ) -> None:
        if isinstance(event_to_process, events.basic.SequentialEvent):
            self._apply_tempo_envelope_on_sequential_event(
                event_to_process, absolute_entry_delay
            )

        elif isinstance(event_to_process, events.basic.SimultaneousEvent,):
            self._apply_tempo_envelope_on_simultaneous_event(
                event_to_process, absolute_entry_delay
            )

        elif isinstance(event_to_process, events.basic.SimpleEvent,):
            self._apply_tempo_envelope_on_simple_event(
                event_to_process, absolute_entry_delay
            )

        else:
            msg = "Can't apply tempo curve on object '{}' of type '{}'.".format(
                event_to_process, type(event_to_process)
            )
            raise TypeError(msg)

    def _apply_tempo_envelope_on_sequential_event(
        self,
        sequential_event: events.basic.SequentialEvent[events.abc.Event],
        absolute_entry_delay: parameters.durations.abc.DurationType,
    ) -> None:
        for event_index, additional_delay in enumerate(sequential_event.absolute_times):
            self._apply_tempo_envelope_on_event(
                sequential_event[event_index], absolute_entry_delay + additional_delay
            )

    def _apply_tempo_envelope_on_simple_event(
        self,
        simple_event: events.basic.SimpleEvent,
        absolute_entry_delay: parameters.durations.abc.DurationType,
    ) -> None:
        simple_event.duration = self.envelope.integrate_interval(
            absolute_entry_delay, simple_event.duration + absolute_entry_delay
        )

    def _apply_tempo_envelope_on_simultaneous_event(
        self,
        simultaneous_event: events.basic.SimultaneousEvent[events.abc.Event],
        absolute_entry_delay: parameters.durations.abc.DurationType,
    ) -> None:
        [
            self._apply_tempo_envelope_on_event(
                event, absolute_entry_delay
            )
            for event in simultaneous_event
        ]

    def convert(self, event_to_convert: events.abc.Event) -> events.abc.Event:
        copied_event_to_convert = event_to_convert.destructive_copy()
        self._apply_tempo_envelope_on_event(copied_event_to_convert, 0)
        return copied_event_to_convert
