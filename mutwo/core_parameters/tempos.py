"""Submodule for the parameter tempo.
"""

import typing

from mutwo import core_constants
from mutwo import core_parameters

__all__ = ("DirectTempoPoint",)


class DirectTempoPoint(core_parameters.abc.TempoPoint):
    """Represent the active tempo at a specific moment in time.

    :param tempo_or_tempo_range_in_beats_per_minute: Specify a tempo in
        `beats per minute <https://en.wikipedia.org/wiki/Tempo#Measurement>`_.
        Tempo can also be a tempo range where the first value indicates a
        minimal tempo and the second value the maximum tempo. If the user
        specifies a range :mod:`mutwo` will use the minimal tempo in internal
        calculations.
    :param reference: The reference with which the tempo will be multiplied.
        In terms of Western notation a reference = 1 will be a 1/4 beat, a
        reference of 2 will be a 1/2 beat, etc. Default to 1.
    :type reference: float
    :param textual_indication: Sometimes it is desired to specify an extra
        text indication how fast or slow the music should be (for instance
        "Adagio" in Western music). Default to `None`.
    :type textual_indication: typing.Optional[str]

    **Example:**

    >>> from mutwo import core_events
    >>> from mutwo import core_parameters
    >>> tempo_envelope = core_events.TempoEnvelope([
    ...     [0, core_parameters.DirectTempoPoint(60, reference=2)]
    ... ])
    """

    def __init__(
        self,
        tempo_or_tempo_range_in_beats_per_minute: core_parameters.constants.TempoOrTempoRangeInBeatsPerMinute,
        reference: core_constants.Real = 1,
        textual_indication: typing.Optional[str] = None,
    ):
        self.tempo_or_tempo_range_in_beats_per_minute = (
            tempo_or_tempo_range_in_beats_per_minute
        )
        self.reference = reference
        self.textual_indication = textual_indication

    # XXX: Dummy getter / setter to avoid TypeError due to
    # abstract parent class.
    @property
    def reference(self) -> float:
        return self._reference

    @reference.setter
    def reference(self, reference: float):
        self._reference = reference

    @property
    def tempo_or_tempo_range_in_beats_per_minute(
        self,
    ) -> core_parameters.constants.TempoOrTempoRangeInBeatsPerMinute:
        return self._tempo_or_tempo_range_in_beats_per_minute

    @tempo_or_tempo_range_in_beats_per_minute.setter
    def tempo_or_tempo_range_in_beats_per_minute(
        self,
        tempo_or_tempo_range_in_beats_per_minute: core_parameters.constants.TempoOrTempoRangeInBeatsPerMinute,
    ):
        self._tempo_or_tempo_range_in_beats_per_minute = (
            tempo_or_tempo_range_in_beats_per_minute
        )
        return self._tempo_or_tempo_range_in_beats_per_minute
