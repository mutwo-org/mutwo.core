"""Apply :class:`~mutwo.parameters.abc.PlayingIndicator` on :class:`~mutwo.events.abc.Event`.

"""

import abc
import copy
import itertools
import typing
import warnings

try:
    import quicktions as fractions  # type: ignore
except ImportError:
    import fractions  # type: ignore

from mutwo.core import converters
from mutwo.core import events
from mutwo.core import parameters
from mutwo.core.utilities import constants


__all__ = (
    "PlayingIndicatorConverter",
    "ArpeggioConverter",
    "ArticulationConverter",
    "PlayingIndicatorsConverter",
)


class PlayingIndicatorConverter(converters.abc.Converter):
    """Abstract base class to apply :class:`~mutwo.parameters.abc.PlayingIndicator` on a :class:`~mutwo.events.basic.SimpleEvent`.

    :param simple_event_to_playing_indicator_collection: Function to extract from a
        :class:`mutwo.events.basic.SimpleEvent` a
        :class:`mutwo.parameters.playing_indicators.PlayingIndicatorCollection`
        object. By default it asks the Event for its
        :attr:`~mutwo.events.music.NoteLike.playing_indicator_collection`
        attribute (because by default :class:`mutwo.events.music.NoteLike`
        objects are expected).
        When using different Event classes than :class:`~mutwo.events.music.NoteLike`
        with a different name for their playing_indicator_collection property, this argument
        should be overridden. If the
        function call raises an :obj:`AttributeError` (e.g. if no playing indicator
        collection can be extracted), mutwo will build a playing indicator collection
        from :const:`~mutwo.events.music_constants.DEFAULT_PLAYING_INDICATORS_COLLECTION_CLASS`.
    :type simple_event_to_playing_indicator_collection: typing.Callable[[events.basic.SimpleEvent], parameters.playing_indicators.PlayingIndicatorCollection], optional
    """

    def __init__(
        self,
        simple_event_to_playing_indicator_collection: typing.Callable[
            [events.basic.SimpleEvent],
            parameters.playing_indicators.PlayingIndicatorCollection,
        ] = lambda simple_event: simple_event.playing_indicator_collection,  # type: ignore
    ):
        self._simple_event_to_playing_indicator_collection = (
            simple_event_to_playing_indicator_collection
        )

    @abc.abstractmethod
    def _apply_playing_indicator(
        self,
        simple_event_to_convert: events.basic.SimpleEvent,
        playing_indicator_collection: parameters.playing_indicators.PlayingIndicatorCollection,
    ) -> events.basic.SequentialEvent[events.basic.SimpleEvent]:
        raise NotImplementedError()

    def convert(
        self, simple_event_to_convert: events.basic.SimpleEvent
    ) -> events.basic.SequentialEvent[events.basic.SimpleEvent]:
        """Apply PlayingIndicator on simple_event.

        :param simple_event_to_convert: The event which shall be converted.
        :type simple_event_to_convert: events.basic.SimpleEvent
        """

        simple_event_to_playing_indicator_collection = (
            self._simple_event_to_playing_indicator_collection
        )

        try:
            playing_indicator_collection = simple_event_to_playing_indicator_collection(
                simple_event_to_convert
            )
        except AttributeError:
            playing_indicator_collection = (
                events.music_constants.DEFAULT_PLAYING_INDICATORS_COLLECTION_CLASS()
            )

        return self._apply_playing_indicator(
            simple_event_to_convert, playing_indicator_collection
        )


