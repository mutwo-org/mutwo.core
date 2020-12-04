import abc


class Event(abc.ABC):

    # TODO so now the big question is: how do we want to type duration?
    @property
    @abc.abstractmethod
    def duration(self) -> float:
        raise NotImplementedError
