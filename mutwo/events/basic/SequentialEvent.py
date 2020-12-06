import typing

from mutwo import events
from mutwo.utilities import tools


class SequentialEvent(events.abc.ComplexEvent):
    """Event-Object which contains other Event-Objects which happen in a linear order."""

    @events.abc.ComplexEvent.duration.getter
    def duration(self):
        return sum(event.duration for event in self)

    @property
    def absolute_points(self) -> typing.Iterable:
        """Return absolute point in time for each event."""
        return tools.accumulate_from_zero((event.duration for event in self))
