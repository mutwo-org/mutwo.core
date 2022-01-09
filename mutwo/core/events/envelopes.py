"""Envelope events"""

from __future__ import annotations

import typing

from mutwo.core import events
from mutwo.core.utilities import constants
from mutwo.core.utilities import tools


__all__ = ("Envelope",)

T = typing.TypeVar("T", bound=events.abc.Event)


class Envelope(events.basic.SequentialEvent, typing.Generic[T]):
    """Model continuous changing values (e.g. glissandi, crescendo).

    :param iterable: An iterable filled with events. Each event represents
        a point in a two dimensional graph where the y-axis presents time
        and the x-axis a changing value. Any event class can be used. It is
        more important that the used event classes fit with the functions
        passed in the following parameters.
    :type iterable: typing.Iterable[T]
    :param event_to_value: A function which receives an event and has to
        return a value. A value is any object which support mathematical
        operations. By default the function will ask the event for its
        `value` property. If the property can't be found it will return 0.
    :type event_to_value: typing.Callable[[events.abc.Event], Value]
    :param event_to_curve_shape: A function which receives an event and has
        to return a curve_shape. A curve_shape is either a float, an integer
        or a fraction. For a curve_shape = 0 a linear transition between two
        points is created. For a curve_shape > 0 the envelope changes slower
        at the beginning and faster at the end, for a curve_shape < 0 it is
        the inverse behaviour. The default function will ask the event for its
        `curve_shape` property. If the property can't be found
        it will return 0.
    :type event_to_curve_shape: typing.Callable[[events.abc.Event], CurveShape]

    This class is inspired by Marc Evanstein `Envelope` class in his
    `expenvelope <https://git.sr.ht/~marcevanstein/expenvelope>`_
    python package and made to fit more into the `mutwo` ecosystem.
    """

    Value = constants.Real
    CurveShape = constants.Real

    ValueOrParameter = typing.Union[constants.Real, constants.ParameterType]

    IncompletePoint = tuple[constants.DurationType, ValueOrParameter]
    CompletePoint = tuple[
        constants.DurationType, ValueOrParameter, CurveShape  # type: ignore
    ]
    Point = typing.Union[CompletePoint, IncompletePoint]

    def __init__(
        self,
        iterable: typing.Iterable[T],
        event_to_value: typing.Callable[
            [events.abc.Event], Value
        ] = lambda event: getattr(
            event, events.envelopes_constants.DEFAULT_VALUE_ATTRIBUTE_NAME
        )
        if hasattr(event, events.envelopes_constants.DEFAULT_VALUE_ATTRIBUTE_NAME)
        else 0,
        event_to_curve_shape: typing.Callable[
            [events.abc.Event], CurveShape
        ] = lambda event: getattr(
            event, events.envelopes_constants.DEFAULT_CURVE_SHAPE_ATTRIBUTE_NAME
        )
        if hasattr(event, events.envelopes_constants.DEFAULT_CURVE_SHAPE_ATTRIBUTE_NAME)
        else 0,
    ):
        self.event_to_value = event_to_value
        self.event_to_curve_shape = event_to_curve_shape
        super().__init__(iterable)

    @classmethod
    def from_points(
        cls,
        *point: Point,
        event_class: type = events.basic.SimpleEvent,
        initialise_event_class: typing.Callable[
            [type, constants.DurationType], events.abc.Event
        ] = lambda simple_event, duration: simple_event(duration),
        apply_value_or_parameter_on_event: typing.Callable[
            [events.abc.Event, ValueOrParameter], None
        ] = lambda event, value_or_parameter: setattr(
            event,
            events.envelopes_constants.DEFAULT_VALUE_ATTRIBUTE_NAME,
            value_or_parameter,
        ),
        apply_curve_shape_on_event: typing.Callable[
            [events.abc.Event, CurveShape], None
        ] = lambda event, curve_shape: setattr(
            event,
            events.envelopes_constants.DEFAULT_CURVE_SHAPE_ATTRIBUTE_NAME,
            curve_shape,
        ),
        **kwargs,
    ) -> Envelope:
        corrected_point_list = []
        for point_tuple in point:
            point_length = len(point_tuple)
            if point_length == 2:
                point_tuple += (0,)  # type: ignore
            elif point_length != 3:
                raise TypeError(
                    f"Found invalid point: '{point}' with {point_length} "
                    "items! Points should have two or three items."
                )
            corrected_point_list.append(point_tuple)
        event_list = []
        for point_tuple0, point_tuple1 in zip(
            corrected_point_list, corrected_point_list[1:] + [None]
        ):
            absolute_time0, value_or_parameter, curve_shape = point_tuple0
            if point_tuple1:
                absolute_time1 = point_tuple1[0]
                assert absolute_time1 >= absolute_time0
            else:
                absolute_time1 = absolute_time0
            duration = absolute_time1 - absolute_time0
            event = initialise_event_class(event_class, duration)
            apply_value_or_parameter_on_event(event, value_or_parameter)
            apply_curve_shape_on_event(event, curve_shape)
            event_list.append(event)
        return cls(event_list, **kwargs)

    def value_at(self, absolute_time: constants.DurationType) -> Value:
        absolute_time_tuple = self.absolute_time_tuple

        use_only_first_event = absolute_time <= absolute_time_tuple[0]
        use_only_last_event = absolute_time >= absolute_time_tuple[-1]
        if use_only_first_event or use_only_last_event:
            index = 0 if use_only_first_event else -1
            return self.event_to_value(self[index])

        event_0_index = self._get_index_at_from_absolute_time_tuple(
            absolute_time, absolute_time_tuple, self.duration
        )
        assert event_0_index is not None

        value0, value1 = (
            self.event_to_value(self[event_0_index + n]) for n in range(2)
        )
        curve_shape = self.event_to_curve_shape(self[event_0_index])

        return tools.scale(
            absolute_time,
            absolute_time_tuple[event_0_index],
            absolute_time_tuple[event_0_index + 1],
            value0,
            value1,
            curve_shape,
        )
