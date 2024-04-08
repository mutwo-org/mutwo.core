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

"""Configurations which are shared for all event classes in :mod:`mutwo.core_events`."""

import functools


# Avoid circular import problem
@functools.cache
def __simpleEvent():
    return __import__("mutwo.core_events").core_events.Chronon


DEFAULT_DURATION_TO_WHITE_SPACE = lambda duration: __simpleEvent()(duration)
"""Default conversion for parameter `duration_to_white_space` in
:func:`mutwo.core_events.abc.Compound.extend_until`. This simply
returns a :class:`mutwo.core_events.Chronon` with the given
duration."""

del functools
