"""Mutwo is an event based framework for composing music or other time-based arts.

The structure of the framework is centred around objects with a *duration* property that
are named **Events** (and which are defined in the *events* package). These events may
have several more attributes besides their duration attribute (e. g. pitch, volume).
Abstractions for such attributes are defined in the *parameters* package. The
*converters* package aims to translate mutwo data to third-party software data (or
upside down). The *generators* package supports algorithmic generation of artistic data.
"""

from . import utilities
from . import parameters
from . import converters
from . import events
from . import generators
