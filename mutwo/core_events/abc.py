"""Abstract base classes for events (definition of public API)."""

from __future__ import annotations

import abc
import copy
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
        try:
            assert condition(start, end)
        except AssertionError:
            raise ValueError(
                f"Invalid values for start and end property (start = '{start}' "
                f"and end = '{end}')!"
                " Value for 'end' has to be bigger than value for 'start'."
            )

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
        >>>     [my_simple_event_0, my_simple_event_1, my_simple_event_0]
        >>> )
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

    @abc.abstractmethod
    def get_parameter(
        self, parameter_name: str, flat: bool = False
    ) -> typing.Union[
        tuple[core_constants.ParameterType, ...], core_constants.ParameterType
    ]:
        """Return event attribute with the entered name.

        :param parameter_name: The name of the attribute that shall be returned.
        :type parameter_name: str
        :param flat: ``True`` for flat sequence of parameter values, ``False`` if the
            resulting ``tuple`` shall repeat the nested structure of the event.
        :type flat: bool
        :returns: Return tuple containing the assigned values for each contained
            event. If an event doesn't posses the asked parameter, mutwo will simply
            add None to the tuple for the respective event.

        **Example:**

        >>> from mutwo import core_events
        >>> sequential_event = core_events.SequentialEvent(
        >>>     [core_events.SimpleEvent(2), core_events.SimpleEvent(3)]
        >>> )
        >>> sequential_event.get_parameter('duration')
        (2, 3)
        """

    @abc.abstractmethod
    def set_parameter(
        self,
        parameter_name: str,
        object_or_function: typing.Union[
            typing.Callable[
                [core_constants.ParameterType], core_constants.ParameterType
            ],
            core_constants.ParameterType,
        ],
        set_unassigned_parameter: bool = True,
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

        **Example:**

        >>> from mutwo import core_events
        >>> sequential_event = core_events.SequentialEvent(
        >>>     [core_events.SimpleEvent(2), core_events.SimpleEvent(3)]
        >>> )
        >>> sequential_event.set_parameter('duration', lambda duration: duration * 2)
        >>> sequential_event.get_parameter('duration')
        (4, 6)
        """

    @abc.abstractmethod
    def mutate_parameter(
        self,
        parameter_name: str,
        function: typing.Union[
            typing.Callable[[core_constants.ParameterType], None], typing.Any
        ],
    ) -> typing.Optional[Event]:
        """Mutate parameter with a function.

        :param parameter_name: The name of the parameter which shall be mutated.
        :param function: The function which mutates the parameter. The function gets
            as an input the assigned value for the passed parameter_name of the
            respective object. The function shouldn't return anything, but simply
            calls a method of the parameter value.

        This method is useful when a particular parameter has been assigned to objects
        that know methods which mutate themselves. Then 'mutate_parameter' is a
        convenient wrapper to call the methods of those parameters for all children
        events.

        **Example:**

        >>> from mutwo import core_events
        >>> from mutwo import music_events
        >>> from mutwo import music_parameters
        >>> sequential_event = core_events.SequentialEvent(
        >>>     [
        >>>         music_events.NoteLike(
        >>>             [
        >>>                 music_parameters.WesternPitch('c', 4),
        >>>                 music_parameters.WesternPitch('e', 4)],
        >>>             ],
        >>>             2, 1,
        >>>         )
        >>>     ]
        >>> )
        >>> sequential_event.mutate_parameter(
        >>>     'pitch_list', lambda pitch_list: [pitch.add(12) for pitch in pitch_list]
        >>> )
        >>> # now all pitches should be one octave higher (from 4 to 5)
        >>> sequential_event.get_parameter('pitch_list')
        ([WesternPitch(c5), WesternPitch(e5)],)
        """

    @core_utilities.add_copy_option
    def reset_tempo_envelope(self) -> Event:
        """Set events tempo envelope so that one beat equals one second (tempo 60).

        **Example:**

        >>> from mutwo import core_events
        >>> simple_event = core_events.SimpleEvent(duration = 1)
        >>> simple_event.tempo_envelope[0].value = 100
        >>> print(simple_event.tempo_envelope)
        TempoEnvelope([SimpleEvent(curve_shape = 0, duration = DirectDuration(duration = 1), value = 100), SimpleEvent(curve_shape = 0, duration = DirectDuration(duration = 0), value = 60)])
        >>> simple_event.reset_tempo_envelope()
        >>> print(simple_event.tempo_envelope)
        TempoEnvelope([SimpleEvent(curve_shape = 0, duration = DirectDuration(duration = 1), value = 60), SimpleEvent(curve_shape = 0, duration = DirectDuration(duration = 0), value = 60)])
        """

        self.tempo_envelope = core_events.TempoEnvelope([[0, 60], [1, 60]])

    @abc.abstractmethod
    def metrize(self) -> typing.Optional[Event]:
        """Apply tempo envelope of event on itself

        Metrize is only syntactic sugar for a call of
        :class:`EventToMetrizedEvent`:

        >>> from mutwo import core_converters
        >>> core_converters.EventToMetrizedEvent().convert(
        >>>     my_event
        >>> ) == my_event.metrize()
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
        >>>     [core_events.SimpleEvent(3), core_events.SimpleEvent(2)]
        >>> )
        >>> sequential_event.cut_out(1, 4)
        >>> print(sequential_event)
        SequentialEvent([SimpleEvent(duration = 2), SimpleEvent(duration = 1)])
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
        >>>     [core_events.SimpleEvent(3), core_events.SimpleEvent(2)]
        >>> )
        >>> sequential_event.cut_off(1, 3)
        >>> print(sequential_event)
        SequentialEvent([SimpleEvent(duration = 1), SimpleEvent(duration = 1)])
        """

    def split_at(
        self, absolute_time: core_parameters.abc.Duration
    ) -> tuple[Event, Event]:
        """Split event in two events at :attr:`absolute_time`.

        :param absolute_time: where event shall be split
        :return: Two events that result from splitting the present event.

        **Example:**

        >>> from mutwo import core_events
        >>> sequential_event = core_events.SequentialEvent([core_events.SimpleEvent(3)])
        >>> sequential_event.split_at(1)
        (SequentialEvent([SimpleEvent(duration = 1)]), SequentialEvent([SimpleEvent(duration = 2)]))
        >>> sequential_event[0].split_at(1)
        (SimpleEvent(duration = 1), SimpleEvent(duration = 2))
        """

        absolute_time = core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(
            absolute_time
        )

        return (
            self.cut_out(0, absolute_time, mutate=False),  # type: ignore
            self.cut_out(absolute_time, self.duration, mutate=False),  # type: ignore
        )


T = typing.TypeVar("T", bound=Event)


class ComplexEvent(Event, list[T], typing.Generic[T]):
    """Abstract Event-Object, which contains other Event-Objects."""

    # TODO(Add docstring)
    # TODO(Set '_class_specific_side_attribute_tuple' in __init_subclass__)
    _class_specific_side_attribute_tuple: tuple[str, ...] = ("tempo_envelope",)

    def __init__(
        self,
        iterable: typing.Iterable[T],
        tempo_envelope: typing.Optional[core_events.TempoEnvelope] = None,
    ):
        Event.__init__(self, tempo_envelope)
        list.__init__(self, iterable)

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
    def __getitem__(self, index_or_slice: int) -> T:
        ...

    @typing.overload
    def __getitem__(self, index_or_slice: slice) -> ComplexEvent[T]:
        ...

    def __getitem__(
        self, index_or_slice: typing.Union[int, slice]
    ) -> typing.Union[T, ComplexEvent[T]]:
        event = super().__getitem__(index_or_slice)
        if isinstance(index_or_slice, slice):
            empty_event = self.empty_copy()
            empty_event.extend(event)
            return empty_event
        else:
            return event

    # ###################################################################### #
    #                           properties                                   #
    # ###################################################################### #

    @Event.duration.setter  # type: ignore
    def duration(self, duration: core_parameters.abc.Duration):
        duration = core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(duration)
        old_duration = self.duration
        self.set_parameter(
            "duration",
            lambda event_duration: core_utilities.scale(
                event_duration, 0, old_duration, 0, duration
            ),
        )

    # ###################################################################### #
    #                           private methods                              #
    # ###################################################################### #

    def _assert_start_in_range(self, start: core_parameters.abc.Duration):
        """Helper method to make sure that start < event.duration.

        Can be used within the different squash_in methods.
        """
        try:
            assert self.duration >= start
        except AssertionError:
            raise ValueError(
                f"Invalid value for start = '{start}' in 'squash_in' call "
                f"for event with duration = '{self.duration}'!"
                " Start has to be equal or smaller than the events duration."
            )

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
        >>>     [core_events.SequentialEvent([core_events.SimpleEvent(2)])]
        >>> )
        >>> nested_sequential_event.get_event_from_index_sequence((0, 0))
        SimpleEvent(duration = 2)
        >>> # this is equal to:
        >>> nested_sequential_event[0][0]
        SimpleEvent(duration = 2)
        """

        return core_utilities.get_nested_item_from_index_sequence(index_sequence, self)

    def get_parameter(
        self, parameter_name: str, flat: bool = False
    ) -> tuple[core_constants.ParameterType, ...]:
        parameter_value_list: list[core_constants.ParameterType] = []
        for event in self:
            parameter_values_of_event = event.get_parameter(parameter_name, flat=flat)
            if flat:
                parameter_value_list.extend(parameter_values_of_event)
            else:
                parameter_value_list.append(parameter_values_of_event)
        return tuple(parameter_value_list)

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
    ) -> ComplexEvent[T]:
        [
            event.set_parameter(
                parameter_name,
                object_or_function,
                set_unassigned_parameter=set_unassigned_parameter,
            )
            for event in self
        ]

    @core_utilities.add_copy_option
    def mutate_parameter(  # type: ignore
        self,
        parameter_name: str,
        function: typing.Union[
            typing.Callable[[core_constants.ParameterType], None], typing.Any
        ],
    ) -> ComplexEvent[T]:
        [event.mutate_parameter(parameter_name, function) for event in self]

    @core_utilities.add_copy_option
    def filter(  # type: ignore
        self, condition: typing.Callable[[Event], bool]
    ) -> ComplexEvent[T]:
        """Condition-based deletion of child events.

        :param condition: Function which takes a :class:`Event` and returns ``True``
            or ``False``. If the return value of the function is ``False`` the
            respective `Event` will be deleted.
        :type condition: typing.Callable[[Event], bool]

        **Example:**

        >>> from mutwo import core_events
        >>> simultaneous_event = core_events.SimultaneousEvent(
            [core_events.SimpleEvent(1), core_events.SimpleEvent(3), core_events.SimpleEvent(2)]
        )
        >>> simultaneous_event.filter(lambda event: event.duration > 2)
        >>> simultaneous_event
        SimultaneousEvent([SimpleEvent(duration = 3)])
        """

        for nth_item, item in zip(reversed(range(len(self))), reversed(self)):
            shall_survive = condition(item)
            if not shall_survive:
                del self[nth_item]

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

    @core_utilities.add_copy_option
    def metrize(self):
        # XXX: import in method to avoid circular import error
        metrized_event = __import__(
            "mutwo.core_converters"
        ).core_converters.EventToMetrizedEvent()(self)
        self.tempo_envelope = metrized_event.tempo_envelope
        self[:] = metrized_event[:]

    @abc.abstractmethod
    def squash_in(
        self, start: core_parameters.abc.Duration, event_to_squash_in: Event
    ) -> typing.Optional[ComplexEvent[T]]:
        """Time-based insert of a new event into the present event.

        :param start: Absolute time where the event shall be inserted.
        :param event_to_squash_in: the event that shall be squashed into
            the present event.

        Squash in a new event to the present event.

        **Example:**

        >>> from mutwo import core_events
        >>> sequential_event = core_events.SequentialEvent([core_events.SimpleEvent(3)])
        >>> sequential_event.squash_in(1, core_events.SimpleEvent(1.5))
        >>> print(sequential_event)
        SequentialEvent([SimpleEvent(duration = 1), SimpleEvent(duration = 1.5), SimpleEvent(duration = 0.5)])
        """

    @abc.abstractmethod
    def split_child_at(
        self, absolute_time: core_parameters.abc.Duration
    ) -> typing.Optional[ComplexEvent[T]]:
        """Split child event in two events at :attr:`absolute_time`.

        :param absolute_time: where child event shall be split

        **Example:**

        >>> from mutwo import core_events
        >>> sequential_event = core_events.SequentialEvent([core_events.SimpleEvent(3)])
        >>> sequential_event.split_child_at(1)
        >>> sequential_event
        SequentialEvent([SimpleEvent(duration = 1), SimpleEvent(duration = 2)])
        """