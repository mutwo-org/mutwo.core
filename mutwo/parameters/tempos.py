import typing

from mutwo import parameters
from mutwo.utilities import constants

__all__ = ("TempoPoint",)


class TempoPoint(parameters.abc.Parameter):
    def __init__(
        self,
        tempo_in_beats_per_minute: float,
        reference: constants.Real = 1,
        textual_indication: typing.Optional[str] = None
    ):
        self.tempo_in_beats_per_minute = tempo_in_beats_per_minute
        self.reference = reference
        self.textual_indication = textual_indication

    def __repr__(self) -> str:
        return "{}(BPM: {}, reference: {})".format(
            type(self).__name__, self.tempo_in_beats_per_minute, self.reference
        )

    @property
    def absolute_tempo_in_beat_per_minute(self) -> float:
        return self.tempo_in_beats_per_minute * self.reference
