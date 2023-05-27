"""Apply tempo curve on any :class:`~mutwo.core_events.abc.Event` and convert :class:`~mutwo.core_parameters.abc.TempoPoint` to beat-length-in-seconds.

"""

import functools
import typing

from mutwo import core_constants
from mutwo import core_converters
from mutwo import core_events
from mutwo import core_parameters
from mutwo import core_utilities


__all__ = (
    "TempoPointToBeatLengthInSeconds",
    "TempoConverter",
    "EventToMetrizedEvent",
)


class TempoPointToBeatLengthInSeconds(core_converters.abc.Converter):
    """Convert a :class:`~mutwo.core_parameters.abc.TempoPoint` with BPM to beat-length-in-seconds.

    A :class:`TempoPoint` is defined as an object that has a particular tempo in
    beats per seconds (BPM) and a reference value (1 for a quarter note, 4
    for a whole note, etc.). Besides elaborate :class:`mutwo.core_parameters.abc.TempoPoint`
    objects, any number can also be interpreted as a `TempoPoint`. In this case
    the number simply represents the BPM number and the reference will be set to 1.
    The returned beat-length-in-seconds always indicates the length for one quarter
    note.

    **Example:**

    >>> from mutwo import core_converters
    >>> tempo_point_converter = core_converters.TempoPointToBeatLengthInSeconds()
    """

    TempoPoint = core_parameters.abc.TempoPoint | core_constants.Real

    def __init__(self):
        self._logger = core_utilities.get_cls_logger(type(self))

    @staticmethod
    def _beats_per_minute_to_seconds_per_beat(
        beats_per_minute: core_constants.Real,
    ) -> float:
        return float(60 / beats_per_minute)

    def _extract_beats_per_minute_and_reference_from_tempo_point(
        self, tempo_point: TempoPoint
    ) -> tuple[core_constants.Real, core_constants.Real]:
        try:
            beats_per_minute = tempo_point.tempo_in_beats_per_minute  # type: ignore
        except AttributeError:
            beats_per_minute = float(tempo_point)  # type: ignore

        try:
            reference = tempo_point.reference  # type: ignore
        except AttributeError:
            self._logger.warn(core_utilities.UndefinedReferenceWarning(tempo_point))
            reference = 1

        return beats_per_minute, reference

    def convert(self, tempo_point_to_convert: TempoPoint) -> float:
        """Converts a :class:`TempoPoint` to beat-length-in-seconds.

        :param tempo_point_to_convert: A tempo point defines the active tempo
            from which the beat-length-in-seconds shall be calculated. The argument
            can either be any number (which will be interpreted as beats per
            minute [BPM]) or a ``mutwo.core_parameters.abc.TempoPoint`` object.
        :return: The duration of one beat in seconds within the passed tempo.

        **Example:**

        >>> from mutwo import core_converters
        >>> converter = core_converters.TempoPointToBeatLengthInSeconds()
        >>> converter.convert(60)  # one beat in tempo 60 bpm takes 1 second
        1.0
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
            TempoPointToBeatLengthInSeconds._beats_per_minute_to_seconds_per_beat(
                beats_per_minute
            )
            / reference
        )


class TempoConverter(core_converters.abc.EventConverter):
    """Apply tempo curves on mutwo events

    :param tempo_envelope: The tempo curve that shall be applied on the
        mutwo events. This is expected to be a :class:`core_events.TempoEnvelope`
        which values are filled with numbers that will be interpreted as BPM
        [beats per minute]) or with :class:`mutwo.core_parameters.abc.TempoPoint`
        objects.
    :param apply_converter_on_events_tempo_envelope: If set to `True` the
        converter will also adjust the :attr:`tempo_envelope` attribute of
        each converted event. Default to `True`.

    **Example:**

    >>> from mutwo import core_converters
    >>> from mutwo import core_events
    >>> from mutwo import core_parameters
    >>> tempo_envelope = core_events.Envelope(
    ...     [[0, core_parameters.DirectTempoPoint(60)], [3, 60], [3, 30], [5, 50]],
    ... )
    >>> my_tempo_converter = core_converters.TempoConverter(tempo_envelope)
    """

    _tempo_point_to_beat_length_in_seconds = TempoPointToBeatLengthInSeconds().convert

    # Define private tempo envelope class which catches its
    # '_absolute_time_in_floats_tuple_and_duration'. With this we can
    # improve the performance of the 'value_at' method and with this
    # improvment we can have a faster converter.
    #
    # This is actually not safe, because the envelope is still mutable.
    # But we trust that no one changes anything with our internal envelope
    # and hope everything goes well. The long term solution is to implement
    # a 'freeze' method for all mutwo objects, which auto-converts all
    # properties to catched properties. But this may still takes some time
    # and we already want to have faster converters now.
    class _CatchedTempoEnvelope(core_events.TempoEnvelope):
        @functools.cached_property
        def _absolute_time_in_floats_tuple_and_duration(
            self,
        ) -> tuple[tuple[float, ...], float]:
            return super()._absolute_time_in_floats_tuple_and_duration

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
        # Catches for better performance
        self._start_and_end_to_tempo_converter_dict = {}
        self._start_and_end_to_integration = {}

    # ###################################################################### #
    #                          static methods                                #
    # ###################################################################### #

    @staticmethod
    def _tempo_envelope_to_beat_length_in_seconds_envelope(
        tempo_envelope: core_events.Envelope,
    ) -> core_events.Envelope:
        """Convert bpm / TempoPoint based env to beat-length-in-seconds env."""

        level_list: list[float] = []
        for tempo_point in tempo_envelope.parameter_tuple:
            beat_length_in_seconds = (
                TempoConverter._tempo_point_to_beat_length_in_seconds(tempo_point)
            )
            level_list.append(beat_length_in_seconds)

        return TempoConverter._CatchedTempoEnvelope(
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

    def _start_and_end_to_tempo_converter(self, start, end):
        key = (start.duration, end.duration)
        try:
            t = self._start_and_end_to_tempo_converter_dict[key]
        except KeyError:
            t = self._start_and_end_to_tempo_converter_dict[key] = TempoConverter(
                self._tempo_envelope.cut_out(
                    start,
                    end,
                    mutate=False,
                ),
                apply_converter_on_events_tempo_envelope=False,
            )
        return t

    def _integrate(
        self, start: core_parameters.abc.Duration, end: core_parameters.abc.Duration
    ):
        key = (start.duration, end.duration)
        try:
            i = self._start_and_end_to_integration[key]
        except KeyError:
            i = self._start_and_end_to_integration[
                key
            ] = self._beat_length_in_seconds_envelope.integrate_interval(start, end)
        return i

    def _convert_simple_event(
        self,
        simple_event: core_events.SimpleEvent,
        absolute_entry_delay: core_parameters.abc.Duration | float | int,
        depth: int = 0,
    ) -> tuple[typing.Any, ...]:
        simple_event.duration = self._integrate(
            absolute_entry_delay, absolute_entry_delay + simple_event.duration
        )
        return tuple([])

    def _convert_event(
        self,
        event_to_convert: core_events.abc.Event,
        absolute_entry_delay: core_parameters.abc.Duration | float | int,
        depth: int = 0,
    ) -> core_events.abc.ComplexEvent[core_events.abc.Event]:
        tempo_envelope = event_to_convert.tempo_envelope
        is_tempo_envelope_effectless = (
            tempo_envelope.is_static and tempo_envelope.value_tuple[0] == 60
        )
        if (
            self._apply_converter_on_events_tempo_envelope
            and not is_tempo_envelope_effectless
        ):
            start, end = (
                absolute_entry_delay,
                absolute_entry_delay + event_to_convert.duration,
            )
            local_tempo_converter = self._start_and_end_to_tempo_converter(start, end)
            event_to_convert.tempo_envelope = local_tempo_converter(tempo_envelope)
        rvalue = super()._convert_event(event_to_convert, absolute_entry_delay, depth)
        if is_tempo_envelope_effectless:
            # Yes we simply override the tempo_envelope of the event which we
            # just converted. This is because the TempoConverter copies the
            # event at the start of the algorithm and simply mutates this
            # copied event.
            event_to_convert.tempo_envelope.duration = event_to_convert.duration
        return rvalue

    # ###################################################################### #
    #               public methods for interaction with the user             #
    # ###################################################################### #

    def convert(self, event_to_convert: core_events.abc.Event) -> core_events.abc.Event:
        """Apply tempo curve of the converter to the entered event.

        The method doesn't change the original event, but returns a copied
        version with different values for its duration attributes depending
        on the tempo curve.

        :param event_to_convert: The event to convert. Can be any object
            that inherits from ``mutwo.core_events.abc.Event``. If the event that
            shall be converted is longer than the tempo curve of the
            ``TempoConverter``, then the last tempo of the curve will be hold.
        :return: A new ``Event`` object which duration property has been adapted
            by the tempo curve of the ``TempoConverter``.

        **Example:**

        >>> from mutwo import core_converters
        >>> from mutwo import core_events
        >>> from mutwo import core_parameters
        >>> tempo_envelope = core_events.Envelope(
        ...     [[0, core_parameters.DirectTempoPoint(60)], [3, 60], [3, 30], [5, 50]],
        ... )
        >>> my_tempo_converter = core_converters.TempoConverter(tempo_envelope)
        >>> my_events = core_events.SequentialEvent([core_events.SimpleEvent(d) for d in (3, 2, 5)])
        >>> my_tempo_converter.convert(my_events)
        SequentialEvent([SimpleEvent(duration = DirectDuration(duration = 3)), SimpleEvent(duration = DirectDuration(duration = 7205759403792795/2251799813685248)), SimpleEvent(duration = DirectDuration(duration = 6))])
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
        absolute_entry_delay: core_parameters.abc.Duration | float | int,
        depth: int = 0,
    ) -> core_events.SimpleEvent:
        return event_to_convert

    def _convert_event(
        self,
        event_to_convert: core_events.abc.Event,
        absolute_entry_delay: core_parameters.abc.Duration | float | int,
        depth: int = 0,
    ) -> core_events.abc.ComplexEvent[core_events.abc.Event]:
        if (self._skip_level_count is None or self._skip_level_count < depth) and (
            self._maxima_depth_count is None or depth < self._maxima_depth_count
        ):
            tempo_converter = TempoConverter(event_to_convert.tempo_envelope)
            event_to_convert = tempo_converter.convert(event_to_convert)
            event_to_convert.reset_tempo_envelope()
        else:
            # Ensure we return copied event!
            event_to_convert = event_to_convert.destructive_copy()
        return super()._convert_event(event_to_convert, absolute_entry_delay, depth)

    def convert(self, event_to_convert: core_events.abc.Event) -> core_events.abc.Event:
        """Apply tempo envelope of event on itself"""
        return self._convert_event(event_to_convert, 0, 0)
