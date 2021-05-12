"""Set default values for :class:`mutwo.events.music.NoteLike`."""

from mutwo import parameters

DEFAULT_PLAYING_INDICATORS_COLLECTION_CLASS = (
    parameters.playing_indicators.PlayingIndicatorCollection
)
"""Default value for :attr:`~mutwo.events.music.NoteLike.playing_indicators`
in :class:`~mutwo.events.music.NoteLike`"""

DEFAULT_NOTATION_INDICATORS_COLLECTION_CLASS = (
    parameters.notation_indicators.NotationIndicatorCollection
)
"""Default value for :attr:`~mutwo.events.music.NoteLike.notation_indicators`
in :class:`~mutwo.events.music.NoteLike`"""
