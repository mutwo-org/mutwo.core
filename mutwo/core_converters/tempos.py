# This file is part of mutwo, ecosystem for time-based arts.
#
# Copyright (C) 2020-2024
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

"""Apply tempo curve on any :class:`~mutwo.core_events.abc.Event` and convert :class:`~mutwo.core_parameters.abc.Tempo` to beat-length-in-seconds.

"""

import functools
import typing

from mutwo import core_converters
from mutwo import core_events
from mutwo import core_parameters


__all__ = ("TempoConverter", "EventToMetrizedEvent")


class TempoConverter(core_converters.abc.EventConverter):
    """Apply tempo on an :class:`~mutwo.core_events.abc.Event`.

    :param tempo: The tempo that shall be applied on the mutwo events.
        This must be a :class:`~mutwo.core_parameters.abc.Tempo` object.
    :param apply_converter_on_events_tempo: If set to `True` the
        converter adjusts the :attr:`tempo` attribute of each
        converted event. Default to `True`.

    **Example:**

    >>> from mutwo import core_converters
    >>> from mutwo import core_parameters
    >>> tempo = core_parameters.FlexTempo(
    ...     [[0, core_parameters.DirectTempo(60)], [3, 60], [3, 30], [5, 50]],
    ... )
    >>> c = core_converters.TempoConverter(tempo)
    """

    # Define private envelope class which catches its absolute times
    # and durations. With this we can improve the performance of the
    # 'value_at' method and with this improvement we can have a faster
    # converter.
    #
    # This is actually not safe, because the envelope is still mutable.
    # But we trust that no one changes anything with our internal envelope
    # and hope everything goes well.
    class _CatchedEnvelope(core_events.Envelope):
        @functools.cached_property
        def _abstf_tuple_and_dur(self) -> tuple[tuple[float, ...], float]:
            return super()._abstf_tuple_and_dur

        @functools.cached_property
        def _abst_tuple_and_dur(self) -> tuple[tuple[float, ...], float]:
            return super()._abst_tuple_and_dur

    def __init__(
        self,
        tempo: core_parameters.abc.Tempo,
        apply_converter_on_events_tempo: bool = True,
    ):
        self._tempo = core_parameters.FlexTempo.from_parameter(tempo)
        self._beat_length_in_seconds_envelope = (
            TempoConverter._tempo_to_beat_length_in_seconds_envelope(self._tempo)
        )
        self._apply_converter_on_events_tempo = apply_converter_on_events_tempo
        # Catches for better performance
        self._start_and_end_to_tempo_converter_dict = {}
        self._start_and_end_to_integration = {}

    # ###################################################################### #
    #                          static methods                                #
    # ###################################################################### #

    @staticmethod
    def _tempo_to_beat_length_in_seconds_envelope(
        tempo: core_events.Envelope,
    ) -> core_events.Envelope:
        """Convert bpm / Tempo based env to beat-length-in-seconds env."""
        e = tempo
        value_list: list[float] = []
        for tp in e.parameter_tuple:
            value_list.append(tp.seconds)

        return TempoConverter._CatchedEnvelope(
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
                self._tempo.copy().cut_out(
                    start,
                    end,
                ),
                apply_converter_on_events_tempo=False,
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
    ) -> core_events.abc.Compound[core_events.abc.Event]:
        tempo = core_parameters.FlexTempo.from_parameter(event_to_convert.tempo)
        is_tempo_effectless = tempo.is_static and tempo.value_tuple[0] == 60
        if self._apply_converter_on_events_tempo and not is_tempo_effectless:
            start, end = (
                absolute_time,
                absolute_time + event_to_convert.duration,
            )
            local_tempo_converter = self._start_and_end_to_tempo_converter(start, end)
            event_to_convert.tempo = local_tempo_converter(tempo)
        rvalue = super()._convert_event(event_to_convert, absolute_time, depth)
        if is_tempo_effectless:
            # Yes we simply override the tempo of the event which we
            # just converted. This is because the TempoConverter copies the
            # event at the start of the algorithm and simply mutates this
            # copied event.
            event_to_convert.tempo = tempo
            event_to_convert.tempo.duration = event_to_convert.duration
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
        >>> tempo = core_parameters.FlexTempo(
        ...     [[0, core_parameters.DirectTempo(60)], [3, 60], [3, 30], [5, 50]],
        ... )
        >>> my_tempo_converter = core_converters.TempoConverter(tempo)
        >>> my_events = core_events.Consecution([core_events.Chronon(d) for d in (3, 2, 5)])
        >>> my_tempo_converter.convert(my_events)
        Consecution([Chronon(duration=DirectDuration(3.0)), Chronon(duration=DirectDuration(3.2)), Chronon(duration=DirectDuration(6.0))])
        """
        e = event_to_convert.destructive_copy()
        self._convert_event(e, core_parameters.DirectDuration(0))
        return e


class EventToMetrizedEvent(core_converters.abc.SymmetricalEventConverter):
    """Apply tempo of event on copy of itself"""

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
    ) -> core_events.abc.Compound[core_events.abc.Event]:
        if (self._skip_level_count is None or self._skip_level_count < depth) and (
            self._maxima_depth_count is None or depth < self._maxima_depth_count
        ):
            tempo_converter = TempoConverter(event_to_convert.tempo)
            e = tempo_converter.convert(event_to_convert)
            e.reset_tempo()
        else:
            # Ensure we return copied event!
            e = event_to_convert.destructive_copy()
        return super()._convert_event(e, absolute_time, depth)

    def convert(self, event_to_convert: core_events.abc.Event) -> core_events.abc.Event:
        """Apply tempo of event on copy of itself"""
        return self._convert_event(event_to_convert, 0, 0)
