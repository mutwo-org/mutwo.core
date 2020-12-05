from mutwo.events import abc


class SequentialEvent(abc.ComplexEvent):
    """Event-Object, which contains other Event-Objects, which happen one after another."""

    @abc.ComplexEvent.duration.getter
    def duration(self):
        return sum(event.duration for event in self)

    # TODO we need inspect absolute timepoints or get absolute times (or both)
