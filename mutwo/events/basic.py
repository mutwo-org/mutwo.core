"""Generic event classes which can be used in multiple contexts.

The different events differ in their timing structure and whether they
are nested or not:
"""

from __future__ import annotations

import bisect
import copy
import types
import typing

from mutwo import events
from mutwo import parameters
from mutwo.utilities import constants
from mutwo.utilities import decorators
from mutwo.utilities import exceptions
from mutwo.utilities import tools


__all__ = (
    "SimpleEvent",
    "SequentialEvent",
    "SimultaneousEvent",
    "TaggedSimpleEvent",
    "TaggedSequentialEvent",
    "TaggedSimultaneousEvent",
)


class SimpleEvent(events.abc.Event):
    """Event-Object which doesn't contain other Event-Objects (the node or leaf).

    :param new_duration: The duration of the ``SimpleEvent``. This can be any number.
        The unit of the duration is up to the interpretation of the user and the
        respective converter routine that will be used.

    **Example:**

    >>> from mutwo.events import basic
    >>> simple_event = basic.SimpleEvent(2)
    >>> print(simple_event)
    SimpleEvent(duration = 2)
    """

    def __init__(self, new_duration: parameters.abc.DurationType):
        self.duration = new_duration

    # ###################################################################### #
    #                           magic methods                                #
    # ###################################################################### #

    def __eq__(self, other: typing.Any) -> bool:
        """Test for checking if two objects are equal."""
        try:
            return self._is_equal(other) and other._is_equal(self)
        except AttributeError:
            return False

    def __repr__(self) -> str:
        attributes = (
            "{} = {}".format(attribute, getattr(self, attribute))
            for attribute in self._parameters_to_print
        )
        return "{}({})".format(type(self).__name__, ", ".join(attributes))

    # ###################################################################### #
    #                           properties                                   #
    # ###################################################################### #

    @property
    def _parameters_to_print(self) -> typing.Tuple[str, ...]:
        """Return tuple of attribute names which shall be printed for repr."""
        return self._parameters_to_compare

    @property
    def _parameters_to_compare(self) -> typing.Tuple[str, ...]:
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
    def duration(self) -> parameters.abc.DurationType:
        return tools.round_floats(
            self._duration, events.basic_constants.ROUND_DURATION_TO_N_DIGITS
        )

    @duration.setter
    def duration(self, new_duration: parameters.abc.DurationType):
        self._duration = new_duration

    # ###################################################################### #
    #                           private methods                              #
    # ###################################################################### #

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

    # ###################################################################### #
    #                           public methods                               #
    # ###################################################################### #

    def destructive_copy(self) -> SimpleEvent:
        return copy.deepcopy(self)

    def get_parameter(self, parameter_name: str) -> typing.Any:
        """Return event attribute with the entered name.

        :parameter_name: The name of the attribute that shall be returned.
        :returns: Return the value that has been assigned to the passed
            parameter_name. If an event doesn't posses the asked parameter,
            the method will simply return None.

        **Example:**

        >>> from mutwo.events import basic
        >>> simple_event = basic.SimpleEvent(2)
        >>> simple_event.pitch = 200
        >>> simple_event.get_parameter('pitch')
        200
        >>> simple_event.get_parameter('pitches')
        None
        """
        try:
            return getattr(self, parameter_name)
        except AttributeError:
            return None

    @decorators.add_return_option
    def set_parameter(  # type: ignore
        self,
        parameter_name: str,
        object_or_function: typing.Union[
            typing.Callable[[parameters.abc.Parameter], parameters.abc.Parameter],
            typing.Any,
        ],
        set_unassigned_parameter: bool = True,
    ) -> typing.Optional[SimpleEvent]:
        """Sets event parameter to new value.

        :param parameter_name: The name of the parameter which values shall be changed.
        :param object_or_function: For setting the parameter either a new value can be
            passed directly or a function can be passed. The function gets as an
            argument the previous value that has had been assigned to the respective
            object and has to return a new value that will be assigned to the object.
        :param set_unassigned_parameter: If set to False a new parameter will only be
            assigned to an Event if the Event already has a attribute with the
            respective `parameter_name`. If the Event doesn't know the attribute yet
            and `set_unassigned_parameter` is False, the method call will simply be
            ignored.

        **Example:**

        >>> from mutwo.events import basic
        >>> simple_event = basic.SimpleEvent(2)
        >>> simple_event.set_parameter('duration', lambda old_duration: old_duration * 2)
        >>> simple_event.duration
        4
        >>> simple_event.set_parameter('duration', 3)
        >>> simple_event.duration
        3
        >>> simple_event.set_parameter('unknown_parameter', 10, set_unassigned_parameter=False)  # this will be ignored
        >>> simple_event.unknown_parameter
        AttributeError: 'SimpleEvent' object has no attribute 'unknown_parameter'
        >>> simple_event.set_parameter('unknown_parameter', 10, set_unassigned_parameter=True)  # this will be written
        >>> simple_event.unknown_parameter
        10
        """

        old_parameter = self.get_parameter(parameter_name)
        if set_unassigned_parameter or old_parameter is not None:
            if hasattr(object_or_function, "__call__"):
                new_parameter = object_or_function(old_parameter)
            else:
                new_parameter = object_or_function
            setattr(self, parameter_name, new_parameter)

    @decorators.add_return_option
    def mutate_parameter(  # type: ignore
        self,
        parameter_name: str,
        function: typing.Union[
            typing.Callable[[parameters.abc.Parameter], None], typing.Any
        ],
    ) -> typing.Optional[SimpleEvent]:
        parameter = self.get_parameter(parameter_name)
        if parameter is not None:
            function(parameter)

    @decorators.add_return_option
    def cut_out(  # type: ignore
        self, start: parameters.abc.DurationType, end: parameters.abc.DurationType,
    ) -> typing.Optional[SimpleEvent]:
        self._assert_correct_start_and_end_values(
            start, end, condition=lambda start, end: start < end
        )

        duration = self.duration

        difference_to_duration: constants.Real = 0

        if start > 0:
            difference_to_duration += start
        if end < duration:
            difference_to_duration += duration - end

        try:
            assert difference_to_duration < duration
        except AssertionError:
            message = (
                f"Can't cut out SimpleEvent '{self}' with duration '{duration}' from"
                f" (start = {start} to end = {end})."
            )
            raise ValueError(message)

        self.duration -= difference_to_duration

    @decorators.add_return_option
    def cut_off(  # type: ignore
        self, start: parameters.abc.DurationType, end: parameters.abc.DurationType,
    ) -> typing.Optional[SimpleEvent]:
        self._assert_correct_start_and_end_values(start, end)

        duration = self.duration
        if start < duration:
            if end > duration:
                end = duration

            self.duration -= end - start


