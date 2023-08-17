"""Classes and functions that generate data with the potential of artistic use.

"""

from .generic import *

from . import generic

__all__ = generic.__all__

# Force flat structure
del generic
