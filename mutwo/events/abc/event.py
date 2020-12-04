import abc


class Event(abc.ABC):

    # TODO is this the right way?
    @classmethod
    @abc.abstractmethod
    def is_rest(cls) -> bool:
        raise NotImplementedError

    # TODO so now the big question is: how do we want to type duration?
    @property
    @abc.abstractmethod
    def duration(self) -> float:
        raise NotImplementedError
