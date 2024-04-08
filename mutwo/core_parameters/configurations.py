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

"""Configurations which are shared for all parameter classes in :mod:`mutwo.core_parameters`."""

try:
    import quicktions as fractions
except ImportError:
    import fractions

ROUND_DURATION_TO_N_DIGITS = 10
"""Set floating point precision for the `duration` property of all
:class:`~mutwo.core_parameters.abc.Duration` classes in the :mod:`mutwo.core_parameters`
module.

When returning the `duration` property all mentioned events
should round their actual duration. This behaviour has been added
with version 0.28.1 to avoid floating point rounding errors which
could occur in all duration related methods of the different event
classes (as it can happen in for instance the
:func:`mutwo.core_events.abc.Compound.squash_in` method or
the :func:`mutwo.core_events.abc.Event.cut_off` method)."""

DEFAULT_REFERENCE: fractions.Fraction = fractions.Fraction(1, 4)
"""The default value for the 'reference' parameter of
:class:`mutwo.core_parameters.WesternTempo`. By default
it is set to 1/4 because it's most common to think that
the tempo in BPM refers to a 1/4 note (so that tempo = 60 BPM
means that a 1/4 beat takes one second). Therefore a tempo
of '60' in :class:`~mutwo.core_parameters.WesternTempo` is
by default 4 times slower than a tempo of '60' in
:class:`~mutwo.core_parameters.DirectTempo`."""
