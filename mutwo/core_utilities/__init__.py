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

"""Utility functions."""

from . import configurations

from .decorators import *
from .exceptions import *
from .tools import *
from .tests import *
from .mutwo import *

from . import decorators, exceptions, mutwo, tools

__all__ = tools.get_all(decorators, exceptions, mutwo, tools)

# Force flat structure
del decorators, exceptions, mutwo, tools
