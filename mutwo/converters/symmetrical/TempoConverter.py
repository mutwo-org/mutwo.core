import typing

import expenvelope

from mutwo import converters
from mutwo import events
from mutwo import parameters

from mutwo.converters.symmetrical.TempoPointConverter import (
    TempoPointConverter as converters_symmetrical_TempoPointConverter,
)


TempoEvents = events.basic.SequentialEvent[events.basic.EnvelopeEvent]


class TempoConverter(converters.abc.Converter):
    """Class for applying tempo curves on mutwo events.

    :param tempo_events: The tempo curve that shall be applied on the
        mutwo events. This is expected to be a SequentialEvent that is filled
        with EnvelopeEvent objects. Each EnvelopeEvent can either be initialised
        via numbers for start and end attributes (the numbers will be interpreted
        as BPM [beats per minute]) or via mutwo.parameters.tempo.TempoPoint objects.

    Example:
        >>> from mutwo.converters import symmetrical
        >>> from mutwo.events import basic
        >>> from mutwo.parameters import tempos
        >>> tempo_events = basic.SequentialEvent(
        >>>     [basic.EnvelopeEvent(3, tempos.TempoPoint(60)),  # start with bpm = 60
        >>>      basic.EnvelopeEvent(2, 30, 50),                 # acc. from 30 to 50
        >>>      basic.EnvelopeEvent(5, 50)]                     # stay on bpm = 50
        >>> )
        >>> my_tempo_converter = symmetrical.TempoConverter(tempo_events)
    """

    _tempo_point_converter = converters_symmetrical_TempoPointConverter()

    def __init__(self, tempo_events: TempoEvents):
        self.tempo_events = tempo_events

    @staticmethod
    def _find_beat_length_at_start_and_end(
        tempo_event: events.basic.EnvelopeEvent,
    ) -> typing.Tuple[float]:
        """Extracts the beat-length-in-seconds at start and end of a TempoEvent.

        """
        beat_length_at_start_and_end = []
        for tempo_point in (tempo_event.object_start, tempo_event.object_stop):
            beat_length_at_start_and_end.append(
                TempoConverter._tempo_point_converter.convert(tempo_point)
            )

        return beat_length_at_start_and_end

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

            beat_length_at_start_and_end = TempoConverter._find_beat_length_at_start_and_end(
                tempo_event
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
        """Applies tempo envelope on any object that inherits from events.abc.Event.

        Make type checks to differentiate between different timing structures
        of SequentialEvent, SimultaneousEvent and SimpleEvent.
        """
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
            self._apply_tempo_envelope_on_event(event, absolute_entry_delay)
            for event in simultaneous_event
        ]

    def convert(self, event_to_convert: events.abc.Event) -> events.abc.Event:
        """Apply tempo curve of the converter to the entered event.

        The method doesn't change the original event, but returns a copied
        version with different values for its duration attributes depending
        on the tempo curve.

        :param event_to_convert: The event to convert. Can be any object
            that inherits from mutwo.events.abc.Event. If the event to convert
            is longer than tempo curve of the TempoConverter, the last tempo
            of the curve will be hold.
        """
        copied_event_to_convert = event_to_convert.destructive_copy()
        self._apply_tempo_envelope_on_event(copied_event_to_convert, 0)
        return copied_event_to_convert
