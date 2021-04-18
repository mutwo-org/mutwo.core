import typing

from mutwo import parameters
from mutwo.utilities import constants

__all__ = ("TempoPoint",)


class TempoPoint(parameters.abc.Parameter):
    def __init__(
        self,
        tempo_in_beats_per_minute: float,
        reference: constants.Real = 1,
        textual_indication: typing.Optional[str] = None,
    ):
        self.tempo_in_beats_per_minute = tempo_in_beats_per_minute
        self.reference = reference
        self.textual_indication = textual_indication

    def __repr__(self) -> str:
        return "{}(BPM: {}, reference: {})".format(
            type(self).__name__, self.tempo_in_beats_per_minute, self.reference
        )

    def __eq__(self, other: object) -> bool:
        attributes_to_compare = (
            "tempo_in_beats_per_minute",
            "reference",
            "textual_indication",
        )
        try:
            comparision_tuple = tuple(
                getattr(other, attribute) for attribute in attributes_to_compare
            )
        except AttributeError:
            return False

        return all(
            tuple(
                getattr(self, attribute) == value_of_other
                for attribute, value_of_other in zip(
                    attributes_to_compare, comparision_tuple
                )
            )
        )

    @property
    def absolute_tempo_in_beat_per_minute(self) -> float:
        return self.tempo_in_beats_per_minute * self.reference
