import typing

from mutwo import events
from mutwo.parameters import durations

T = typing.TypeVar("T")


class SimultaneousEvent(events.abc.ComplexEvent, typing.Generic[T]):
    """Event-Object which contains other Event-Objects which happen at the same time."""

    @events.abc.ComplexEvent.duration.getter
    def duration(self) -> durations.abc.DurationType:
        return max(event.duration for event in self)
