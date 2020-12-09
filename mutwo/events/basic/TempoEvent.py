import numbers

from mutwo.events import basic
from mutwo import parameters


class TempoEvent(basic.SimpleEvent):
    def __init__(
        self,
        duration: parameters.durations.abc.DurationType,
        tempo_start,
        tempo_end=None,
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

    @staticmethod
    def bpm_to_seconds_per_beat(bpm: numbers.Number) -> float:
        return 60 / bpm

    def __repr__(self) -> str:
        return "{}({}, {}, {})".format(
            type(self).__name__, self.duration, self.tempo_start, self.tempo_end
        )
