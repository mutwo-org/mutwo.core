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


__all__ = ("Envelope", "RelativeEnvelope", "TempoEnvelope")

T = typing.TypeVar("T", bound=core_events.abc.Event)


class Envelope(
    core_events.SequentialEvent,
    typing.Generic[T],
    class_specific_side_attribute_tuple=(
        "event_to_parameter",
        "event_to_curve_shape",
        "value_to_parameter",
        "parameter_to_value",
        "apply_parameter_on_event",
        "apply_curve_shape_on_event",
        "default_event_class",
        "initialise_default_event_class",
    ),
):
    """Model continuous changing values (e.g. glissandi, crescendo).

    :param event_iterable_or_point_sequence: An iterable filled with events
        or with points. If the sequence is filled with points, the points
        will be converted to events. Each event represents a point in a
        two dimensional graph where the x-axis presents time and the y-axis
        a changing value. Any event class can be used. It is
        more important that the used event classes fit with the functions
        passed in the following parameters.
    :type event_iterable_or_point_sequence: typing.Iterable[T]
    :param event_to_parameter: A function which receives an event and has to
        return a parameter object (any object). By default the function will
        ask the event for its `value` property. If the property can't be found
        it will return 0.
    :type event_to_parameter: typing.Callable[[core_events.abc.Event], typing.Any]
    :param event_to_curve_shape: A function which receives an event and has
        to return a curve_shape. A curve_shape is either a float, an integer
        or a fraction. For a curve_shape = 0 a linear transition between two
        points is created. For a curve_shape > 0 the envelope changes slower
        at the beginning and faster at the end, for a curve_shape < 0 it is
        the inverse behaviour. The default function will ask the event for its
        `curve_shape` property. If the property can't be found
        it will return 0.
    :type event_to_curve_shape: typing.Callable[[core_events.abc.Event], CurveShape]
    :param parameter_to_value: Convert a parameter to a value. A value is any
        object which supports mathematical operations.
    :type parameter_to_value: typing.Callable[[Value], typing.Any]
    :param value_to_parameter: A callable object which converts a value to a parameter.
    :type value_to_parameter: typing.Callable[[Value], typing.Any]
    :param apply_parameter_on_event: A callable object which applies a parameter on an event.
    :type apply_parameter_on_event: typing.Callable[[core_events.abc.Event, typing.Any], None]
    :param apply_curve_shape_on_event: A callable object which applies a curve shape on an event.
    :type apply_curve_shape_on_event: typing.Callable[[core_events.abc.Event, CurveShape], None]
    :param default_event_class: The default event class which describes a point.
    :type default_event_class: type[core_events.abc.Event]
    :param initialise_default_event_class:
    :type initialise_default_event_class: typing.Callable[[type[core_events.abc.Event], core_parameters.abc.Duration], core_events.abc.Event]

    This class is inspired by Marc Evansteins `Envelope` class in his
    `expenvelope <https://git.sr.ht/~marcevanstein/expenvelope>`_
    python package and is made to fit better into the `mutwo` ecosystem.

    **Hint:**

    When comparing two envelopes (e.g. `env0 == env1`) `mutwo` will only return
    `True` in case all control points (= simple events inside the envelope) are
    equal between both envelopes. So `mutwo` won't make the much more
    complicated test to check if two envelopes have the same shape (= the same
    value at each `env0.value_at(x) == env1.value_at(x)` for each possible
    `x`). Such a test is not implemented yet.

    **Example:**

    >>> from mutwo import core_events
    >>> core_events.Envelope([[0, 0, 1], [0.5, 1]])
    Envelope([SimpleEvent(curve_shape=1, duration=DirectDuration(0.5), value=0), SimpleEvent(curve_shape=0, duration=DirectDuration(0.0), value=1)])
    """

    # Type definitions
    Value = core_constants.Real
    Parameter = typing.Any
    CurveShape = core_constants.Real
    IncompletePoint = tuple["core_parameters.abc.Duration", Parameter]
    CompletePoint = tuple[
        "core_parameters.abc.Duration", Parameter, CurveShape  # type: ignore
    ]
    Point = CompletePoint | IncompletePoint

    def __init__(
        self,
        event_iterable_or_point_sequence: typing.Iterable[T] | typing.Sequence[Point],
        tempo_envelope: typing.Optional[core_events.TempoEnvelope] = None,
        tag: typing.Optional[str] = None,
        event_to_parameter: typing.Callable[
            [core_events.abc.Event], typing.Any
        ] = lambda event: getattr(
            event, core_events.configurations.DEFAULT_PARAMETER_ATTRIBUTE_NAME
        )
        if hasattr(event, core_events.configurations.DEFAULT_PARAMETER_ATTRIBUTE_NAME)
        else 0,
        event_to_curve_shape: typing.Callable[
            [core_events.abc.Event], CurveShape
        ] = lambda event: getattr(
            event, core_events.configurations.DEFAULT_CURVE_SHAPE_ATTRIBUTE_NAME
        )
        if hasattr(event, core_events.configurations.DEFAULT_CURVE_SHAPE_ATTRIBUTE_NAME)
        else 0,
        parameter_to_value: typing.Callable[
            [Value], typing.Any
        ] = lambda parameter: parameter,
        value_to_parameter: typing.Callable[
            [Value], typing.Any
        ] = lambda value: value,
        apply_parameter_on_event: typing.Callable[
            [core_events.abc.Event, typing.Any], None
        ] = lambda event, parameter: setattr(
            event,
            core_events.configurations.DEFAULT_PARAMETER_ATTRIBUTE_NAME,
            parameter,
        ),
        apply_curve_shape_on_event: typing.Callable[
            [core_events.abc.Event, CurveShape], None
        ] = lambda event, curve_shape: setattr(
            event,
            core_events.configurations.DEFAULT_CURVE_SHAPE_ATTRIBUTE_NAME,
            curve_shape,
        ),
        default_event_class: type[core_events.abc.Event] = core_events.SimpleEvent,
        initialise_default_event_class: typing.Callable[
            [type[core_events.abc.Event], "core_parameters.abc.Duration"],
            core_events.abc.Event,
        ] = lambda simple_event_class, duration: simple_event_class(
            duration
        ),  # type: ignore
    ):
        self.event_to_parameter = event_to_parameter
        self.event_to_curve_shape = event_to_curve_shape
        self.value_to_parameter = value_to_parameter
        self.parameter_to_value = parameter_to_value
        self.apply_parameter_on_event = apply_parameter_on_event
        self.apply_curve_shape_on_event = apply_curve_shape_on_event
        self.default_event_class = default_event_class
        self.initialise_default_event_class = initialise_default_event_class

        event_iterable = self._event_iterable_or_point_sequence_to_event_iterable(
            event_iterable_or_point_sequence
        )
        super().__init__(event_iterable, tempo_envelope, tag=tag)

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
        corrected_point_list: list[Envelope.CompletePoint | None] = []
        for point in point_or_invalid_type_sequence:
            point_count = len(point)
            if point_count == 2:
                point += (0,)  # type: ignore
            elif point_count != 3:
                raise core_utilities.InvalidPointError(point, point_count)
            corrected_point_list.append(point)  # type: ignore
        return corrected_point_list

    # ###################################################################### #
    #                         private methods                                #
    # ###################################################################### #

    def _make_event(self, duration, parameter, curve_shape):
        event = self.initialise_default_event_class(self.default_event_class, duration)
        self.apply_parameter_on_event(event, parameter)
        self.apply_curve_shape_on_event(event, curve_shape)
        return event

    def _point_sequence_to_event_list(
        self,
        point_or_invalid_type_sequence: typing.Sequence[Point | typing.Any],
    ) -> list[core_events.abc.Event]:
        corrected_point_list = Envelope._point_sequence_to_corrected_point_list(
            point_or_invalid_type_sequence
        )
        corrected_point_list.append(None)
        event_list = []
        for point0, point1 in zip(corrected_point_list, corrected_point_list[1:]):
            if point0 is not None:
                absolute_time0, value_or_parameter, curve_shape = point0
            else:
                raise TypeError("Found unexpected position of None in provided points.")
            if point1:
                absolute_time1 = point1[0]
                assert absolute_time1 >= absolute_time0
            else:
                absolute_time1 = absolute_time0
            duration = absolute_time1 - absolute_time0
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
        absolute_time: "core_parameters.abc.Duration",
        absolute_time_tuple: tuple["core_parameters.abc.Duration", ...],
        duration: "core_parameters.abc.Duration",
    ):
        if not self:
            raise core_utilities.EmptyEnvelopeError(self, "curve_shape_at")
        old_event_index = (
            core_events.SequentialEvent._get_index_at_from_absolute_time_tuple(
                absolute_time, absolute_time_tuple, duration
            )
        )
        if old_event_index is not None:
            old_event = self[old_event_index]
            curve_shape = self.event_to_curve_shape(old_event)
            curve_shape_old_event = (
                (absolute_time - absolute_time_tuple[old_event_index])
                / old_event.duration
            ).duration * curve_shape
            curve_shape_new_event = curve_shape - curve_shape_old_event
            self.apply_curve_shape_on_event(old_event, curve_shape_old_event)
        else:
            curve_shape_new_event = 0

        return curve_shape_new_event

    def _value_at(
        self,
        absolute_time: "core_parameters.abc.Duration",
        absolute_time_tuple: tuple["core_parameters.abc.Duration", ...],
        duration: "core_parameters.abc.Duration",
    ):
        absolute_time_in_floats = absolute_time.duration
        absolute_time_in_floats_tuple = tuple(map(float, absolute_time_tuple))
        duration_in_floats = float(duration)

        try:
            use_only_first_event = (
                absolute_time_in_floats <= absolute_time_in_floats_tuple[0]
            )
        except IndexError:
            raise core_utilities.EmptyEnvelopeError(self, "value_at")

        use_only_last_event = absolute_time_in_floats >= (
            # If the duration of the last event == 0 there is the danger
            # of floating point errors (the value in absolute_time_tuple could
            # be slightly higher than the duration of the Envelope. If this
            # happens the function will raise an AssertionError, because
            # "_get_index_at_from_absolute_time_tuple" will return
            # "None"). With explicitly testing if the last duration
            # equals 0 we can avoid this danger.
            absolute_time_in_floats_tuple[-1]
            if self[-1].duration > 0
            else duration_in_floats
        )
        if use_only_first_event or use_only_last_event:
            index = 0 if use_only_first_event else -1
            return self._event_to_value(self[index])

        event_0_index = self._get_index_at_from_absolute_time_tuple(
            absolute_time, absolute_time_in_floats_tuple, duration_in_floats
        )
        assert event_0_index is not None

        value0, value1 = (
            self._event_to_value(self[event_0_index + n]) for n in range(2)
        )
        curve_shape = self.event_to_curve_shape(self[event_0_index])

        return core_utilities.scale(
            absolute_time_in_floats,
            absolute_time_in_floats_tuple[event_0_index],
            absolute_time_in_floats_tuple[event_0_index + 1],
            value0,
            value1,
            curve_shape,
        )

    def _parameter_at(
        self,
        absolute_time: "core_parameters.abc.Duration",
        absolute_time_tuple: tuple["core_parameters.abc.Duration", ...],
        duration: "core_parameters.abc.Duration",
    ):
        return self.value_to_parameter(
            self._value_at(absolute_time, absolute_time_tuple, duration)
        )

    def _point_at(
        self,
        absolute_time: "core_parameters.abc.Duration",
        absolute_time_tuple: tuple["core_parameters.abc.Duration", ...],
        duration: "core_parameters.abc.Duration",
    ):
        if not self:
            raise core_utilities.EmptyEnvelopeError(self, "point_at")

        if absolute_time not in (absolute_time_tuple := self.absolute_time_tuple):
            point = (
                absolute_time,
                self._value_at(absolute_time, absolute_time_tuple, duration),
                self._curve_shape_at(absolute_time, absolute_time_tuple, duration),
            )

        else:
            e = self[absolute_time_tuple.index(absolute_time)]
            point = (
                absolute_time,
                self._event_to_value(e),
                self.event_to_curve_shape(e),
            )

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

    def value_at(self, absolute_time: "core_parameters.abc.Duration") -> Value:
        """Get `value` at `absolute_time`.

        :param absolute_time: Absolute position in time at which value shall be found.
            This is 'x' in the function notation 'f(x)'.
        :type absolute_time: core_parameters.abc.Duration

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
        absolute_time = core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(
            absolute_time
        )
        return self._value_at(absolute_time, *self._absolute_time_tuple_and_duration)

    def parameter_at(
        self, absolute_time: "core_parameters.abc.Duration"
    ) -> typing.Any:
        """Get `parameter` at `absolute_time`.

        :param absolute_time: Absolute position in time at which parameter shall
            be found. This is 'x' in the function notation 'f(x)'.
        :type absolute_time: core_parameters.abc.Duration
        """
        return self.value_to_parameter(self.value_at(absolute_time))

    def curve_shape_at(self, absolute_time: "core_parameters.abc.Duration") -> float:
        """Get `curve_shape` at `absolute_time`.

        :param absolute_time: Absolute position in time at which curve shape shall
            be found. This is 'x' in the function notation 'f(x)'.
        :type absolute_time: core_parameters.abc.Duration
        """
        absolute_time = core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(
            absolute_time
        )
        return self._curve_shape_at(
            absolute_time, *self._absolute_time_tuple_and_duration
        )

    def point_at(
        self,
        absolute_time: "core_parameters.abc.Duration",
    ):
        """Get `point` at `absolute_time`.

        :param absolute_time: Absolute position in time at which point shall
            be found. This is 'x' in the function notation 'f(x)'.
        :type absolute_time: core_parameters.abc.Duration

        A point is a tuple with (absolute_time, value, curve_shape).
        """
        absolute_time = core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(
            absolute_time
        )
        return self._point_at(
            absolute_time,
            *self._absolute_time_tuple_and_duration,
        )

    def sample_at(
        self,
        absolute_time: "core_parameters.abc.Duration",
        append_duration: "core_parameters.abc.Duration" = 0,
    ) -> Envelope:
        """Discretize envelope at given time

        :param absolute_time: Position in time where the envelope should
            define a new event.
        :type absolute_time: core_parameters.abc.Duration
        :param append_duration: In case we add a new control point after any
            already defined point, the duration of this control point will be
            equal to "append_duration". Default to core_parameters.DirectDuration(0)
        """

        def find_duration(
            absolute_time: "core_parameters.abc.Duration",
            absolute_time_tuple: tuple["core_parameters.abc.Duration", ...],
        ):
            """Find duration of new control point"""
            next_event_start_index = bisect.bisect_right(
                absolute_time_tuple, absolute_time
            )
            try:
                next_event_start = absolute_time_tuple[next_event_start_index]
            # In case we call "sample_at" at a position after any already
            # specified point.
            except IndexError:
                duration_new_event = append_duration
            else:
                duration_new_event = next_event_start - absolute_time

            return duration_new_event

        if not self:
            raise core_utilities.EmptyEnvelopeError(self, "sample_at")

        absolute_time, append_duration = (
            core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(unknown_object)
            for unknown_object in (absolute_time, append_duration)
        )

        self._assert_valid_absolute_time(absolute_time)

        absolute_time_tuple, duration = self._absolute_time_tuple_and_duration

        # We only add a new event in case there isn't any event yet at
        # given point in time.
        if absolute_time not in absolute_time_tuple:
            point = self._point_at(
                absolute_time,
                absolute_time_tuple,
                duration,
            )
            event = self._make_event(
                find_duration(absolute_time, absolute_time_tuple),
                self.value_to_parameter(point[1]),
                point[2],
            )

            try:
                self.squash_in(absolute_time, event)
            # This means we want to squash in at a position much
            # later than any already defined event.
            except core_utilities.InvalidStartValueError:
                difference = absolute_time - duration
                self[-1].duration += difference
                self.append(event)

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
            core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(o)
            for o in (time_range.start, time_range.end)
        )
        absolute_time_tuple, duration = self._absolute_time_tuple_and_duration

        p = functools.partial(  # point_at
            self._point_at, absolute_time_tuple=absolute_time_tuple, duration=duration
        )

        point_list = []

        if start not in absolute_time_tuple:
            point_list.append(p(start))
            i0 = bisect.bisect_left(absolute_time_tuple, start)
        else:
            i0 = absolute_time_tuple.index(start)

        if end not in absolute_time_tuple:
            i1 = bisect.bisect_left(absolute_time_tuple, end)
            last_point = p(end)
        else:
            i1 = absolute_time_tuple.index(end) + 1
            last_point = None

        for t, ev in zip(absolute_time_tuple[i0:i1], self[i0:i1]):
            point_list.append(
                (t, self._event_to_value(ev), self.event_to_curve_shape(ev))
            )

        if last_point is not None:
            point_list.append(last_point)

        return tuple(point_list)

    def integrate_interval(
        self, start: "core_parameters.abc.Duration", end: "core_parameters.abc.Duration"
    ) -> float:
        """Integrate envelope above given interval.

        :param start: Beginning of integration interval.
        :type start: core_parameters.abc.Duration
        :param end: End of integration interval.
        :type end: core_parameters.abc.Duration
        """
        start, end = (
            core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(t)
            for t in (start, end)
        )
        if start == end:
            return 0

        point_tuple = self.time_range_to_point_tuple(ranges.Range(start, end))
        integral = 0
        for p0, p1 in zip(point_tuple, point_tuple[1:]):
            t0, v0, cs0 = p0  # (absolute_time, value, curve_shape)
            t1, v1, _ = p1
            if (d0 := float(t1 - t0)) > 0:
                if cs0 != 0:
                    # See https://git.sr.ht/~marcevanstein/expenvelope/tree/cd4a3710/item/expenvelope/envelope_segment.py#L102-103
                    A = v0 - (v1 - v0) / (math.exp(cs0) - 1)
                    B = (v1 - v0) / (cs0 * (math.exp(cs0) - 1))

                    def antiderivative(tn):
                        # See https://git.sr.ht/~marcevanstein/expenvelope/tree/cd4a3710/item/expenvelope/envelope_segment.py#L239
                        return A * tn + B * math.exp(cs0 * tn)

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
        start: typing.Optional["core_parameters.abc.Duration"] = None,
        end: typing.Optional["core_parameters.abc.Duration"] = None,
    ) -> Value:
        """Find average `value` in given interval.

        :param start: The beginning of the interval. If set to `None` this
            will be 0. Default to `None`.
        :type start: typing.Optional[core_parameters.abc.Duration]
        :param end: The end of the interval. If set to `None` this
            will be the duration of the :class:`Envelope`.. Default to `None`.
        :type end: typing.Optional[core_parameters.abc.Duration]

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

        start, end = (
            core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(unknown_object)
            for unknown_object in (start, end)
        )

        duration = end - start
        if duration == 0:
            self._logger.warning(core_utilities.InvalidAverageValueStartAndEndWarning())
            return self.value_at(start)
        return self.integrate_interval(start, end) / duration.duration

    def get_average_parameter(
        self,
        start: typing.Optional["core_parameters.abc.Duration"] = None,
        end: typing.Optional["core_parameters.abc.Duration"] = None,
    ) -> typing.Any:
        """Find average `parameter` in given interval.

        :param start: The beginning of the interval. If set to `None` this
            will be 0. Default to `None`.
        :type start: typing.Optional[core_parameters.abc.Duration]
        :param end: The end of the interval. If set to `None` this
            will be the duration of the :class:`Envelope`.. Default to `None`.
        :type end: typing.Optional[core_parameters.abc.Duration]

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
        start: "core_parameters.abc.Duration",
        end: "core_parameters.abc.Duration",
    ) -> Envelope[T]:
        start, end = (
            core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(unknown_object)
            for unknown_object in (start, end)
        )
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
        start: "core_parameters.abc.Duration",
        end: "core_parameters.abc.Duration",
    ) -> Envelope[T]:
        start, end = (
            core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(unknown_object)
            for unknown_object in (start, end)
        )
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
        duration: "core_parameters.abc.Duration",
        duration_to_white_space: typing.Optional[
            typing.Callable[["core_parameters.abc.Duration"], core_events.abc.Event]
        ] = None,
        prolong_simple_event: bool = True,
    ) -> Envelope[T]:
        if not self:
            raise core_utilities.EmptyEnvelopeError(self, "extend_until")
        return self.sample_at(duration)

    def split_at(
        self,
        *absolute_time: "core_parameters.abc.Duration",
        ignore_invalid_split_point: bool = False,
    ) -> tuple[Envelope, ...]:
        if not absolute_time:
            raise core_utilities.NoSplitTimeError()

        absolute_time = sorted(absolute_time)
        if absolute_time[-1] > self.duration and not ignore_invalid_split_point:
            raise core_utilities.SplitError(absolute_time[-1])

        # We copy, because the 'sample_at' calls would change our envelope.
        self = self.copy()

        for t in absolute_time:
            self.sample_at(t)

        def add(s, value):
            s.append(s._make_event(0, s.value_to_parameter(value), 0))

        segment_tuple = super().split_at(
            *absolute_time, ignore_invalid_split_point=ignore_invalid_split_point
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


class RelativeEnvelope(Envelope, typing.Generic[T]):
    __parent_doc_string = Envelope.__doc__.split("\n")[2:]  # type: ignore
    __after_parameter_text_index = __parent_doc_string.index("")
    __doc__ = "\n".join(
        ["Envelope with relative durations and values / parameters.\n"]
        + __parent_doc_string[:__after_parameter_text_index]
        + [
            "    :param base_parameter_and_relative_parameter_to_absolute_parameter: A function",
            "        which runs when the :func:`resolve` is called. It expects the base parameter",
            "        and the relative parameter (which is extracted from the envelope events)",
            "        and should return an absolute parameter.",
        ]
        + __parent_doc_string[__after_parameter_text_index:]
        + [
            "    The :class:`RelativeEnvelope` adds the :func:`resolve` method",
            "    to the base class :class:`Envelope`.",
        ]
    )

    def __init__(
        self,
        *args,
        base_parameter_and_relative_parameter_to_absolute_parameter: typing.Callable[
            [typing.Any, typing.Any],
            typing.Any,
        ],
        **kwargs,
    ):
        self.base_parameter_and_relative_parameter_to_absolute_parameter = (
            base_parameter_and_relative_parameter_to_absolute_parameter
        )
        super().__init__(*args, **kwargs)

    def resolve(
        self,
        duration: "core_parameters.abc.Duration",
        base_parameter: typing.Any,
        resolve_envelope_class: type[Envelope] = Envelope,
    ) -> Envelope:
        duration = core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(duration)
        point_list = []
        try:
            duration_factor = duration / self.duration
        except ZeroDivisionError:
            duration_factor = core_parameters.DirectDuration(0)
        for absolute_time, event in zip(self.absolute_time_tuple, self):
            relative_parameter = self.event_to_parameter(event)
            new_parameter = (
                self.base_parameter_and_relative_parameter_to_absolute_parameter(
                    base_parameter, relative_parameter
                )
            )
            point = (
                absolute_time * duration_factor,
                new_parameter,
                self.event_to_curve_shape(event),
            )
            point_list.append(point)
        return resolve_envelope_class(point_list)


TempoPoint: typing.TypeAlias = "core_parameters.abc.TempoPoint | core_constants.Real"


class TempoEnvelope(Envelope):
    """Define dynamic or static tempo trajectories.

    You can either define a new `TempoEnvelope` with instances
    of classes which inherit from :class:`mutwo.core_parameters.abc.TempoPoint`
    (for instance :class:`mutwo.core_parameters.DirectTempoPoint`) or with
    `float` or `int` objects which represent beats per minute.

    Please see the :class:`mutwo.core_events.Envelope` for full documentation
    for initialization attributes.

    The default parameters of the `TempoEnvelope` class expects
    :class:`mutwo.core_events.SimpleEvent` to which a tempo point
    was assigned by the name "tempo_point". This is specified in the global
    `mutwo.core_events.configurations.DEFAULT_TEMPO_ENVELOPE_PARAMETER_NAME`
    and can be adjusted.

    **Example:**

    >>> from mutwo import core_events
    >>> from mutwo import core_parameters
    >>> # (1) define with floats
    >>> #     So we have an envelope which moves from tempo 60 to 30
    >>> #     and back to 60.
    >>> tempo_envelope_with_float = core_events.TempoEnvelope(
    ...     [[0, 60], [1, 30], [2, 60]]
    ... )
    >>> # (2) define with tempo points
    >>> tempo_envelope_with_tempo_points = core_events.TempoEnvelope(
    ...     [
    ...         [0, core_parameters.DirectTempoPoint(60)],
    ...         [1, core_parameters.DirectTempoPoint(30)],
    ...         [2, core_parameters.DirectTempoPoint(30, reference=2)],
    ...     ]
    ... )
    """

    def __init__(
        self,
        *args,
        event_to_parameter: typing.Optional[
            typing.Callable[[core_events.abc.Event], typing.Any]
        ] = None,
        value_to_parameter: typing.Optional[
            typing.Callable[[core_events.Envelope.Value], typing.Any]
        ] = None,
        parameter_to_value: typing.Optional[
            typing.Callable[[typing.Any], core_events.Envelope.Value]
        ] = None,
        apply_parameter_on_event: typing.Optional[
            typing.Callable[[core_events.abc.Event, typing.Any], None]
        ] = None,
        default_event_class: type[core_events.abc.Event] = core_events.TempoEvent,
        initialise_default_event_class: typing.Callable[
            [type[core_events.abc.Event], "core_parameters.abc.Duration"],
            core_events.abc.Event,
        ] = lambda simple_event_class, duration: simple_event_class(
            tempo_point=1, duration=duration
        ),
        **kwargs,
    ):
        def default_event_to_parameter(event: core_events.abc.Event) -> TempoPoint:
            return getattr(
                event,
                core_events.configurations.DEFAULT_TEMPO_ENVELOPE_PARAMETER_NAME,
            )

        def default_value_to_parameter(value: float) -> TempoPoint:
            return core_parameters.DirectTempoPoint(value)

        def default_parameter_to_value(parameter: TempoPoint) -> float:
            # Here we specify, that we allow either core_parameters.abc.TempoPoint
            # or float/number objects.
            # So in case we have a core_parameters.abc.TempoPoint 'getattr' is
            # successful, if not it will return 'parameter', because it
            # will assume that we have a number based tempo point.
            return float(
                getattr(parameter, "absolute_tempo_in_beats_per_minute", parameter)
            )

        def default_apply_parameter_on_event(
            event: core_events.abc.Event, parameter: TempoPoint
        ):
            setattr(
                event,
                core_events.configurations.DEFAULT_TEMPO_ENVELOPE_PARAMETER_NAME,
                parameter,
            )

        super().__init__(
            *args,
            event_to_parameter=event_to_parameter or default_event_to_parameter,
            value_to_parameter=value_to_parameter or default_value_to_parameter,
            parameter_to_value=parameter_to_value or default_parameter_to_value,
            apply_parameter_on_event=apply_parameter_on_event
            or default_apply_parameter_on_event,
            default_event_class=default_event_class,
            initialise_default_event_class=initialise_default_event_class,
            **kwargs,
        )

    def __eq__(self, other: typing.Any):
        # TempoEnvelope can't use the default '__eq__' method inherited
        # from list, because this would create endless recursion
        # (because every event has a TempoEnvelope, so Python would forever
        #  compare the TempoEnvelopes of TempoEnvelopes).
        try:
            return (
                # Prefer lazy evaluation for better performance
                # (use 'and' instead of 'all').
                self.absolute_time_tuple == other.absolute_time_tuple
                and self.curve_shape_tuple == other.curve_shape_tuple
                and self.value_tuple == other.value_tuple
            )
        except AttributeError:
            return False
