"""Abstract base classes for events (definition of public API)."""

from __future__ import annotations

import abc
import copy
import typing

from mutwo import parameters
from mutwo.utilities import decorators
from mutwo.utilities import tools

__all__ = ("Event", "ComplexEvent")


class Event(abc.ABC):
    """Abstract Event-Object"""

    # ###################################################################### #
    #                           properties                                   #
    # ###################################################################### #

    @property
    @abc.abstractmethod
    def duration(self) -> parameters.abc.DurationType:
        """The duration of an event (which can be any number).

        The unit of the duration is up to the interpretation of the user
        and the respective conversion routine that will be used. For
        instance when using :class:`CsoundScoreConverter`, the duration will be
        understood as seconds, while :class:`MidiFileConverter` will read duration
        as beats.
        """
        raise NotImplementedError

    # ###################################################################### #
    #                           private methods                              #
    # ###################################################################### #

    @staticmethod
    def _assert_correct_start_and_end_values(
        start: parameters.abc.DurationType,
        end: parameters.abc.DurationType,
        condition: typing.Callable[
            [parameters.abc.DurationType, parameters.abc.DurationType], bool
        ] = lambda start, end: end
        >= start,
    ):
        """Helper method to make sure that start < end.

        Can be used within the different cut_out methods.
        """
        try:
            assert condition(start, end)
        except AssertionError:
            message = (
                "Invalid values for start and end property (start = '{}' and end ="
                " '{}')!".format(start, end)
            )
            message += " Value for end has to be bigger than value for start."
            raise ValueError(message)

    # ###################################################################### #
    #                           public methods                               #
    # ###################################################################### #

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
        >>> from mutwo.events import basic
        >>> my_simple_event_0 = basic.SimpleEvent(2)
        >>> my_simple_event_1 = basic.SimpleEvent(3)
        >>> my_sequential_event = basic.SequentialEvent([my_simple_event_0, my_simple_event_1, my_simple_event_0])
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

        raise NotImplementedError

    @abc.abstractmethod
    def get_parameter(
        self, parameter_name: str
    ) -> typing.Union[typing.Tuple[typing.Any, ...], typing.Any]:
        """Return event attribute with the entered name.

        :param parameter_name: The name of the attribute that shall be returned.
        :returns: Return tuple containing the assigned values for each contained
            event. If an event doesn't posses the asked parameter, mutwo will simply
            add None to the tuple for the respective event.

        **Example:**

        >>> from mutwo.events import basic
        >>> sequential_event = basic.SequentialEvent([basic.SimpleEvent(2), basic.SimpleEvent(3)])
        >>> sequential_event.get_parameter('duration')
        (2, 3)
        """

        raise NotImplementedError

    @abc.abstractmethod
    def set_parameter(
        self,
        parameter_name: str,
        object_or_function: typing.Union[
            typing.Callable[
                [parameters.abc.ParameterType], parameters.abc.ParameterType
            ],
            typing.Any,
        ],
        set_unassigned_parameter: bool = True,
    ) -> None:
        """Sets parameter to new value for all children events.

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
        >>> sequential_event = basic.SequentialEvent([basic.SimpleEvent(2), basic.SimpleEvent(3)])
        >>> sequential_event.set_parameter('duration', lambda duration: duration * 2)
        >>> sequential_event.get_parameter('duration')
        (4, 6)
        """

        raise NotImplementedError

    @abc.abstractmethod
    def mutate_parameter(
        self,
        parameter_name: str,
        function: typing.Union[
            typing.Callable[[parameters.abc.Parameter], None], typing.Any
        ],
    ) -> None:
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

        >>> from mutwo.events import basic, music
        >>> from mutwo.parameters import pitches
        >>> sequential_event = basic.SequentialEvent([music.NoteLike([pitches.WesternPitch('c', 4), pitches.WesternPitch('e', 4)], 2, 1)])
        >>> sequential_event.mutate_parameter('pitch_or_pitches', lambda pitch_or_pitches: [pitch.add(12) for pitch in pitch_or_pitches])
        >>> # now all pitches should be one octave higher (from 4 to 5)
        >>> sequential_event.get_parameter('pitch_or_pitches')
        ([WesternPitch(c5), WesternPitch(e5)],)
        """

        raise NotImplementedError

    @abc.abstractmethod
    def cut_out(
        self, start: parameters.abc.DurationType, end: parameters.abc.DurationType,
    ) -> typing.Optional[Event]:
        """Time-based slicing of the respective event.

        :param start: number that indicates the point when the
            cut out shall start.
        :param end: number that indicates the point when the cut
            up shall end.

        **Example:**

        >>> from mutwo.events import basic
        >>> sequential_event = basic.SequentialEvent([basic.SimpleEvent(3), basic.SimpleEvent(2)])
        >>> sequential_event.cut_out(1, 4)
        >>> print(sequential_event)
        SequentialEvent([SimpleEvent(duration = 2), SimpleEvent(duration = 1)])
        """

        raise NotImplementedError

    @abc.abstractmethod
    def cut_off(
        self, start: parameters.abc.DurationType, end: parameters.abc.DurationType,
    ) -> typing.Optional[Event]:
        """Time-based deletion / shortening of the respective event.

        :param start: number that indicates absolute time when the
            cut off shall start.
        :param end: number that indicates the absolute time when the cut
            off shall end.

        **Example:**

        >>> from mutwo.events import basic
        >>> sequential_event = basic.SequentialEvent([basic.SimpleEvent(3), basic.SimpleEvent(2)])
        >>> sequential_event.cut_off(1, 3)
        >>> print(sequential_event)
        SequentialEvent([SimpleEvent(duration = 1), SimpleEvent(duration = 1)])
        """

        raise NotImplementedError

    def split_at(
        self, absolute_time: parameters.abc.DurationType
    ) -> typing.Tuple[Event, Event]:
        """Split event in two events at :attr:`absolute_time`.

        :param absolute_time: where event shall be split
        :return: Two events that result from splitting the present event.

        **Example:**

        >>> from mutwo.events import basic
        >>> sequential_event = basic.SequentialEvent([basic.SimpleEvent(3)])
        >>> sequential_event.split_at(1)
        (SequentialEvent([SimpleEvent(duration = 1)]), SequentialEvent([SimpleEvent(duration = 2)]))
        >>> sequential_event[0].split_at(1)
        (SimpleEvent(duration = 1), SimpleEvent(duration = 2))
        """

        return (
            self.cut_out(0, absolute_time, mutate=False),  # type: ignore
            self.cut_out(absolute_time, self.duration, mutate=False),  # type: ignore
        )


T = typing.TypeVar("T", bound=Event)


class ComplexEvent(Event, typing.List[T], typing.Generic[T]):
    """Abstract Event-Object, which contains other Event-Objects."""

    def __init__(self, iterable: typing.Iterable[T]):
        super().__init__(iterable)

    # ###################################################################### #
    #                           magic methods                                #
    # ###################################################################### #

    def __repr__(self) -> str:
        return "{}({})".format(type(self).__name__, super().__repr__())

    def __add__(self, event: typing.List[T]) -> ComplexEvent[T]:
        return type(self)(super().__add__(event))

    def __mul__(self, factor: int) -> ComplexEvent[T]:
        return type(self)(super().__mul__(factor))

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
            event = type(self)(event)  # type: ignore
        return event  # type: ignore

    # ###################################################################### #
    #                           properties                                   #
    # ###################################################################### #

    @Event.duration.setter  # type: ignore
    def duration(self, new_duration: parameters.abc.DurationType):
        old_duration = self.duration
        self.set_parameter(
            "duration",
            lambda duration: tools.scale(duration, 0, old_duration, 0, new_duration),  # type: ignore
        )

    # ###################################################################### #
    #                           private methods                              #
    # ###################################################################### #

    def _assert_start_in_range(self, start: parameters.abc.DurationType):
        """Helper method to make sure that start < event.duration.

        Can be used within the different squash_in methods.
        """
        try:
            assert self.duration >= start
        except AssertionError:
            message = (
                "Invalid value for start = '{}' in 'squash_in' call for event with"
                " duration = '{}'!".format(start, self.duration)
            )
            message += " Start has to be equal or smaller than the events duration."
            raise ValueError(message)

    # ###################################################################### #
    #                           public methods                               #
    # ###################################################################### #

    def copy(self) -> ComplexEvent[T]:
        """Return a deep copy of the ComplexEvent."""
        return copy.deepcopy(self)

    def destructive_copy(self) -> ComplexEvent[T]:
        return type(self)([event.destructive_copy() for event in self])  # type: ignore

    def get_event_from_indices(self, indices: typing.Sequence[int]) -> Event:
        """Get nested :class:`Event` from a sequence of indices.

        :param indices: The indices of the nested :class:`Event`.
        :type indices: typing.Sequence[int]

        **Example:**

        >>> from mutwo.events import basic
        >>> nested_sequential_event = basic.SequentialEvent([basic.SequentialEvent([basic.SimpleEvent(2)])])
        >>> nested_sequential_event.get_event_from_indices((0, 0))
        SimpleEvent(duration = 2)
        >>> # this is equal to:
        >>> nested_sequential_event[0][0]
        SimpleEvent(duration = 2)
        """

        return tools.get_nested_item_from_indices(indices, self)

    def get_parameter(self, parameter_name: str) -> typing.Tuple[typing.Any, ...]:
        return tuple(event.get_parameter(parameter_name) for event in self)

    @decorators.add_return_option
    def set_parameter(  # type: ignore
        self,
        parameter_name: str,
        object_or_function: typing.Union[
            typing.Callable[
                [parameters.abc.ParameterType], parameters.abc.ParameterType
            ],
            typing.Any,
        ],
        set_unassigned_parameter: bool = True,
    ) -> typing.Optional[ComplexEvent[T]]:
        [
            event.set_parameter(
                parameter_name,
                object_or_function,
                set_unassigned_parameter=set_unassigned_parameter,
            )
            for event in self
        ]

    @decorators.add_return_option
    def mutate_parameter(  # type: ignore
        self,
        parameter_name: str,
        function: typing.Union[
            typing.Callable[[parameters.abc.Parameter], None], typing.Any
        ],
    ) -> typing.Optional[ComplexEvent[T]]:
        [event.mutate_parameter(parameter_name, function) for event in self]

    @decorators.add_return_option
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
    ) -> typing.Optional[ComplexEvent[T]]:
        """Condition-based deletion of neighboring events.

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
            :class:`mutwo.events.basic.SimpleEvent`.
        :param event_to_remove: `True` if the second (left) event shall be removed
            and `False` if the first (right) event shall be removed.
        """

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
            events = self[pointer], self[pointer + 1]
            if all(isinstance(event, event_type_to_examine) for event in events):
                shall_delete = condition(*events)
                if shall_delete:
                    if event_to_remove:
                        process_surviving_event(*events)
                        del self[pointer + 1]
                    else:
                        process_surviving_event(*reversed(events))
                        del self[pointer]
                else:
                    pointer += 1
            # if event doesn't contain the event type which shall be tied,
            # it may still contain nested events which contains events with
            # the searched type
            else:
                tie_by_if_available(events[0])
                pointer += 1

        # Previously only the first event of the examined pairs has been tied,
        # therefore the very last event could have been forgotten.
        if not isinstance(self[-1], event_type_to_examine):
            tie_by_if_available(self[-1])

    # ###################################################################### #
    #                           abstract methods                             #
    # ###################################################################### #

    @abc.abstractmethod
    def squash_in(
        self, start: parameters.abc.DurationType, event_to_squash_in: Event
    ) -> typing.Optional[ComplexEvent[T]]:
        """Time-based insert of a new event into the present event.

        :param start: Absolute time where the event shall be inserted.
        :param event_to_squash_in: the event that shall be squashed into
            the present event.

        Squash in a new event to the present event.

        **Example:**

        >>> from mutwo.events import basic
        >>> sequential_event = basic.SequentialEvent([basic.SimpleEvent(3)])
        >>> sequential_event.squash_in(1, basic.SimpleEvent(1.5))
        >>> print(sequential_event)
        SequentialEvent([SimpleEvent(duration = 1), SimpleEvent(duration = 1.5), SimpleEvent(duration = 0.5)])
        """

        raise NotImplementedError

    @abc.abstractmethod
    def split_child_at(
        self, absolute_time: parameters.abc.DurationType
    ) -> typing.Optional[ComplexEvent[T]]:
        """Split child event in two events at :attr:`absolute_time`.

        :param absolute_time: where child event shall be split

        **Example:**

        >>> from mutwo.events import basic
        >>> sequential_event = basic.SequentialEvent([basic.SimpleEvent(3)])
        >>> sequential_event.split_child_at(1)
        >>> sequential_event
        SequentialEvent([SimpleEvent(duration = 1), SimpleEvent(duration = 2)])
        """

        raise NotImplementedError
