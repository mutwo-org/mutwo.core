import typing

from mutwo.events import abc
from mutwo import parameters


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

    def get_parameter(self, parameter_name: str) -> tuple:
        """Return tuple filled with the value of each event for the asked parameter.

        If an event doesn't posses the asked attribute, 'None' will be added.
        """
        try:
            return getattr(self, parameter_name)
        except AttributeError:
            return None

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
