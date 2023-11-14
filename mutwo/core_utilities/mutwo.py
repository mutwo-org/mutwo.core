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
