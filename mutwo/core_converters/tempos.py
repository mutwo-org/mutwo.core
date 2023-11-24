# This file is part of mutwo, ecosystem for time-based arts.
#
# Copyright (C) 2020-2023
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Apply tempo curve on any :class:`~mutwo.core_events.abc.Event` and convert :class:`~mutwo.core_parameters.abc.TempoPoint` to beat-length-in-seconds.

"""

import functools
import typing

from mutwo import core_converters
from mutwo import core_events
from mutwo import core_parameters


__all__ = (
    "TempoPointToBeatLengthInSeconds",
    "TempoConverter",
    "EventToMetrizedEvent",
)


class TempoPointToBeatLengthInSeconds(core_converters.abc.Converter):
    """Convert a :class:`~mutwo.core_parameters.abc.TempoPoint` to beat length in seconds.

    **Example:**

    >>> from mutwo import core_converters
    >>> tempo_point_converter = core_converters.TempoPointToBeatLengthInSeconds()
    """

    def convert(
        self, tempo_point_to_convert: core_parameters.abc.TempoPoint.Type
    ) -> float:
        """Converts a :class:`TempoPoint` to beat-length-in-seconds.

        :param tempo_point_to_convert: A tempo point defines the active tempo
            from which the beat-length-in-seconds shall be calculated.
        :return: The duration of one beat in seconds within the passed tempo.

        **Example:**

        >>> from mutwo import core_converters
        >>> converter = core_converters.TempoPointToBeatLengthInSeconds()
        >>> converter.convert(60)  # one beat in tempo 60 bpm takes 1 second
        1.0
        >>> converter.convert(120)  # one beat in tempo 120 bpm takes 0.5 second
        0.5
        """
        t = core_parameters.abc.TempoPoint.from_any(tempo_point_to_convert)
        return float(60 / t.bpm)


class TempoConverter(core_converters.abc.EventConverter):
    """Apply tempo curve on an :class:`~mutwo.core_events.abc.Event`.

    :param tempo_envelope: The tempo curve that shall be applied on the
        mutwo events. This is expected to be a :class:`core_events.TempoEnvelope`
        which values are filled with numbers that will be interpreted as BPM
        [beats per minute]) or with :class:`mutwo.core_parameters.abc.TempoPoint`
        objects.
    :param apply_converter_on_events_tempo_envelope: If set to `True` the
        converter adjusts the :attr:`tempo_envelope` attribute of each
        converted event. Default to `True`.

    **Example:**

    >>> from mutwo import core_converters
    >>> from mutwo import core_events
    >>> from mutwo import core_parameters
    >>> tempo_envelope = core_events.Envelope(
    ...     [[0, core_parameters.DirectTempoPoint(60)], [3, 60], [3, 30], [5, 50]],
    ... )
    >>> c = core_converters.TempoConverter(tempo_envelope)
    """

    _tempo_point_to_beat_length_in_seconds = TempoPointToBeatLengthInSeconds().convert

    # Define private tempo envelope class which catches its
    # absolute times and durations. With this we can
    # improve the performance of the 'value_at' method and with this
    # improvment we can have a faster converter.
    #
    # This is actually not safe, because the envelope is still mutable.
    # But we trust that no one changes anything with our internal envelope
    # and hope everything goes well.
    class _CatchedTempoEnvelope(core_events.TempoEnvelope):
        @functools.cached_property
        def _abstf_tuple_and_dur(self) -> tuple[tuple[float, ...], float]:
            return super()._abstf_tuple_and_dur

        @functools.cached_property
        def _abst_tuple_and_dur(self) -> tuple[tuple[float, ...], float]:
            return super()._abst_tuple_and_dur

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
        e = tempo_envelope
        value_list: list[float] = []
        for tp in e.parameter_tuple:
            value_list.append(TempoConverter._tempo_point_to_beat_length_in_seconds(tp))

        return TempoConverter._CatchedTempoEnvelope(
            [
                [t, v, cs]
                for t, v, cs in zip(
                    e.absolute_time_tuple, value_list, e.curve_shape_tuple
                )
            ]
        )

    # ###################################################################### #
    #                         private methods                                #
    # ###################################################################### #

    def _start_and_end_to_tempo_converter(self, start, end):
        key = (start.beat_count, end.beat_count)
        try:
            t = self._start_and_end_to_tempo_converter_dict[key]
        except KeyError:
            t = self._start_and_end_to_tempo_converter_dict[key] = TempoConverter(
                self._tempo_envelope.copy().cut_out(
                    start,
                    end,
                ),
                apply_converter_on_events_tempo_envelope=False,
            )
        return t

    def _integrate(
        self, start: core_parameters.abc.Duration, end: core_parameters.abc.Duration
    ):
        key = (start.beat_count, end.beat_count)
        try:
            i = self._start_and_end_to_integration[key]
        except KeyError:
            i = self._start_and_end_to_integration[
                key
            ] = self._beat_length_in_seconds_envelope.integrate_interval(start, end)
        return i

    def _convert_chronon(
        self,
        chronon: core_events.Chronon,
        absolute_time: core_parameters.abc.Duration | float | int,
        depth: int = 0,
    ) -> tuple[typing.Any, ...]:
        chronon.duration = self._integrate(
            absolute_time, absolute_time + chronon.duration
        )
        return tuple([])

    def _convert_event(
        self,
        event_to_convert: core_events.abc.Event,
        absolute_time: core_parameters.abc.Duration | float | int,
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
                absolute_time,
                absolute_time + event_to_convert.duration,
            )
            local_tempo_converter = self._start_and_end_to_tempo_converter(start, end)
            event_to_convert.tempo_envelope = local_tempo_converter(tempo_envelope)
        rvalue = super()._convert_event(event_to_convert, absolute_time, depth)
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
        """Apply tempo curve of the converter on copy of 'event_to_convert'.

        :param event_to_convert: The event to convert. Can be any object
            that inherits from :class:`mutwo.core_events.abc.Event`. If the event that
            shall be converted is longer than the tempo curve of the
            :class:`TempoConverter`, then the last tempo of the curve is hold.
        :return: A new :class:`~mutwo.core_events.abc.Event` which duration has been
            adapted by the tempo curve of the :class:`TempoConverter`.

        **Example:**

        >>> from mutwo import core_converters
        >>> from mutwo import core_events
        >>> from mutwo import core_parameters
        >>> tempo_envelope = core_events.Envelope(
        ...     [[0, core_parameters.DirectTempoPoint(60)], [3, 60], [3, 30], [5, 50]],
        ... )
        >>> my_tempo_converter = core_converters.TempoConverter(tempo_envelope)
        >>> my_events = core_events.Consecution([core_events.Chronon(d) for d in (3, 2, 5)])
        >>> my_tempo_converter.convert(my_events)
        Consecution([Chronon(duration=DirectDuration(3.0)), Chronon(duration=DirectDuration(3.2)), Chronon(duration=DirectDuration(6.0))])
        """
        e = event_to_convert.destructive_copy()
        self._convert_event(e, core_parameters.DirectDuration(0))
        return e


class EventToMetrizedEvent(core_converters.abc.SymmetricalEventConverter):
    """Apply tempo envelope of event on copy of itself"""

    def __init__(
        self,
        skip_level_count: typing.Optional[int] = None,
        maxima_depth_count: typing.Optional[int] = None,
    ):
        self._skip_level_count = skip_level_count
        self._maxima_depth_count = maxima_depth_count

    def _convert_chronon(
        self,
        event_to_convert: core_events.Chronon,
        absolute_time: core_parameters.abc.Duration | float | int,
        depth: int = 0,
    ) -> core_events.Chronon:
        return event_to_convert

    def _convert_event(
        self,
        event_to_convert: core_events.abc.Event,
        absolute_time: core_parameters.abc.Duration | float | int,
        depth: int = 0,
    ) -> core_events.abc.ComplexEvent[core_events.abc.Event]:
        if (self._skip_level_count is None or self._skip_level_count < depth) and (
            self._maxima_depth_count is None or depth < self._maxima_depth_count
        ):
            tempo_converter = TempoConverter(event_to_convert.tempo_envelope)
            e = tempo_converter.convert(event_to_convert)
            e.reset_tempo_envelope()
        else:
            # Ensure we return copied event!
            e = event_to_convert.destructive_copy()
        return super()._convert_event(e, absolute_time, depth)

    def convert(self, event_to_convert: core_events.abc.Event) -> core_events.abc.Event:
        """Apply tempo envelope of event on copy of itself"""
        return self._convert_event(event_to_convert, 0, 0)
