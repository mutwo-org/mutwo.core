"""Time-based Event abstractions.

Event objects can be understood as the core objects
of the :mod:`mutwo` framework. They all own a :attr:`duration`
attribute (which can be any number). Further more complex
Event classes with more relevant attributes can be generated
through inheriting from basic classes. :mod:`mutwo` already offers
support for several more complex representations (for instance
:class:`mutwo.events.music.NoteLike`).

The most often used classes may be:
    - :class:`mutwo.core.events.basic.SimpleEvent`
    - :class:`mutwo.core.events.basic.SequentialEvent`
    - :class:`mutwo.core.events.basic.SimultaneousEvent`
"""

from . import basic_constants
from . import envelopes_constants

from . import abc
from . import basic
from . import envelopes