class ArpeggioConverter(PlayingIndicatorConverter):
    """Apply arpeggio on :class:`~mutwo.events.basic.SimpleEvent`.

    :param duration_for_each_attack: Set how long each attack of the
        Arpeggio lasts. Default to 0.1.
    :type duration_for_each_attack: constants.DurationType
    :param simple_event_to_pitches: Function to extract from a
        :class:`mutwo.events.basic.SimpleEvent` a tuple that contains pitch objects
        (objects that inherit from :class:`mutwo.parameters.abc.Pitch`).
        By default it asks the Event for its
        :attr:`~mutwo.events.music.NoteLike.pitch_list` attribute
        (because by default :class:`mutwo.events.music.NoteLike` objects are expected).
        When using different Event classes than :class:`~mutwo.events.music.NoteLike`
        with a different name for their pitch property, this argument
        should be overridden.
        If the function call raises an :obj:`AttributeError` (e.g. if no pitch can be
        extracted), mutwo will assume an event without any pitches.
    :type simple_event_to_pitches: typing.Callable[[events.basic.SimpleEvent], parameters.abc.Pitch], optional
    :param simple_event_to_playing_indicator_collection: Function to extract from a
        :class:`mutwo.events.basic.SimpleEvent` a
        :class:`mutwo.parameters.playing_indicators.PlayingIndicatorCollection`
        object. By default it asks the Event for its
        :attr:`~mutwo.events.music.NoteLike.playing_indicator_collection`
        attribute (because by default :class:`mutwo.events.music.NoteLike`
        objects are expected).
        When using different Event classes than :class:`~mutwo.events.music.NoteLike`
        with a different name for their playing_indicator_collection property, this argument
        should be overridden. If the
        function call raises an :obj:`AttributeError` (e.g. if no playing indicator
        collection can be extracted), mutwo will build a playing indicator collection
        from :const:`~mutwo.events.music_constants.DEFAULT_PLAYING_INDICATORS_COLLECTION_CLASS`.
    :type simple_event_to_playing_indicator_collection: typing.Callable[[events.basic.SimpleEvent], parameters.playing_indicators.PlayingIndicatorCollection,], optional
    :param set_pitch_list_for_simple_event: Function which assigns
        a list of :class:`~mutwo.parameters.abc.Pitch` objects to a
        :class:`~mutwo.events.basic.SimpleEvent`. By default the
        function assigns the passed pitches to the
        :attr:`~mutwo.events.music.NoteLike.pitch_list` attribute
        (because by default :class:`mutwo.events.music.NoteLike` objects
        are expected).
    :type set_pitch_list_for_simple_event: typing.Callable[[events.basic.SimpleEvent, list[parameters.abc.Pitch]], None]
    """

    def __init__(
        self,
        duration_for_each_attack: constants.DurationType = 0.1,
        simple_event_to_pitches: typing.Callable[
            [events.basic.SimpleEvent], list[parameters.abc.Pitch]
        ] = lambda simple_event: simple_event.pitch_list,  # type: ignore
        simple_event_to_playing_indicator_collection: typing.Callable[
            [events.basic.SimpleEvent],
            parameters.playing_indicators.PlayingIndicatorCollection,
        ] = lambda simple_event: simple_event.playing_indicator_collection,  # type: ignore
        set_pitch_list_for_simple_event: typing.Callable[
            [events.basic.SimpleEvent, list[parameters.abc.Pitch]], None
        ] = lambda simple_event, pitch_list: simple_event.set_parameter(  # type: ignore
            "pitch_list", pitch_list, set_unassigned_parameter=True
        ),
    ):
        super().__init__(
            simple_event_to_playing_indicator_collection=simple_event_to_playing_indicator_collection
        )
        self._duration_for_each_attack = duration_for_each_attack
        self._simple_event_to_pitches = simple_event_to_pitches
        self._set_pitch_list_for_simple_event = set_pitch_list_for_simple_event

    def _apply_arpeggio(
        self,
        simple_event_to_convert: events.basic.SimpleEvent,
        arpeggio: parameters.playing_indicators.Arpeggio,
    ) -> events.basic.SequentialEvent[events.basic.SimpleEvent]:
        try:
            pitch_list = list(self._simple_event_to_pitches(simple_event_to_convert))
        except AttributeError:
            pitch_list = []

        # sort pitches according to Arpeggio direction
        pitch_list.sort(reverse=arpeggio.direction != "up")

        converted_event: events.basic.SequentialEvent[
            events.basic.SimpleEvent
        ] = events.basic.SequentialEvent(
            [copy.copy(simple_event_to_convert) for _ in pitch_list]
        )

        # apply pitches on events
        for nth_event, pitch in enumerate(pitch_list):
            self._set_pitch_list_for_simple_event(converted_event[nth_event], [pitch])

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
        playing_indicator_collection: parameters.playing_indicators.PlayingIndicatorCollection,
    ) -> events.basic.SequentialEvent[events.basic.SimpleEvent]:
        try:
            arpeggio = playing_indicator_collection.arpeggio
        except AttributeError:
            arpeggio = parameters.playing_indicators.Arpeggio()

        if arpeggio.is_active:
            return self._apply_arpeggio(simple_event_to_convert, arpeggio)
        else:
            return events.basic.SequentialEvent([copy.copy(simple_event_to_convert)])


