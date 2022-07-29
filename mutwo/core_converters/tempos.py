"""Apply tempo curve on any :class:`~mutwo.events.abc.Event` and convert :class:`~mutwo.parameters.tempos.TempoPoint` to beat-length-in-seconds.

"""

import typing
import warnings

from mutwo import core_constants
from mutwo import core_converters
from mutwo import core_events
from mutwo import core_parameters


__all__ = (
    "TempoPointConverter",
    "TempoConverter",
    "EventToMetrizedEvent",
)


class UndefinedReferenceWarning(RuntimeWarning):
    def __init__(self, tempo_point: typing.Any):
        super().__init__(
            f"Tempo point '{tempo_point}' of type '{type(tempo_point)}' "
            "doesn't know attribute 'reference'."
            " Therefore reference has been set to 1."
        )


class TempoPointConverter(core_converters.abc.Converter):
    """Convert a :class:`~mutwo.parameters.tempos.TempoPoint` with BPM to beat-length-in-seconds.

    A :class:`TempoPoint` is defined as an object that has a particular tempo in
    beats per seconds (BPM) and a reference value (1 for a quarter note, 4
    for a whole note, etc.). Besides elaborate :class:`mutwo.parameters.tempos.TempoPoint`
    objects, any number can also be interpreted as a `TempoPoint`. In this case
    the number simply represents the BPM number and the reference will be set to 1.
    The returned beat-length-in-seconds always indicates the length for one quarter
    note.

    **Example:**

    >>> from mutwo.converters import symmetrical
    >>> tempo_point_converter = symmetrical.tempos.TempoPointConverter()
    """

    TempoPoint = typing.Union[core_parameters.TempoPoint, core_constants.Real]

    @staticmethod
    def _beats_per_minute_to_seconds_per_beat(
        beats_per_minute: core_constants.Real,
    ) -> float:
        return float(60 / beats_per_minute)

    @staticmethod
    def _extract_beats_per_minute_and_reference_from_tempo_point(
        tempo_point: TempoPoint,
    ) -> tuple[core_constants.Real, core_constants.Real]:
        try:
            beats_per_minute = tempo_point.tempo_in_beats_per_minute  # type: ignore
        except AttributeError:
            beats_per_minute = float(tempo_point)  # type: ignore

        try:
            reference = tempo_point.reference  # type: ignore
        except AttributeError:
            warnings.warn(UndefinedReferenceWarning(tempo_point))
            reference = 1

        return beats_per_minute, reference

    def convert(self, tempo_point_to_convert: TempoPoint) -> float:
        """Converts a :class:`TempoPoint` to beat-length-in-seconds.

        :param tempo_point_to_convert: A tempo point defines the active tempo
            from which the beat-length-in-seconds shall be calculated. The argument
            can either be any number (which will be interpreted as beats per
            minute [BPM]) or a ``mutwo.parameters.tempos.TempoPoint`` object.
        :return: The duration of one beat in seconds within the passed tempo.

        **Example:**

        >>> from mutwo.converters import symmetrical
        >>> converter = symmetrical.tempos.TempoPointConverter()
        >>> converter.convert(60)  # one beat in tempo 60 bpm takes 1 second
        1
        >>> converter.convert(120)  # one beat in tempo 120 bpm takes 0.5 second
        0.5
        """

        (
            beats_per_minute,
            reference,
        ) = self._extract_beats_per_minute_and_reference_from_tempo_point(
            tempo_point_to_convert
        )
        return (
            TempoPointConverter._beats_per_minute_to_seconds_per_beat(beats_per_minute)
            / reference
        )


