"""This module contains the most basic event classes which can be used.

The different events differ in their timing structure and whether they
are nested or not:
"""

import copy
import itertools
import numbers
import types
import typing

from mutwo import events
from mutwo import parameters
from mutwo.utilities import decorators
from mutwo.utilities import tools


__all__ = ("SimpleEvent", "SequentialEvent", "SimultaneousEvent", "EnvelopeEvent")


class SimpleEvent(events.abc.Event):
    """Event-Object, which doesn't contain other Event-Objects.

    :param new_duration: The duration of the SimpleEvent.

    >>> from mutwo.events import basic
    >>> simple_event = basic.SimpleEvent(2)
    >>> print(simple_event)
    SimpleEvent(duration = 2)
    """

    def __init__(self, new_duration: parameters.abc.DurationType):
        self.duration = new_duration

    def __eq__(self, other: typing.Any) -> bool:
        """Test for checking if two objects are equal."""
        try:
            return self._is_equal(other) and other._is_equal(self)
        except AttributeError:
            return False

    def __repr__(self) -> str:
        attributes = (
            "{} = {}".format(attribute, getattr(self, attribute))
            for attribute in self._parameters_to_compare
        )
        return "{}({})".format(type(self).__name__, ", ".join(attributes))

    def _is_equal(self, other: typing.Any) -> bool:
        """Helper function to inspect if two SimpleEvent objects are equal."""

        for parameter_to_compare in self._parameters_to_compare:
            try:
                # if the assigned values of the specific parameter aren't
                # equal, both objects can't be equal
                if getattr(self, parameter_to_compare) != getattr(
                    other, parameter_to_compare
                ):
                    return False

            # if the other object doesn't know the essential parameter
            # mutwo assumes that both objects can't be equal
            except AttributeError:
                return False

        # if all compared parameters are equal, return True
        return True

    @property
    def _parameters_to_compare(self) -> typing.Tuple[str]:
        """Return tuple of attribute names which values define the SimpleEvent.

        The returned attribute names are used for equality check between two
        SimpleEvent objects.
        """
        return tuple(
            attribute
            for attribute in dir(self)
            # no private attributes
            if attribute[0] != "_"
            # no methods
            and not isinstance(getattr(self, attribute), types.MethodType)
        )

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, new_duration: parameters.abc.DurationType):
        self._duration = new_duration

    def destructive_copy(self) -> "SimpleEvent":
        return copy.deepcopy(self)

    def get_parameter(self, parameter_name: str) -> typing.Any:
        """Return event attribute with the entered name.

        :parameter_name: The name of the attribute that shall be returned.
        :returns: Return the value that has been assigned to the passed
            parameter_name. If an event doesn't posses the asked parameter,
            the method will simply return None.
        """
        try:
            return getattr(self, parameter_name)
        except AttributeError:
            return None

    @decorators.add_return_option
    def set_parameter(
        self,
        parameter_name: str,
        object_or_function: typing.Union[
            typing.Callable[[parameters.abc.Parameter], parameters.abc.Parameter],
            typing.Any,
        ],
    ) -> None:
        """Sets event parameter to new value.

        :param parameter_name: The name of the parameter which values shall be changed.
        :param object_or_function: For setting the parameter either a new value can be
            passed directly or a function can be passed. The function gets as an
            argument the previous value that has had been assigned to the respective
            object and has to return a new value that will be assigned to the object.
        """

        old_parameter = self.get_parameter(parameter_name)
        try:
            new_parameter = object_or_function(old_parameter)
        except TypeError:
            new_parameter = object_or_function
        setattr(self, parameter_name, new_parameter)

    @decorators.add_return_option
    def mutate_parameter(
        self,
        parameter_name: str,
        function: typing.Union[
            typing.Callable[[parameters.abc.Parameter], None], typing.Any
        ],
    ) -> None:
        parameter = self.get_parameter(parameter_name)
        if parameter is not None:
            function(parameter)

    @decorators.add_return_option
    def cut_up(
        self, start: parameters.abc.DurationType, end: parameters.abc.DurationType,
    ) -> typing.Union[None, "SimpleEvent"]:
        self._assert_correct_start_and_end_values(start, end)

        duration = self.duration

        difference_to_duration = 0

        if start > 0:
            difference_to_duration += start
        if end < duration:
            difference_to_duration += duration - end

        try:
            assert difference_to_duration < duration
        except AssertionError:
            message = (
                "Can't cut up SimpleEvent '{}' with duration '{}' from (start = {} to"
                " end = {}).".format(self, duration, start, end)
            )
            raise ValueError(message)

        self.duration -= difference_to_duration


