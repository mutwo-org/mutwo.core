"""Abstract base classes for events (definition of public API)."""

from __future__ import annotations

import abc
import copy
import functools
import typing

from mutwo import core_constants
from mutwo import core_events
from mutwo import core_parameters
from mutwo import core_utilities


__all__ = ("Event", "ComplexEvent")


class Event(abc.ABC):
    """Abstract Event-Object

    :param tempo_envelope: An envelope which describes the dynamic tempo of an event.
    """

    def __init__(
        self,
        tempo_envelope: typing.Optional[core_events.TempoEnvelope] = None,
    ):
        self.tempo_envelope = tempo_envelope

    # ###################################################################### #
    #                        abstract properties                             #
    # ###################################################################### #

    @property
    @abc.abstractmethod
    def duration(self) -> core_parameters.abc.Duration:
        """The duration of an event.

        This has to be an instance of :class:`mutwo.core_parameters.abc.Duration`.
        """

    # ###################################################################### #
    #                           private methods                              #
    # ###################################################################### #

    @staticmethod
    def _assert_correct_start_and_end_values(
        start: core_parameters.abc.Duration,
        end: core_parameters.abc.Duration,
        condition: typing.Callable[
            [core_parameters.abc.Duration, core_parameters.abc.Duration], bool
        ] = lambda start, end: end
        >= start,
    ):
        """Helper method to make sure that start < end.

        Can be used within the different cut_out methods.
        """
        if not condition(start, end):
            raise core_utilities.InvalidStartAndEndValueError(start, end)

    @staticmethod
    def _assert_valid_absolute_time(t: core_parameters.abc.Duration):
        if t < 0:
            raise core_utilities.InvalidAbsoluteTime(t)

    @functools.cached_property
    def _event_to_metrized_event(self):
        # Import in method to avoid circular import error
        return __import__(
            "mutwo.core_converters"
        ).core_converters.EventToMetrizedEvent()

    @abc.abstractmethod
    def _set_parameter(
        self,
        parameter_name: str,
        object_or_function: typing.Callable[
            [core_constants.ParameterType], core_constants.ParameterType
        ]
        | core_constants.ParameterType,
        set_unassigned_parameter: bool,
        id_set: set[int],
    ) -> Event:
        ...

    @abc.abstractmethod
    def _mutate_parameter(
        self,
        parameter_name: str,
        function: typing.Callable[[core_constants.ParameterType], None] | typing.Any,
        id_set: set[int],
    ) -> Event:
        ...

    # ###################################################################### #
    #                           public properties                            #
    # ###################################################################### #

    @property
    def tempo_envelope(self) -> core_events.TempoEnvelope:
        """The dynamic tempo of an event; specified as an envelope.

        Tempo envelopes are represented as :class:`core_events.TempoEnvelope`
        objects. Tempo envelopes are valid for its respective event and all its
        children events.
        """
        if self._tempo_envelope is None:
            self.reset_tempo_envelope()
        return self._tempo_envelope

    @tempo_envelope.setter
    def tempo_envelope(
        self, tempo_envelope: typing.Optional[core_events.TempoEnvelope]
    ):
        self._tempo_envelope = tempo_envelope

    # ###################################################################### #
    #                           public methods                               #
    # ###################################################################### #

    def copy(self) -> Event:
        """Return a deep copy of the given Event."""
        return copy.deepcopy(self)

    @abc.abstractmethod
    def destructive_copy(self) -> Event:
        """Adapted deep copy method that returns a new object for every leaf.

        It's called 'destructive', because it forgets potential repetitions of
        the same object in compound objects. Instead of reproducing the original
        structure of the compound object that shall be copied, every repetition
        of the same reference will return a new unique independent object.

        The following example shall illustrate the difference between copy.deepcopy
        and destructive_copy:

        >>> import copy
        >>> from mutwo import core_events
        >>> my_simple_event_0 = core_events.SimpleEvent(2)
        >>> my_simple_event_1 = core_events.SimpleEvent(3)
        >>> my_sequential_event = core_events.SequentialEvent(
        ...     [my_simple_event_0, my_simple_event_1, my_simple_event_0]
        ... )
        >>> deepcopied_event = copy.deepcopy(my_sequential_event)
        >>> destructivecopied_event = my_sequential_event.destructive_copy()
        >>> deepcopied_event[0].duration = 10  # setting the duration of the first event
        >>> destructivecopied_event[0].duration = 10
        >>> # return True because the first and the third objects share the same
        >>> # reference (both are the same copy of 'my_simple_event_0')
        >>> deepcopied_event[0].duration == deepcopied_event[2].duration
        True
        >>> # return False because destructive_copy forgets the shared reference
        >>> destructivecopied_event[0].duration == destructivecopied_event[2].duration
        False
        """

    @core_utilities.add_copy_option
    def set(self, attribute_name: str, value: typing.Any) -> Event:
        """Set an attribute of the object to a specific value

        :param attribute_name: The name of the attribute which value shall be set.
        :param value: The value which shall be assigned to the given
            :attr:`attribute_name`
        :param mutate: If ``False`` the function will return a copy of the given object.
            If set to ``True`` the object itself will be changed and the function will
            return the changed object. Default to ``True``.
        :return: The event.

        This function is merely a convenience wrapper for...

        ``event.attribute_name = value``

        Because the function return the event itself it can be used
        in function composition.

        **Example:**

        >>> from mutwo import core_events
        >>> sequential_event = core_events.SequentialEvent([core_events.SimpleEvent(2)])
        >>> sequential_event.set('duration', 10).set('my_new_attribute', 'hello-world!')
        SequentialEvent([SimpleEvent(duration = DirectDuration(duration = 10))])
        """
        setattr(self, attribute_name, value)
        return self

    @abc.abstractmethod
    def get_parameter(
        self, parameter_name: str, flat: bool = False, filter_undefined: bool = False
    ) -> tuple[core_constants.ParameterType, ...] | core_constants.ParameterType:
        """Return event attribute with the entered name.

        :param parameter_name: The name of the attribute that shall be returned.
        :type parameter_name: str
        :param flat: ``True`` for flat sequence of parameter values, ``False`` if the
            resulting ``tuple`` shall repeat the nested structure of the event.
        :type flat: bool
        :param filter_undefined: If set to ``True`` all ``None`` values will be filtered
            from the returned tuple. Default to ``False``. This flag has no effect on
            :func:`get_parameter` of :class:`mutwo.core_events.SimpleEvent`.
        :type flat: bool
        :return: Return tuple containing the assigned values for each contained
            event. If an event doesn't posses the asked parameter, mutwo will simply
            add None to the tuple for the respective event.

        **Example:**

        >>> from mutwo import core_events
        >>> sequential_event = core_events.SequentialEvent(
        ...     [core_events.SimpleEvent(2), core_events.SimpleEvent(3)]
        ... )
        >>> sequential_event.get_parameter('duration')
        (DirectDuration(2), DirectDuration(3))
        >>> simple_event = core_events.SimpleEvent(10)
        >>> simple_event.get_parameter('duration')
        DirectDuration(10)
        >>> simple_event.get_parameter('undefined_parameter')
        """

    def set_parameter(
        self,
        parameter_name: str,
        object_or_function: typing.Callable[
            [core_constants.ParameterType], core_constants.ParameterType
        ]
        | core_constants.ParameterType,
        set_unassigned_parameter: bool = True,
        mutate: bool = True,
    ) -> typing.Optional[Event]:
        """Sets parameter to new value for all children events.

        :param parameter_name: The name of the parameter which values shall be changed.
        :type parameter_name: str
        :param object_or_function: For setting the parameter either a new value can be
            passed directly or a function can be passed. The function gets as an
            argument the previous value that has had been assigned to the respective
            object and has to return a new value that will be assigned to the object.
        :param set_unassigned_parameter: If set to False a new parameter will only be
            assigned to an Event if the Event already has a attribute with the
            respective `parameter_name`. If the Event doesn't know the attribute yet
            and `set_unassigned_parameter` is False, the method call will simply be
            ignored.
        :param mutate: If ``False`` the function will return a copy of the given object.
            If set to ``True`` the object itself will be changed and the function will
            return the changed object. Default to ``True``.
        :return: The event.

        **Example:**

        >>> from mutwo import core_events
        >>> sequential_event = core_events.SequentialEvent(
        ...     [core_events.SimpleEvent(2), core_events.SimpleEvent(3)]
        ... )
        >>> sequential_event.set_parameter('duration', lambda duration: duration * 2)
        SequentialEvent([SimpleEvent(duration = DirectDuration(duration = 4)), SimpleEvent(duration = DirectDuration(duration = 6))])
        >>> sequential_event.get_parameter('duration')
        (DirectDuration(4), DirectDuration(6))

        **Warning:**

        If there are multiple references of the same Event inside a
        :class:`~mutwo.core_events.SequentialEvent` or a
        ~mutwo.core_events.SimultaneousEvent`, ``set_parameter`` will
        only be called once for each Event. So multiple references
        of the same event will be ignored. This behaviour ensures,
        that on a big scale level each item inside the
        :class:`mutwo.core_events.abc.ComplexEvent` is treated equally
        (so for instance the duration of each item is doubled, and
        nor for some doubled and for those with references which
        appear twice quadrupled).
        """
        return self._set_parameter(
            parameter_name,
            object_or_function,
            set_unassigned_parameter=set_unassigned_parameter,
            mutate=mutate,
            id_set=set([]),
        )

    def mutate_parameter(
        self,
        parameter_name: str,
        function: typing.Callable[[core_constants.ParameterType], None] | typing.Any,
        mutate: bool = True,
    ) -> typing.Optional[Event]:
        """Mutate parameter with a function.

        :param parameter_name: The name of the parameter which shall be mutated.
        :param function: The function which mutates the parameter. The function gets
            as an input the assigned value for the passed parameter_name of the
            respective object. The function shouldn't return anything, but simply
            calls a method of the parameter value.
        :param mutate: If ``False`` the function will return a copy of the given object.
            If set to ``True`` the object itself will be changed and the function will
            return the changed object. Default to ``True``.

        This method is useful when a particular parameter has been assigned to objects
        that know methods which mutate themselves. Then 'mutate_parameter' is a
        convenient wrapper to call the methods of those parameters for all children
        events.

        **Example:**

        >>> from mutwo import core_events
        >>> sequential_event = core_events.SequentialEvent(
        ...     [core_events.SimpleEvent(1)]
        ... )
        >>> sequential_event.mutate_parameter(
        ...     'duration', lambda duration: duration.add(1)
        ... )
        SequentialEvent([SimpleEvent(duration = DirectDuration(duration = 2))])
        >>> # now duration should be + 1
        >>> sequential_event.get_parameter('duration')
        (DirectDuration(2),)

        **Warning:**

        If there are multiple references of the same Event inside a
        :class:`~mutwo.core_events.SequentialEvent` or a
        ~mutwo.core_events.SimultaneousEvent`, ``mutate_parameter`` will
        only be called once for each Event. So multiple references
        of the same event will be ignored. This behaviour ensures,
        that on a big scale level each item inside the
        :class:`mutwo.core_events.abc.ComplexEvent` is treated equally
        (so for instance the duration of each item is doubled, and
        nor for some doubled and for those with references which
        appear twice quadrupled).
        """
        return self._mutate_parameter(
            parameter_name,
            function,
            mutate=mutate,
            id_set=set([]),
        )

    @core_utilities.add_copy_option
    def reset_tempo_envelope(self) -> Event:
        """Set events tempo envelope so that one beat equals one second (tempo 60).

        :param mutate: If ``False`` the function will return a copy of the given object.
            If set to ``True`` the object itself will be changed and the function will
            return the changed object. Default to ``True``.

        **Example:**

        >>> from mutwo import core_events
        >>> simple_event = core_events.SimpleEvent(duration = 1)
        >>> simple_event.tempo_envelope[0].value = 100
        >>> simple_event.tempo_envelope
        TempoEnvelope([TempoEvent(curve_shape = 0, duration = DirectDuration(duration = 1), tempo_point = DirectTempoPoint(BPM = 60, reference = 1), value = 100), TempoEvent(curve_shape = 0, duration = DirectDuration(duration = 0), tempo_point = DirectTempoPoint(BPM = 60, reference = 1))])
        >>> simple_event.reset_tempo_envelope()
        SimpleEvent(duration = DirectDuration(duration = 1))
        >>> simple_event.tempo_envelope
        TempoEnvelope([TempoEvent(curve_shape = 0, duration = DirectDuration(duration = 1), tempo_point = DirectTempoPoint(BPM = 60, reference = 1)), TempoEvent(curve_shape = 0, duration = DirectDuration(duration = 0), tempo_point = DirectTempoPoint(BPM = 60, reference = 1))])
        """

        self.tempo_envelope = core_events.TempoEnvelope([[0, 60], [1, 60]])

    @abc.abstractmethod
    def metrize(self) -> typing.Optional[Event]:
        """Apply tempo envelope of event on itself

        Metrize is only syntactic sugar for a call of
        :class:`EventToMetrizedEvent`:

        >>> from mutwo import core_converters
        >>> from mutwo import core_events
        >>> my_event = core_events.SimpleEvent(1)
        >>> my_event.tempo_envelope = core_events.TempoEnvelope([[0, 100], [1, 40]])
        >>> core_converters.EventToMetrizedEvent().convert(
        ...     my_event
        ... ) == my_event.metrize()
        True
        """

    @abc.abstractmethod
    def cut_out(
        self,
        start: core_parameters.abc.Duration,
        end: core_parameters.abc.Duration,
    ) -> typing.Optional[Event]:
        """Time-based slicing of the respective event.

        :param start: Duration when the cut out shall start.
        :param end: Duration when the cut up shall end.

        **Example:**

        >>> from mutwo import core_events
        >>> sequential_event = core_events.SequentialEvent(
        ...     [core_events.SimpleEvent(3), core_events.SimpleEvent(2)]
        ... )
        >>> sequential_event.cut_out(1, 4)
        SequentialEvent([SimpleEvent(duration = DirectDuration(duration = 2)), SimpleEvent(duration = DirectDuration(duration = 1))])
        """

    @abc.abstractmethod
    def cut_off(
        self,
        start: core_parameters.abc.Duration,
        end: core_parameters.abc.Duration,
    ) -> typing.Optional[Event]:
        """Time-based deletion / shortening of the respective event.

        :param start: Duration when the cut off shall start.
        :param end: Duration when the cut off shall end.

        **Example:**

        >>> from mutwo import core_events
        >>> sequential_event = core_events.SequentialEvent(
        ...     [core_events.SimpleEvent(3), core_events.SimpleEvent(2)]
        ... )
        >>> sequential_event.cut_off(1, 3)
        SequentialEvent([SimpleEvent(duration = DirectDuration(duration = 1)), SimpleEvent(duration = DirectDuration(duration = 2))])
        """

    def split_at(
        self,
        *absolute_time: core_parameters.abc.Duration,
        ignore_invalid_split_point: bool = False,
    ) -> tuple[Event, ...]:
        """Split event into *n* events at :attr:`absolute_time`.

        :param *absolute_time: where event shall be split
        :param ignore_invalid_split_point: If set to `True` `split_at` won't raise
            :class:`mutwo.core_utilities.SplitError` in case a split time isn't
            inside the duration range of the event. Otherwise the exception is raised.
            Default to ``False``.
        :raises: :class:`mutwo.core_utilities.NoSplitTimeError` if no `absolute_time`
            is given. Raises :class:`mutwo.core_utilities.InvalidAbsoluteTime` if any
            absolute_time is smaller than 0. Raises :class:`mutwo.core_utilities.SplitError`
            if any absolute_time is bigger than the events duration and
            `ignore_invalid_split_point` is not set.
        :return:  Tuple of events that result from splitting the present event.

        **Hint:**

        Calling ``split_at`` once with multiple split time arguments is much more efficient
        than calling ``split_at`` multiple times with only one split time for
        :class:`mutwo.core_events.SequentialEvent`.

        **Example:**

        >>> from mutwo import core_events
        >>> sequential_event = core_events.SequentialEvent([core_events.SimpleEvent(3)])
        >>> sequential_event.split_at(1)
        (SequentialEvent([SimpleEvent(duration = DirectDuration(duration = 1))]), SequentialEvent([SimpleEvent(duration = DirectDuration(duration = 2))]))
        >>> sequential_event[0].split_at(1)
        (SimpleEvent(duration = DirectDuration(duration = 1)), SimpleEvent(duration = DirectDuration(duration = 2)))
        """
        if not absolute_time:
            raise core_utilities.NoSplitTimeError()

        absolute_time_list = list(sorted(absolute_time))
        # Already sorted => check if smallest t < 0
        self._assert_valid_absolute_time(absolute_time_list[0])
        if 0 not in absolute_time_list:
            absolute_time_list.insert(0, core_parameters.DirectDuration(0))

        if (duration := self.duration) > absolute_time_list[-1]:
            absolute_time_list.append(duration)
        elif duration < absolute_time_list[-1] and not ignore_invalid_split_point:
            raise core_utilities.SplitError(absolute_time_list[-1])

        split_event_list = []
        for t0, t1 in zip(absolute_time_list, absolute_time_list[1:]):
            try:
                split_event_list.append(self.cut_out(t0, t1, mutate=False))
            except (
                core_utilities.InvalidStartAndEndValueError,
                core_utilities.InvalidCutOutStartAndEndValuesError,
            ):
                if not ignore_invalid_split_point:
                    raise core_utilities.SplitError(t0)

        return tuple(split_event_list)


