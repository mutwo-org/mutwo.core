from mutwo.events import abc


class SimpleEvent(abc.Event):
    """Event-Object, which doesn't contain other Event-Objects."""

    def __init__(self, new_duration):
        self.duration = new_duration

    # TODO double
    @classmethod
    def is_rest(cls) -> bool:
        return False

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, new_duration):
        self._duration = new_duration
