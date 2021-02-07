import numbers

from mutwo import events
from mutwo import parameters


class ValueEvent(events.basic.SimpleEvent):
    def __init__(
        self,
        duration: parameters.abc.DurationType,
        value: numbers.Number,
    ):
        self.value = value
        super().__init__(duration)
