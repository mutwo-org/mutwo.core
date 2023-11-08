"""Time-based Event abstractions.

Event objects can be understood as the core objects
of the :mod:`mutwo` framework. They all own a :attr:`~mutwo.core_events.abc.Event.duration`
(of type :class:`~mutwo.core_parameters.abc.Duration`), a :attr:`~mutwo.core_events.abc.Event.tempo_envelope`
(of type :class:`~mutwo.core_events.TempoEnvelope`) and a :attr:`~mutwo.core_events.abc.Event.tag`
(of type ``str`` or ``None``).

The most often used classes are:

    - :class:`mutwo.core_events.SimpleEvent`: the leaf or the node of a tree
    - :class:`mutwo.core_events.SequentialEvent`: a sequence of other events
    - :class:`mutwo.core_events.SimultaneousEvent`: a simultaneous set of other events

Further more complex Event classes with more relevant attributes
can be generated through inheriting from basic classes.
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
