from .event import Event


class SimpleEvent(Event):
    """Event-Object, which doesn't contain other Event-Objects."""

    # TODO double
    @classmethod
    def is_rest(cls) -> bool:
        return False

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, dur):
        self._duration = dur
