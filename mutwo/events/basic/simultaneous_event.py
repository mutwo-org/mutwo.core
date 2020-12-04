from mutwo.events import abc


# TODO still interesting. is this a set?
class SimultaneousEvent(abc.ComplexEvent):
    """Event-Object, which contains other Event-Objects, which happen simultaneously."""

    @property
    def duration(self):
        return max(tuple(event.duration for event in self))

    @duration.setter
    def duration(self, new_duration):
        for event in self:
            event.duration = new_duration
