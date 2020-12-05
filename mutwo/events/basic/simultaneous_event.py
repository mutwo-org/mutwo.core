from mutwo import events


class SimultaneousEvent(events.abc.ComplexEvent):
    """Event-Object, which contains other Event-Objects, which happen simultaneously."""

    @events.abc.ComplexEvent.duration.getter
    def duration(self):
        return max(tuple(event.duration for event in self))