T = typing.TypeVar("T", bound=events.abc.Event)


class SequentialEvent(events.abc.ComplexEvent, typing.Generic[T]):
    """Event-Object which contains other Events which happen in a linear order."""

    # ###################################################################### #
    #                    private static methods                              #
    # ###################################################################### #

    @staticmethod
    def _get_index_at_from_absolute_times(
        absolute_time: parameters.abc.DurationType,
        absolute_times: typing.Tuple[parameters.abc.DurationType, ...],
        duration: parameters.abc.DurationType,
    ) -> typing.Optional[int]:
        if absolute_time < duration and absolute_time >= 0:
            return bisect.bisect_right(absolute_times, absolute_time) - 1
        else:
            return None

    # ###################################################################### #
    #                           properties                                   #
    # ###################################################################### #

    @events.abc.ComplexEvent.duration.getter
    def duration(self) -> parameters.abc.DurationType:
        return tools.round_floats(
            sum(event.duration for event in self),
            events.basic_constants.ROUND_DURATION_TO_N_DIGITS,
        )

    @property
    def absolute_times(self) -> typing.Tuple[constants.Real, ...]:
        """Return absolute point in time for each event."""

        durations = (event.duration for event in self)
        return tuple(tools.accumulate_from_zero(durations))[:-1]

    @property
    def start_and_end_time_per_event(
        self,
    ) -> typing.Tuple[typing.Tuple[constants.Real, constants.Real], ...]:
        """Return start and end time for each event."""

        durations = (event.duration for event in self)
        absolute_times = tuple(tools.accumulate_from_zero(durations))
        return tuple(zip(absolute_times, absolute_times[1:]))

    # ###################################################################### #
    #                           public methods                               #
    # ###################################################################### #

    def get_event_index_at(
        self, absolute_time: parameters.abc.DurationType
    ) -> typing.Optional[int]:
        """Get index of event which is active at the passed absolute_time.

        :param absolute_time: The absolute time where the method shall search
            for the active event.
        :type absolute_time: parameters.abc.DurationType
        :return: Index of event if there is any event at the requested absolute time
            and ``None`` if there isn't any event.

        **Example:**

        >>> from mutwo.events import basic
        >>> sequential_event = basic.SequentialEvent([basic.SimpleEvent(2), basic.SimpleEvent(3)])
        >>> sequential_event.get_event_index_at(1)
        0
        >>> sequential_event.get_event_index_at(3)
        1
        >>> sequential_event.get_event_index_at(100)
        None
        """

        absolute_times = self.absolute_times
        return SequentialEvent._get_index_at_from_absolute_times(
            absolute_time, absolute_times, self.duration
        )

    def get_event_at(
        self, absolute_time: parameters.abc.DurationType
    ) -> typing.Optional[T]:
        """Get event which is active at the passed absolute_time.

        :param absolute_time: The absolute time where the method shall search
            for the active event.
        :type absolute_time: parameters.abc.DurationType
        :return: Event if there is any event at the requested absolute time
            and ``None`` if there isn't any event.

        **Example:**

        >>> from mutwo.events import basic
        >>> sequential_event = basic.SequentialEvent([basic.SimpleEvent(2), basic.SimpleEvent(3)])
        >>> sequential_event.get_event_at(1)
        SimpleEvent(duration = 2)
        >>> sequential_event.get_event_at(3)
        SimpleEvent(duration = 3)
        >>> sequential_event.get_event_at(100)
        None
        """

        event_index = self.get_event_index_at(absolute_time)
        if event_index is None:
            return None
        else:
            return self[event_index]  # type: ignore

    @decorators.add_return_option
    def cut_out(  # type: ignore
        self, start: parameters.abc.DurationType, end: parameters.abc.DurationType,
    ) -> typing.Optional[SequentialEvent[T]]:
        self._assert_correct_start_and_end_values(start, end)

        remove_nth_event = []
        for nth_event, event_start, event in zip(
            range(len(self)), self.absolute_times, self
        ):
            event_duration = event.duration
            event_end = event_start + event_duration

            cut_out_start: constants.Real = 0
            cut_out_end = event_duration

            if event_start < start:
                cut_out_start += start - event_start

            if event_end > end:
                cut_out_end -= event_end - end

            if cut_out_start < cut_out_end:
                event.cut_out(cut_out_start, cut_out_end)
            else:
                remove_nth_event.append(nth_event)

        for nth_event_to_remove in reversed(remove_nth_event):
            del self[nth_event_to_remove]

    @decorators.add_return_option
    def cut_off(  # type: ignore
        self, start: parameters.abc.DurationType, end: parameters.abc.DurationType,
    ) -> typing.Optional[SequentialEvent[T]]:
        cut_off_duration = end - start

        # avoid unnecessary iterations
        if cut_off_duration > 0:

            # collect events which are only active within the
            # cut_off - range
            events_to_delete = []
            for event_index, event_start, event in zip(
                range(len(self)), self.absolute_times, self
            ):
                event_end = event_start + event.duration
                if event_start >= start and event_end <= end:
                    events_to_delete.append(event_index)

                # shorten event which are partly active within the
                # cut_off - range
                elif event_start <= start and event_end >= start:
                    difference_to_event_start = start - event_start
                    event.cut_off(
                        difference_to_event_start,
                        difference_to_event_start + cut_off_duration,
                    )

                elif event_start < end and event_end > end:
                    difference_to_event_start = event_start - start
                    event.cut_off(0, cut_off_duration - difference_to_event_start)

            for index in reversed(events_to_delete):
                del self[index]

    @decorators.add_return_option
    def squash_in(  # type: ignore
        self, start: parameters.abc.DurationType, event_to_squash_in: events.abc.Event
    ) -> typing.Optional[SequentialEvent[T]]:
        self._assert_start_in_range(start)

        cut_off_end = start + event_to_squash_in.duration

        self.cut_off(start, cut_off_end)

        if start == self.duration:
            self.append(event_to_squash_in)

        else:
            absolute_times = self.absolute_times
            active_event_index = self.get_event_index_at(start)
            split_position = start - absolute_times[active_event_index]
            # avoid floating point error
            rounded_split_position = tools.round_floats(
                split_position, events.basic_constants.ROUND_DURATION_TO_N_DIGITS,
            )
            # potentially split event
            if (
                rounded_split_position > 0
                and rounded_split_position < self[active_event_index].duration
            ):
                split_active_event = self[active_event_index].split_at(rounded_split_position)
                self[active_event_index] = split_active_event[1]
                self.insert(active_event_index, split_active_event[0])
                active_event_index += 1

            self.insert(active_event_index, event_to_squash_in)

    @decorators.add_return_option
    def split_child_at(
        self, absolute_time: parameters.abc.DurationType
    ) -> typing.Optional[SequentialEvent[T]]:
        absolute_times = self.absolute_times
        nth_event = SequentialEvent._get_index_at_from_absolute_times(
            absolute_time, absolute_times, self.duration
        )

        # if there is no event at the requested time, raise error
        if nth_event is None:
            raise exceptions.SplitUnavailableChildError(absolute_time)

        # only try to split child event at the requested time if there isn't
        # a segregation already anyway
        elif absolute_time != absolute_times[nth_event]:
            try:
                end = absolute_times[nth_event + 1]
            except IndexError:
                end = self.duration

            difference = end - absolute_time
            first_event, second_event = self[nth_event].split_at(difference)
            self[nth_event] = first_event
            self.insert(nth_event, second_event)


