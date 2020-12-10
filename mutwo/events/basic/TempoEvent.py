import numbers
import typing

from mutwo.events import basic
from mutwo import parameters

BPM = typing.NewType("BPM", numbers.Number)


class TempoEvent(basic.SimpleEvent):
    def __init__(
        self,
        duration: parameters.durations.abc.DurationType,
        tempo_start: BPM,
        tempo_end: BPM = None,
        curve_shape: float = 0,
        reference: parameters.durations.abc.DurationType = 1,
    ):
        super().__init__(duration)

        if tempo_end is None:
            tempo_end = tempo_start

        self.tempo_start = tempo_start
        self.tempo_end = tempo_end
        self.curve_shape = curve_shape
        self.reference = reference

    def __repr__(self) -> str:
        return "{}({}: {} BPM to {} BPM)".format(
            type(self).__name__, self.duration, self.tempo_start, self.tempo_end
        )

    def is_static(self) -> bool:
        return self.tempo_start == self.tempo_end
