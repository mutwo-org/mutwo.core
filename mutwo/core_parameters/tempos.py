# This file is part of mutwo, ecosystem for time-based arts.
#
# Copyright (C) 2020-2023
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Submodule for the parameter tempo.
"""

import typing

from mutwo import core_constants
from mutwo import core_parameters

__all__ = ("DirectTempoPoint",)


class DirectTempoPoint(core_parameters.abc.TempoPoint):
    """Represent the active tempo at a specific moment in time.

    :param tempo_or_tempo_range: Specify a tempo in
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
        tempo_or_tempo_range: core_parameters.constants.TempoOrTempoRangeInBeatsPerMinute,
        reference: core_constants.Real = 1,
        textual_indication: typing.Optional[str] = None,
    ):
        self.tempo_or_tempo_range = tempo_or_tempo_range
        self.reference = reference
        self.textual_indication = textual_indication

    # NOTE: Dummy getter / setter to avoid TypeError due to
    # abstract parent class.
    @property
    def reference(self) -> float:
        return self._reference

    @reference.setter
    def reference(self, reference: core_constants.Real):
        self._reference = float(reference)

    @property
    def tempo_or_tempo_range(
        self,
    ) -> core_parameters.constants.TempoOrTempoRangeInBeatsPerMinute:
        return self._tempo_or_tempo_range

    @tempo_or_tempo_range.setter
    def tempo_or_tempo_range(
        self,
        tempo_or_tempo_range: core_parameters.constants.TempoOrTempoRangeInBeatsPerMinute,
    ):
        self._tempo_or_tempo_range = tempo_or_tempo_range
        return self._tempo_or_tempo_range
