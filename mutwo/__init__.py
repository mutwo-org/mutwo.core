"""Mutwo is an event based framework for composing music or other time-based arts.

The structure of the framework is centred around objects with a :attr:`duration`
property which are called **Events** (and which are defined in the :mod:`mutwo.events`
package). These events may have several more attributes besides their duration
attribute (e. g. pitch, volume). Abstractions for such attributes are defined in
:mod:`mutwo.parameters`. The :mod:`mutwo.converters` package aims to translate
mutwo data to third-party software data (or upside down). The :mod:`mutwo.generators`
package supports algorithmic generation of artistic data.
"""

from . import utilities
from . import parameters
from . import converters
from . import events
from . import generators
