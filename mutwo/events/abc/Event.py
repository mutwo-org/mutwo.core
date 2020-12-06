import abc
import numbers


class Event(abc.ABC):
    """abstract Event-Object"""

    @property
    @abc.abstractmethod
    def duration(self) -> numbers.Number:
        raise NotImplementedError
