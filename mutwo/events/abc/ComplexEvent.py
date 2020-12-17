import copy
import typing

import mutwo.events.abc as events_abc
from mutwo import parameters
from mutwo.utilities import decorators
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
        self.set_parameter(
            "duration",
            lambda duration: tools.scale(duration, 0, old_duration, 0, new_duration),
        )

    def destructive_copy(self) -> "ComplexEvent":
        return type(self)([event.destructive_copy() for event in self])

    def get_parameter(self, parameter_name: str) -> tuple:
        """Return tuple filled with the value of each event for the asked parameter.

        If an event doesn't posses the asked attribute 'None' will be added.
        """
        return tuple(event.get_parameter(parameter_name) for event in self)

    @decorators.add_return_option
    def set_parameter(
        self,
        parameter_name: str,
        object_or_function: typing.Union[
            typing.Callable[[parameters.abc.Parameter], parameters.abc.Parameter],
            typing.Any,
        ],
    ) -> None:
        """Sets parameter to new value for all children events.

        For setting the parameter either a new value can be passed directly or a
        function can be passed. The function gets as an argument the previous value
        that has had been assigned to the respective object and has to return the
        new value.
        """
        [event.set_parameter(parameter_name, object_or_function) for event in self]

    @decorators.add_return_option
    def mutate_parameter(
        self,
        parameter_name: str,
        function: typing.Union[
            typing.Callable[[parameters.abc.Parameter], None], typing.Any
        ],
    ) -> None:
        [event.mutate_parameter(parameter_name, function) for event in self]
