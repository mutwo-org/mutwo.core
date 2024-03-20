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

"""Envelope events"""

from __future__ import annotations

import bisect
import functools
import math
import typing

import ranges

from mutwo import core_constants
from mutwo import core_events
from mutwo import core_parameters
from mutwo import core_utilities


__all__ = ("Envelope",)

T = typing.TypeVar("T", bound=core_events.abc.Event)


class Envelope(core_events.Consecution, typing.Generic[T]):
    """Model continuous changing values (e.g. glissandi, crescendo).

    :param event_iterable_or_point_sequence: An iterable filled with events
        or with points. If the sequence is filled with points, the points
        are converted to events. Each event represents a point in a
        two dimensional graph where the x-axis presents time and the y-axis
        a changing value. Any event class can be used. It is
        more important that the used event classes fit with the functions
        passed in the following parameters.
    :type event_iterable_or_point_sequence: typing.Iterable[T]

    This class is inspired by Marc Evansteins `Envelope` class in his
    `expenvelope <https://git.sr.ht/~marcevanstein/expenvelope>`_
    python package and is made to fit better into the `mutwo` ecosystem.

    **Hint:**

    When comparing two envelopes (e.g. `env0 == env1`) `mutwo` only returns
    `True` in case all control points (= events inside the envelope) are
    equal between both envelopes. So `mutwo` won't make the much more
    complicated test to check if two envelopes have the same shape (= the same
    value at each `env0.value_at(x) == env1.value_at(x)` for each possible
    `x`). Such a test is not implemented yet.

    **Example:**

    >>> from mutwo import core_events
    >>> core_events.Envelope([[0, 0, 1], [0.5, 1]])
    Envelope([Chronon(curve_shape=1, duration=DirectDuration(0.5), value=0), Chronon(curve_shape=0, duration=DirectDuration(0.0), value=1)])
    """

    # Type definitions
    Value: typing.TypeAlias = core_constants.Real
    Parameter: typing.TypeAlias = typing.Any
    CurveShape: typing.TypeAlias = core_constants.Real
    IncompletePoint: typing.TypeAlias = tuple["core_parameters.abc.Duration", Parameter]
    CompletePoint: typing.TypeAlias = tuple[
        "core_parameters.abc.Duration", Parameter, CurveShape  # type: ignore
    ]
    Point: typing.TypeAlias = CompletePoint | IncompletePoint

    default_event_class = core_events.Chronon

    _short_name_length = 3

    def __init__(
        self,
        event_iterable_or_point_sequence: typing.Iterable[T] | typing.Sequence[Point],
        *args,
        **kwargs,
    ):
        event_iterable = self._event_iterable_or_point_sequence_to_event_iterable(
            event_iterable_or_point_sequence
        )
        super().__init__(event_iterable, *args, **kwargs)

    # ###################################################################### #
    #                           magic methods                                #
    # ###################################################################### #

    @typing.overload  # type: ignore
    def __setitem__(self, index_or_slice: int, event_or_sequence: T):
        ...

    @typing.overload
    def __setitem__(
        self,
        index_or_slice: slice,
        event_or_sequence: typing.Iterable[T] | typing.Iterable[Envelope.Point],
    ):
        ...

    def __setitem__(
        self,
        index_or_slice: int | slice,
        event_or_sequence: T | typing.Iterable[T] | typing.Iterable[Envelope.Point],
    ):
        if isinstance(index_or_slice, slice) and isinstance(
            event_or_sequence, typing.Iterable
        ):
            event_or_sequence = self._event_iterable_or_point_sequence_to_event_iterable(  # type: ignore
                event_or_sequence  # type: ignore
            )
        super().__setitem__(index_or_slice, event_or_sequence)  # type: ignore

    # ###################################################################### #
    #                    private static methods                              #
    # ###################################################################### #

    @staticmethod
    def _point_sequence_to_corrected_point_list(
        point_or_invalid_type_sequence: typing.Sequence[Point | typing.Any],
    ) -> list[Envelope.CompletePoint | None]:
        pnorm_list: list[Envelope.CompletePoint | None] = []
        for p in point_or_invalid_type_sequence:
            if (point_size := len(p)) == 2:
                p += (0,)  # type: ignore
            elif point_size != 3:
                raise core_utilities.InvalidPointError(p, point_size)
            pnorm_list.append(p)  # type: ignore
        return pnorm_list

    # ###################################################################### #
    #                         private methods                                #
    # ###################################################################### #

    def _make_event(self, duration, parameter, curve_shape):
        event = self.initialise_default_event_class(duration)
        self.apply_parameter_on_event(event, parameter)
        self.apply_curve_shape_on_event(event, curve_shape)
        return event

    def _point_sequence_to_event_list(
        self,
        point_or_invalid_type_sequence: typing.Sequence[Point | typing.Any],
    ) -> list[core_events.abc.Event]:
        pnorm_list = Envelope._point_sequence_to_corrected_point_list(
            point_or_invalid_type_sequence
        )
        pnorm_list.append(None)
        event_list = []
        for p0, p1 in zip(pnorm_list, pnorm_list[1:]):
            if p0 is not None:
                abst0, value_or_parameter, curve_shape = p0
            else:
                raise TypeError("Found unexpected position of None in provided points.")
            if p1:
                abst1 = p1[0]
                assert abst1 >= abst0
            else:
                abst1 = abst0
            duration = abst1 - abst0
            event = self._make_event(duration, value_or_parameter, curve_shape)
            event_list.append(event)
        return event_list

    def _event_iterable_or_point_sequence_to_event_iterable(
        self,
        event_iterable_or_point_sequence: typing.Iterable[T] | typing.Sequence[Point],
    ) -> typing.Iterable[core_events.abc.Event]:
        item_type_list = [
            isinstance(event_or_point, core_events.abc.Event)
            for event_or_point in event_iterable_or_point_sequence
        ]
        if all(item_type_list):
            event_iterable = event_iterable_or_point_sequence
        elif any(item_type_list):
            raise TypeError(
                "Found inconsistent iterable with mixed types. "
                "Please only use events or only use points for "
                "'event_iterable_or_point_sequence'. First 200 "
                "characters of the problematic iterable: \n"
                f"{str(event_iterable_or_point_sequence)[:200]}"
            )
        else:
            event_iterable = self._point_sequence_to_event_list(
                event_iterable_or_point_sequence  # type: ignore
            )
        return event_iterable  # type: ignore

    def _event_to_value(self, event: core_events.abc.Event) -> Value:
        return self.parameter_to_value(self.event_to_parameter(event))

    # Keep this part private so that functions can cache
    # absolute_time_tuple if it helps their performance.
    def _curve_shape_at(
        self,
        abst: "core_parameters.abc.Duration",
        abst_tuple: tuple["core_parameters.abc.Duration", ...],
        dur: "core_parameters.abc.Duration",
    ):
        if not self:
            raise core_utilities.EmptyEnvelopeError(self, "curve_shape_at")
        e_idx = core_events.Consecution._get_index_at_from_absolute_time_tuple(
            abst, abst_tuple, dur
        )
        if e_idx is not None:
            e = self[e_idx]
            cs = self.event_to_curve_shape(e)
            csx = ((abst - abst_tuple[e_idx]) / e.duration).beat_count * cs
            cs_at_abst = cs - csx
            self.apply_curve_shape_on_event(e, csx)
        else:
            cs_at_abst = 0
        return cs_at_abst

    def _value_at(
        self,
        abst: "core_parameters.abc.Duration",
        abst_tuple: tuple["core_parameters.abc.Duration", ...],
        dur: "core_parameters.abc.Duration",
    ):
        abstf = abst.beat_count
        abstf_tuple = tuple(map(float, abst_tuple))
        durf = float(dur)

        try:
            use_only_first_event = abstf <= abstf_tuple[0]
        except IndexError:
            raise core_utilities.EmptyEnvelopeError(self, "value_at")

        use_only_last_event = abstf >= (
            # If the duration of the last event == 0 there is the danger
            # of floating point errors (the value in absolute_time_tuple could
            # be slightly higher than the duration of the Envelope. If this
            # happens the function raises an AssertionError, because
            # "_get_index_at_from_absolute_time_tuple" returns
            # "None"). With explicitly testing if the last duration
            # equals 0 we can avoid this danger.
            abstf_tuple[-1]
            if self[-1].duration > 0
            else durf
        )
        if use_only_first_event or use_only_last_event:
            index = 0 if use_only_first_event else -1
            return self._event_to_value(self[index])

        event_0_index = self._get_index_at_from_absolute_time_tuple(
            abstf, abstf_tuple, durf
        )
        assert event_0_index is not None

        v0, v1 = (self._event_to_value(self[event_0_index + n]) for n in range(2))
        cs = self.event_to_curve_shape(self[event_0_index])

        return core_utilities.scale(
            abstf,
            abstf_tuple[event_0_index],
            abstf_tuple[event_0_index + 1],
            v0,
            v1,
            cs,
        )

    def _parameter_at(
        self,
        abst: "core_parameters.abc.Duration",
        abst_tuple: tuple["core_parameters.abc.Duration", ...],
        dur: "core_parameters.abc.Duration",
    ):
        return self.value_to_parameter(self._value_at(abst, abst_tuple, dur))

    def _point_at(
        self,
        abst: "core_parameters.abc.Duration",
        abst_tuple: tuple["core_parameters.abc.Duration", ...],
        dur: "core_parameters.abc.Duration",
    ):
        if not self:
            raise core_utilities.EmptyEnvelopeError(self, "point_at")
        if abst not in abst_tuple:
            point = (
                abst,
                self._value_at(abst, abst_tuple, dur),
                self._curve_shape_at(abst, abst_tuple, dur),
            )
        else:
            e = self[abst_tuple.index(abst)]
            point = (abst, self._event_to_value(e), self.event_to_curve_shape(e))
        return point

    # ###################################################################### #
    #                         public properties                              #
    # ###################################################################### #

    @property
    def parameter_tuple(self) -> tuple[typing.Any, ...]:
        """Get `parameter` for each event inside :class:`Envelope`."""
        return tuple(map(self.event_to_parameter, self))

    @property
    def value_tuple(self) -> tuple[Value, ...]:
        """Get `value` for each event inside :class:`Envelope`."""
        return tuple(map(self.parameter_to_value, self.parameter_tuple))

    @property
    def curve_shape_tuple(self) -> tuple[CurveShape, ...]:
        """Get `curve_shape` for each event inside :class:`Envelope`."""
        return tuple(map(self.event_to_curve_shape, self))

    @property
    def is_static(self) -> bool:
        """Return `True` if :class:`Envelope` only has one static value."""
        return len(set(self.value_tuple)) <= 1

    # ###################################################################### #
    #                          public methods                                #
    # ###################################################################### #

    def event_to_parameter(self, event: core_events.abc.Event) -> typing.Any:
        """Fetch 'parameter' from event."""
        return event.value

    def event_to_curve_shape(self, event: core_events.abc.Event) -> core_constants.Real:
        """Fetch 'curve_shape' from event."""
        return event.curve_shape

    def parameter_to_value(self, parameter: typing.Any) -> core_constants.Real:
        """Convert from 'parameter' to 'value'."""
        return parameter

    def value_to_parameter(self, value: core_constants.Real) -> typing.Any:
        """Convert from 'value' to 'parameter'."""
        return value

    def apply_parameter_on_event(
        self, event: core_events.abc.Event, parameter: typing.Any
    ):
        """Apply 'parameter' on given event"""
        event.value = parameter

    def apply_curve_shape_on_event(
        self, event: core_events.abc.Event, curve_shape: core_constants.Real
    ):
        """Apply 'curve_shape' on given event"""
        event.curve_shape = curve_shape

    def initialise_default_event_class(
        self, duration: core_parameters.abc.Duration
    ) -> core_events.abc.Event:
        """Create new event object from event type."""
        return self.default_event_class(duration=duration)

    def value_at(self, absolute_time: "core_parameters.abc.Duration.Type") -> Value:
        """Get `value` at `absolute_time`.

        :param absolute_time: Absolute position in time at which value shall be found.
            This is 'x' in the function notation 'f(x)'.
        :type absolute_time: core_parameters.abc.Duration.Type

        This function interpolates between the control points according to
        their `curve_shape` property.

        **Example:**

        >>> from mutwo import core_events
        >>> e = core_events.Envelope([[0, 0], [1, 2]])
        >>> e.value_at(0)
        0
        >>> e.value_at(1)
        2
        >>> e.value_at(0.5)
        1.0
        """
        abst = core_parameters.abc.Duration.from_any(absolute_time)
        return self._value_at(abst, *self._abst_tuple_and_dur)

    def parameter_at(
        self, absolute_time: "core_parameters.abc.Duration.Type"
    ) -> typing.Any:
        """Get `parameter` at `absolute_time`.

        :param absolute_time: Absolute position in time at which parameter shall
            be found. This is 'x' in the function notation 'f(x)'.
        :type absolute_time: core_parameters.abc.Duration.Type
        """
        return self.value_to_parameter(self.value_at(absolute_time))

    def curve_shape_at(
        self, absolute_time: "core_parameters.abc.Duration.Type"
    ) -> float:
        """Get `curve_shape` at `absolute_time`.

        :param absolute_time: Absolute position in time at which curve shape shall
            be found. This is 'x' in the function notation 'f(x)'.
        :type absolute_time: core_parameters.abc.Duration.Type
        """
        abst = core_parameters.abc.Duration.from_any(absolute_time)
        return self._curve_shape_at(abst, *self._abst_tuple_and_dur)

    def point_at(
        self,
        absolute_time: "core_parameters.abc.Duration.Type",
    ):
        """Get `point` at `absolute_time`.

        :param absolute_time: Absolute position in time at which point shall
            be found. This is 'x' in the function notation 'f(x)'.
        :type absolute_time: core_parameters.abc.Duration.Type

        A point is a tuple with (absolute_time, value, curve_shape).
        """
        abst = core_parameters.abc.Duration.from_any(absolute_time)
        return self._point_at(abst, *self._abst_tuple_and_dur)

    def sample_at(
        self,
        absolute_time: "core_parameters.abc.Duration.Type",
        append_duration: "core_parameters.abc.Duration.Type" = 0,
    ) -> Envelope:
        """Discretize envelope at given time

        :param absolute_time: Position in time where the envelope should
            define a new event.
        :type absolute_time: core_parameters.abc.Duration.Type
        :param append_duration: In case we add a new control point after any
            already defined point, the duration of this control point will be
            equal to "append_duration". Default to core_parameters.DirectDuration(0)
        """

        def find_dur(
            abst: "core_parameters.abc.Duration",
            abst_tuple: tuple["core_parameters.abc.Duration", ...],
        ):
            """Find duration of new control point"""
            next_event_start_index = bisect.bisect_right(abst_tuple, abst)
            try:
                next_event_start = abst_tuple[next_event_start_index]
            # In case we call "sample_at" at a position after any already
            # specified point.
            except IndexError:
                return append_duration
            else:
                return next_event_start - abst

        if not self:
            raise core_utilities.EmptyEnvelopeError(self, "sample_at")

        abst, append_duration = (
            core_parameters.abc.Duration.from_any(o)
            for o in (absolute_time, append_duration)
        )

        self._assert_valid_absolute_time(abst)
        abst_tuple, dur = self._abst_tuple_and_dur

        # We only add a new event in case there isn't any event yet at
        # given point in time.
        if abst not in abst_tuple:
            p = self._point_at(abst, abst_tuple, dur)
            e = self._make_event(
                find_dur(abst, abst_tuple), self.value_to_parameter(p[1]), p[2]
            )

            try:
                self.squash_in(abst, e)
            # This means we want to squash in at a position much
            # later than any already defined event.
            except core_utilities.InvalidStartValueError:
                difference = abst - dur
                self[-1].duration += difference
                self.append(e)

        return self

    def time_range_to_point_tuple(
        self, time_range: ranges.Range
    ) -> tuple[CompletePoint, ...]:
        """Return all control points in given time range.

        :param time_range: Start and end time encapsulated in a
            :class:`ranges.Range` object.
        :type time_range: ranges.Range

        If at start and end time aren't any control points, the functions
        creates them ad-hoc via ``point_at``.
        """
        start, end = (
            core_parameters.abc.Duration.from_any(o)
            for o in (time_range.start, time_range.end)
        )
        abst_tuple, dur = self._abst_tuple_and_dur
        p = functools.partial(  # point_at
            self._point_at, abst_tuple=abst_tuple, dur=dur
        )

        plist = []
        if start not in abst_tuple:
            plist.append(p(start))
            i0 = bisect.bisect_left(abst_tuple, start)
        else:
            i0 = abst_tuple.index(start)
        if end not in abst_tuple:
            i1 = bisect.bisect_left(abst_tuple, end)
            last_point = p(end)
        else:
            i1 = abst_tuple.index(end) + 1
            last_point = None
        for t, ev in zip(abst_tuple[i0:i1], self[i0:i1]):
            plist.append((t, self._event_to_value(ev), self.event_to_curve_shape(ev)))
        if last_point is not None:
            plist.append(last_point)
        return tuple(plist)

    def integrate_interval(
        self,
        start: "core_parameters.abc.Duration.Type",
        end: "core_parameters.abc.Duration.Type",
    ) -> float:
        """Integrate envelope above given interval.

        :param start: Beginning of integration interval.
        :type start: core_parameters.abc.Duration.Type
        :param end: End of integration interval.
        :type end: core_parameters.abc.Duration.Type
        """
        start, end = (core_parameters.abc.Duration.from_any(o) for o in (start, end))
        if start == end:
            return 0

        point_tuple = self.time_range_to_point_tuple(ranges.Range(start, end))
        integral = 0
        for p0, p1 in zip(point_tuple, point_tuple[1:]):
            t0, v0, cchr0 = p0  # (absolute_time, value, curve_shape)
            t1, v1, _ = p1
            if (d0 := float(t1 - t0)) > 0:
                if cchr0 != 0:
                    # See https://git.sr.ht/~marcevanstein/expenvelope/tree/cd4a3710/item/expenvelope/envelope_segment.py#L102-103
                    A = v0 - (v1 - v0) / (math.exp(cchr0) - 1)
                    B = (v1 - v0) / (cchr0 * (math.exp(cchr0) - 1))

                    def antiderivative(tn):
                        # See https://git.sr.ht/~marcevanstein/expenvelope/tree/cd4a3710/item/expenvelope/envelope_segment.py#L239
                        return A * tn + B * math.exp(cchr0 * tn)

                    a0, a1 = (antiderivative(i) for i in (0, 1))
                    integral += d0 * (a1 - a0)
                else:  # linear interpolation
                    diff = v1 - v0 if v1 > v0 else v0 - v1
                    square = d0 * min((v0, v1))
                    triangle = 0.5 * d0 * diff
                    integral += square + triangle

        return float(integral)

    def get_average_value(
        self,
        start: typing.Optional["core_parameters.abc.Duration.Type"] = None,
        end: typing.Optional["core_parameters.abc.Duration.Type"] = None,
    ) -> Value:
        """Find average `value` in given interval.

        :param start: The beginning of the interval. If set to `None` this
            is set to0. Default to `None`.
        :type start: typing.Optional[core_parameters.abc.Duration.Type]
        :param end: The end of the interval. If set to `None` this
            is set to the duration of the :class:`Envelope`.. Default to `None`.
        :type end: typing.Optional[core_parameters.abc.Duration.Type]

        **Example:**

        >>> from mutwo import core_events
        >>> e = core_events.Envelope([[0, 1], [2, 0]])
        >>> e.get_average_value()
        0.5
        >>> e.get_average_value(0.5)
        0.375
        >>> e.get_average_value(0.5, 1)
        0.625
        """
        if start is None:
            start = core_parameters.DirectDuration(0)
        if end is None:
            end = self.duration

        start, end = (core_parameters.abc.Duration.from_any(o) for o in (start, end))

        duration = end - start
        if duration == 0:
            self._logger.warning(core_utilities.InvalidAverageValueStartAndEndWarning())
            return self.value_at(start)
        return self.integrate_interval(start, end) / duration.beat_count

    def get_average_parameter(
        self,
        start: typing.Optional["core_parameters.abc.Duration.Type"] = None,
        end: typing.Optional["core_parameters.abc.Duration.Type"] = None,
    ) -> typing.Any:
        """Find average `parameter` in given interval.

        :param start: The beginning of the interval. If set to `None` this
            is set be 0. Default to `None`.
        :type start: typing.Optional[core_parameters.abc.Duration.Type]
        :param end: The end of the interval. If set to `None` this
            is set to the duration of the :class:`Envelope`.. Default to `None`.
        :type end: typing.Optional[core_parameters.abc.Duration.Type]

        **Example:**

        >>> from mutwo import core_events
        >>> e = core_events.Envelope([[0, 1], [2, 0]])
        >>> e.get_average_parameter()
        0.5
        >>> e.get_average_parameter(0.5)
        0.375
        >>> e.get_average_parameter(0.5, 1)
        0.625
        """
        return self.value_to_parameter(self.get_average_value(start, end))

    def cut_out(
        self,
        start: "core_parameters.abc.Duration.Type",
        end: "core_parameters.abc.Duration.Type",
    ) -> Envelope[T]:
        start, end = (core_parameters.abc.Duration.from_any(o) for o in (start, end))
        # _assert_correct_start_and_end_values and _assert_valid_absolute_time
        # is called when super().cut_out is called later.

        self.sample_at(start, append_duration=end - start)
        self.sample_at(end)

        last_point = self.get_event_at(end)

        # In case last_point.duration == 0 "get_event_at" won't return
        # any object. This only happens in case
        #
        #   end > self.duration
        #
        # So the new point will be appended.
        if last_point is None:
            last_point = self[-1]
        assert last_point

        cut_out_envelope = super().cut_out(start, end)
        cut_out_envelope.append(last_point.set("duration", 0))

        return cut_out_envelope

    def cut_off(
        self,
        start: "core_parameters.abc.Duration.Type",
        end: "core_parameters.abc.Duration.Type",
    ) -> Envelope[T]:
        start, end = (core_parameters.abc.Duration.from_any(o) for o in (start, end))
        self._assert_valid_absolute_time(start)
        self._assert_correct_start_and_end_values(
            start, end, condition=lambda start, end: start < end
        )

        if (cut_off_duration := end - start) > 0:
            # It is sufficient to find the first control point
            # by simply using "parameter_at" instead of "sample_at":
            # We don't need an accurate curve_shape or duration,
            # because this point only exists in an infinitely short
            # moment in time anyway (or better: its main function is
            # to ensure that interpolation from the previous point
            # to this point works as expected).
            parameter_0 = self.parameter_at(start)
            event_0 = self._make_event(0, parameter_0, 0)

            self.sample_at(end)

            self._cut_off(start, end, cut_off_duration)
            self.squash_in(start, event_0)

        return self

    def extend_until(
        self,
        duration: "core_parameters.abc.Duration.Type",
        duration_to_white_space: typing.Optional[
            typing.Callable[["core_parameters.abc.Duration"], core_events.abc.Event]
        ] = None,
        prolong_chronon: bool = True,
    ) -> Envelope[T]:
        if not self:
            raise core_utilities.EmptyEnvelopeError(self, "extend_until")
        return self.sample_at(duration)

    def split_at(
        self,
        *absolute_time: "core_parameters.abc.Duration.Type",
        ignore_invalid_split_point: bool = False,
    ) -> tuple[Envelope, ...]:
        if not absolute_time:
            raise core_utilities.NoSplitTimeError()

        abst_list = sorted(
            [core_parameters.abc.Duration.from_any(t) for t in absolute_time]
        )
        if abst_list[-1] > self.duration and not ignore_invalid_split_point:
            raise core_utilities.SplitError(abst_list[-1])

        # We copy, because the 'sample_at' calls would change our envelope.
        self = self.copy()

        for t in abst_list:
            self.sample_at(t)

        def add(s, value):
            s.append(s._make_event(0, s.value_to_parameter(value), 0))

        segment_tuple = super().split_at(
            *abst_list, ignore_invalid_split_point=ignore_invalid_split_point
        )

        # We already added the interpolation points with 'self.sample_at(*t)',
        # but they are always only available in the segments after the split
        # point (because for each segment the start is included, but the end
        # duration isn't included anymore). So we need to add them to the
        # segments before the split points, otherwise 'value_at' returns wrong
        # values.
        for segment0, segment1 in zip(segment_tuple, segment_tuple[1:]):
            add(segment0, segment1.value_at(0))

        if segment_tuple:
            s = segment_tuple[-1]
            v = self.value_at(self.duration)
            # Only add control point, if it isn't present
            # yet anyway (minimal changes).
            # This condition is 'true' if we only split at
            # start time ('env.split_at(0)').
            if s.value_at(s.duration) != v:
                add(s, v)

        return segment_tuple
