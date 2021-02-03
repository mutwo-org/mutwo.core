import abc
import typing

from mutwo import parameters


class Event(abc.ABC):
    """Abstract Event-Object"""

    @property
    @abc.abstractmethod
    def duration(self) -> parameters.durations.abc.DurationType:
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
        raise NotImplementedError

    @abc.abstractmethod
    def mutate_parameter(
        self,
        parameter_name: str,
        function: typing.Union[
            typing.Callable[[parameters.abc.Parameter], None], typing.Any
        ],
    ) -> None:
        raise NotImplementedError

    @staticmethod
    def _assert_correct_start_and_end_values(
        start: parameters.durations.abc.DurationType,
        end: parameters.durations.abc.DurationType,
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
        self,
        start: parameters.durations.abc.DurationType,
        end: parameters.durations.abc.DurationType,
    ) -> typing.Union[None, "Event"]:
        """Time-based slicing of the respective event.

        :param start: number that indicates the point when the
            cut up shall start.
        :param end: number that indicates the point when the cut
            up shall end.
        """

        raise NotImplementedError
