"""Abstractions for attributes that can be assigned to Event objects.

"""

from . import configurations
from . import abc

from .durations import *
from .tempos import *

# Force flat structure
del durations, tempos
