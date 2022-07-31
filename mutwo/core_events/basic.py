"""Generic event classes which can be used in multiple contexts.

The different events differ in their timing structure and whether they
are nested or not:
"""

from __future__ import annotations

import bisect
import copy
import functools
import operator
import types
import typing

import ranges

from mutwo import core_constants
from mutwo import core_events
from mutwo import core_parameters
from mutwo import core_utilities


__all__ = (
    "SimpleEvent",
    "SequentialEvent",
    "SimultaneousEvent",
    "TaggedSimpleEvent",
    "TaggedSequentialEvent",
    "TaggedSimultaneousEvent",
)


class SimpleEvent(core_events.abc.Event):
    """Event-Object which doesn't contain other Event-Objects (the node or leaf).

    :param duration: The duration of the ``SimpleEvent``. Mutwo will convert
        the incoming object to a :class:`mutwo.core_parameters.abc.Duration` object
        with the global `core_events.configurations.UNKNOWN_OBJECT_TO_DURATION`
        callable.

    **Example:**

    >>> from mutwo import core_events
    >>> simple_event = core_events.SimpleEvent(2)
    >>> print(simple_event)
    SimpleEvent(duration = DirectDuration(2))
    """

    parameter_to_exclude_from_representation_tuple = ("tempo_envelope",)

    def __init__(
        self,
        duration: core_parameters.abc.Duration,
        tempo_envelope: typing.Optional[core_events.TempoEnvelope] = None,
    ):
        super().__init__(tempo_envelope)
        self.duration = duration

    # ###################################################################### #
    #                           magic methods                                #
    # ###################################################################### #

    def __eq__(self, other: typing.Any) -> bool:
        """Test for checking if two objects are equal."""
        try:
            parameter_to_compare_set = set([])
            for object_ in (self, other):
                for parameter_to_compare in object_._parameter_to_compare_tuple:
                    parameter_to_compare_set.add(parameter_to_compare)
        except AttributeError:
            return False
        return core_utilities.test_if_objects_are_equal_by_parameter_tuple(
            self, other, tuple(parameter_to_compare_set)
        )

    def __repr__(self) -> str:
        attribute_iterator = (
            "{} = {}".format(attribute, getattr(self, attribute))
            for attribute in self._parameter_to_print_tuple
        )
        return "{}({})".format(type(self).__name__, ", ".join(attribute_iterator))

    # ###################################################################### #
    #                           properties                                   #
    # ###################################################################### #

    @property
    def _parameter_to_print_tuple(self) -> tuple[str, ...]:
        """Return tuple of attribute names which shall be printed for repr."""
        # XXX: Fix infinite circular loop (due to 'tempo_envelope')
        # and avoid printing too verbose parameters.
        return tuple(
            filter(
                lambda attribute: attribute
                not in self.parameter_to_exclude_from_representation_tuple,
                self._parameter_to_compare_tuple,
            )
        )

    @property
    def _parameter_to_compare_tuple(self) -> tuple[str, ...]:
        """Return tuple of attribute names which values define the :class:`SimpleEvent`.

        The returned attribute names are used for equality check between two
        :class:`SimpleEvent` objects.
        """
        return tuple(
            attribute
            for attribute in dir(self)
            # XXX: We have to use 'and' (lazy evaluation) instead of
            #      'all', to avoid redundant checks!
            #
            # no private attributes
            if attribute[0] != "_"
            # no redundant comparisons
            and attribute not in ("parameter_to_exclude_from_representation_tuple",)
            # no methods
            and not isinstance(getattr(self, attribute), types.MethodType)
        )

    @property
    def duration(self) -> core_parameters.abc.Duration:
        return self._duration

    @duration.setter
    def duration(self, duration: core_parameters.abc.Duration):
        self._duration = core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(duration)

    # ###################################################################### #
    #                           public methods                               #
    # ###################################################################### #

    def destructive_copy(self) -> SimpleEvent:
        return copy.deepcopy(self)

    def get_parameter(
        self, parameter_name: str, flat: bool = False, filter_undefined: bool = False
    ) -> core_constants.ParameterType:
        return getattr(self, parameter_name, None)

    @core_utilities.add_copy_option
    def set_parameter(  # type: ignore
        self,
        parameter_name: str,
        object_or_function: typing.Union[
            typing.Callable[
                [core_constants.ParameterType], core_constants.ParameterType
            ],
            core_constants.ParameterType,
        ],
        set_unassigned_parameter: bool = True,
    ) -> SimpleEvent:
        """Sets event parameter to new value.

        :param parameter_name: The name of the parameter which values shall be changed.
        :param object_or_function: For setting the parameter either a new value can be
            passed directly or a function can be passed. The function gets as an
            argument the previous value that has had been assigned to the respective
            object and has to return a new value that will be assigned to the object.
        :param set_unassigned_parameter: If set to ``False`` a new parameter will only
            be assigned to an Event if the Event already has a attribute with the
            respective `parameter_name`. If the Event doesn't know the attribute yet
            and `set_unassigned_parameter` is False, the method call will simply be
            ignored.
        :param mutate: If ``False`` the function will return a copy of the given object.
            If set to ``True`` the object itself will be changed and the function will
            return the changed object. Default to ``True``.

        **Example:**

        >>> from mutwo import core_events
        >>> simple_event = core_events.SimpleEvent(2)
        >>> simple_event.set_parameter(
        >>>     'duration', lambda old_duration: old_duration * 2
        >>> )
        >>> simple_event.duration
        4
        >>> simple_event.set_parameter('duration', 3)
        >>> simple_event.duration
        3
        >>> simple_event.set_parameter(
        >>>     'unknown_parameter', 10, set_unassigned_parameter=False
        >>> )  # this will be ignored
        >>> simple_event.unknown_parameter
        AttributeError: 'SimpleEvent' object has no attribute 'unknown_parameter'
        >>> simple_event.set_parameter(
        >>>     'unknown_parameter', 10, set_unassigned_parameter=True
        >>> )  # this will be written
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

    @core_utilities.add_copy_option
    def mutate_parameter(  # type: ignore
        self,
        parameter_name: str,
        function: typing.Union[
            typing.Callable[[core_constants.ParameterType], None], typing.Any
        ],
    ) -> SimpleEvent:
        parameter = self.get_parameter(parameter_name)
        if parameter is not None:
            function(parameter)

    def metrize(self, mutate: bool = True) -> SimpleEvent:
        # XXX: import in method to avoid circular import error
        metrized_event = __import__(
            "mutwo.core_converters"
        ).core_converters.EventToMetrizedEvent()(self)
        if mutate:
            self.duration = metrized_event.duration
            self.tempo_envelope = metrized_event.tempo_envelope
            return self
        else:
            return metrized_event

    @core_utilities.add_copy_option
    def cut_out(  # type: ignore
        self,
        start: core_parameters.abc.Duration,
        end: core_parameters.abc.Duration,
    ) -> SimpleEvent:
        start, end = (
            core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(unknown_object)
            for unknown_object in (start, end)
        )
        self._assert_correct_start_and_end_values(
            start, end, condition=lambda start, end: start < end
        )

        duration = self.duration

        difference_to_duration: core_parameters.DirectDuration = (
            core_parameters.DirectDuration(0)
        )

        if start > 0:
            difference_to_duration += start
        if end < duration:
            difference_to_duration += duration - end

        if difference_to_duration >= duration:
            raise core_utilities.InvalidCutOutStartAndEndValuesError(
                start, end, self, duration
            )

        self.duration -= difference_to_duration

    @core_utilities.add_copy_option
    def cut_off(  # type: ignore
        self,
        start: core_parameters.abc.Duration,
        end: core_parameters.abc.Duration,
    ) -> SimpleEvent:
        start, end = (
            core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(unknown_object)
            for unknown_object in (start, end)
        )

        self._assert_correct_start_and_end_values(start, end)

        duration = self.duration
        if start < duration:
            if end > duration:
                end = duration

            self.duration -= end - start


T = typing.TypeVar("T", bound=core_events.abc.Event)


class SequentialEvent(core_events.abc.ComplexEvent, typing.Generic[T]):
    """Event-Object which contains other Events which happen in a linear order."""

    # ###################################################################### #
    #                    private static methods                              #
    # ###################################################################### #

    @staticmethod
    def _get_index_at_from_absolute_time_tuple(
        absolute_time: typing.Union[core_parameters.abc.Duration, typing.Any],
        absolute_time_tuple: tuple[core_constants.DurationType, ...],
        duration: core_constants.DurationType,
    ) -> typing.Optional[int]:
        absolute_time = core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(
            absolute_time
        )
        if absolute_time < duration and absolute_time >= 0:
            return bisect.bisect_right(absolute_time_tuple, absolute_time) - 1
        else:
            return None

    # ###################################################################### #
    #                           properties                                   #
    # ###################################################################### #

    @core_events.abc.ComplexEvent.duration.getter
    def duration(self) -> core_parameters.abc.Duration:
        try:
            return functools.reduce(operator.add, (event.duration for event in self))
        # If SequentialEvent is empty
        except TypeError:
            return core_parameters.DirectDuration(0)

    @property
    def absolute_time_tuple(self) -> tuple[core_constants.Real, ...]:
        """Return absolute point in time for each event."""

        duration_iterator = (event.duration for event in self)
        return tuple(
            core_utilities.accumulate_from_n(
                duration_iterator, core_parameters.DirectDuration(0)
            )
        )[:-1]

    @property
    def start_and_end_time_per_event(
        self,
    ) -> tuple[ranges.Range, ...]:
        """Return start and end time for each event."""

        duration_iterator = (event.duration for event in self)
        absolute_time_tuple = tuple(
            core_utilities.accumulate_from_n(
                duration_iterator, core_parameters.DirectDuration(0)
            )
        )
        return tuple(
            ranges.Range(*start_and_end_time)
            for start_and_end_time in zip(absolute_time_tuple, absolute_time_tuple[1:])
        )

    # ###################################################################### #
    #                           public methods                               #
    # ###################################################################### #

    def get_event_index_at(
        self, absolute_time: typing.Union[core_parameters.abc.Duration, typing.Any]
    ) -> typing.Optional[int]:
        """Get index of event which is active at the passed absolute_time.

        :param absolute_time: The absolute time where the method shall search
            for the active event.
        :type absolute_time: typing.Union[core_parameters.abc.Duration, typing.Any]
        :return: Index of event if there is any event at the requested absolute time
            and ``None`` if there isn't any event.

        **Example:**

        >>> from mutwo import core_events
        >>> sequential_event = core_events.SequentialEvent([core_events.SimpleEvent(2), core_events.SimpleEvent(3)])
        >>> sequential_event.get_event_index_at(1)
        0
        >>> sequential_event.get_event_index_at(3)
        1
        >>> sequential_event.get_event_index_at(100)
        None
        """

        absolute_time_tuple = self.absolute_time_tuple
        return SequentialEvent._get_index_at_from_absolute_time_tuple(
            absolute_time, absolute_time_tuple, self.duration
        )

    def get_event_at(
        self, absolute_time: typing.Union[core_parameters.abc.Duration, typing.Any]
    ) -> typing.Optional[T]:
        """Get event which is active at the passed absolute_time.

        :param absolute_time: The absolute time where the method shall search
            for the active event.
        :type absolute_time: typing.Union[core_parameters.abc.Duration, typing.Any]
        :return: Event if there is any event at the requested absolute time
            and ``None`` if there isn't any event.

        **Example:**

        >>> from mutwo import core_events
        >>> sequential_event = core_events.SequentialEvent([core_events.SimpleEvent(2), core_events.SimpleEvent(3)])
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

    @core_utilities.add_copy_option
    def cut_out(  # type: ignore
        self,
        start: core_constants.DurationType,
        end: core_constants.DurationType,
    ) -> SequentialEvent[T]:
        start, end = (
            core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(unknown_object)
            for unknown_object in (start, end)
        )
        self._assert_correct_start_and_end_values(start, end)

        event_to_remove_index_list = []
        for event_index, event_start, event in zip(
            range(len(self)), self.absolute_time_tuple, self
        ):
            event_duration = event.duration
            event_end = event_start + event_duration

            cut_out_start: core_parameters.DirectDuration = (
                core_parameters.DirectDuration(0)
            )
            cut_out_end = event_duration

            if event_start < start:
                cut_out_start += start - event_start

            if event_end > end:
                cut_out_end -= event_end - end

            if cut_out_start < cut_out_end:
                event.cut_out(cut_out_start, cut_out_end)
            elif not (
                # XXX: Support special case of events with duration = 0.
                event.duration == 0
                and event_start >= start
                and event_start <= end
            ):
                event_to_remove_index_list.append(event_index)

        for event_to_remove_index in reversed(event_to_remove_index_list):
            del self[event_to_remove_index]

    @core_utilities.add_copy_option
    def cut_off(  # type: ignore
        self,
        start: core_constants.DurationType,
        end: core_constants.DurationType,
    ) -> SequentialEvent[T]:
        start, end = (
            core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(unknown_object)
            for unknown_object in (start, end)
        )
        cut_off_duration = end - start

        # Avoid unnecessary iterations
        if cut_off_duration > 0:

            # Collect core_events which are only active within the
            # cut_off - range
            event_to_delete_list = []
            for event_index, event_start, event in zip(
                range(len(self)), self.absolute_time_tuple, self
            ):
                event_end = event_start + event.duration
                if event_start >= start and event_end <= end:
                    event_to_delete_list.append(event_index)

                # Shorten event which are partly active within the
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

            for index in reversed(event_to_delete_list):
                del self[index]

    @core_utilities.add_copy_option
    def squash_in(  # type: ignore
        self,
        start: typing.Union[core_parameters.abc.Duration, typing.Any],
        event_to_squash_in: core_events.abc.Event,
    ) -> SequentialEvent[T]:
        start = core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(start)
        self._assert_start_in_range(start)

        cut_off_end = start + event_to_squash_in.duration

        self.cut_off(start, cut_off_end)

        # We already know that the given start is within the
        # range of the event. This means that if the start
        # is bigger than the duration, it is only due to a
        # floating point rounding error. To avoid odd bugs
        # we therefore have to define the bigger-equal
        # relationship.
        if start >= self.duration:
            self.append(event_to_squash_in)

        else:
            absolute_time_tuple = self.absolute_time_tuple
            active_event_index = self.get_event_index_at(start)
            split_position = start - absolute_time_tuple[active_event_index]
            if (
                split_position > 0
                and split_position < self[active_event_index].duration
            ):
                split_active_event = self[active_event_index].split_at(split_position)
                self[active_event_index] = split_active_event[1]
                self.insert(active_event_index, split_active_event[0])
                active_event_index += 1

            self.insert(active_event_index, event_to_squash_in)

    @core_utilities.add_copy_option
    def split_child_at(
        self, absolute_time: typing.Union[core_parameters.abc.Duration, typing.Any]
    ) -> SequentialEvent[T]:
        absolute_time_tuple = self.absolute_time_tuple
        event_index = SequentialEvent._get_index_at_from_absolute_time_tuple(
            absolute_time, absolute_time_tuple, self.duration
        )

        # If there is no event at the requested time, raise error
        if event_index is None:
            raise core_utilities.SplitUnavailableChildError(absolute_time)

        # Only try to split child event at the requested time if there isn't
        # a segregation already anyway
        elif absolute_time != absolute_time_tuple[event_index]:
            try:
                end = absolute_time_tuple[event_index + 1]
            except IndexError:
                end = self.duration

            difference = end - absolute_time
            first_event, second_event = self[event_index].split_at(difference)
            self[event_index] = first_event
            self.insert(event_index, second_event)


