"""Constants to be used for and with :mod:`mutwo.converters.frontends.abjad`.
"""

import inspect

from mutwo.converters.frontends import abjad_attachments
from mutwo.utilities import tools


DEFAULT_ABJAD_ATTACHMENT_NAME_TO_ABJAD_ATTACHMENT = {
    tools.class_name_to_object_name(cls_name): cls
    for cls_name, cls in inspect.getmembers(abjad_attachments, inspect.isclass)
    if not inspect.isabstract(cls)
}
"""Default value for argument `abjad_attachment_name_to_abjad_attachment` in
:class:`~mutwo.converters.frontends.SequentialEventToAbjadVoiceConverter`."""
