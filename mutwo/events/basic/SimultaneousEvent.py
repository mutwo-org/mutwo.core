from mutwo import events


class SimultaneousEvent(events.abc.ComplexEvent):
    """Event-Object, which contains other Event-Objects, which happen at the same time."""

    @events.abc.ComplexEvent.duration.getter
    def duration(self):
        return max(event.duration for event in self)