class SimultaneousEvent(core_events.abc.ComplexEvent, typing.Generic[T]):
    """Event-Object which contains other Event-Objects which happen at the same time."""

    # ###################################################################### #
    #                           properties                                   #
    # ###################################################################### #

    @core_events.abc.ComplexEvent.duration.getter
    def duration(self) -> core_constants.DurationType:
        try:
            return max(event.duration for event in self)
        # If SimultaneousEvent is empty
        except ValueError:
            return core_parameters.DirectDuration(0)

    # ###################################################################### #
    #                           public methods                               #
    # ###################################################################### #

    @core_utilities.add_copy_option
    def cut_out(  # type: ignore
        self,
        start: typing.Union[core_parameters.abc.Duration, typing.Any],
        end: typing.Union[core_parameters.abc.Duration, typing.Any],
    ) -> SimultaneousEvent[T]:
        start, end = (
            core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(unknown_object)
            for unknown_object in (start, end)
        )
        self._assert_correct_start_and_end_values(start, end)
        [event.cut_out(start, end) for event in self]

    @core_utilities.add_copy_option
    def cut_off(  # type: ignore
        self,
        start: core_constants.DurationType,
        end: core_constants.DurationType,
    ) -> SimultaneousEvent[T]:
        start, end = (
            core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(unknown_object)
            for unknown_object in (start, end)
        )
        self._assert_correct_start_and_end_values(start, end)
        [event.cut_off(start, end) for event in self]

    @core_utilities.add_copy_option
    def squash_in(  # type: ignore
        self,
        start: typing.Union[core_parameters.abc.Duration, typing.Any],
        event_to_squash_in: core_events.abc.Event,
    ) -> SimultaneousEvent[T]:
        start = core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(start)
        self._assert_start_in_range(start)

        for event in self:
            try:
                event.squash_in(start, event_to_squash_in)  # type: ignore
            # Simple events don't have a 'squash_in' method.
            except AttributeError:
                raise core_utilities.ImpossibleToSquashInError(self, event_to_squash_in)

    @core_utilities.add_copy_option
    def split_child_at(
        self, absolute_time: core_constants.DurationType
    ) -> SimultaneousEvent[T]:
        for event_index, event in enumerate(self):
            try:
                event.split_child_at(absolute_time)
            # simple events don't have a 'split_child_at' method
            except AttributeError:
                split_event = event.split_at(absolute_time)
                self[event_index] = SequentialEvent(split_event)


@core_utilities.add_tag_to_class
class TaggedSimpleEvent(SimpleEvent):
    """:class:`SimpleEvent` with tag."""


@core_utilities.add_tag_to_class
class TaggedSequentialEvent(
    SequentialEvent, typing.Generic[T], class_specific_side_attribute_tuple=("tag",)
):
    """:class:`SequentialEvent` with tag."""


@core_utilities.add_tag_to_class
class TaggedSimultaneousEvent(
    SimultaneousEvent, typing.Generic[T], class_specific_side_attribute_tuple=("tag",)
):
    """:class:`SimultaneousEvent` with tag."""
