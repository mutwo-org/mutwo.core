import itertools
import numbers

from mutwo import events
from mutwo.utilities import tools


class SequentialEvent(events.abc.ComplexEvent):
    """Event-Object which contains other Events which happen in a linear order."""

    @events.abc.ComplexEvent.duration.getter
    def duration(self):
        return sum(event.duration for event in self)

    @property
    def absolute_times(self) -> tuple:
        """Return absolute point in time for each event."""
        durations = (event.duration for event in self)
        return tuple(tools.accumulate_from_zero(durations))[:-1]

    @property
    def start_and_end_time_per_event(self) -> tuple:
        """Return start and end time  for each event."""
        durations = (event.duration for event in self)
        absolute_times = tuple(tools.accumulate_from_zero(durations))
        return tuple(zip(absolute_times, absolute_times[1:]))

    def get_event_at(self, absolute_time: numbers.Number) -> events.abc.Event:
        absolute_times = self.absolute_times
        after_absolute_time = itertools.dropwhile(
            lambda x: absolute_time < x[0],
            zip(reversed(absolute_times), reversed(self)),
        )
        return next(after_absolute_time)[1]
