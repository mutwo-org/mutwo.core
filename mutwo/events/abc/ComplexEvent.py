import copy
import typing

import mutwo.events.abc as events_abc
from mutwo import parameters
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

    def __add__(self, event: "ComplexEvent") -> "ComplexEvent":
        return type(self)(super().__add__(event))

    def __getitem__(self, index_or_slice: typing.Union[int, slice]) -> events_abc.Event:
        event = super().__getitem__(index_or_slice)
        if isinstance(index_or_slice, slice):
            return type(self)(event)
        return event

    @events_abc.Event.duration.setter
    def duration(self, new_duration: parameters.durations.abc.DurationType) -> None:
        old_duration = self.duration
        # TODO(this is shit. we want a more general approach to manipulate attributes
        # of sequences)
        for event in self:
            event.duration = tools.scale(
                event.duration, 0, old_duration, 0, new_duration
            )

    def get_parameter(self, parameter_name: str) -> tuple:
        """Return tuple filled with the value of each event for the asked parameter.

        If an event doesn't posses the asked attribute 'None' will be added.
        """
        return tuple(event.get_parameter(parameter_name) for event in self)

    def set_parameter(
        self,
        parameter_name: str,
        object_or_function: typing.Union[
            typing.Callable[[parameters.abc.Parameter], parameters.abc.Parameter],
            typing.Any,
        ],
    ) -> None:
        [event.set_parameter(parameter_name, object_or_function) for event in self]

    def change_parameter(
        self, parameter_name: str,
        function: typing.Union[
            typing.Callable[[parameters.abc.Parameter], None], typing.Any
        ],
    ) -> None:
        [event.change_parameter(parameter_name, function) for event in self]