class TempoConverter(core_converters.abc.EventConverter):
    """Apply tempo curves on mutwo events

    :param tempo_envelope: The tempo curve that shall be applied on the
        mutwo events. This is expected to be a :class:`core_events.TempoEnvelope`
        which values are filled with numbers that will be interpreted as BPM
        [beats per minute]) or with :class:`mutwo.core_parameters.TempoPoint`
        objects.
    :param apply_converter_on_events_tempo_envelope: If set to `True` the
        converter will also adjust the :attr:`tempo_envelope` attribute of
        each converted event. Default to `True`.

    **Example:**

    >>> from mutwo import core_converters
    >>> from mutwo import core_events
    >>> from mutwo import core_parameters
    >>> tempo_envelope = core_events.Envelope(
    >>>     [[0, tempos.TempoPoint(60)], [3, 60], [3, 30], [5, 50]],
    >>> )
    >>> my_tempo_converter = core_converters.TempoConverter(tempo_envelope)
    """

    _tempo_point_to_beat_length_in_seconds = TempoPointConverter().convert

    def __init__(
        self,
        tempo_envelope: core_events.TempoEnvelope,
        apply_converter_on_events_tempo_envelope: bool = True,
    ):
        self._tempo_envelope = tempo_envelope
        self._beat_length_in_seconds_envelope = (
            TempoConverter._tempo_envelope_to_beat_length_in_seconds_envelope(
                tempo_envelope
            )
        )
        self._apply_converter_on_events_tempo_envelope = (
            apply_converter_on_events_tempo_envelope
        )

    # ###################################################################### #
    #                          static methods                                #
    # ###################################################################### #

    @staticmethod
    def _tempo_envelope_to_beat_length_in_seconds_envelope(
        tempo_envelope: core_events.Envelope,
    ) -> core_events.Envelope:
        """Convert bpm / TempoPoint based env to beat-length-in-seconds env."""

        level_list: list[float] = []
        for tempo_point in tempo_envelope.value_tuple:
            beat_length_in_seconds = (
                TempoConverter._tempo_point_to_beat_length_in_seconds(tempo_point)
            )
            level_list.append(beat_length_in_seconds)

        return core_events.Envelope(
            [
                [absolute_time, value, curve_shape]
                for absolute_time, value, curve_shape in zip(
                    tempo_envelope.absolute_time_tuple,
                    level_list,
                    tempo_envelope.curve_shape_tuple,
                )
            ]
        )

    # ###################################################################### #
    #                         private methods                                #
    # ###################################################################### #

    def _convert_simple_event(
        self,
        simple_event: core_events.SimpleEvent,
        absolute_entry_delay: typing.Union[core_parameters.abc.Duration, float, int],
        depth: int = 0,
    ) -> tuple[typing.Any, ...]:
        simple_event.duration = (
            self._beat_length_in_seconds_envelope.integrate_interval(
                absolute_entry_delay, simple_event.duration + absolute_entry_delay
            )
        )
        return tuple([])

    def _convert_event(
        self,
        event_to_convert: core_events.abc.Event,
        absolute_entry_delay: typing.Union[core_parameters.abc.Duration, float, int],
        depth: int = 0,
    ) -> core_events.abc.ComplexEvent[core_events.abc.Event]:
        if self._apply_converter_on_events_tempo_envelope:
            event_to_convert.tempo_envelope = TempoConverter(
                self._tempo_envelope.cut_out(
                    absolute_entry_delay,
                    absolute_entry_delay + event_to_convert.duration,
                    mutate=False,
                ),
                apply_converter_on_events_tempo_envelope=False,
            ).convert(event_to_convert.tempo_envelope)
        return super()._convert_event(event_to_convert, absolute_entry_delay, depth)

    # ###################################################################### #
    #               public methods for interaction with the user             #
    # ###################################################################### #

    def convert(self, event_to_convert: core_events.abc.Event) -> core_events.abc.Event:
        """Apply tempo curve of the converter to the entered event.

        The method doesn't change the original event, but returns a copied
        version with different values for its duration attributes depending
        on the tempo curve.

        :param event_to_convert: The event to convert. Can be any object
            that inherits from ``mutwo.events.abc.Event``. If the event that
            shall be converted is longer than the tempo curve of the
            ``TempoConverter``, then the last tempo of the curve will be hold.
        :return: A new ``Event`` object which duration property has been adapted
            by the tempo curve of the ``TempoConverter``.

        **Example:**

        >>> from mutwo import core_converters
        >>> from mutwo import core_events
        >>> from mutwo import core_parameters
        >>> tempo_envelope = core_events.Envelope(
        >>>     [[0, tempos.TempoPoint(60)], [3, 60], [3, 30], [5, 50]],
        >>> )
        >>> my_tempo_converter = core_converters.TempoConverter(tempo_envelope)
        >>> my_events = core_events.SequentialEvent([core_events.SimpleEvent(d) for d in (3, 2, 5)])
        >>> my_tempo_converter.convert(my_events)
        SequentialEvent([SimpleEvent(duration = 3.0), SimpleEvent(duration = 1.5), SimpleEvent(duration = 2.5)])
        """
        copied_event_to_convert = event_to_convert.destructive_copy()
        self._convert_event(copied_event_to_convert, core_parameters.DirectDuration(0))
        return copied_event_to_convert


class EventToMetrizedEvent(core_converters.abc.SymmetricalEventConverter):
    """Apply tempo envelope of event on itself"""

    def __init__(
        self,
        skip_level_count: typing.Optional[int] = None,
        maxima_depth_count: typing.Optional[int] = None,
    ):
        self._skip_level_count = skip_level_count
        self._maxima_depth_count = maxima_depth_count

    def _convert_simple_event(
        self,
        event_to_convert: core_events.SimpleEvent,
        absolute_entry_delay: typing.Union[core_parameters.abc.Duration, float, int],
        depth: int = 0,
    ) -> core_events.SimpleEvent:
        return event_to_convert

    def _convert_event(
        self,
        event_to_convert: core_events.abc.Event,
        absolute_entry_delay: typing.Union[core_parameters.abc.Duration, float, int],
        depth: int = 0,
    ) -> core_events.abc.ComplexEvent[core_events.abc.Event]:
        if (self._skip_level_count is None or self._skip_level_count < depth) and (
            self._maxima_depth_count is None or depth < self._maxima_depth_count
        ):
            tempo_converter = TempoConverter(event_to_convert.tempo_envelope)
            event_to_convert = tempo_converter.convert(event_to_convert)
            event_to_convert.reset_tempo_envelope()
        else:
            # XXX: Ensure we return copied event!
            event_to_convert = event_to_convert.destructive_copy()
        return super()._convert_event(event_to_convert, absolute_entry_delay, depth)

    def convert(self, event_to_convert: core_events.abc.Event) -> core_events.abc.Event:
        """Apply tempo envelope of event on itself"""
        return self._convert_event(event_to_convert, 0, 0)
