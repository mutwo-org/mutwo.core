import typing

from mutwo import parameters
from mutwo.utilities import constants

__all__ = ("TempoPoint",)

TempoInBeatsPerMinute = typing.NewType("TempoInBeatsPerMinute", float)


class TempoPoint(parameters.abc.Parameter):
    def __init__(
        self,
        tempo_in_beats_per_minute: TempoInBeatsPerMinute,
        reference: constants.Real = 1,
    ):
        self.tempo_in_beats_per_minute = tempo_in_beats_per_minute
        self.reference = reference

    def __repr__(self) -> str:
        return "{}(BPM: {}, reference: {})".format(
            type(self).__name__, self.tempo_in_beats_per_minute, self.reference
        )
