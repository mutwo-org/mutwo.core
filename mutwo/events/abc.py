"""This file contains abstract base classes for the event module."""

import abc
import copy
import typing

from mutwo import parameters
from mutwo.utilities import decorators
from mutwo.utilities import tools

__all__ = ("Event", "ComplexEvent")


class Event(abc.ABC):
    """Abstract Event-Object"""

    @property
    @abc.abstractmethod
    def duration(self) -> parameters.abc.DurationType:
        """Return the duration of an event (which can be any number).

        The unit of the duration is up to the interpretation of the user
        and the respective conversion routine that will be used. For
        instance when using the CsoundScoreConverter, the duration will be
        understood as seconds, while the MidiFileConverter will read duration
        as beats.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def destructive_copy(self) -> "Event":
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
    def get_parameter(self, parameter_name: str) -> typing.Union[tuple, typing.Any]:
        """Return event attribute with the entered name.

        :parameter_name: The name of the attribute that shall be returned.
        :returns: Return tuple containing the assigned values for each contained
            event. If an event doesn't posses the asked parameter, mutwo will simply
            add None to the tuple for the respective event.

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
            typing.Callable[[parameters.abc.Parameter], parameters.abc.Parameter],
            typing.Any,
        ],
    ) -> None:
        """Sets parameter to new value for all children events.

        :param parameter_name: The name of the parameter which values shall be changed.
        :param object_or_function: For setting the parameter either a new value can be
            passed directly or a function can be passed. The function gets as an
            argument the previous value that has had been assigned to the respective
            object and has to return a new value that will be assigned to the object.

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

        >>> from mutwo.events import basic, music
        >>> from mutwo.parameters import pitches
        >>> sequential_event = basic.SequentialEvent([music.NoteLike([pitches.WesternPitch('c', 4), pitches.WesternPitch('e', 4)], 2, 1)])
        >>> sequential_event.mutate_parameter('pitch_or_pitches', lambda pitch_or_pitches: [pitch.add(12) for pitch in pitch_or_pitches])
        >>> # now all pitches should be one octave higher (from 4 to 5)
        >>> sequential_event.get_parameter('pitch_or_pitches')
        ([WesternPitch(c5), WesternPitch(e5)],)
        """

        raise NotImplementedError

    @staticmethod
    def _assert_correct_start_and_end_values(
        start: parameters.abc.DurationType, end: parameters.abc.DurationType,
    ):
        """Helper method to make sure that start < end.

        Can be used within the different cut_up methods.
        """
        try:
            assert end > start
        except AssertionError:
            message = (
                "Invalid values for start and end property (start = '{}' and end ="
                " '{}')!".format(start, end)
            )
            message += " Value for end has to be bigger than value for start."
            raise ValueError(message)

    @abc.abstractmethod
    def cut_up(
        self, start: parameters.abc.DurationType, end: parameters.abc.DurationType,
    ) -> typing.Union[None, "Event"]:
        """Time-based slicing of the respective event.

        :param start: number that indicates the point when the
            cut up shall start.
        :param end: number that indicates the point when the cut
            up shall end.

        >>> from mutwo.events import basic
        >>> sequential_event = basic.SequentialEvent([basic.SimpleEvent(3), basic.SimpleEvent(2)])
        >>> sequential_event.cut_up(1, 4)
        >>> print(sequential_event)
        SequentialEvent([SimpleEvent(duration = 2), SimpleEvent(duration = 1)])
        """

        raise NotImplementedError


class ComplexEvent(Event, list):
    """Event-Object, which contains other Event-Objects."""

    def __init__(self, iterable: typing.Iterable[Event]):
        super().__init__(iterable)

    def __repr__(self) -> str:
        return "{}({})".format(type(self).__name__, super().__repr__())

    def copy(self) -> "ComplexEvent":
        """Return a deep copy of the ComplexEvent."""
        return copy.deepcopy(self)

    def __add__(self, event: "ComplexEvent") -> "ComplexEvent":
        return type(self)(super().__add__(event))

    def __getitem__(self, index_or_slice: typing.Union[int, slice]) -> Event:
        event = super().__getitem__(index_or_slice)
        if isinstance(index_or_slice, slice):
            return type(self)(event)
        return event

    @Event.duration.setter
    def duration(self, new_duration: parameters.abc.DurationType) -> None:
        old_duration = self.duration
        self.set_parameter(
            "duration",
            lambda duration: tools.scale(duration, 0, old_duration, 0, new_duration),
        )

    def destructive_copy(self) -> "ComplexEvent":
        return type(self)([event.destructive_copy() for event in self])

    def get_parameter(self, parameter_name: str) -> typing.Tuple[typing.Any]:
        return tuple(event.get_parameter(parameter_name) for event in self)

    @decorators.add_return_option
    def set_parameter(
        self,
        parameter_name: str,
        object_or_function: typing.Union[
            typing.Callable[[parameters.abc.Parameter], parameters.abc.Parameter],
            typing.Any,
        ],
    ) -> None:
        [event.set_parameter(parameter_name, object_or_function) for event in self]

    @decorators.add_return_option
    def mutate_parameter(
        self,
        parameter_name: str,
        function: typing.Union[
            typing.Callable[[parameters.abc.Parameter], None], typing.Any
        ],
    ) -> None:
        [event.mutate_parameter(parameter_name, function) for event in self]
