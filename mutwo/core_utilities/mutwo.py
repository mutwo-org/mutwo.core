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

from __future__ import annotations

import copy
import pickle
import typing

__all__ = ("MutwoObject",)

T = typing.TypeVar("T")

class MutwoObject(object):
    """Base class for mutwo objects

    This class collects functionality that's useful for any object in the
    mutwo ecosystem.
    """

    def copy(self: T) -> T:
        """Return a deep copy of mutwo object."""
        # NOTE: using pickle speeds up the copy operation by ~200%.
        # Because we often need to copy events in 'mutwo', this is a very
        # useful speedup for the whole ecosystem.
        try:
            return pickle.loads(pickle.dumps(self))
        # Some objects as lambda functions or modules can't be pickled: in
        # case our MutwoObject contains such unpickable objects, fall
        # back to less efficient deepcopy method.
        except (pickle.PicklingError, TypeError):
            return copy.deepcopy(self)
