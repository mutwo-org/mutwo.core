import itertools
import numbers
import typing

from mutwo import events
from mutwo.utilities import tools


class SequentialEvent(events.abc.ComplexEvent):
    """Event-Object which contains other Event-Objects which happen in a linear order."""

    @events.abc.ComplexEvent.duration.getter
    def duration(self):
        return sum(event.duration for event in self)

    @property
    def absolute_times(self) -> typing.Sequence:
        """Return absolute point in time for each event."""
        durations = (event.duration for event in self)
        return tuple(tools.accumulate_from_zero(durations))[:-1]

    def get_event_at(self, absolute_time: numbers.Number) -> events.abc.Event:
        absolute_times = self.absolute_times
        after_absolute_time = itertools.dropwhile(
            lambda x: absolute_time < x[0],
            zip(reversed(absolute_times), reversed(self)),
        )
        return next(after_absolute_time)[1]
