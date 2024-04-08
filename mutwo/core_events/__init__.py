# This file is part of mutwo, ecosystem for time-based arts.
#
# Copyright (C) 2020-2024
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

"""Time-based Event abstractions.

Event objects can be understood as the core objects
of the :mod:`mutwo` framework. They all own a :attr:`~mutwo.core_events.abc.Event.duration`
(of type :class:`~mutwo.core_parameters.abc.Duration`), a :attr:`~mutwo.core_events.abc.Event.tempo`
(of type :class:`~mutwo.core_parameters.abc.Tempo`) and a :attr:`~mutwo.core_events.abc.Event.tag`
(of type ``str`` or ``None``).

The most often used classes are:

    - :class:`mutwo.core_events.Chronon`: the leaf or the node of a tree
    - :class:`mutwo.core_events.Consecution`: a sequence of other events
    - :class:`mutwo.core_events.Concurrence`: a simultaneous set of other events

Further more complex Event classes with more relevant attributes
can be generated through inheriting from basic classes.
"""

from . import configurations
from . import abc

from .basic import *
from .envelopes import *

from . import basic, envelopes

from mutwo import core_utilities

__all__ = core_utilities.get_all(basic, envelopes)

# BBB: Before mutwo.core < 2.0.0, basic events had different
# names. As this was the most stable, never touched part of mutwo during the
# first four years of development, we keep these backwards compatibility
# pointers for easier migration of code that used mutwo.core < 2.0.0.
TaggedSequentialEvent = SequentialEvent = core_utilities.deprecated(
    "'SequentialEvent' is deprecated, use 'Consecution'."
)(Consecution)
TaggedSimultaneousEvent = SimultaneousEvent = core_utilities.deprecated(
    "'SimultaneousEvent' is deprecated, use 'Concurrence'."
)(Concurrence)
TaggedSimpleEvent = SimpleEvent = core_utilities.deprecated(
    "'SimpleEvent' is deprecated, use 'Chronon'."
)(Chronon)

# Force flat structure
del basic, core_utilities, envelopes

from . import patchparameters

del patchparameters
