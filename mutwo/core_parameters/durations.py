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
    >>> # create duration with duration = 10 beats
    >>> my_duration = core_parameters.DirectDuration(10)
    >>> my_duration.duration
    10.0
    """

    def __init__(self, duration: core_constants.Real):
        self.duration = duration

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.duration})"

    @property
    def duration(self) -> float:
        return self._duration

    @duration.setter
    def duration(self, duration: core_constants.Real):
        self._duration = core_utilities.round_floats(
            float(duration),
            core_parameters.configurations.ROUND_DURATION_TO_N_DIGITS,
        )


class RatioDuration(core_parameters.abc.Duration):
    """`Duration` defined by a ratio (= a fraction).

    **Example:**

    >>> from mutwo import core_parameters
    >>> # create duration with duration = 10 beats
    >>> d = core_parameters.RatioDuration('2/3')
    >>> d.ratio
    Fraction(2, 3)
    >>> d.duration
    0.6666666667
    """

    def __init__(self, ratio: core_constants.Real | str):
        self.ratio = ratio

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.duration})"

    @property
    def ratio(self) -> fractions.Fraction:
        return self._ratio

    @ratio.setter
    def ratio(self, ratio: core_constants.Real | str):
        self._ratio = fractions.Fraction(ratio)
        try:
            del self._duration
        except AttributeError:
            pass

    @property
    def duration(self) -> float:
        return self._duration

    @duration.setter
    def duration(self, duration: core_constants.Real | str):
        self.ratio = duration

    @functools.cached_property
    def _duration(self) -> float:
        return core_utilities.round_floats(
            float(self.ratio),
            core_parameters.configurations.ROUND_DURATION_TO_N_DIGITS,
        )
