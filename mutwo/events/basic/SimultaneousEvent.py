import typing

from mutwo import events
from mutwo.parameters import durations

from mutwo.utilities import decorators

T = typing.TypeVar("T")


class SimultaneousEvent(events.abc.ComplexEvent, typing.Generic[T]):
    """Event-Object which contains other Event-Objects which happen at the same time."""

    @events.abc.ComplexEvent.duration.getter
    def duration(self) -> durations.abc.DurationType:
        return max(event.duration for event in self)

    @decorators.add_return_option
    def cut_up(
        self, start: durations.abc.DurationType, end: durations.abc.DurationType,
    ) -> typing.Union[None, "SimultaneousEvent"]:
        self._assert_correct_start_and_end_values(start, end)
        cut_up_events = []

        for event in self:
            cut_up_events.append(event.cut_up(start, end, mutate=False))

        self[:] = cut_up_events
