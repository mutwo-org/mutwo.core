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

__all__ = ("DirectDuration", "RatioDuration")

import functools

try:
    import quicktions as fractions
except ImportError:
    import fractions

from mutwo import core_constants
from mutwo import core_parameters
from mutwo import core_utilities


class DirectDuration(core_parameters.abc.Duration):
    """Simple `Duration` which is directly initialised by its value.

    **Example:**

    >>> from mutwo import core_parameters
    >>> # create duration with beat_count = 10
    >>> my_duration = core_parameters.DirectDuration(10)
    >>> my_duration.beat_count
    10.0
    """

    def __init__(self, beat_count: core_constants.Real):
        self.beat_count = beat_count

    @property
    def beat_count(self) -> float:
        return self._beat_count

    @beat_count.setter
    def beat_count(self, beat_count: core_constants.Real):
        self._beat_count = core_utilities.round_floats(
            float(beat_count),
            core_parameters.configurations.ROUND_DURATION_TO_N_DIGITS,
        )


class RatioDuration(core_parameters.abc.Duration):
    """`Duration` defined by a ratio (= a fraction).

    **Example:**

    >>> from mutwo import core_parameters
    >>> # create duration with duration = 10 beats
    >>> d = core_parameters.RatioDuration('2/3')
    >>> d
    RatioDuration(0.6666666667)
    >>> print(d)
    R(2/3)
    >>> d.ratio
    Fraction(2, 3)
    >>> d.beat_count
    0.6666666667
    """

    def __init__(self, ratio: core_constants.Real | str):
        self.ratio = ratio

    def __str_content__(self) -> str:
        return f"{self.ratio}"

    @property
    def ratio(self) -> fractions.Fraction:
        return self._ratio

    @ratio.setter
    def ratio(self, ratio: core_constants.Real | str):
        self._ratio = fractions.Fraction(ratio)
        try:
            del self._beat_count
        except AttributeError:
            pass

    @property
    def beat_count(self) -> float:
        return self._beat_count

    @beat_count.setter
    def beat_count(self, beat_count: core_constants.Real | str):
        self.ratio = beat_count

    @functools.cached_property
    def _beat_count(self) -> float:
        return core_utilities.round_floats(
            float(self.ratio),
            core_parameters.configurations.ROUND_DURATION_TO_N_DIGITS,
        )
