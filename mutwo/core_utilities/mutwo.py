from __future__ import annotations

import copy
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
        return copy.deepcopy(self)
