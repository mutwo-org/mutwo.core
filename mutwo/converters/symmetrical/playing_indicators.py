"""Apply :class:`~mutwo.parameters.abc.PlayingIndicator` on :class:`~mutwo.events.abc.Event`.

"""

import abc
import copy
import typing

from mutwo import converters
from mutwo import events
from mutwo import parameters


__all__ = (
    "PlayingIndicatorConverter",
    "ArpeggioConverter",
    "PlayingIndicatorsConverter",
)


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
    def _apply_playing_indicator(
        self,
        simple_event_to_convert: events.basic.SimpleEvent,
        playing_indicators: parameters.playing_indicators.PlayingIndicatorCollection,
    ) -> events.basic.SequentialEvent[events.basic.SimpleEvent]:
        raise NotImplementedError()

    def convert(
        self, simple_event_to_convert: events.basic.SimpleEvent
    ) -> events.basic.SequentialEvent[events.basic.SimpleEvent]:
        """Apply PlayingIndicator on simple_event.

        :param simple_event_to_convert: The event which shall be converted.
        :type simple_event_to_convert: events.basic.SimpleEvent
        """

        try:
            playing_indicators = self._simple_event_to_playing_indicators(
                simple_event_to_convert
            )
        except AttributeError:
            playing_indicators = (
                events.music_constants.DEFAULT_PLAYING_INDICATORS_COLLECTION_CLASS()
            )

        return self._apply_playing_indicator(
            simple_event_to_convert, playing_indicators
        )


class ArpeggioConverter(PlayingIndicatorConverter):
    """Apply arpeggio on :class:`~mutwo.events.basic.SimpleEvent`.

    :param duration_for_each_attack: Set how long each attack of the
        Arpeggio lasts. Default to 0.1.
    :type duration_for_each_attack: parameters.abc.DurationType
    :param simple_event_to_pitches: Function to extract from a
        :class:`mutwo.events.basic.SimpleEvent` a tuple that contains pitch objects
        (objects that inherit from :class:`mutwo.parameters.abc.Pitch`).
        By default it asks the Event for its
        :attr:`~mutwo.events.music.NoteLike.pitch_or_pitches` attribute
        (because by default :class:`mutwo.events.music.NoteLike` objects are expected).
        When using different Event classes than :class:`~mutwo.events.music.NoteLike`
        with a different name for their pitch property, this argument
        should be overridden.
        If the function call raises an :obj:`AttributeError` (e.g. if no pitch can be
        extracted), mutwo will assume an event without any pitches.
    :type simple_event_to_pitches: typing.Callable[[events.basic.SimpleEvent], parameters.abc.Pitch], optional
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
    :type simple_event_to_playing_indicators: typing.Callable[[events.basic.SimpleEvent], parameters.playing_indicators.PlayingIndicatorCollection,], optional
    :param set_pitches_for_simple_event: Function which assigns
        a list of :class:`~mutwo.parameters.abc.Pitch` objects to a
        :class:`~mutwo.events.basic.SimpleEvent`. By default the
        function assigns the passed pitches to the
        :attr:`~mutwo.events.music.NoteLike.pitch_or_pitches` attribute
        (because by default :class:`mutwo.events.music.NoteLike` objects
        are expected).
    :type set_pitches_for_simple_event: typing.Callable[[events.basic.SimpleEvent, typing.List[parameters.abc.Pitch]], None]
    """

    def __init__(
        self,
        duration_for_each_attack: parameters.abc.DurationType = 0.1,
        simple_event_to_pitches: typing.Callable[
            [events.basic.SimpleEvent], typing.List[parameters.abc.Pitch]
        ] = lambda simple_event: simple_event.pitch_or_pitches,  # type: ignore
        simple_event_to_playing_indicators: typing.Callable[
            [events.basic.SimpleEvent],
            parameters.playing_indicators.PlayingIndicatorCollection,
        ] = lambda simple_event: simple_event.playing_indicators,  # type: ignore
        set_pitches_for_simple_event: typing.Callable[
            [events.basic.SimpleEvent, typing.List[parameters.abc.Pitch]], None
        ] = lambda simple_event, pitch_or_pitches: simple_event.set_parameter(  # type: ignore
            "pitch_or_pitches", pitch_or_pitches, set_unassigned_parameter=True
        ),
    ):
        super().__init__(
            simple_event_to_playing_indicators=simple_event_to_playing_indicators
        )
        self._duration_for_each_attack = duration_for_each_attack
        self._simple_event_to_pitches = simple_event_to_pitches
        self._set_pitches_for_simple_event = set_pitches_for_simple_event

    def _apply_arpeggio(
        self,
        simple_event_to_convert: events.basic.SimpleEvent,
        arpeggio: parameters.playing_indicators.Arpeggio,
    ) -> events.basic.SequentialEvent[events.basic.SimpleEvent]:
        try:
            pitch_or_pitches = list(
                self._simple_event_to_pitches(simple_event_to_convert)
            )
        except AttributeError:
            pitch_or_pitches = []

        # sort pitches according to Arpeggio direction
        pitch_or_pitches.sort(reverse=arpeggio.direction != "up")

        converted_event: events.basic.SequentialEvent[
            events.basic.SimpleEvent
        ] = events.basic.SequentialEvent(
            [copy.copy(simple_event_to_convert) for _ in pitch_or_pitches]
        )

        # apply pitches on events
        for nth_event, pitch in enumerate(pitch_or_pitches):
            self._set_pitches_for_simple_event(converted_event[nth_event], [pitch])

        # set correct duration for each event
        n_events = len(converted_event)
        duration_of_each_attack = self._duration_for_each_attack
        if n_events * duration_of_each_attack > simple_event_to_convert.duration:
            duration_of_each_attack = simple_event_to_convert.duration / n_events

        for nth_event in range(n_events - 1):
            converted_event[nth_event].duration = duration_of_each_attack

        converted_event[-1].duration -= (
            converted_event.duration - simple_event_to_convert.duration
        )

        return converted_event

    def _apply_playing_indicator(
        self,
        simple_event_to_convert: events.basic.SimpleEvent,
        playing_indicators: parameters.playing_indicators.PlayingIndicatorCollection,
    ) -> events.basic.SequentialEvent[events.basic.SimpleEvent]:
        try:
            arpeggio = playing_indicators.arpeggio
        except AttributeError:
            arpeggio = parameters.playing_indicators.Arpeggio()

        if arpeggio.is_active:
            return self._apply_arpeggio(simple_event_to_convert, arpeggio)
        else:
            return events.basic.SequentialEvent([copy.copy(simple_event_to_convert)])


class PlayingIndicatorsConverter(converters.abc.SymmetricalEventConverter):
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
            new_converted_event: typing.List[events.basic.SimpleEvent] = []
            for simple_event in converted_event:
                converted_simple_event = playing_indicator_converter.convert(
                    simple_event
                )
                new_converted_event.extend(converted_simple_event)

            converted_event = new_converted_event

        return events.basic.SequentialEvent(converted_event)

    def convert(self, event_to_convert: events.abc.Event) -> events.abc.Event:
        return self._convert_event(event_to_convert, 0)
