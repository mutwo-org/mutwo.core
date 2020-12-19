import copy
import numbers
import typing

from mutwo.events import basic
from mutwo import parameters


class EnvelopeEvent(basic.SimpleEvent):
    def __init__(
        self,
        duration: parameters.durations.abc.DurationType,
        object_start: typing.Any,
        object_stop: typing.Any = None,
        curve_shape: float = 0,
        key: typing.Callable[[typing.Any], numbers.Number] = lambda object_: object_,
    ):
        super().__init__(duration)

        self.key = key
        if object_stop is None:
            object_stop = copy.deepcopy(object_start)

        self.object_start = object_start
        self.object_stop = object_stop
        self.curve_shape = curve_shape

    @property
    def value_start(self) -> numbers.Number:
        return self.key(self.object_start)

    @property
    def value_stop(self) -> numbers.Number:
        return self.key(self.object_stop)

    def __repr__(self) -> str:
        return "{}({}: {} to {})".format(
            type(self).__name__, self.duration, self.value_start, self.value_stop
        )

    def is_static(self) -> bool:
        return self.value_start == self.value_stop
