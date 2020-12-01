import abc


class Event(abc.ABC):

    # TODO is this the right way?
    @abc.abstractclassmethod
    def is_rest(self) -> bool:
        raise NotImplementedError

    # TODO so now the big question is: how do we want to type duration?
    @property
    @abc.abstractmethod
    def duration(self) -> float:
        raise NotImplementedError
