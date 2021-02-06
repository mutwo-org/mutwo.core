import numbers
import typing

from mutwo import parameters

TempoInBeatsPerMinute = typing.NewType("BPM", numbers.Number)


class TempoPoint(parameters.abc.Parameter):
    def __init__(
        self,
        tempo_in_beats_per_minute: TempoInBeatsPerMinute,
        reference: numbers.Number = 1,
    ):
        self.tempo_in_beats_per_minute = tempo_in_beats_per_minute
        self.reference = reference

    def __repr__(self) -> str:
        return "{}(BPM: {}, reference: {})".format(
            type(self).__name__, self.tempo_in_beats_per_minute, self.reference
        )
