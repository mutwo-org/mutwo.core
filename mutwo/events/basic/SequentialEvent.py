import itertools
import numbers
import typing

from mutwo import events
from mutwo import parameters
from mutwo.utilities import decorators
from mutwo.utilities import tools

T = typing.TypeVar("T")


class SequentialEvent(events.abc.ComplexEvent, typing.Generic[T]):
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

    @decorators.add_return_option
    def cut_up(
        self,
        start: parameters.durations.abc.DurationType,
        end: parameters.durations.abc.DurationType,
    ) -> typing.Union[None, "SequentialEvent"]:
        cut_up_events = []

        for event_start, event in zip(self.absolute_times, self):
            event_end = event_start + event.duration
            appendable_conditions = (
                event_start >= start and event_start < end,
                event_end <= end and event_end > start,
                event_start <= start and event_end >= end,
            )

            appendable = any(appendable_conditions)
            if appendable:
                cut_up_start = 0
                cut_up_end = event.duration

                if event_start < start:
                    cut_up_start += start - event_start

                if event_end > end:
                    cut_up_end -= event_end - end

                event = event.cut_up(cut_up_start, cut_up_end, mutate=False)
                cut_up_events.append(event)

        self[:] = cut_up_events
