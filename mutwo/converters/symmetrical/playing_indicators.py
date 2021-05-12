"""Apply :class:`~mutwo.parameters.abc.PlayingIndicator` on :class:`~mutwo.events.abc.Event`.

"""

import abc
import typing

from mutwo import converters
from mutwo import events
from mutwo import parameters


class PlayingIndicatorConverter(converters.abc.Converter):
    """Abstract base class to apply :class:`~mutwo.parameters.abc.PlayingIndicator` on a :class:`~mutwo.events.basic.SimpleEvent`.

    :param simple_event_to_playing_indicators: Function to extract from a
        :class:`mutwo.events.basic.SimpleEvent` a
        :class:`mutwo.parameters.playing_indicators.PlayingIndicatorCollection`
        object. By default it asks the Event for its
        :attr:`~mutwo.events.music.NoteLike.playing_indicators`
        attribute (because by default :class:`mutwo.events.music.NoteLike`
        objects are expected).
        When using different Event classes than :class:`~mutwo.events.music.NoteLike`
        with a different name for their playing_indicators property, this argument
        should be overridden. If the
        function call raises an :obj:`AttributeError` (e.g. if no playing indicator
        collection can be extracted), mutwo will build a playing indicator collection
        from :const:`~mutwo.events.music_constants.DEFAULT_PLAYING_INDICATORS_COLLECTION_CLASS`.
    :type simple_event_to_playing_indicators: typing.Callable[[events.basic.SimpleEvent], parameters.playing_indicators.PlayingIndicatorCollection], optional
    """

    def __init__(
        self,
        simple_event_to_playing_indicators: typing.Callable[
            [events.basic.SimpleEvent],
            parameters.playing_indicators.PlayingIndicatorCollection,
        ] = lambda simple_event: simple_event.playing_indicators,  # type: ignore
    ):
        self._simple_event_to_playing_indicators = simple_event_to_playing_indicators

    @abc.abstractmethod
    def convert(
        self, simple_event_to_convert: events.basic.SimpleEvent
    ) -> events.basic.SequentialEvent[events.basic.SimpleEvent]:
        raise NotImplementedError


class PlayingIndicatorsConverter(converters.abc.EventConverter):
    """Apply :class:`~mutwo.parameters.abc.PlayingIndicator` on any :class:`~mutwo.events.abc.Event`.

    :param playing_indicator_converters: A sequence of :class:`PlayingIndicatorConverter` which shall
        be applied on each :class:`~mutwo.events.basic.SimpleEvent`.
    :type playing_indicator_converters: typing.Sequence[PlayingIndicatorConverter]
    """

    def __init__(
        self, playing_indicator_converters: typing.Sequence[PlayingIndicatorConverter],
    ):
        self._playing_indicator_converters = playing_indicator_converters

    def _convert_simple_event(
        self,
        event_to_convert: events.basic.SimpleEvent,
        absolute_entry_delay: parameters.abc.DurationType,
    ) -> events.basic.SequentialEvent[events.basic.SimpleEvent]:
        """Convert instance of :class:`mutwo.events.basic.SimpleEvent`."""

        converted_event = [event_to_convert]

        for playing_indicator_converter in self._playing_indicator_converters:
            new_converted_event = []
            for simple_event in converted_event:
                converted_simple_event = playing_indicator_converter.convert(
                    simple_event
                )
                new_converted_event.extend(converted_simple_event)

            converted_event = new_converted_event

        return events.basic.SequentialEvent(converted_event)

    def convert(self, event_to_convert: events.abc.Event) -> events.abc.Event:
        return self._convert_event(event_to_convert, 0)
