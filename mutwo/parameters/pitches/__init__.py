"""Submodule for the parameter pitch.

'Pitch' is defined as any object that knows a 'frequency' attribute.
The two major modern tuning systems Just intonation and Equal-divided-octave
are supported by the JustIntonationPitch and EqualDividedOctavePitch classes.
For using Western nomenclature (e.g. c, d, e, f, ...) mutwo offers the
WesternPitch class (which inherits from EqualDividedOctavePitch).
For a straight frequency-based approach one may use the DirectPitch class.

If desired the default concert pitch can be adjusted after importing mutwo:

    >>> from mutwo.parameters import pitches
    >>> pitches.constants.DEFAULT_CONCERT_PITCH = 443

All pitch objects with a concert pitch attribute that become initialised after
overriding the default concert pitch value will by default use the new
overriden default concert pitch value.
"""

from . import constants
from . import abc
from .DirectPitch import DirectPitch
from .EqualDividedOctavePitch import EqualDividedOctavePitch
from .WesternPitch import WesternPitch
from .JustIntonationPitch import JustIntonationPitch
