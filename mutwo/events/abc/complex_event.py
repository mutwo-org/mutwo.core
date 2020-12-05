import typing

# here it is not possible to write 'from mutwo import events; events.abc'
# TODO(find smarter solution)
import mutwo.events.abc as events_abc
from mutwo.utilities import tools


class ComplexEvent(events_abc.Event, list):
    """Event-Object, which contains other Event-Objects."""

    def __init__(self, iterable: typing.Iterable[events_abc.Event]):
        super().__init__(iterable)

    @events_abc.Event.duration.setter
    def duration(self, new_duration) -> None:
        old_duration = self.duration
        # TODO this is shit. we want a more general approach to manipulate attributes of sequences
        for event in self:
            event.duration = tools.scale(
                event.duration, 0, old_duration, 0, new_duration
            )
