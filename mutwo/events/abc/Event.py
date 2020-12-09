import abc

from mutwo.parameters import durations


class Event(abc.ABC):
    """abstract Event-Object"""

    @property
    @abc.abstractmethod
    def duration(self) -> durations.abc.DurationType:
        raise NotImplementedError

    @abc.abstractmethod
    def get_parameter(self, parameter_name: str) -> tuple:
        raise NotImplementedError

    def get_allocated_parameter(self, parameter_name: str) -> tuple:
        return tuple(
            filter(lambda value: value is not None, self.get_parameter(parameter_name))
        )
