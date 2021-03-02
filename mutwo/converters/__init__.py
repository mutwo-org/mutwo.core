"""Several subpackages to convert data from and to mutwo.

The subpackages differentiate in their conversion mapping:
    - backends:     external data                   **->** mutwo or generic Python objects
    - frontends:    mutwo or generic Python objects **->** external data
    - symmetrical:  mutwo or generic Python objects **->** mutwo or generic Python objects

*External data* can be a file, a Python object from a third-party library or a Stream
object (that can be started to play for triggering events in real-time).
"""

from . import abc
from . import frontends
from . import backends
from . import symmetrical
