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

"""Abstractions for attributes that can be assigned to Event objects.

"""

from . import configurations
from . import abc

from .durations import *
from .tempos import *

from . import durations, tempos

from mutwo import core_utilities

__all__ = core_utilities.get_all(durations, tempos)


# Force flat structure
del core_utilities, durations, tempos

# Force core_parameters patch in core_events
from mutwo import core_events

del core_events
