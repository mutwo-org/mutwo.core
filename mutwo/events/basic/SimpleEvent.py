import copy
import typing

from mutwo.events import abc
from mutwo import parameters
from mutwo.utilities import decorators


class SimpleEvent(abc.Event):
    """Event-Object, which doesn't contain other Event-Objects."""

    def __init__(self, new_duration: parameters.durations.abc.DurationType):
        self.duration = new_duration

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, new_duration: parameters.durations.abc.DurationType):
        self._duration = new_duration

    def destructive_copy(self) -> "SimpleEvent":
        return copy.deepcopy(self)

    def get_parameter(self, parameter_name: str) -> typing.Any:
        """Return attribute if it has been assigned to the object.

        Otherwise returns None.
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
        self,
        start: parameters.durations.abc.DurationType,
        end: parameters.durations.abc.DurationType,
    ) -> typing.Union[None, "SimpleEvent"]:
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
