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
    SimpleEvent(duration = DirectDuration(duration = 2))
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
    #                           private methods                              #
    # ###################################################################### #

    @core_utilities.add_copy_option
    def _set_parameter(
        self,
        parameter_name: str,
        object_or_function: typing.Callable[
            [core_constants.ParameterType], core_constants.ParameterType
        ]
        | core_constants.ParameterType,
        set_unassigned_parameter: bool,
        id_set: set[int],
    ) -> SimpleEvent:
        old_parameter = self.get_parameter(parameter_name)
        if set_unassigned_parameter or old_parameter is not None:
            if hasattr(object_or_function, "__call__"):
                new_parameter = object_or_function(old_parameter)
            else:
                new_parameter = object_or_function
            setattr(self, parameter_name, new_parameter)

    @core_utilities.add_copy_option
    def _mutate_parameter(
        self,
        parameter_name: str,
        function: typing.Callable[[core_constants.ParameterType], None] | typing.Any,
        id_set: set[int],
    ) -> SimpleEvent:
        parameter = self.get_parameter(parameter_name)
        if parameter is not None:
            function(parameter)

    # ###################################################################### #
    #                           properties                                   #
    # ###################################################################### #

    @property
    def _parameter_to_print_tuple(self) -> tuple[str, ...]:
        """Return tuple of attribute names which shall be printed for repr."""
        # Fix infinite circular loop (due to 'tempo_envelope')
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
            # We have to use 'and' (lazy evaluation) instead of
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

    # Update docstring
    def set_parameter(  # type: ignore
        self,
        *args,
        **kwargs,
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
        ...     'duration', lambda old_duration: old_duration * 2
        ... )
        SimpleEvent(duration = DirectDuration(duration = 4))
        >>> simple_event.duration
        DirectDuration(4)
        >>> simple_event.set_parameter('duration', 3)
        SimpleEvent(duration = DirectDuration(duration = 3))
        >>> simple_event.duration
        DirectDuration(3)
        >>> simple_event.set_parameter(
        ...     'unknown_parameter', 10, set_unassigned_parameter=False
        ... )  # this will be ignored
        SimpleEvent(duration = DirectDuration(duration = 3))
        >>> simple_event.unknown_parameter
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        AttributeError: 'SimpleEvent' object has no attribute 'unknown_parameter'
        >>> simple_event.set_parameter(
        ...     'unknown_parameter', 10, set_unassigned_parameter=True
        ... )  # this will be written
        SimpleEvent(duration = DirectDuration(duration = 3), unknown_parameter = 10)
        >>> simple_event.unknown_parameter
        10
        """

        return super().set_parameter(*args, **kwargs)

    def metrize(self, mutate: bool = True) -> SimpleEvent:
        metrized_event = self._event_to_metrized_event(self)
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
        self._assert_valid_absolute_time(start)
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

        self._assert_valid_absolute_time(start)
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
    #                           magic methods                                #
    # ###################################################################### #

    def __add__(self, event: list[T]) -> SequentialEvent[T]:
        e = self.copy()
        e._concatenate_tempo_envelope(event)
        e.extend(event)
        return e

    # ###################################################################### #
    #                    private static methods                              #
    # ###################################################################### #

    @staticmethod
    def _get_index_at_from_absolute_time_tuple(
        absolute_time: float,
        absolute_time_tuple: float,
        duration: float,
    ) -> typing.Optional[int]:
        if absolute_time < duration and absolute_time >= 0:
            return bisect.bisect_right(absolute_time_tuple, absolute_time) - 1
        else:
            return None

    # ###################################################################### #
    #                        private  methods                                #
    # ###################################################################### #

    # We need to have a private "_cut_off" method to simplify
    # overriding the public "cut_off" method in children classes
    # of SequentialEvent. This is necessary, because the implementation
    # of "squash_in" makes use of "_cut_off". In this way it is possible
    # to adjust the meaning of the public "cut_off" method, without
    # having to change the meaning of "squash_in" (this happens for instance
    # in the mutwo.core_events.Envelope class).
    def _cut_off(
        self,
        start: core_parameters.abc.Duration,
        end: core_parameters.abc.Duration,
        cut_off_duration: typing.Optional[core_parameters.abc.Duration] = None,
    ) -> SequentialEvent[T]:
        if cut_off_duration is None:
            cut_off_duration = end - start

        # Collect core_events which are only active within the
        # cut_off - range
        event_to_delete_list = []
        absolute_time_tuple = self.absolute_time_tuple
        for event_index, event_start, event_end, event in zip(
            range(len(self)),
            absolute_time_tuple,
            absolute_time_tuple[1:] + (None,),
            self,
        ):
            if event_end is None:
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

        return self

    def _split_child_at(
        self,
        absolute_time: core_parameters.abc.Duration | typing.Any,
        absolute_time_in_floats_tuple: tuple[float, ...],
        duration_in_floats: float,
    ) -> int:
        absolute_time = core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(
            absolute_time
        )
        self._assert_valid_absolute_time(absolute_time)
        absolute_time_in_floats = absolute_time.duration_in_floats

        event_index = SequentialEvent._get_index_at_from_absolute_time_tuple(
            absolute_time_in_floats, absolute_time_in_floats_tuple, duration_in_floats
        )

        # If there is no event at the requested time, raise error
        if event_index is None:
            raise core_utilities.SplitUnavailableChildError(absolute_time)

        # Only try to split child event at the requested time if there isn't
        # a segregation already anyway
        elif absolute_time_in_floats != absolute_time_in_floats_tuple[event_index]:
            try:
                end = absolute_time_in_floats_tuple[event_index + 1]
            except IndexError:
                end = duration_in_floats

            difference = end - absolute_time_in_floats
            split_event = self[event_index].split_at(difference)
            split_event_count = len(split_event)
            match split_event_count:
                case 1:
                    pass
                case 2:
                    self[event_index] = split_event[0]
                    self.insert(event_index, split_event[1])
                case _:
                    raise RuntimeError("Unexpected event count!")

            return event_index + 1
        return event_index

    # ###################################################################### #
    #                        private   properties                            #
    # ###################################################################### #

    @property
    def _absolute_time_tuple_and_duration(
        self,
    ) -> [tuple[core_parameters.abc.Duration, ...], core_parameters.abc.Duration]:
        """Return start time for each event and the end time of the last event.

        This property helps to improve performance of various functions
        which uses duration and absolute_time_tuple attribute.
        """

        duration_iterator = (event.duration for event in self)
        absolute_time_tuple = tuple(
            core_utilities.accumulate_from_n(
                duration_iterator, core_parameters.DirectDuration(0)
            )
        )
        return absolute_time_tuple[:-1], absolute_time_tuple[-1]

    @property
    def _absolute_time_in_floats_tuple_and_duration(
        self,
    ) -> tuple[tuple[float, ...], float]:
        """Return start time for each event and the end time of the last event.

        This property helps to improve performance of various functions
        which uses duration and absolute_time_tuple attribute.
        """

        duration_iterator = (event.duration.duration_in_floats for event in self)
        absolute_time_tuple = tuple(
            # We need to round each duration again after accumulation,
            # because floats were summed which could lead to
            # potential floating point errors again, which will
            # lead to bad errors later (for instance in
            # core_utilities.scale).
            map(
                lambda d: core_utilities.round_floats(
                    d,
                    core_parameters.configurations.ROUND_DURATION_TO_N_DIGITS,
                ),
                core_utilities.accumulate_from_n(duration_iterator, 0),
            )
        )
        return absolute_time_tuple[:-1], absolute_time_tuple[-1]

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
    def absolute_time_tuple(self) -> tuple[core_parameters.abc.Duration, ...]:
        """Return start time as :class:`core_parameters.abc.Duration` for each event."""
        return self._absolute_time_tuple_and_duration[0]

    @property
    def absolute_time_in_floats_tuple(self) -> tuple[float, ...]:
        """Return start time as `float` for each event."""
        return self._absolute_time_in_floats_tuple_and_duration[0]

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
        self, absolute_time: core_parameters.abc.Duration | typing.Any
    ) -> typing.Optional[int]:
        """Get index of event which is active at the passed absolute_time.

        :param absolute_time: The absolute time where the method shall search
            for the active event.
        :type absolute_time: core_parameters.abc.Duration | typing.Any
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

        **Warning:**

        This method ignores events with duration == 0.
        """

        absolute_time_in_floats = core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(
            absolute_time
        ).duration_in_floats
        (
            absolute_time_in_floats_tuple,
            duration_in_floats,
        ) = self._absolute_time_in_floats_tuple_and_duration
        return SequentialEvent._get_index_at_from_absolute_time_tuple(
            absolute_time_in_floats, absolute_time_in_floats_tuple, duration_in_floats
        )

    def get_event_at(
        self, absolute_time: core_parameters.abc.Duration | typing.Any
    ) -> typing.Optional[T]:
        """Get event which is active at the passed absolute_time.

        :param absolute_time: The absolute time where the method shall search
            for the active event.
        :type absolute_time: core_parameters.abc.Duration | typing.Any
        :return: Event if there is any event at the requested absolute time
            and ``None`` if there isn't any event.

        **Example:**

        >>> from mutwo import core_events
        >>> sequential_event = core_events.SequentialEvent([core_events.SimpleEvent(2), core_events.SimpleEvent(3)])
        >>> sequential_event.get_event_at(1)
        SimpleEvent(duration = DirectDuration(duration = 2))
        >>> sequential_event.get_event_at(3)
        SimpleEvent(duration = DirectDuration(duration = 3))
        >>> sequential_event.get_event_at(100)

        **Warning:**

        This method ignores events with duration == 0.
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
        self._assert_valid_absolute_time(start)
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
                # Support special case of events with duration = 0.
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
        self._assert_valid_absolute_time(start)

        cut_off_duration = end - start

        # Avoid unnecessary iterations
        if cut_off_duration > 0:
            return self._cut_off(start, end, cut_off_duration)

    @core_utilities.add_copy_option
    def squash_in(  # type: ignore
        self,
        start: core_parameters.abc.Duration | typing.Any,
        event_to_squash_in: core_events.abc.Event,
    ) -> SequentialEvent[T]:
        start = core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(start)
        self._assert_valid_absolute_time(start)
        start_in_floats = start.duration_in_floats
        self._assert_start_in_range(start_in_floats)

        # Only run cut_off if necessary -> Improve performance
        if (event_to_squash_in_duration := event_to_squash_in.duration) > 0:
            cut_off_end = start + event_to_squash_in_duration
            self._cut_off(start, cut_off_end, event_to_squash_in_duration)

        # We already know that the given start is within the
        # range of the event. This means that if the start
        # is bigger than the duration, it is only due to a
        # floating point rounding error. To avoid odd bugs
        # we therefore have to define the bigger-equal
        # relationship.
        (
            absolute_time_in_floats_tuple,
            duration_in_floats,
        ) = self._absolute_time_in_floats_tuple_and_duration
        if start_in_floats >= duration_in_floats:
            self.append(event_to_squash_in)
        else:
            try:
                insert_index = absolute_time_in_floats_tuple.index(start)
            # There is an event on the given point which need to be
            # split.
            except ValueError:
                active_event_index = (
                    SequentialEvent._get_index_at_from_absolute_time_tuple(
                        start_in_floats,
                        absolute_time_in_floats_tuple,
                        duration_in_floats,
                    )
                )
                split_position = (
                    start_in_floats - absolute_time_in_floats_tuple[active_event_index]
                )
                if (
                    split_position > 0
                    and split_position < self[active_event_index].duration
                ):
                    split_active_event = self[active_event_index].split_at(
                        split_position
                    )
                    self[active_event_index] = split_active_event[1]
                    self.insert(active_event_index, split_active_event[0])
                    active_event_index += 1

                insert_index = active_event_index

            self.insert(insert_index, event_to_squash_in)

    @core_utilities.add_copy_option
    def slide_in(
        self,
        start: core_parameters.abc.Duration,
        event_to_slide_in: core_events.abc.Event,
    ) -> SequentialEvent[T]:
        start = core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(start)
        self._assert_valid_absolute_time(start)
        start_in_floats = start.duration_in_floats
        if start_in_floats == 0:
            self.insert(0, event_to_slide_in)
            return self
        self._assert_start_in_range(start_in_floats)
        try:
            self[:], b = self.split_at(start)
        except ValueError:  # Only one event => start == duration.
            self.append(event_to_slide_in)
        else:
            self.extend([event_to_slide_in] + b)
        return self

    @core_utilities.add_copy_option
    def split_child_at(
        self, absolute_time: core_parameters.abc.Duration | typing.Any
    ) -> SequentialEvent[T]:
        (
            absolute_time_in_floats_tuple,
            duration_in_floats,
        ) = self._absolute_time_in_floats_tuple_and_duration

        return self._split_child_at(
            absolute_time, absolute_time_in_floats_tuple, duration_in_floats
        )

    def split_at(
        self,
        *absolute_time: core_parameters.abc.Duration,
        ignore_invalid_split_point: bool = False,
    ) -> tuple[SequentialEvent, ...]:
        if not absolute_time:
            raise core_utilities.NoSplitTimeError()

        (
            absolute_time_in_floats_tuple,
            duration_in_floats,
        ) = self._absolute_time_in_floats_tuple_and_duration

        absolute_time_list = list(absolute_time_in_floats_tuple)

        # NOTE: maybe we can add a 'mutate=False' keyword in case
        # someone doesn't care about keeping the old event and wants
        # to save some seconds of expensive copy-operation?
        c = self.copy()

        index_list = []
        is_first = True
        for t in sorted(absolute_time):
            if is_first:  # First is smallest, check if t < 0
                self._assert_valid_absolute_time(t)
                is_first = False
            # Improve performance: don't try to split if we know it is
            # already split here. We also need to be sure to not
            # add any duplicates to 'absolute_time_list', so we need
            # to check anyway.
            if t in absolute_time_list:
                index_list.append(absolute_time_list.index(t))
                continue
            # It's okay to ignore, this is still within the given event
            # (if we don't continue 'split_child_at' raises an error).
            if t == duration_in_floats:
                continue
            try:
                i = c._split_child_at(t, tuple(absolute_time_list), duration_in_floats)
            except core_utilities.SplitUnavailableChildError:
                if not ignore_invalid_split_point:
                    raise core_utilities.SplitError(t)
                # We can stop, because if there isn't any child at this time
                # there won't be any child at a later time (remember: our
                # absolute times are sorted).
                break
            index_list.append(i)
            absolute_time_list.append(t)
            absolute_time_list.sort()

        # Add frame indices (if not already present)
        if 0 not in index_list:
            index_list.insert(0, 0)

        if (event_count := len(c)) not in index_list:
            index_list.append(event_count)

        return tuple(c[i0:i1] for i0, i1 in zip(index_list, index_list[1:]))

    @core_utilities.add_copy_option
    def extend_until(
        self,
        duration: core_parameters.abc.Duration,
        duration_to_white_space: typing.Optional[
            typing.Callable[[core_parameters.abc.Duration], core_events.abc.Event]
        ] = None,
        prolong_simple_event: bool = True,
    ) -> SequentialEvent[T]:
        duration = core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(duration)
        duration_to_white_space = (
            duration_to_white_space
            or core_events.configurations.DEFAULT_DURATION_TO_WHITE_SPACE
        )
        if (difference := duration - self.duration) > 0:
            self.append(duration_to_white_space(difference))