class SimultaneousEvent(events.abc.ComplexEvent, typing.Generic[T]):
    """Event-Object which contains other Event-Objects which happen at the same time."""

    # ###################################################################### #
    #                           properties                                   #
    # ###################################################################### #

    @events.abc.ComplexEvent.duration.getter
    def duration(self) -> parameters.abc.DurationType:
        return tools.round_floats(
            max(event.duration for event in self),
            events.basic_constants.ROUND_DURATION_TO_N_DIGITS,
        )

    # ###################################################################### #
    #                           public methods                               #
    # ###################################################################### #

    @decorators.add_return_option
    def cut_out(  # type: ignore
        self, start: parameters.abc.DurationType, end: parameters.abc.DurationType,
    ) -> typing.Optional[SimultaneousEvent[T]]:
        self._assert_correct_start_and_end_values(start, end)
        [event.cut_out(start, end) for event in self]

    @decorators.add_return_option
    def cut_off(  # type: ignore
        self, start: parameters.abc.DurationType, end: parameters.abc.DurationType,
    ) -> typing.Optional[SimultaneousEvent[T]]:
        self._assert_correct_start_and_end_values(start, end)
        [event.cut_off(start, end) for event in self]

    @decorators.add_return_option
    def squash_in(  # type: ignore
        self, start: parameters.abc.DurationType, event_to_squash_in: events.abc.Event
    ) -> typing.Optional[SimultaneousEvent[T]]:
        self._assert_start_in_range(start)

        for event in self:
            try:
                event.squash_in(start, event_to_squash_in)  # type: ignore

            # simple events don't have a 'squash_in' method
            except AttributeError:
                message = (
                    f"Can't squash '{event_to_squash_in}' in '{self}'. Does the"
                    " SimultaneousEvent contain SimpleEvents or events that inherit"
                    " from SimpleEvent? For being able to squash in, the"
                    " SimultaneousEvent needs to only contain SequentialEvents or"
                    " SimultaneousEvents."
                )
                raise TypeError(message)

    @decorators.add_return_option
    def split_child_at(
        self, absolute_time: parameters.abc.DurationType
    ) -> typing.Optional[SimultaneousEvent[T]]:
        for nth_event, event in enumerate(self):
            try:
                event.split_child_at(absolute_time)
            # simple events don't have a 'split_child_at' method
            except AttributeError:
                split_event = event.split_at(absolute_time)
                self[nth_event] = SequentialEvent(split_event)


@decorators.add_tag_to_class
class TaggedSimpleEvent(SimpleEvent):
    """:class:`SimpleEvent` with tag."""

    pass


@decorators.add_tag_to_class
class TaggedSequentialEvent(SequentialEvent, typing.Generic[T]):
    """:class:`SequentialEvent` with tag."""

    _class_specific_side_attributes = ("tag",)


@decorators.add_tag_to_class
class TaggedSimultaneousEvent(SimultaneousEvent, typing.Generic[T]):
    """:class:`SimultaneousEvent` with tag."""

    _class_specific_side_attributes = ("tag",)