T = typing.TypeVar("T", bound=Event)


# FIXME(This Event can be initialised (no abstract error).
# Please see the following issue for comparison:
#   https://bugs.python.org/issue35815
class ComplexEvent(Event, abc.ABC, list[T], typing.Generic[T]):
    """Abstract Event-Object, which contains other Event-Objects."""

    def __init__(
        self,
        iterable: typing.Iterable[T] = [],
        tempo_envelope: typing.Optional[core_events.TempoEnvelope] = None,
    ):
        Event.__init__(self, tempo_envelope)
        list.__init__(self, iterable)
        self._logger = core_utilities.get_cls_logger(type(self))

    def __init_subclass__(
        cls, class_specific_side_attribute_tuple: tuple[str, ...] = tuple([])
    ):
        # It's better to prove `class_specific_side_attribute_tuple`
        # as a class initialisation attribute instead of a simple class attribute,
        # because with a simple class attribute we have no guarantee that the
        # content of the parent class is available and we always have to explicitly
        # make it available with something like:
        #
        #   class MyComplexEvent(ComplexEvent):
        #        _class_specific_side_attribute_tuple = (("new_attribute",) +
        #          ComplexEvent._class_specific_side_attribute_tuple)
        #
        # With __init_subclass__ we can simply write:
        #
        #   class MyComplexEvent(
        #     ComplexEvent,
        #    class_specific_side_attribute_tuple = ("new_attribute",)
        #   ): pass
        #
        super_class_class_specific_side_attribute_tuple = getattr(
            cls, "_class_specific_side_attribute_tuple", ("tempo_envelope",)
        )
        class_specific_side_attribute_tuple = (
            super_class_class_specific_side_attribute_tuple
            + class_specific_side_attribute_tuple
        )
        cls._class_specific_side_attribute_tuple = class_specific_side_attribute_tuple

    # ###################################################################### #
    #                           magic methods                                #
    # ###################################################################### #

    def __repr__(self) -> str:
        return "{}({})".format(type(self).__name__, super().__repr__())

    def __add__(self, event: list[T]) -> ComplexEvent[T]:
        empty_copy = self.empty_copy()
        empty_copy.extend(super().__add__(event))
        return empty_copy

    def __mul__(self, factor: int) -> ComplexEvent[T]:
        empty_copy = self.empty_copy()
        empty_copy.extend(super().__mul__(factor))
        return empty_copy

    @typing.overload
    def __getitem__(self, index_or_slice_or_tag: int) -> T:
        ...

    @typing.overload
    def __getitem__(self, index_or_slice_or_tag: slice) -> ComplexEvent[T]:
        ...

    @typing.overload
    def __getitem__(self, index_or_slice_or_tag: str) -> T:
        ...

    def __getitem__(
        self, index_or_slice_or_tag: int | slice | str
    ) -> T | ComplexEvent[T]:
        try:
            event = super().__getitem__(index_or_slice_or_tag)
        except TypeError as error:
            if isinstance(index_or_slice_or_tag, str):
                return self.__getitem__(self._tag_to_index(index_or_slice_or_tag))
            # It can't be a tag, therefore simply raise
            # original exception.
            raise error
        if isinstance(index_or_slice_or_tag, slice):
            empty_event = self.empty_copy()
            empty_event.extend(event)
            return empty_event
        else:
            return event

    @typing.overload
    def __setitem__(self, index_or_slice_or_tag: int, event: core_events.abc.Event):
        ...

    @typing.overload
    def __setitem__(self, index_or_slice_or_tag: slice, event: core_events.abc.Event):
        ...

    @typing.overload
    def __setitem__(self, index_or_slice_or_tag: str, event: core_events.abc.Event):
        ...

    def __setitem__(
        self, index_or_slice_or_tag: int | slice | str, event: core_events.abc.Event
    ):
        try:
            super().__setitem__(index_or_slice_or_tag, event)
        except TypeError as error:
            if isinstance(index_or_slice_or_tag, str):
                return self.__setitem__(
                    self._tag_to_index(index_or_slice_or_tag), event
                )
            # It can't be a tag, therefore simply raise
            # original exception.
            raise error

    # We write custom __delitem__ to support deletion via tag.
    @typing.overload
    def __delitem__(self, index_or_slice_or_tag: int):
        ...

    @typing.overload
    def __delitem__(self, index_or_slice_or_tag: slice):
        ...

    @typing.overload
    def __delitem__(self, index_or_slice_or_tag: str):
        ...

    def __delitem__(self, index_or_slice_or_tag: int | slice | str):
        try:
            super().__delitem__(index_or_slice_or_tag)
        except TypeError as error:
            if isinstance(index_or_slice_or_tag, str):
                return self.__delitem__(self._tag_to_index(index_or_slice_or_tag))
            # It can't be a tag, therefore simply raise
            # original exception.
            raise error

    def __eq__(self, other: typing.Any) -> bool:
        """Test for checking if two objects are equal."""
        try:
            parameter_to_compare_set = set([])
            for object_ in (self, other):
                for (
                    parameter_to_compare
                ) in object_._class_specific_side_attribute_tuple:
                    parameter_to_compare_set.add(parameter_to_compare)
        except AttributeError:
            return False
        return core_utilities.test_if_objects_are_equal_by_parameter_tuple(
            self, other, tuple(parameter_to_compare_set)
        ) and super().__eq__(other)

    def __ne__(self, other: typing.Any):
        return not self.__eq__(other)

    # ###################################################################### #
    #                           properties                                   #
    # ###################################################################### #

    @Event.duration.setter  # type: ignore
    def duration(self, duration: core_parameters.abc.Duration):
        if not self:  # If empty and duration == 0, we'd run into ZeroDivision
            raise core_utilities.CannotSetDurationOfEmptyComplexEvent()

        duration = core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(duration)
        if (old_duration := self.duration) != 0:

            def f(event_duration: core_parameters.abc.Duration):
                return core_utilities.scale(
                    event_duration, 0, old_duration, 0, duration
                )

        else:
            f = duration / len(self)

        self.set_parameter("duration", f)

    # ###################################################################### #
    #                           private methods                              #
    # ###################################################################### #

    # Keep private because:
    #   (1) Then we can later change the internal implementation of
    #       ComplexEvent (for instance: no longer inheriting from list).
    #   (2) It's not sure if tag_to_index is valuable for end users of
    #       ComplexEvent
    def _tag_to_index(self, tag: str) -> int:
        # Find index of an event by its tag.
        # param tag: The `tag` of the event which shall be found.
        # type tag: str

        for event_index, event in enumerate(self):
            try:
                event_tag = event.tag
            except AttributeError:
                continue
            if tag == event_tag:
                return event_index
        raise KeyError(f"No event found with tag = '{tag}'.")

    def _assert_start_in_range(self, start: core_parameters.abc.Duration):
        """Helper method to make sure that start < event.duration.

        Can be used within the different squash_in methods.
        """
        if self.duration < start:
            raise core_utilities.InvalidStartValueError(start, self.duration)

    def _apply_once_per_event(
        self, method_name: str, *args, id_set: set[int], **kwargs
    ):
        for event in self:
            if (event_id := id(event)) not in id_set:
                id_set.add(event_id)
                getattr(event, method_name)(*args, id_set=id_set, **kwargs)

    @core_utilities.add_copy_option
    def _set_parameter(  # type: ignore
        self,
        parameter_name: str,
        object_or_function: typing.Callable[
            [core_constants.ParameterType], core_constants.ParameterType
        ]
        | core_constants.ParameterType,
        set_unassigned_parameter: bool,
        id_set: set[int],
    ) -> ComplexEvent[T]:
        self._apply_once_per_event(
            "_set_parameter",
            parameter_name,
            object_or_function,
            id_set=id_set,
            set_unassigned_parameter=set_unassigned_parameter,
        )

    @core_utilities.add_copy_option
    def _mutate_parameter(  # type: ignore
        self,
        parameter_name: str,
        function: typing.Callable[[core_constants.ParameterType], None] | typing.Any,
        id_set: set[int],
    ) -> ComplexEvent[T]:
        self._apply_once_per_event(
            "_mutate_parameter",
            parameter_name,
            function,
            id_set=id_set,
        )

    def _concatenate_tempo_envelope(self, other: ComplexEvent):
        """Concatenate the tempo of event with tempo of other event.

        If we concatenate events on the time axis, we also want to
        ensure that the tempo information is not lost.
        This includes the `+` magic method of ``SequentialEvent``,
        but also the `concatenate_by...` methods of ``SimultaneousEvent``.

        It's important to first call this method before appending the
        child events of the other container, because we still need
        to know the original duration of the target event. Due to this
        difficulty this method is private.
        """
        # We need to ensure the tempo envelope of the event
        # is as long as it's duration, otherwise the others tempo
        # envelope may be postponed (if our envelope is longer
        # than the event) or may be too early (if our envelope
        # is shorted than the event).
        # We don't care here if the others event envelope is too
        # short or too long, because the relationships are still
        # the same.
        if (d := self.duration) < (d_env := self.tempo_envelope.duration):
            self._logger.warning(
                f"Tempo envelope of '{str(self)[:35]}...' needed "
                "to be truncated because the envelope was "
                "longer than the actual event."
            )
            self.tempo_envelope.cut_out(0, d)
        elif d > d_env:
            self.tempo_envelope.extend_until(d)
        self.tempo_envelope.extend(other.tempo_envelope.copy())

    # ###################################################################### #
    #                           public methods                               #
    # ###################################################################### #

    def destructive_copy(self) -> ComplexEvent[T]:
        empty_copy = self.empty_copy()
        empty_copy.extend([event.destructive_copy() for event in self])
        return empty_copy

    def empty_copy(self) -> ComplexEvent[T]:
        """Make a copy of the `ComplexEvent` without any child events.

        This method is useful if one wants to copy an instance of :class:`ComplexEvent`
        and make sure that all side attributes (e.g. any assigned properties specific
        to the respective subclass) get saved.

        **Example:**

        >>> from mutwo import core_events
        >>> piano_voice_0 = core_events.TaggedSequentialEvent([core_events.SimpleEvent(2)], tag="piano")
        >>> piano_voice_1 = piano_voice_0.empty_copy()
        >>> piano_voice_1.tag
        'piano'
        >>> piano_voice_1
        TaggedSequentialEvent([])
        """
        return type(self)(
            [],
            **{
                attribute_name: getattr(self, attribute_name)
                for attribute_name in self._class_specific_side_attribute_tuple
            },
        )

    def get_event_from_index_sequence(
        self, index_sequence: typing.Sequence[int]
    ) -> Event:
        """Get nested :class:`Event` from a sequence of indices.

        :param index_sequence: The indices of the nested :class:`Event`.
        :type index_sequence: typing.Sequence[int]

        **Example:**

        >>> from mutwo import core_events
        >>> nested_sequential_event = core_events.SequentialEvent(
        ...     [core_events.SequentialEvent([core_events.SimpleEvent(2)])]
        ... )
        >>> nested_sequential_event.get_event_from_index_sequence((0, 0))
        SimpleEvent(duration = DirectDuration(duration = 2))
        >>> # this is equal to:
        >>> nested_sequential_event[0][0]
        SimpleEvent(duration = DirectDuration(duration = 2))
        """

        return core_utilities.get_nested_item_from_index_sequence(index_sequence, self)

    def get_parameter(
        self, parameter_name: str, flat: bool = False, filter_undefined: bool = False
    ) -> tuple[core_constants.ParameterType, ...]:
        parameter_value_list: list[core_constants.ParameterType] = []
        for event in self:
            parameter_value_or_parameter_value_tuple = event.get_parameter(
                parameter_name, flat=flat
            )

            if is_simple_event := isinstance(event, core_events.SimpleEvent):
                parameter_value_tuple = (parameter_value_or_parameter_value_tuple,)
            else:
                parameter_value_tuple = parameter_value_or_parameter_value_tuple
            if filter_undefined:
                parameter_value_tuple = tuple(
                    filter(
                        lambda parameter_value: parameter_value is not None,
                        parameter_value_tuple,
                    )
                )
            if flat:
                parameter_value_list.extend(parameter_value_tuple)
            else:
                # Simple events should be added without tuple, they only
                # provide one parameter.
                if is_simple_event:
                    if parameter_value_tuple:
                        parameter_value_list.append(parameter_value_tuple[0])
                else:
                    parameter_value_list.append(parameter_value_tuple)
        return tuple(parameter_value_list)

    @core_utilities.add_copy_option
    def remove_by(  # type: ignore
        self, condition: typing.Callable[[Event], bool]
    ) -> ComplexEvent[T]:
        """Condition-based deletion of child events.

        :param condition: Function which takes a :class:`Event` and returns ``True``
            or ``False``. If the return value of the function is ``False`` the
            respective `Event` will be deleted.
        :type condition: typing.Callable[[Event], bool]
        :param mutate: If ``False`` the function will return a copy of the given object.
            If set to ``True`` the object itself will be changed and the function will
            return the changed object. Default to ``True``.

        **Example:**

        >>> from mutwo import core_events
        >>> simultaneous_event = core_events.SimultaneousEvent(
        ...     [core_events.SimpleEvent(1), core_events.SimpleEvent(3), core_events.SimpleEvent(2)]
        ... )
        >>> simultaneous_event.remove_by(lambda event: event.duration > 2)
        SimultaneousEvent([SimpleEvent(duration = DirectDuration(duration = 3))])
        """

        for item_index, item in zip(reversed(range(len(self))), reversed(self)):
            shall_survive = condition(item)
            if not shall_survive:
                del self[item_index]

    @core_utilities.add_copy_option
    def tie_by(  # type: ignore
        self,
        condition: typing.Callable[[Event, Event], bool],
        process_surviving_event: typing.Callable[
            [Event, Event], None
        ] = lambda event_to_survive, event_to_delete: event_to_survive.__setattr__(
            "duration", event_to_delete.duration + event_to_survive.duration
        ),
        event_type_to_examine: typing.Type[Event] = Event,
        event_to_remove: bool = True,
    ) -> ComplexEvent[T]:
        """Condition-based deletion of neighboring child events.

        :param condition: Function which compares two neighboring
            events and decides whether one of those events shall be
            removed. The function should return `True` for deletion and
            `False` for keeping both events.
        :param process_surviving_event: Function which gets two arguments: first
            the surviving event and second the event which shall be removed.
            The function should process the surviving event depending on
            the removed event. By default, mutwo will simply add the
            :attr:`duration` of the removed event to the duration of the surviving
            event.
        :param event_type_to_examine: Defines which events shall be compared.
            If one only wants to process the leaves, this should perhaps be
            :class:`mutwo.core_events.SimpleEvent`.
        :param event_to_remove: `True` if the second (left) event shall be removed
            and `False` if the first (right) event shall be removed.
        :param mutate: If ``False`` the function will return a copy of the given object.
            If set to ``True`` the object itself will be changed and the function will
            return the changed object. Default to ``True``.
        """

        # Nothing to tie if no child events exist
        if not self:
            return self

        def tie_by_if_available(event_to_tie: Event):
            if hasattr(event_to_tie, "tie_by"):
                event_to_tie.tie_by(
                    condition,
                    process_surviving_event,
                    event_type_to_examine,
                    event_to_remove,
                )

        pointer = 0
        while pointer + 1 < len(self):
            event_tuple = self[pointer], self[pointer + 1]
            if all(isinstance(event, event_type_to_examine) for event in event_tuple):
                shall_delete = condition(*event_tuple)
                if shall_delete:
                    if event_to_remove:
                        process_surviving_event(*event_tuple)
                        del self[pointer + 1]
                    else:
                        process_surviving_event(*reversed(event_tuple))
                        del self[pointer]
                else:
                    pointer += 1
            # If event doesn't contain the event type which shall be tied,
            # it may still contain nested events which contains events with
            # the searched type
            else:
                tie_by_if_available(event_tuple[0])
                pointer += 1

        # Previously only the first event of the examined pairs has been tied,
        # therefore the very last event could have been forgotten.
        if not isinstance(self[-1], event_type_to_examine):
            tie_by_if_available(self[-1])

    # ###################################################################### #
    #                           abstract methods                             #
    # ###################################################################### #

    def metrize(self, mutate: bool = True) -> ComplexEvent:
        metrized_event = self._event_to_metrized_event(self)
        if mutate:
            self.tempo_envelope = metrized_event.tempo_envelope
            self[:] = metrized_event[:]
            return self
        else:
            return metrized_event

    @abc.abstractmethod
    def squash_in(
        self, start: core_parameters.abc.Duration, event_to_squash_in: Event
    ) -> typing.Optional[ComplexEvent[T]]:
        """Time-based insert of a new event with overriding given event.

        :param start: Absolute time where the event shall be inserted.
        :param event_to_squash_in: the event that shall be squashed into
            the present event.
        :param mutate: If ``False`` the function will return a copy of the given object.
            If set to ``True`` the object itself will be changed and the function will
            return the changed object. Default to ``True``.

        Unlike `ComplexEvent.slide_in` the events duration won't change.
        If there is already an event at `start` this event will be shortened
        or removed.

        **Example:**

        >>> from mutwo import core_events
        >>> sequential_event = core_events.SequentialEvent([core_events.SimpleEvent(3)])
        >>> sequential_event.squash_in(1, core_events.SimpleEvent(1.5))
        SequentialEvent([SimpleEvent(duration = DirectDuration(duration = 1)), SimpleEvent(duration = DirectDuration(duration = 3/2)), SimpleEvent(duration = DirectDuration(duration = 1/2))])
        """

    @abc.abstractmethod
    def slide_in(
        self, start: core_parameters.abc.Duration, event_to_slide_in: Event
    ) -> ComplexEvent[T]:
        """Time-based insert of a new event into the present event.

        :param start: Absolute time where the event shall be inserted.
        :param event_to_slide_in: the event that shall be slide into
            the present event.
        :param mutate: If ``False`` the function will return a copy of the given object.
            If set to ``True`` the object itself will be changed and the function will
            return the changed object. Default to ``True``.

        Unlike `ComplexEvent.squash_in` the events duration will be prolonged
        by the event which is added. If there is an event at `start` the
        event will be split into two parts, but it won't be shortened or
        processed in any other way.

        **Example:**

        >>> from mutwo import core_events
        >>> sequential_event = core_events.SequentialEvent([core_events.SimpleEvent(3)])
        >>> sequential_event.slide_in(1, core_events.SimpleEvent(1.5))
        SequentialEvent([SimpleEvent(duration = DirectDuration(duration = 1)), SimpleEvent(duration = DirectDuration(duration = 3/2)), SimpleEvent(duration = DirectDuration(duration = 2))])
        """

    @abc.abstractmethod
    def split_child_at(
        self, absolute_time: core_parameters.abc.Duration
    ) -> typing.Optional[ComplexEvent[T]]:
        """Split child event in two events at :attr:`absolute_time`.

        :param absolute_time: where child event shall be split
        :param mutate: If ``False`` the function will return a copy of the given object.
            If set to ``True`` the object itself will be changed and the function will
            return the changed object. Default to ``True``.

        **Example:**

        >>> from mutwo import core_events
        >>> sequential_event = core_events.SequentialEvent([core_events.SimpleEvent(3)])
        >>> sequential_event.split_child_at(1)
        SequentialEvent([SimpleEvent(duration = DirectDuration(duration = 1)), SimpleEvent(duration = DirectDuration(duration = 2))])
        """

    @abc.abstractmethod
    def extend_until(
        self,
        duration: core_parameters.abc.Duration,
        duration_to_white_space: typing.Optional[
            typing.Callable[[core_parameters.abc.Duration], Event]
        ] = None,
        prolong_simple_event: bool = True,
    ) -> ComplexEvent:
        """Prolong event until at least `duration` by appending an empty event.

        :param duration: Until which duration the event shall be extended.
            If event is already longer than or equal to given `duration`,
            nothing will be changed. For :class:`~mutwo.core_events.SimultaneousEvent`
            the default value is `None` which is equal to the duration of
            the `SimultaneousEvent`.
        :type duration: core_parameters.abc.Duration
        :param duration_to_white_space: A function which creates the 'rest' or
            'white space' event from :class:`~mutwo.core_parameters.abc.Duration`.
            If this is ``None`` `mutwo` will fall back to use the default function
            which is `mutwo.core_events.configurations.DEFAULT_DURATION_TO_WHITE_SPACE`.
            Default to `None`.
        :type duration_to_white_space: typing.Optional[typing.Callable[[core_parameters.abc.Duration], Event]]
        :param prolong_simple_event: If set to ``True`` `mutwo` will prolong a single
            :class:`~mutwo.core_events.SimpleEvent` inside a :class:`~mutwo.core_events.SimultaneousEvent`.
            If set to ``False`` `mutwo` will raise an :class:`~mutwo.core_utilities.ImpossibleToExtendUntilError`
            in case it finds a single `SimpleEvent` inside a `SimultaneousEvent`.
            This doesn't effect `SimpleEvent` inside a `SequentialEvent`, here we can
            simply append a new white space event.
        :type prolong_simple_event: bool
        :param mutate: If ``False`` the function will return a copy of the given object.
            If set to ``True`` the object itself will be changed and the function will
            return the changed object. Default to ``True``.
        :type mutate: bool

        **Example:**

        >>> from mutwo import core_events
        >>> s = core_events.SequentialEvent([core_events.SimpleEvent(1)])
        >>> s.extend_until(10)
        SequentialEvent([SimpleEvent(duration = DirectDuration(duration = 1)), SimpleEvent(duration = DirectDuration(duration = 9))])
        """