T = typing.TypeVar("T")


class SequentialEvent(events.abc.ComplexEvent, typing.Generic[T]):
    """Event-Object which contains other Events which happen in a linear order."""

    @events.abc.ComplexEvent.duration.getter
    def duration(self):
        return sum(event.duration for event in self)

    @property
    def absolute_times(self) -> typing.Tuple[numbers.Number]:
        """Return absolute point in time for each event."""

        durations = (event.duration for event in self)
        return tuple(tools.accumulate_from_zero(durations))[:-1]

    @property
    def start_and_end_time_per_event(
        self,
    ) -> typing.Tuple[typing.Tuple[numbers.Number]]:
        """Return start and end time for each event."""

        durations = (event.duration for event in self)
        absolute_times = tuple(tools.accumulate_from_zero(durations))
        return tuple(zip(absolute_times, absolute_times[1:]))

    def get_event_at(self, absolute_time: numbers.Number) -> events.abc.Event:
        """Get event which is active at the passed absolute_time.

            :param absolute_time: The absolute time where the method shall search
                for the active event.

        >>> from mutwo.events import basic
        >>> sequential_event = basic.SequentialEvent([basic.SimpleEvent(2), basic.SimpleEvent(3)])
        >>> sequential_event.get_event_at(1)
        SimpleEvent(duration = 2)
        >>> sequential_event.get_event_at(3)
        SimpleEvent(duration = 3)
        """

        absolute_times = self.absolute_times
        after_absolute_time = itertools.dropwhile(
            lambda x: absolute_time < x[0],
            zip(reversed(absolute_times), reversed(self)),
        )
        return next(after_absolute_time)[1]

    @decorators.add_return_option
    def cut_up(
        self, start: parameters.abc.DurationType, end: parameters.abc.DurationType,
    ) -> typing.Union[None, "SequentialEvent"]:
        self._assert_correct_start_and_end_values(start, end)

        cut_up_events = []

        for event_start, event in zip(self.absolute_times, self):
            event_end = event_start + event.duration
            appendable_conditions = (
                event_start >= start and event_start < end,
                event_end <= end and event_end > start,
                event_start <= start and event_end >= end,
            )

            appendable = any(appendable_conditions)
            if appendable:
                cut_up_start = 0
                cut_up_end = event.duration

                if event_start < start:
                    cut_up_start += start - event_start

                if event_end > end:
                    cut_up_end -= event_end - end

                if cut_up_start < cut_up_end:
                    event = event.cut_up(cut_up_start, cut_up_end, mutate=False)
                    cut_up_events.append(event)

        self[:] = cut_up_events


class SimultaneousEvent(events.abc.ComplexEvent, typing.Generic[T]):
    """Event-Object which contains other Event-Objects which happen at the same time."""

    @events.abc.ComplexEvent.duration.getter
    def duration(self) -> parameters.abc.DurationType:
        return max(event.duration for event in self)

    @decorators.add_return_option
    def cut_up(
        self, start: parameters.abc.DurationType, end: parameters.abc.DurationType,
    ) -> typing.Union[None, "SimultaneousEvent"]:
        self._assert_correct_start_and_end_values(start, end)
        cut_up_events = []

        for event in self:
            cut_up_events.append(event.cut_up(start, end, mutate=False))

        self[:] = cut_up_events


class EnvelopeEvent(SimpleEvent):
    def __init__(
        self,
        duration: parameters.abc.DurationType,
        object_start: typing.Any,
        object_stop: typing.Any = None,
        curve_shape: float = 0,
        key: typing.Callable[[typing.Any], numbers.Number] = lambda object_: object_,
    ):
        super().__init__(duration)

        self.key = key
        if object_stop is None:
            object_stop = copy.deepcopy(object_start)

        self.object_start = object_start
        self.object_stop = object_stop
        self.curve_shape = curve_shape

    @property
    def value_start(self) -> numbers.Number:
        return self.key(self.object_start)

    @property
    def value_stop(self) -> numbers.Number:
        return self.key(self.object_stop)

    def __repr__(self) -> str:
        return "{}({}: {} to {})".format(
            type(self).__name__, self.duration, self.value_start, self.value_stop
        )

    def is_static(self) -> bool:
        return self.value_start == self.value_stop