class StacattoConverter(PlayingIndicatorConverter):
    """Apply staccato on :class:`~mutwo.events.basic.SimpleEvent`.

    :param factor:
    :param allowed_articulation_name_sequence:
    :param simple_event_to_playing_indicator_collection: Function to extract from a
        :class:`mutwo.events.basic.SimpleEvent` a
        :class:`mutwo.parameters.playing_indicators.PlayingIndicatorCollection`
        object. By default it asks the Event for its
        :attr:`~mutwo.events.music.NoteLike.playing_indicator_collection`
        attribute (because by default :class:`mutwo.events.music.NoteLike`
        objects are expected).
        When using different Event classes than :class:`~mutwo.events.music.NoteLike`
        with a different name for their playing_indicator_collection property, this argument
        should be overridden. If the
        function call raises an :obj:`AttributeError` (e.g. if no playing indicator
        collection can be extracted), mutwo will build a playing indicator collection
        from :const:`~mutwo.events.music_constants.DEFAULT_PLAYING_INDICATORS_COLLECTION_CLASS`.
    :type simple_event_to_playing_indicator_collection: typing.Callable[[events.basic.SimpleEvent], parameters.playing_indicators.PlayingIndicatorCollection,], optional
    """

    def __init__(
        self,
        factor: float = 0.5,
        allowed_articulation_name_sequence: typing.Sequence[str] = ("staccato", "."),
        simple_event_to_playing_indicator_collection: typing.Callable[
            [events.basic.SimpleEvent],
            parameters.playing_indicators.PlayingIndicatorCollection,
        ] = lambda simple_event: simple_event.playing_indicator_collection,  # type: ignore
    ):
        self._allowed_articulation_name_sequence = allowed_articulation_name_sequence
        self._factor = factor
        super().__init__(simple_event_to_playing_indicator_collection)

    def _apply_stacatto(
        self,
        simple_event_to_convert: events.basic.SimpleEvent,
    ) -> events.basic.SequentialEvent[events.basic.SimpleEvent]:
        duration = simple_event_to_convert.duration * self._factor
        sequential_event = events.basic.SequentialEvent(
            [
                simple_event_to_convert.set_parameter(
                    "duration", duration, mutate=False
                ),
                events.basic.SimpleEvent(duration),
            ]
        )
        return sequential_event

    def _apply_playing_indicator(
        self,
        simple_event_to_convert: events.basic.SimpleEvent,
        playing_indicator_collection: parameters.playing_indicators.PlayingIndicatorCollection,
    ) -> events.basic.SequentialEvent[events.basic.SimpleEvent]:
        try:
            articulation = playing_indicator_collection.articulation
        except AttributeError:
            articulation = parameters.playing_indicators.Articulation()

        if (
            articulation.is_active
            and articulation.name in self._allowed_articulation_name_sequence
        ):
            return self._apply_stacatto(simple_event_to_convert)
        else:
            return events.basic.SequentialEvent([copy.copy(simple_event_to_convert)])


