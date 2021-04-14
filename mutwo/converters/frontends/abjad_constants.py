"""Constants to be used for and with :mod:`mutwo.converters.frontends.abjad`.
"""

import inspect

from mutwo.converters.frontends import abjad_attachments
from mutwo.parameters import notation_indicators
from mutwo.parameters import playing_indicators
from mutwo.utilities import tools


_abjad_attachment_class_name_to_class = {
    tools.class_name_to_object_name(cls_name): cls
    for cls_name, cls in inspect.getmembers(abjad_attachments, inspect.isclass)
    if not inspect.isabstract(cls)
}
PLAYING_INDICATOR_TO_ABJAD_ATTACHMENT = {
    playing_indicator_name: _abjad_attachment_class_name_to_class[
        playing_indicator_name
    ]
    for playing_indicator_name in playing_indicators.PlayingIndicatorCollection.__dataclass_fields__.keys()  # type: ignore
    if playing_indicator_name in _abjad_attachment_class_name_to_class
}
NOTATION_INDICATOR_TO_ABJAD_ATTACHMENT = {
    notation_indicator_name: _abjad_attachment_class_name_to_class[
        notation_indicator_name
    ]
    for notation_indicator_name in notation_indicators.NotationIndicatorCollection.__dataclass_fields__.keys()  # type: ignore
    if notation_indicator_name in _abjad_attachment_class_name_to_class
}
AVAILABLE_ABJAD_ATTACHMENTS = _abjad_attachment_class_name_to_class.keys()

del _abjad_attachment_class_name_to_class
