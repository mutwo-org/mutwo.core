from mutwo.events import abc


# TODO still interesting. is this a set?
class SimultaneousEvent(abc.ComplexEvent):
    """Event-Object, which contains other Event-Objects, which happen simultaneously."""

    @property
    def duration(self):
        return max(tuple(event.duration for event in self))
