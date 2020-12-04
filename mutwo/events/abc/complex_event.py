import abc

from mutwo.events.abc.event import Event


# TODO does this already get a constructor? so we can express that this consists only of EVENTS
class ComplexEvent(Event):
    """Event-Object, which might contain other Event-Objects."""

    # TODO double
    @classmethod
    def is_rest(cls) -> bool:
        return False

    @abc.abstractmethod
    def __iter__(self):
        raise NotImplementedError

    # TODO we nee append, concatenation etc, or?
    # we need also the get parameter iterator shit
