"""Submodule for the parameter tempo.
"""

import typing

from mutwo import core_constants
from mutwo import core_utilities

__all__ = ("TempoPoint",)

TempoInBeatsPerMinute = float
TempoRangeInBeatsPerMinute = tuple[TempoInBeatsPerMinute, TempoInBeatsPerMinute]
TempoOrTempoRangeInBeatsPerMinute = typing.Union[
    TempoInBeatsPerMinute, TempoRangeInBeatsPerMinute
]


class TempoPoint(object):
    """Represent the active tempo at a specific moment in time.

    :param tempo_or_tempo_range_in_beats_per_minute: Specify a tempo in
        `beats per minute <https://en.wikipedia.org/wiki/Tempo#Measurement>`_.
        Tempo can also be a tempo range where the first value indicates a minimal
        tempo and the second value the maximum tempo. If the user specifies a
        range :mod:`mutwo` will use the minimal tempo in internal calculations.
    :param reference: The reference with which the tempo will be multiplied.
        In terms of Western notation a reference = 1 will be a 1/4 beat, a
        reference of 2 will be a 1/2 beat, etc. Default to 1.
    :param textual_indication: Sometimes it is desired to specify an extra
        text indication how fast or slow the music should be (for instance
        "Adagio" in Western music). Default to `None`.

    **Example:**

    >>> from mutwo import core_events
    >>> from mutwo import core_parameters
    >>> tempo_envelope = core_events.TempoEnvelope([
    >>>     [0, core_parameters.TempoPoint(60, reference=2)]
    >>> ])
    """

    def __init__(
        self,
        tempo_or_tempo_range_in_beats_per_minute: TempoOrTempoRangeInBeatsPerMinute,
        reference: core_constants.Real = 1,
        textual_indication: typing.Optional[str] = None,
    ):
        self.tempo_or_tempo_range_in_beats_per_minute = (
            tempo_or_tempo_range_in_beats_per_minute
        )
        self.reference = reference
        self.textual_indication = textual_indication

    def __repr__(self) -> str:
        return "{}(BPM = {}, reference = {})".format(
            type(self).__name__, self.tempo_in_beats_per_minute, self.reference
        )

    def __eq__(self, other: object) -> bool:
        attribute_to_compare_tuple = (
            "tempo_in_beats_per_minute",
            "reference",
            "textual_indication",
        )
        return core_utilities.test_if_objects_are_equal_by_parameter_tuple(
            self, other, attribute_to_compare_tuple
        )

    @property
    def tempo_in_beats_per_minute(self) -> TempoInBeatsPerMinute:
        """Get tempo in `beats per minute <https://en.wikipedia.org/wiki/Tempo#Measurement>`_

        If :attr:`tempo_or_tempo_range_in_beats_per_minute` is a range
        mutwo will return the minimal tempo.
        """

        if isinstance(self.tempo_or_tempo_range_in_beats_per_minute, tuple):
            return self.tempo_or_tempo_range_in_beats_per_minute[0]
        else:
            return self.tempo_or_tempo_range_in_beats_per_minute

    @property
    def absolute_tempo_in_beats_per_minute(self) -> float:
        """Get absolute tempo in `beats per minute <https://en.wikipedia.org/wiki/Tempo#Measurement>`_

        The absolute tempo takes the :attr:`reference` of the :class:`TempoPoint`
        into account.
        """

        return self.tempo_in_beats_per_minute * self.reference
