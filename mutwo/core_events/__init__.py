"""Time-based Event abstractions.

Event objects can be understood as the core objects
of the :mod:`mutwo` framework. They all own a :attr:`duration`
attribute (which can be any number). Further more complex
Event classes with more relevant attributes can be generated
through inheriting from basic classes. :mod:`mutwo` already offers
support for several more complex representations (for instance
:class:`mutwo.music_events.NoteLike`).
The most often used classes may be:
    - :class:`mutwo.core_events.SimpleEvent`
    - :class:`mutwo.core_events.SequentialEvent`
    - :class:`mutwo.core_events.SimultaneousEvent`
"""

from . import configurations
from . import abc

from .basic import *
from .tempos import *
from .envelopes import *

from . import basic, envelopes

from mutwo import core_utilities

__all__ = core_utilities.get_all(basic, envelopes)

# Force flat structure
del basic, core_utilities, envelopes