class ArticulationConverter(PlayingIndicatorConverter):
    """Apply articulation on :class:`~mutwo.events.basic.SimpleEvent`.

    :param articulation_name_tuple_to_playing_indicator_converter:
    :type articulation_name_tuple_to_playing_indicator_converter: dict[tuple[str, ...], PlayingIndicatorConverter]
    :param simple_event_to_playing_indicator_collection: Function to extract from a
        :class:`mutwo.events.basic.SimpleEvent` a
        :class:`mutwo.parameters.playing_indicators.PlayingIndicatorCollection`
        object. By default it asks the Event for its
        :attr:`~mutwo.events.music.NoteLike.playing_indicator_collection`
        attribute (because by default :class:`mutwo.events.music.NoteLike`
        objects are expected).
        When using different Event classes than :class:`~mutwo.events.music.NoteLike`
        with a different name for their playing_indicator_collection property, this argument
        should be overridden. If the
        function call raises an :obj:`AttributeError` (e.g. if no playing indicator
        collection can be extracted), mutwo will build a playing indicator collection
        from :const:`~mutwo.events.music_constants.DEFAULT_PLAYING_INDICATORS_COLLECTION_CLASS`.
    :type simple_event_to_playing_indicator_collection: typing.Callable[[events.basic.SimpleEvent], parameters.playing_indicators.PlayingIndicatorCollection,], optional
    """

    def __init__(
        self,
        articulation_name_tuple_to_playing_indicator_converter: dict[
            tuple[str, ...], PlayingIndicatorConverter
        ] = {("staccato", "."): StacattoConverter()},
        simple_event_to_playing_indicator_collection: typing.Callable[
            [events.basic.SimpleEvent],
            parameters.playing_indicators.PlayingIndicatorCollection,
        ] = lambda simple_event: simple_event.playing_indicator_collection,  # type: ignore
    ):
        articulation_name_to_playing_indicator_converter = {}
        for (
            articulation_name_tuple,
            playing_indicator_converter,
        ) in articulation_name_tuple_to_playing_indicator_converter.items():
            for articulation_name in articulation_name_tuple:
                try:
                    assert (
                        articulation_name
                        not in articulation_name_to_playing_indicator_converter
                    )
                except AssertionError:
                    message = "Found two playing indicator converter mappings for "
                    message += f"articulation name '{articulation_name}'! "
                    message += "Mutwo will use the playing indicator converter "
                    message += f"'{playing_indicator_converter}'."
                    warnings.warn(message)
                articulation_name_to_playing_indicator_converter.update(
                    {articulation_name: playing_indicator_converter}
                )

        self._articulation_name_to_playing_indicator_converter = (
            articulation_name_to_playing_indicator_converter
        )
        super().__init__(simple_event_to_playing_indicator_collection)

    def _apply_playing_indicator(
        self,
        simple_event_to_convert: events.basic.SimpleEvent,
        playing_indicator_collection: parameters.playing_indicators.PlayingIndicatorCollection,
    ) -> events.basic.SequentialEvent[events.basic.SimpleEvent]:
        try:
            articulation = playing_indicator_collection.articulation
        except AttributeError:
            articulation = parameters.playing_indicators.Articulation()

        if (
            articulation.is_active
            and articulation.name
            in self._articulation_name_to_playing_indicator_converter
        ):
            return self._articulation_name_to_playing_indicator_converter[
                articulation.name
            ].convert(simple_event_to_convert)
        else:
            return events.basic.SequentialEvent([copy.copy(simple_event_to_convert)])


