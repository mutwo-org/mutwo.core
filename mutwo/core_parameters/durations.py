__all__ = ("DirectDuration",)

try:
    import quicktions as fractions
except ImportError:
    import fractions

from mutwo import core_constants
from mutwo import core_parameters


class DirectDuration(core_parameters.abc.Duration):
    """Simple `Duration` which is directly initialised by its value.

    **Example:**

    >>> from mutwo import core_parameters
    >>> # create duration with duration = 10 beats
    >>> my_duration = core_parameters.DirectDuration(10)
    >>> my_duration.duration
    Fraction(10, 1)
    """

    def __init__(self, duration: float):
        self.duration = duration

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.duration})"

    @property
    def duration(self) -> fractions.Fraction:
        return self._duration

    @duration.setter
    def duration(self, duration: core_constants.Real):
        self._duration = fractions.Fraction(duration)