class SimultaneousEvent(core_events.abc.ComplexEvent, typing.Generic[T]):
    """Event-Object which contains other Event-Objects which happen at the same time."""

    # ###################################################################### #
    #                       private static methods                           #
    # ###################################################################### #

    @staticmethod
    def _extend_ancestor(ancestor: core_events.abc.Event, event: core_events.abc.Event):
        try:
            ancestor._concatenate_tempo_envelope(event)
        # We can't concatenate to a simple event.
        # We also can't concatenate to anything else.
        except AttributeError:
            raise core_utilities.ConcatenationError(ancestor, event)
        match ancestor:
            case core_events.SequentialEvent():
                ancestor.extend(event)
            case core_events.SimultaneousEvent():
                try:
                    ancestor.concatenate_by_tag(event)
                except core_utilities.NoTagError:
                    ancestor.concatenate_by_index(event)
            # This should already fail above, but if this strange object
            # somehow owned '_concatenate_tempo_envelope', it should
            # fail here.
            case _:
                raise core_utilities.ConcatenationError(ancestor, event)

    # ###################################################################### #
    #                           private methods                              #
    # ###################################################################### #

    def _make_event_slice_tuple(
        self,
        absolute_time_list: list[core_parameters.abc.Duration],
        slice_tuple_to_event: typing.Callable[
            [tuple[core_parameters.abc.Event, ...]], core_parameters.abc.Event
        ],
    ) -> tuple[core_events.abc.Event, ...]:
        """Split at given times and cast split events into new events."""

        # Slice all child events
        slices = []
        for e in self:
            slices.append(
                list(e.split_at(*absolute_time_list, ignore_invalid_split_point=True))
            )

        # Ensure all slices have the same amount of entries,
        # because we use 'zip' later and if one of them is
        # shorter we loose some parts of our event.
        if slices:
            slices_count_tuple = tuple(len(s) for s in slices)
            max_slice_count = max(slices_count_tuple)
            for s, c in zip(slices, slices_count_tuple):
                if delta := max_slice_count - c:
                    s.extend([None] * delta)

        # Finally, build new sequence from event slices
        event_list = []
        for slice_tuple in zip(*slices):
            if slice_tuple := tuple(filter(bool, slice_tuple)):
                e = slice_tuple_to_event(slice_tuple)
                event_list.append(e)

        return tuple(event_list)

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
        start: core_parameters.abc.Duration | typing.Any,
        end: core_parameters.abc.Duration | typing.Any,
    ) -> SimultaneousEvent[T]:
        start, end = (
            core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(unknown_object)
            for unknown_object in (start, end)
        )
        self._assert_valid_absolute_time(start)
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
        self._assert_valid_absolute_time(start)
        self._assert_correct_start_and_end_values(start, end)
        [event.cut_off(start, end) for event in self]

    @core_utilities.add_copy_option
    def squash_in(  # type: ignore
        self,
        start: core_parameters.abc.Duration | typing.Any,
        event_to_squash_in: core_events.abc.Event,
    ) -> SimultaneousEvent[T]:
        start = core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(start)
        self._assert_valid_absolute_time(start)
        self._assert_start_in_range(start)

        for event in self:
            try:
                event.squash_in(start, event_to_squash_in)  # type: ignore
            # Simple events don't have a 'squash_in' method.
            except AttributeError:
                raise core_utilities.ImpossibleToSquashInError(self, event_to_squash_in)

    @core_utilities.add_copy_option
    def slide_in(
        self,
        start: core_parameters.abc.Duration,
        event_to_slide_in: core_events.abc.Event,
    ) -> SimultaneousEvent[T]:
        start = core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(start)
        self._assert_valid_absolute_time(start)
        self._assert_start_in_range(start)
        for event in self:
            try:
                event.slide_in(start, event_to_slide_in)  # type: ignore
            # Simple events don't have a 'slide_in' method.
            except AttributeError:
                raise core_utilities.ImpossibleToSlideInError(self, event_to_slide_in)

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

    @core_utilities.add_copy_option
    def extend_until(
        self,
        duration: typing.Optional[core_parameters.abc.Duration] = None,
        duration_to_white_space: typing.Optional[
            typing.Callable[[core_parameters.abc.Duration], core_events.abc.Event]
        ] = None,
        prolong_simple_event: bool = True,
    ) -> SimultaneousEvent[T]:
        duration = (
            self.duration
            if duration is None
            else core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(duration)
        )
        duration_to_white_space = (
            duration_to_white_space
            or core_events.configurations.DEFAULT_DURATION_TO_WHITE_SPACE
        )
        # We only append simple events to sequential events, because there
        # are many problems with the SimultaneousEvent[SimpleEvent] construct
        # ('extend_until' and 'squash_in' will fail on such a container).
        # Therefore calling 'extend_until' on an empty SimultaneousEvent is
        # in fact ineffective: The user would get a SimultaneousEvent which
        # still has duration = 0, which is absolutely unexpected. Therefore
        # we raise an error, to avoid confusion by the user.
        if not self:
            raise core_utilities.IneffectiveExtendUntilError(self)
        for event in self:
            try:
                event.extend_until(
                    duration, duration_to_white_space, prolong_simple_event
                )
            # SimpleEvent
            except AttributeError:
                if prolong_simple_event:
                    if (difference := duration - event.duration) > 0:
                        event.duration += difference
                else:
                    raise core_utilities.ImpossibleToExtendUntilError(event)

    @core_utilities.add_copy_option
    def concatenate_by_index(self, other: SimultaneousEvent) -> SimultaneousEvent:
        """Concatenate with other :class:`~mutwo.core_events.SimultaneousEvent` along their indices.

        :param other: The other `SimultaneousEvent` with which to concatenate.
            The other `SimultaneousEvent` can contain more or less events.
        :type other: SimultaneousEvent
        :param mutate: If ``False`` the function will return a copy of the given object.
            If set to ``True`` the object itself will be changed and the function will
            return the changed object. Default to ``True``.
        :type mutate: bool
        :raises core_utilities.ConcatenationError: If there are any :class:`SimpleEvent`
            inside a :class:`SimultaneousEvent`.

        **Hint:**

        Similarly to Pythons ``list.extend`` the concatenation simply appends
        the children of the other event to the sequence without copying them.
        This means when changing the children in the new event, it also changes
        the child event in the original sequence. If you want to avoid this,
        call ``event.copy()`` before concatenating it to the host event.

        **Example:**

        >>> from mutwo import core_events
        >>> s = core_events.SimultaneousEvent(
        ...     [core_events.SequentialEvent([core_events.SimpleEvent(1)])]
        ... )
        >>> s.concatenate_by_index(s)
        SimultaneousEvent([SequentialEvent([SimpleEvent(duration = DirectDuration(duration = 1)), SimpleEvent(duration = DirectDuration(duration = 1))])])
        """
        if (self_duration := self.duration) > 0:
            self.extend_until(self_duration)
        for index, event in enumerate(other):
            try:
                ancestor = self[index]
            except IndexError:
                if self_duration > 0:
                    # Shallow copy before 'slide_in': We use the same
                    # events, but we don't want to change the other sequence.
                    event_new = event.empty_copy()
                    event_new.extend(event[:])
                    event = event_new.slide_in(0, core_events.SimpleEvent(self_duration))
                self.append(event)
            else:
                self._extend_ancestor(ancestor, event)

    @core_utilities.add_copy_option
    def concatenate_by_tag(self, other: SimultaneousEvent) -> SimultaneousEvent:
        """Concatenate with other :class:`~mutwo.core_events.SimultaneousEvent` along their tags.

        :param other: The other `SimultaneousEvent` with which to concatenate.
            The other `SimultaneousEvent` can contain more or less events.
        :type other: SimultaneousEvent
        :param mutate: If ``False`` the function will return a copy of the given object.
            If set to ``True`` the object itself will be changed and the function will
            return the changed object. Default to ``True``.
        :type mutate: bool
        :return: Concatenated event.
        :raises core_utilities.NoTagError: If any child event doesn't have a 'tag'
            attribute.
        :raises core_utilities.ConcatenationError: If there are any :class:`SimpleEvent`
            inside a :class:`SimultaneousEvent`.

        **Hint:**

        Similarly to Pythons ``list.extend`` the concatenation simply appends
        the children of the other event to the sequence without copying them.
        This means when changing the children in the new event, it also changes
        the child event in the original sequence. If you want to avoid this,
        call ``event.copy()`` before concatenating it to the host event.

        **Example:**

        >>> from mutwo import core_events
        >>> s = core_events.SimultaneousEvent(
        ...      [core_events.TaggedSequentialEvent([core_events.SimpleEvent(1)], tag="test")]
        ...  )
        >>> s.concatenate_by_tag(s)
        SimultaneousEvent([TaggedSequentialEvent([SimpleEvent(duration = DirectDuration(duration = 1)), SimpleEvent(duration = DirectDuration(duration = 1))])])
        """
        if (self_duration := self.duration) > 0:
            self.extend_until(self_duration)
        for tagged_event in other:
            if not hasattr(tagged_event, "tag"):
                raise core_utilities.NoTagError(tagged_event)
            tag = tagged_event.tag
            try:
                ancestor = self[tag]
            except KeyError:
                if self_duration > 0:
                    # Shallow copy before 'slide_in': We use the same
                    # events, but we don't want to change the other sequence.
                    event_new = tagged_event.empty_copy()
                    event_new.extend(tagged_event[:])
                    tagged_event = event_new.slide_in(0, core_events.SimpleEvent(self_duration))
                self.append(tagged_event)
            else:
                self._extend_ancestor(ancestor, tagged_event)

    # NOTE: 'sequentalize' is very generic, it works for all type of child
    # event structure. This is good, but in it's current form it's mostly
    # only useful with rather long and complex user defined 'slice_tuple_to_event'
    # definitions. For instance when sequentializing
    # SimultaneousEvent[SequentialEvent[SimpleEvent]] the returned event will be
    # SequentialEvent[SimultaneousEvent[SequentialEvent[SimpleEvent]]]. Here the
    # inner sequential events are always pointless, since they will always only
    # contain one simple event.
    def sequentialize(
        self,
        slice_tuple_to_event: typing.Optional[
            typing.Callable[
                [tuple[core_parameters.abc.Event, ...]], core_parameters.abc.Event
            ]
        ] = None,
    ) -> core_events.SequentialEvent:
        """Convert parallel structure to a sequential structure.

        :param slice_tuple_to_event: In order to sequentialize the event
            `mutwo` splits each child event into small 'event slices'. These
            'event slices' are simply events created by the `split_at` method.
            Each of those parallel slice groups need to be bound together to
            one new event. These new events are sequentially ordered to result
            in a new sequential structure. The simplest and default way to
            archive this is by simply putting all event parts into a new
            :class:`SimultaneousEvent`, so the resulting :class:`SequentialEvent`
            will be a sequence of `SimultaneousEvent`. This parameter is
            available so that users can convert her/his parallel structure in
            meaningful ways (for instance to imitate the ``.chordify``
            `method from music21 <https://web.mit.edu/music21/doc/usersGuide/usersGuide_09_chordify.html>`
            which transforms polyphonic music to a chord structure).
            If ``None`` `slice_tuple_to_event` is set to
            :class:`SimultaneousEvent`. Default to ``None``.
        :type slice_tuple_to_event: typing.Optional[typing.Callable[[tuple[core_parameters.abc.Event, ...]], core_parameters.abc.Event]]

        **Example:**

        >>> from mutwo import core_events
        >>> e = core_events.SimultaneousEvent(
        ...     [
        ...         core_events.SequentialEvent(
        ...             [core_events.SimpleEvent(2), core_events.SimpleEvent(1)]
        ...         ),
        ...         core_events.SequentialEvent(
        ...             [core_events.SimpleEvent(3)]
        ...         ),
        ...     ]
        ... )
        >>> e.sequentialize()
        SequentialEvent([SimultaneousEvent([SequentialEvent([SimpleEvent(duration = DirectDuration(duration = 2))]), SequentialEvent([SimpleEvent(duration = DirectDuration(duration = 2))])]), SimultaneousEvent([SequentialEvent([SimpleEvent(duration = DirectDuration(duration = 1))]), SequentialEvent([SimpleEvent(duration = DirectDuration(duration = 1))])])])
        """
        if slice_tuple_to_event is None:
            slice_tuple_to_event = SimultaneousEvent

        # Find all start/end times
        absolute_time_set = set([])
        for e in self:
            try:  # SequentialEvent
                (
                    absolute_time_tuple,
                    duration,
                ) = e._absolute_time_in_floats_tuple_and_duration
            except AttributeError:  # SimpleEvent or SimultaneousEvent
                absolute_time_tuple, duration = (0,), e.duration.duration_in_floats
            for t in absolute_time_tuple + (duration,):
                absolute_time_set.add(t)

        # Sort, but also remove the last entry: we don't need
        # to split at complete duration, because after duration
        # there isn't any event left in any child.
        absolute_time_list = sorted(absolute_time_set)[:-1]

        return core_events.SequentialEvent(
            self._make_event_slice_tuple(absolute_time_list, slice_tuple_to_event)
        )

    def split_at(
        self,
        *absolute_time: core_parameters.abc.Duration,
        ignore_invalid_split_point: bool = False,
    ) -> tuple[SimultaneousEvent, ...]:
        if not absolute_time:
            raise core_utilities.NoSplitTimeError()

        absolute_time = sorted(absolute_time)
        self._assert_valid_absolute_time(absolute_time[0])
        if absolute_time[-1] > self.duration and not ignore_invalid_split_point:
            raise core_utilities.SplitError(absolute_time[-1])

        def slice_tuple_to_event(slice_tuple):
            e = self.empty_copy()
            e[:] = slice_tuple
            return e

        return self._make_event_slice_tuple(absolute_time, slice_tuple_to_event)


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

    def sequentialize(self, *args, **kwargs):
        sequential_event = super().sequentialize(*args, **kwargs)
        return TaggedSequentialEvent(sequential_event, tag=self.tag)
