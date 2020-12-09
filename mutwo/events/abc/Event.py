import abc
import typing

from mutwo.parameters import durations


class Event(abc.ABC):
    """abstract Event-Object"""

    @property
    @abc.abstractmethod
    def duration(self) -> durations.abc.DurationType:
        raise NotImplementedError

    @abc.abstractmethod
    def set_parameter(
        self,
        parameter_name: str,
        object_or_function: typing.Union[typing.Callable, typing.Any],
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def change_parameter(
        self, parameter_name: str, function: typing.Union[typing.Callable, typing.Any],
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_parameter(self, parameter_name: str) -> typing.Union[tuple, typing.Any]:
        raise NotImplementedError

    def get_allocated_parameter(self, parameter_name: str) -> tuple:
        return tuple(
            filter(lambda value: value is not None, self.get_parameter(parameter_name))
        )
