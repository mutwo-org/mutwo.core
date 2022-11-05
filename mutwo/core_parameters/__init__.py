"""Abstractions for attributes that can be assigned to Event objects.

"""

from . import constants
from . import configurations
from . import abc

from .durations import *
from .tempos import *

from . import durations, tempos

from mutwo import core_utilities

__all__ = core_utilities.get_all(durations, tempos)


# Force flat structure
del core_utilities, durations, tempos
