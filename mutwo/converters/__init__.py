"""Module that contains several subpackages to convert data from and to mutwo.

The subpackages differentiate in the conversion mapping:
    - backends:     external data -> mutwo objects
    - frontends:    mutwo objects -> external data
    - symmetrical:  mutwo objects -> mutwo objects
"""

from . import abc
from . import frontends
from . import backends
from . import symmetrical