class TrillConverter(PlayingIndicatorConverter):
    """Apply trill on :class:`~mutwo.events.basic.SimpleEvent`.

    :param trill_size:
    :type trill_size: constants.DurationType
    :param simple_event_to_pitch_list: Function to extract from a
        :class:`mutwo.events.basic.SimpleEvent` a tuple that contains pitch objects
        (objects that inherit from :class:`mutwo.parameters.abc.Pitch`).
        By default it asks the Event for its
        :attr:`~mutwo.events.music.NoteLike.pitch_list` attribute
        (because by default :class:`mutwo.events.music.NoteLike` objects are expected).
        When using different Event classes than :class:`~mutwo.events.music.NoteLike`
        with a different name for their pitch property, this argument
        should be overridden.
        If the function call raises an :obj:`AttributeError` (e.g. if no pitch can be
        extracted), mutwo will assume an event without any pitches.
    :type simple_event_to_pitch_list: typing.Callable[[events.basic.SimpleEvent], parameters.abc.Pitch], optional
    :param simple_event_to_playing_indicator_collection: Function to extract from a
        :class:`mutwo.events.basic.SimpleEvent` a
        :class:`mutwo.parameters.playing_indicators.PlayingIndicatorCollection`
        object. By default it asks the Event for its
        :attr:`~mutwo.events.music.NoteLike.playing_indicator_collection`
        attribute (because by default :class:`mutwo.events.music.NoteLike`
        objects are expected).
        When using different Event classes than :class:`~mutwo.events.music.NoteLike`
        with a different name for their playing_indicator_collection property, this argument
        should be overridden. If the
        function call raises an :obj:`AttributeError` (e.g. if no playing indicator
        collection can be extracted), mutwo will build a playing indicator collection
        from :const:`~mutwo.events.music_constants.DEFAULT_PLAYING_INDICATORS_COLLECTION_CLASS`.
    :type simple_event_to_playing_indicator_collection: typing.Callable[[events.basic.SimpleEvent], parameters.playing_indicators.PlayingIndicatorCollection,], optional
    """

    def __init__(
        self,
        trill_size: constants.DurationType = fractions.Fraction(1, 16),
        simple_event_to_pitch_list: typing.Callable[
            [events.basic.SimpleEvent], list[parameters.abc.Pitch]
        ] = lambda simple_event: simple_event.pitch_list,  # type: ignore
        simple_event_to_playing_indicator_collection: typing.Callable[
            [events.basic.SimpleEvent],
            parameters.playing_indicators.PlayingIndicatorCollection,
        ] = lambda simple_event: simple_event.playing_indicator_collection,  # type: ignore
    ):
        self._trill_size = trill_size
        self._simple_event_to_pitch_list = simple_event_to_pitch_list
        super().__init__(simple_event_to_playing_indicator_collection)

    def _apply_trill(
        self,
        simple_event_to_convert: events.basic.SimpleEvent,
        trill: parameters.playing_indicators.Trill,
        pitch_list: list[parameters.abc.Pitch],
    ) -> events.basic.SequentialEvent[events.basic.SimpleEvent]:
        n_trill_items = simple_event_to_convert.duration // self._trill_size
        remaining = simple_event_to_convert.duration - (
            n_trill_items * self._trill_size
        )
        sequential_event = events.basic.SequentialEvent([])
        pitch_cycle = itertools.cycle((pitch_list, trill.pitch))
        for _ in range(int(n_trill_items)):
            simple_event = simple_event_to_convert.set_parameter(
                "duration", self._trill_size, mutate=False
            ).set_parameter("pitch_list", next(pitch_cycle))
            sequential_event.append(simple_event)
        sequential_event[-1].duration += remaining
        return sequential_event

    def _apply_playing_indicator(
        self,
        simple_event_to_convert: events.basic.SimpleEvent,
        playing_indicator_collection: parameters.playing_indicators.PlayingIndicatorCollection,
    ) -> events.basic.SequentialEvent[events.basic.SimpleEvent]:
        try:
            trill = playing_indicator_collection.trill
        except AttributeError:
            trill = parameters.playing_indicators.Trill()

        simple_event_to_pitch_list = self._simple_event_to_pitch_list
        try:
            pitch_list = simple_event_to_pitch_list(simple_event_to_convert)
        except AttributeError:
            pitch_list = []

        if (
            trill.is_active
            and simple_event_to_convert.duration > self._trill_size * 2
            and pitch_list
        ):
            return self._apply_trill(simple_event_to_convert, trill, pitch_list)
        else:
            return events.basic.SequentialEvent([copy.copy(simple_event_to_convert)])


class PlayingIndicatorsConverter(converters.abc.EventConverter):
    """Apply :class:`~mutwo.parameters.abc.PlayingIndicator` on any :class:`~mutwo.events.abc.Event`.

    :param playing_indicator_converters: A sequence of :class:`PlayingIndicatorConverter` which shall
        be applied on each :class:`~mutwo.events.basic.SimpleEvent`.
    :type playing_indicator_converters: typing.Sequence[PlayingIndicatorConverter]
    """

    def __init__(
        self,
        playing_indicator_converters: typing.Sequence[PlayingIndicatorConverter],
    ):
        self._playing_indicator_converters = playing_indicator_converters

    def _convert_simple_event(
        self,
        event_to_convert: events.basic.SimpleEvent,
        _: constants.DurationType,
    ) -> events.basic.SequentialEvent[events.basic.SimpleEvent]:
        """Convert instance of :class:`mutwo.events.basic.SimpleEvent`."""
        converted_event = [event_to_convert]

        for playing_indicator_converter in self._playing_indicator_converters:
            new_converted_event: list[events.basic.SimpleEvent] = []
            for simple_event in converted_event:
                converted_simple_event = playing_indicator_converter.convert(
                    simple_event
                )
                new_converted_event.extend(converted_simple_event)

            converted_event = new_converted_event

        return events.basic.SequentialEvent(converted_event)

    def convert(self, event_to_convert: events.abc.Event) -> events.abc.Event:
        return self._convert_event(event_to_convert, 0)
