import copy
import typing

# here it is not possible to write 'from mutwo import events; events.abc'
# TODO(find smarter solution)
import mutwo.events.abc as events_abc
from mutwo.utilities import tools


class ComplexEvent(events_abc.Event, list):
    """Event-Object, which contains other Event-Objects."""

    def __init__(self, iterable: typing.Iterable[events_abc.Event]):
        super().__init__(iterable)

    def __repr__(self) -> str:
        return "{}({})".format(type(self).__name__, super().__repr__())

    def copy(self) -> "ComplexEvent":
        """Return a deep copy of the ComplexEvent."""
        return copy.deepcopy(self)

    def __add__(self, other: "ComplexEvent") -> "ComplexEvent":
        return type(self)(super().__add__(other))

    def __getitem__(self, index_or_slice: typing.Union[int, slice]) -> events_abc.Event:
        event = super().__getitem__(index_or_slice)
        if isinstance(index_or_slice, slice):
            return type(self)(event)
        return event

    @events_abc.Event.duration.setter
    def duration(self, new_duration) -> None:
        old_duration = self.duration
        # TODO this is shit. we want a more general approach to manipulate attributes of sequences
        for event in self:
            event.duration = tools.scale(
                event.duration, 0, old_duration, 0, new_duration
            )
