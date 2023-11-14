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

"""Configurations which are shared for all parameter classes in :mod:`mutwo.core_parameters`."""

ROUND_DURATION_TO_N_DIGITS = 10
"""Set floating point precision for the `duration` property of all
:class:`~mutwo.core_parameters.abc.Duration` classes in the :mod:`mutwo.core_parameters`
module.

When returning the `duration` property all mentioned events
should round their actual duration. This behaviour has been added
with version 0.28.1 to avoid floating point rounding errors which
could occur in all duration related methods of the different event
classes (as it can happen in for instance the
:func:`mutwo.core_events.abc.ComplexEvent.squash_in` method or
the :func:`mutwo.core_events.abc.Event.cut_off` method)."""
