"""Build Lilypond scores via `Abjad <https://github.com/Abjad/abjad>`_ from Mutwo data.

The following converter classes help to quantize and translate Mutwo data to
Western notation. Due to the complex nature of this task, Mutwo tries to offer as
many optional arguments as possible through which the user can affect the conversion
routines. The most important class and best starting point for organising a conversion
setting is :class:`SequentialEventToAbjadVoiceConverter`.
If one wants to build complete scores from within mutwo, the module offers the
:class:`NestedComplexEventToAbjadContainerConverter`.

**Known bugs and limitations:**

1. Indicators attached to rests which follow another rest won't be translated to
   `abjad`. This behaviour happens because the
   :class:`~mutwo.converters.frontends.SequentialEventToAbjadVoiceConverter`
   ties rests before converting the data to `abjad` objects.

2. Quantization can be slow and not precise. Try both quantization classes.
   Change the parameters. Use different settings and classes for different
   parts of your music.
"""

from . import attachments_constants

from . import attachments
from . import process_container_routines

from . import constants

from .parameters import *
from .events import *

from .parameters import __all__ as _all_parameters
from .events import __all__ as _all_events


__all__ = _all_parameters + _all_events
