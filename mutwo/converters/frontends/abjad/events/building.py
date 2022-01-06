"""Module to build complex multi-level abjad based scores from mutwo events."""

import abc
import inspect
import itertools
import typing

try:
    import quicktions as fractions  # type: ignore
except ImportError:
    import fractions  # type: ignore

import abjad  # type: ignore

from mutwo.converters import abc as converters_abc
from mutwo.converters.frontends.abjad import attachments
from mutwo.converters.frontends.abjad import constants as abjad_constants
from mutwo.converters.frontends.abjad import process_container_routines

from mutwo import events
from mutwo import parameters

from mutwo.utilities import tools

from ..parameters import MutwoPitchToAbjadPitchConverter
from ..parameters import MutwoVolumeToAbjadAttachmentDynamicConverter
from ..parameters import TempoEnvelopeToAbjadAttachmentTempoConverter
from ..parameters import ComplexTempoEnvelopeToAbjadAttachmentTempoConverter

from .quantization import SequentialEventToQuantizedAbjadContainerConverter
from .quantization import NauertSequentialEventToQuantizedAbjadContainerConverter

# from .quantization import RMakersSequentialEventToQuantizedAbjadContainerConverter
from .quantization import (
    NauertSequentialEventToDurationLineBasedQuantizedAbjadContainerConverter,
)
from .quantization import (
    RMakersSequentialEventToDurationLineBasedQuantizedAbjadContainerConverter,
)


__all__ = (
    "ComplexEventToAbjadContainerConverter",
    "SequentialEventToAbjadVoiceConverter",
    "NestedComplexEventToAbjadContainerConverter",
    "NestedComplexEventToComplexEventToAbjadContainerConvertersConverter",
    "CycleBasedNestedComplexEventToComplexEventToAbjadContainerConvertersConverter",
    "TagBasedNestedComplexEventToComplexEventToAbjadContainerConvertersConverter",
)


class ComplexEventToAbjadContainerConverter(converters_abc.Converter):
    def __init__(
        self,
        abjad_container_class: typing.Type[abjad.Container],
        lilypond_type_of_abjad_container: str,
        complex_event_to_abjad_container_name: typing.Callable[
            [events.abc.ComplexEvent], str
        ],
        pre_process_abjad_container_routine_sequence: typing.Sequence[
            process_container_routines.ProcessAbjadContainerRoutine
        ],
        post_process_abjad_container_routine_sequence: typing.Sequence[
            process_container_routines.ProcessAbjadContainerRoutine
        ],
    ):
        self._abjad_container_class = abjad_container_class
        self._lilypond_type_of_abjad_container = lilypond_type_of_abjad_container
        self._complex_event_to_abjad_container_name = (
            complex_event_to_abjad_container_name
        )
        self._pre_process_abjad_container_routine_sequence = (
            pre_process_abjad_container_routine_sequence
        )
        self._post_process_abjad_container_routine_sequence = (
            post_process_abjad_container_routine_sequence
        )

    def _make_empty_abjad_container(
        self, complex_event_to_converter: events.abc.ComplexEvent
    ) -> abjad.Container:
        abjad_container_name = tools.call_function_except_attribute_error(
            self._complex_event_to_abjad_container_name,
            complex_event_to_converter,
            None,
        )

        kwargs = {}

        argument_tuple = tuple(
            inspect.signature(self._abjad_container_class).parameters.keys()
        )

        if "simultaneous" in argument_tuple:
            kwargs.update(
                {
                    "simultaneous": isinstance(
                        complex_event_to_converter, events.basic.SimultaneousEvent
                    )
                }
            )

        if abjad_container_name and "name" in argument_tuple:
            kwargs.update({"name": abjad_container_name})

        if self._lilypond_type_of_abjad_container and "lilypond_type" in argument_tuple:
            kwargs.update({"lilypond_type": self._lilypond_type_of_abjad_container})

        return self._abjad_container_class([], **kwargs)

    def _pre_process_abjad_container(
        self,
        complex_event_to_convert: events.abc.ComplexEvent,
        abjad_container_to_pre_process: abjad.Container,
    ):
        for (
            pre_process_abjad_container_routine
        ) in self._pre_process_abjad_container_routine_sequence:
            pre_process_abjad_container_routine(
                complex_event_to_convert, abjad_container_to_pre_process
            )

    def _post_process_abjad_container(
        self,
        complex_event_to_convert: events.abc.ComplexEvent,
        abjad_container_to_post_process: abjad.Container,
    ):
        for (
            post_process_abjad_container_routine
        ) in self._post_process_abjad_container_routine_sequence:
            post_process_abjad_container_routine(
                complex_event_to_convert, abjad_container_to_post_process
            )

    @abc.abstractmethod
    def _fill_abjad_container(
        self,
        abjad_container_to_fill: abjad.Container,
        complex_event_to_convert: events.abc.ComplexEvent,
    ):
        raise NotImplementedError

    def convert(
        self, complex_event_to_convert: events.abc.ComplexEvent
    ) -> abjad.Container:
        abjad_container = self._make_empty_abjad_container(complex_event_to_convert)
        self._pre_process_abjad_container(complex_event_to_convert, abjad_container)
        self._fill_abjad_container(abjad_container, complex_event_to_convert)
        self._post_process_abjad_container(complex_event_to_convert, abjad_container)
        return abjad_container


class SequentialEventToAbjadVoiceConverter(ComplexEventToAbjadContainerConverter):
    """Convert :class:`~mutwo.events.basic.SequentialEvent` to :class:`abjad.Voice`.

    :param sequential_event_to_quantized_abjad_container_converter: Class which
        defines how the Mutwo data will be quantized. See
        :class:`SequentialEventToQuantizedAbjadContainerConverter` for more information.
    :type sequential_event_to_quantized_abjad_container_converter: SequentialEventToQuantizedAbjadContainerConverter, optional
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
    :param simple_event_to_volume: Function to extract the volume from a
        :class:`mutwo.events.basic.SimpleEvent` in the purpose of generating dynamic
        indicators. The function should return an object that inherits from
        :class:`mutwo.parameters.abc.Volume`. By default it asks the Event for
        its :attr:`~mutwo.events.music.NoteLike.volume` attribute (because by default
        :class:`mutwo.events.music.NoteLike` objects are expected).
        When using different Event classes than :class:`~mutwo.events.music.NoteLike`
        with a different name for their volume property, this argument should
        be overridden.
        If the function call raises an :obj:`AttributeError` (e.g. if no volume can be
        extracted), mutwo will set :attr:`pitch_list` to an empty list and set
        volume to 0.
    :type simple_event_to_volume: typing.Callable[[events.basic.SimpleEvent], parameters.abc.Volume], optional
    :param simple_event_to_grace_note_sequential_event: Function to extract from a
        :class:`mutwo.events.basic.SimpleEvent` a
        :class:`~mutwo.events.basic.SequentialEvent`
        object filled with
        :class:`~mutwo.events.basic.SimpleEvent`.
        By default it asks the Event for its
        :attr:`~mutwo.events.music.NoteLike.grace_note_sequential_event`
        attribute (because by default :class:`mutwo.events.music.NoteLike`
        objects are expected).
        When using different Event classes than :class:`~mutwo.events.music.NoteLike`
        with a different name for their `grace_note_sequential_event` property, this argument
        should be overridden. If the
        function call raises an :obj:`AttributeError` (e.g. if no grace_note_sequential_event can be
        extracted), mutwo will use an empty
        :class:`~mutwo.events.basic.SequentialEvent`.
    :type simple_event_to_grace_note_sequential_event: typing.Callable[[events.basic.SimpleEvent], events.basic.SequentialEvent[events.basic.SimpleEvent]], optional
    :param simple_event_to_after_grace_note_sequential_event: Function to extract from a
        :class:`mutwo.events.basic.SimpleEvent` a
        :class:`~mutwo.events.basic.SequentialEvent`
        object filled with
        :class:`~mutwo.events.basic.SimpleEvent`.
        By default it asks the Event for its
        :attr:`~mutwo.events.music.NoteLike.after_grace_note_sequential_event`
        attribute (because by default :class:`mutwo.events.music.NoteLike`
        objects are expected).
        When using different Event classes than :class:`~mutwo.events.music.NoteLike`
        with a different name for their `after_grace_note_sequential_event` property, this
        argument should be overridden. If the function call
        raises an :obj:`AttributeError` (e.g. if no after_grace_note_sequential_event can be
        extracted), mutwo will use an empty
        :class:`~mutwo.events.basic.SequentialEvent`.
    :type simple_event_to_after_grace_note_sequential_event: typing.Callable[[events.basic.SimpleEvent], events.basic.SequentialEvent[events.basic.SimpleEvent]], optional
    :param simple_event_to_playing_indicator_collection: Function to extract from a
        :class:`mutwo.events.basic.SimpleEvent` a
        :class:`mutwo.parameters.playing_indicators.PlayingIndicatorCollection`
        object. By default it asks the Event for its
        :attr:`~mutwo.events.music.NoteLike.playing_indicator_collection`
        attribute (because by default :class:`mutwo.events.music.NoteLike`
        objects are expected).
        When using different Event classes than :class:`~mutwo.events.music.NoteLike`
        with a different name for their playing_indicators property, this argument
        should be overridden. If the
        function call raises an :obj:`AttributeError` (e.g. if no playing indicator
        collection can be extracted), mutwo will build a playing indicator collection
        from :const:`~mutwo.events.music_constants.DEFAULT_PLAYING_INDICATORS_COLLECTION_CLASS`.
    :type simple_event_to_playing_indicator_collection: typing.Callable[[events.basic.SimpleEvent], parameters.playing_indicators.PlayingIndicatorCollection,], optional
    :param simple_event_to_notation_indicator_collection: Function to extract from a
        :class:`mutwo.events.basic.SimpleEvent` a
        :class:`mutwo.parameters.notation_indicators.NotationIndicatorCollection`
        object. By default it asks the Event for its
        :attr:`~mutwo.events.music.NoteLike.notation_indicators`
        (because by default :class:`mutwo.events.music.NoteLike` objects are expected).
        When using different Event classes than ``NoteLike`` with a different name for
        their playing_indicators property, this argument should be overridden. If the
        function call raises an :obj:`AttributeError` (e.g. if no notation indicator
        collection can be extracted), mutwo will build a notation indicator collection
        from :const:`~mutwo.events.music_constants.DEFAULT_NOTATION_INDICATORS_COLLECTION_CLASS`
    :type simple_event_to_notation_indicator_collection: typing.Callable[[events.basic.SimpleEvent], parameters.notation_indicators.NotationIndicatorCollection,], optional
    :param is_simple_event_rest: Function to detect if the
        the inspected :class:`mutwo.events.basic.SimpleEvent` is a Rest. By
        default Mutwo simply checks if 'pitch_list' contain any objects. If not,
        the Event will be interpreted as a rest.
    :type is_simple_event_rest: typing.Callable[[events.basic.SimpleEvent], bool], optional
    :param mutwo_pitch_to_abjad_pitch_converter: Class which defines how to convert
        :class:`mutwo.parameters.abc.Pitch` objects to :class:`abjad.Pitch` objects.
        See :class:`MutwoPitchToAbjadPitchConverter` for more information.
    :type mutwo_pitch_to_abjad_pitch_converter: MutwoPitchToAbjadPitchConverter, optional
    :param mutwo_volume_to_abjad_attachment_dynamic_converter: Class which defines how
        to convert :class:`mutwo.parameters.abc.Volume` objects to
        :class:`mutwo.converters.frontends.attachments.Dynamic` objects.
        See :class:`MutwoVolumeToAbjadAttachmentDynamicConverter` for more information.
    :type mutwo_volume_to_abjad_attachment_dynamic_converter: MutwoVolumeToAbjadAttachmentDynamicConverter, optional
    :param tempo_envelope_to_abjad_attachment_tempo_converter: Class which defines how
        to convert tempo envelopes to
        :class:`mutwo.converters.frontends.attachments.Tempo` objects.
        See :class:`TempoEnvelopeToAbjadAttachmentTempoConverter` for more information.
    :type tempo_envelope_to_abjad_attachment_tempo_converter: TempoEnvelopeToAbjadAttachmentTempoConverter, optional
    :param abjad_attachment_class_sequence: A tuple which contains all available abjad attachment classes
        which shall be used by the converter.
    :type abjad_attachment_class_sequence: typing.Sequence[attachments.AbjadAttachment], optional
    :param write_multimeasure_rests: Set to ``True`` if the converter should replace
        rests that last a complete bar with multimeasure rests (rests with uppercase
        "R" in Lilypond). Default to ``True``.
    :type write_multimeasure_rests: bool
    """

    ExtractedData = tuple[
        list[parameters.abc.Pitch],
        parameters.abc.Volume,
        events.basic.SequentialEvent[events.basic.SimpleEvent],
        events.basic.SequentialEvent[events.basic.SimpleEvent],
        parameters.playing_indicators.PlayingIndicatorCollection,
        parameters.notation_indicators.NotationIndicatorCollection,
    ]

    ExtractedDataPerSimpleEvent = tuple[ExtractedData, ...]

    _empty_volume = parameters.volumes.DirectVolume(0)
    _empty_grace_note_sequential_event = events.basic.SequentialEvent([])

    def __init__(
        self,
        sequential_event_to_quantized_abjad_container_converter: SequentialEventToQuantizedAbjadContainerConverter = NauertSequentialEventToQuantizedAbjadContainerConverter(),
        simple_event_to_pitch_list: typing.Callable[
            [events.basic.SimpleEvent], list[parameters.abc.Pitch]
        ] = lambda simple_event: simple_event.pitch_list,  # type: ignore
        simple_event_to_volume: typing.Callable[
            [events.basic.SimpleEvent], parameters.abc.Volume
        ] = lambda simple_event: simple_event.volume,  # type: ignore
        simple_event_to_grace_note_sequential_event: typing.Callable[
            [events.basic.SimpleEvent],
            events.basic.SequentialEvent[events.basic.SimpleEvent],
        ] = lambda simple_event: simple_event.grace_note_sequential_event,  # type: ignore
        simple_event_to_after_grace_note_sequential_event: typing.Callable[
            [events.basic.SimpleEvent],
            events.basic.SequentialEvent[events.basic.SimpleEvent],
        ] = lambda simple_event: simple_event.after_grace_note_sequential_event,  # type: ignore
        simple_event_to_playing_indicator_collection: typing.Callable[
            [events.basic.SimpleEvent],
            parameters.playing_indicators.PlayingIndicatorCollection,
        ] = lambda simple_event: simple_event.playing_indicator_collection,  # type: ignore
        simple_event_to_notation_indicator_collection: typing.Callable[
            [events.basic.SimpleEvent],
            parameters.notation_indicators.NotationIndicatorCollection,
        ] = lambda simple_event: simple_event.notation_indicator_collection,  # type: ignore
        is_simple_event_rest: typing.Callable[[events.basic.SimpleEvent], bool] = None,
        mutwo_pitch_to_abjad_pitch_converter: MutwoPitchToAbjadPitchConverter = MutwoPitchToAbjadPitchConverter(),
        mutwo_volume_to_abjad_attachment_dynamic_converter: typing.Optional[
            MutwoVolumeToAbjadAttachmentDynamicConverter
        ] = MutwoVolumeToAbjadAttachmentDynamicConverter(),
        tempo_envelope_to_abjad_attachment_tempo_converter: typing.Optional[
            TempoEnvelopeToAbjadAttachmentTempoConverter
        ] = ComplexTempoEnvelopeToAbjadAttachmentTempoConverter(),
        abjad_attachment_class_sequence: typing.Sequence[
            typing.Type[attachments.AbjadAttachment]
        ] = None,
        write_multimeasure_rests: bool = True,
        abjad_container_class: typing.Type[abjad.Container] = abjad.Voice,
        lilypond_type_of_abjad_container: str = "Voice",
        complex_event_to_abjad_container_name: typing.Callable[
            [events.abc.ComplexEvent], typing.Optional[str]
        ] = lambda _: None,
        pre_process_abjad_container_routine_sequence: typing.Sequence[
            process_container_routines.ProcessAbjadContainerRoutine
        ] = tuple([]),
        post_process_abjad_container_routine_sequence: typing.Sequence[
            process_container_routines.ProcessAbjadContainerRoutine
        ] = tuple([]),
    ):
        # special treatment for duration line based quantizer
        if isinstance(
            sequential_event_to_quantized_abjad_container_converter,
            (
                NauertSequentialEventToDurationLineBasedQuantizedAbjadContainerConverter,
                RMakersSequentialEventToDurationLineBasedQuantizedAbjadContainerConverter,
            ),
        ):
            post_process_abjad_container_routine_sequence += (
                process_container_routines.AddDurationLineEngraver(),
            )

        super().__init__(
            abjad_container_class,
            lilypond_type_of_abjad_container,
            complex_event_to_abjad_container_name,
            pre_process_abjad_container_routine_sequence,
            post_process_abjad_container_routine_sequence,
        )

        if abjad_attachment_class_sequence is None:
            abjad_attachment_class_sequence = (
                abjad_constants.DEFAULT_ABJAD_ATTACHMENT_CLASS_TUPLE
            )
        else:
            abjad_attachment_class_sequence = tuple(abjad_attachment_class_sequence)

        if is_simple_event_rest is None:

            def is_simple_event_rest(simple_event: events.basic.SimpleEvent) -> bool:
                pitch_list = tools.call_function_except_attribute_error(
                    simple_event_to_pitch_list, simple_event, []
                )
                return not bool(pitch_list)

        self._abjad_attachment_class_sequence = abjad_attachment_class_sequence

        self._available_attachment_tuple = tuple(
            abjad_attachment_class.get_class_name()
            for abjad_attachment_class in self._abjad_attachment_class_sequence
        )

        self._sequential_event_to_quantized_abjad_container_converter = (
            sequential_event_to_quantized_abjad_container_converter
        )

        self._simple_event_to_pitch_list = simple_event_to_pitch_list
        self._simple_event_to_volume = simple_event_to_volume
        self._simple_event_to_grace_note_sequential_event = (
            simple_event_to_grace_note_sequential_event
        )
        self._simple_event_to_after_grace_note_sequential_event = (
            simple_event_to_after_grace_note_sequential_event
        )
        self._simple_event_to_playing_indicator_collection = (
            simple_event_to_playing_indicator_collection
        )
        self._simple_event_to_notation_indicator_collection = (
            simple_event_to_notation_indicator_collection
        )
        self._simple_event_to_function_and_exception_value_tuple = (
            (
                self._simple_event_to_pitch_list,
                [],
            ),
            (
                self._simple_event_to_volume,
                self._empty_volume,
            ),
            (
                self._simple_event_to_grace_note_sequential_event,
                self._empty_grace_note_sequential_event,
            ),
            (
                self._simple_event_to_after_grace_note_sequential_event,
                self._empty_grace_note_sequential_event,
            ),
            (
                self._simple_event_to_playing_indicator_collection,
                events.music_constants.DEFAULT_PLAYING_INDICATORS_COLLECTION_CLASS,
            ),
            (
                self._simple_event_to_notation_indicator_collection,
                events.music_constants.DEFAULT_NOTATION_INDICATORS_COLLECTION_CLASS,
            ),
        )

        self._is_simple_event_rest = is_simple_event_rest
        self._mutwo_pitch_to_abjad_pitch_converter = (
            mutwo_pitch_to_abjad_pitch_converter
        )

        self._mutwo_volume_to_abjad_attachment_dynamic_converter = (
            mutwo_volume_to_abjad_attachment_dynamic_converter
        )
        if tempo_envelope_to_abjad_attachment_tempo_converter:
            tempo_attachment_tuple = tempo_envelope_to_abjad_attachment_tempo_converter.convert(
                self._sequential_event_to_quantized_abjad_container_converter.tempo_envelope
            )
        else:
            tempo_attachment_tuple = None
        self._tempo_attachment_tuple = tempo_attachment_tuple

        self._write_multimeasure_rests = write_multimeasure_rests

    # ###################################################################### #
    #                          static methods                                #
    # ###################################################################### #

    @staticmethod
    def _detect_abjad_event_type(pitch_list: list[parameters.abc.Pitch]) -> type:
        n_pitches = len(pitch_list)
        if n_pitches == 0:
            abjad_event_type = abjad.Rest
        elif n_pitches == 1:
            abjad_event_type = abjad.Note
        else:
            abjad_event_type = abjad.Chord
        return abjad_event_type

    @staticmethod
    def _find_absolute_times_of_abjad_leaves(
        abjad_voice: abjad.Voice,
    ) -> tuple[fractions.Fraction, ...]:
        absolute_time_per_leaf_list: list[fractions.Fraction] = []
        for leaf in abjad.select(abjad_voice).leaves():
            start, _ = abjad.get.timespan(leaf).offsets
            absolute_time_per_leaf_list.append(
                fractions.Fraction(start.numerator, start.denominator)
            )
        return tuple(absolute_time_per_leaf_list)

    @staticmethod
    def _replace_rests_with_full_measure_rests(abjad_voice: abjad.Voice) -> None:
        for bar in abjad_voice:
            if all((isinstance(item, abjad.Rest) for item in bar)):
                duration = sum((item.written_duration for item in bar))
                numerator, denominator = duration.numerator, duration.denominator
                abjad.mutate.replace(
                    bar[0],
                    abjad.MultimeasureRest(
                        abjad.Duration(1, denominator), multiplier=numerator
                    ),
                    wrappers=True,
                )
                del bar[1:]

    # ###################################################################### #
    #                          private methods                               #
    # ###################################################################### #

    def _indicator_collection_to_attachments(
        self,
        indicator_collection: parameters.abc.IndicatorCollection,
    ) -> dict[str, attachments.AbjadAttachment]:
        attachment_dict = {}
        for abjad_attachment_class in self._abjad_attachment_class_sequence:
            abjad_attachment = abjad_attachment_class.from_indicator_collection(
                indicator_collection
            )
            if abjad_attachment:
                attachment_dict.update(
                    {abjad_attachment_class.get_class_name(): abjad_attachment}
                )

        return attachment_dict

    def _grace_note_sequential_event_to_abjad_attachment(
        self,
        grace_note_sequential_event_or_after_grace_note_sequential_event: events.basic.SequentialEvent[
            events.basic.SimpleEvent
        ],
        is_before: bool,
    ) -> dict[str, attachments.AbjadAttachment]:
        if not grace_note_sequential_event_or_after_grace_note_sequential_event:
            return {}
        converter = _GraceNotesToAbjadVoiceConverter(
            is_before,
            self._simple_event_to_pitch_list,
            self._simple_event_to_volume,
            self._simple_event_to_playing_indicator_collection,
            self._simple_event_to_notation_indicator_collection,
            self._is_simple_event_rest,
            self._mutwo_pitch_to_abjad_pitch_converter,
        )
        grace_note_sequential_event_container = converter.convert(
            grace_note_sequential_event_or_after_grace_note_sequential_event
        )
        if is_before:
            name = "grace_note_sequential_event"
            abjad_attachment_class = attachments.GraceNoteSequentialEvent
        else:
            name = "after_grace_note_sequential_event"
            abjad_attachment_class = attachments.AfterGraceNoteSequentialEvent
        return {name: abjad_attachment_class(grace_note_sequential_event_container)}

    def _volume_to_abjad_attachment(
        self, volume: parameters.abc.Volume
    ) -> dict[str, attachments.AbjadAttachment]:
        if self._mutwo_volume_to_abjad_attachment_dynamic_converter:
            abjad_attachment_dynamic = (
                self._mutwo_volume_to_abjad_attachment_dynamic_converter.convert(volume)
            )
            if abjad_attachment_dynamic:
                return {"dynamic": abjad_attachment_dynamic}
        return {}

    def _get_tempo_attachment_tuple_for_quantized_abjad_leaves(
        self,
        abjad_voice: abjad.Voice,
    ) -> tuple[
        tuple[
            int,
            typing.Union[attachments.Tempo, attachments.DynamicChangeIndicationStop],
        ],
        ...,
    ]:
        absolute_time_per_leaf = (
            SequentialEventToAbjadVoiceConverter._find_absolute_times_of_abjad_leaves(
                abjad_voice
            )
        )

        assert absolute_time_per_leaf == tuple(sorted(absolute_time_per_leaf))

        leaf_index_to_tempo_attachment_pairs_list: list[
            tuple[
                int,
                typing.Union[
                    attachments.Tempo,
                    attachments.DynamicChangeIndicationStop,
                ],
            ]
        ] = []
        for absolute_time, tempo_attachment in self._tempo_attachment_tuple:
            closest_leaf = tools.find_closest_index(
                absolute_time, absolute_time_per_leaf
            )
            # special case:
            # check for stop dynamic change indication
            # (has to applied to the previous leaf for
            #  better looking results)
            if tempo_attachment.stop_dynamic_change_indicaton:
                leaf_index_to_tempo_attachment_pairs_list.append(
                    (closest_leaf - 1, attachments.DynamicChangeIndicationStop())
                )
            leaf_index_to_tempo_attachment_pairs_list.append(
                (closest_leaf, tempo_attachment)
            )

        return tuple(leaf_index_to_tempo_attachment_pairs_list)

    def _get_attachments_for_quantized_abjad_leaves(
        self,
        extracted_data_per_simple_event: ExtractedDataPerSimpleEvent,
    ) -> tuple[tuple[typing.Optional[attachments.AbjadAttachment], ...], ...]:
        attachments_per_type_per_event: dict[
            str, list[typing.Optional[attachments.AbjadAttachment]]
        ] = {
            attachment_name: [None for _ in extracted_data_per_simple_event]
            for attachment_name in self._available_attachment_tuple
        }
        for nth_event, extracted_data in enumerate(extracted_data_per_simple_event):
            (
                _,
                volume,
                grace_note_sequential_event,
                after_grace_note_sequential_event,
                playing_indicators,
                notation_indicators,
            ) = extracted_data
            attachments_for_nth_event = self._volume_to_abjad_attachment(volume)
            attachments_for_nth_event.update(
                self._grace_note_sequential_event_to_abjad_attachment(
                    grace_note_sequential_event, True
                )
            )
            attachments_for_nth_event.update(
                self._grace_note_sequential_event_to_abjad_attachment(
                    after_grace_note_sequential_event, False
                )
            )
            attachments_for_nth_event.update(
                self._indicator_collection_to_attachments(playing_indicators)
            )
            attachments_for_nth_event.update(
                self._indicator_collection_to_attachments(notation_indicators)
            )
            for attachment_name, attachment in attachments_for_nth_event.items():
                attachments_per_type_per_event[attachment_name][nth_event] = attachment

        return tuple(
            tuple(attachments)
            for attachments in attachments_per_type_per_event.values()
        )

    def _apply_tempos_on_quantized_abjad_leaves(
        self,
        quanitisized_abjad_leaf_voice: abjad.Voice,
    ):
        if self._tempo_attachment_tuple:
            leaves = abjad.select(quanitisized_abjad_leaf_voice).leaves()
            tempo_attachment_data = (
                self._get_tempo_attachment_tuple_for_quantized_abjad_leaves(
                    quanitisized_abjad_leaf_voice
                )
            )
            for nth_event, tempo_attachment in tempo_attachment_data:
                tempo_attachment.process_leaf_tuple((leaves[nth_event],), None)

    def _apply_attachments_on_quantized_abjad_leaves(
        self,
        quanitisized_abjad_leaf_voice: abjad.Voice,
        related_abjad_leaf_index_tuple_tuple_per_simple_event: tuple[tuple[tuple[int, ...], ...], ...],
        attachments_per_type_per_event_tuple: tuple[
            tuple[typing.Optional[attachments.AbjadAttachment], ...], ...
        ],
    ) -> None:
        for attachments_per_type in attachments_per_type_per_event_tuple:
            previous_attachment = None
            for related_abjad_leaf_index_tuple_tuple, attachment in zip(
                related_abjad_leaf_index_tuple_tuple_per_simple_event, attachments_per_type
            ):
                if attachment and attachment.is_active:
                    abjad_leaves = tuple(
                        tools.get_nested_item_from_index_sequence(
                            index_tuple,
                            quanitisized_abjad_leaf_voice,
                        )
                        for index_tuple in related_abjad_leaf_index_tuple_tuple
                    )
                    processed_abjad_leaves = attachment.process_leaf_tuple(
                        abjad_leaves, previous_attachment
                    )
                    for processed_abjad_leaf, index_tuple in zip(
                        processed_abjad_leaves, related_abjad_leaf_index_tuple_tuple
                    ):
                        tools.set_nested_item_from_index_sequence(
                            index_tuple, quanitisized_abjad_leaf_voice, processed_abjad_leaf
                        )

                    previous_attachment = attachment

    def _extract_pitch_list_and_volume_from_simple_event(
        self, simple_event: events.basic.SimpleEvent
    ) -> tuple[list[parameters.abc.Pitch], parameters.abc.Volume]:
        extracted_data = [
            # pitch list
            tools.call_function_except_attribute_error(
                self._simple_event_to_function_and_exception_value_tuple[0][0],
                simple_event,
                self._simple_event_to_function_and_exception_value_tuple[0][1],
            )
        ]

        # TODO(Add option: no dynamic indicator if there aren't any pitches)
        if extracted_data[0]:
            volume = tools.call_function_except_attribute_error(
                self._simple_event_to_function_and_exception_value_tuple[1][0],
                simple_event,
                self._simple_event_to_function_and_exception_value_tuple[1][1],
            )
            if volume == self._empty_volume:
                extracted_data[0] = []
        else:
            volume = self._empty_volume

        extracted_data.append(volume)

        return tuple(extracted_data)

    def _extract_data_from_simple_event(
        self, simple_event: events.basic.SimpleEvent
    ) -> ExtractedData:
        # Special case for pitch_list and volume:
        # if pitch_list is empty, there is also no volume. If volume is empty
        # there is also no pitch_list.
        extracted_data = list(
            self._extract_pitch_list_and_volume_from_simple_event(simple_event)
        )

        for (
            function,
            exception_value,
        ) in self._simple_event_to_function_and_exception_value_tuple[2:]:
            extracted_data.append(
                tools.call_function_except_attribute_error(
                    function,
                    simple_event,
                    exception_value,
                )
            )

        return tuple(extracted_data)

    def _apply_pitch_list_on_quantized_abjad_leaf(
        self,
        quanitisized_abjad_leaf_voice: abjad.Voice,
        abjad_pitch_list: list[abjad.Pitch],
        related_abjad_leaf_index_tuple_tuple: tuple[tuple[int, ...], ...],
    ):
        if len(abjad_pitch_list) == 1:
            leaf_class = abjad.Note
        else:
            leaf_class = abjad.Chord

        for related_abjad_leaf_index_tuple in related_abjad_leaf_index_tuple_tuple:
            abjad_leaf = tools.get_nested_item_from_index_sequence(
                related_abjad_leaf_index_tuple, quanitisized_abjad_leaf_voice
            )
            if leaf_class == abjad.Note:
                # skip don't have note heads
                if hasattr(abjad_leaf, "note_head"):
                    abjad_leaf.note_head._written_pitch = abjad_pitch_list[0]

            else:
                new_abjad_leaf = leaf_class(
                    [abjad.NamedPitch() for _ in abjad_pitch_list],
                    abjad_leaf.written_duration,
                )
                for indicator in abjad.get.indicators(abjad_leaf):
                    if type(indicator) != dict:
                        abjad.attach(indicator, new_abjad_leaf)

                for abjad_pitch, note_head in zip(
                    abjad_pitch_list, new_abjad_leaf.note_heads
                ):
                    note_head._written_pitch = abjad_pitch

                tools.set_nested_item_from_index_sequence(
                    related_abjad_leaf_index_tuple,
                    quanitisized_abjad_leaf_voice,
                    new_abjad_leaf,
                )

    def _apply_pitches_on_quantized_abjad_leaves(
        self,
        quanitisized_abjad_leaf_voice: abjad.Voice,
        related_abjad_leaf_index_tuple_tuple_per_simple_event: tuple[tuple[tuple[int, ...], ...], ...],
        extracted_data_per_simple_event: ExtractedDataPerSimpleEvent,
        is_simple_event_rest_per_simple_event: tuple[bool, ...],
    ):
        for is_simple_event_rest, extracted_data, related_abjad_leaf_index_tuple_tuple in zip(
            is_simple_event_rest_per_simple_event,
            extracted_data_per_simple_event,
            related_abjad_leaf_index_tuple_tuple_per_simple_event,
        ):
            if not is_simple_event_rest:
                pitch_list = extracted_data[0]
                abjad_pitch_list = [
                    self._mutwo_pitch_to_abjad_pitch_converter.convert(pitch)
                    for pitch in pitch_list
                ]
                self._apply_pitch_list_on_quantized_abjad_leaf(
                    quanitisized_abjad_leaf_voice,
                    abjad_pitch_list,
                    related_abjad_leaf_index_tuple_tuple,
                )

    def _quantize_sequential_event(
        self,
        sequential_event_to_convert: events.basic.SequentialEvent[
            events.basic.SimpleEvent
        ],
        is_simple_event_rest_per_simple_event: tuple[bool, ...],
    ) -> tuple[abjad.Container, tuple[tuple[tuple[int, ...], ...], ...],]:
        is_simple_event_rest_per_simple_event_iterator = iter(
            is_simple_event_rest_per_simple_event
        )
        (
            quanitisized_abjad_leaf_voice,
            related_abjad_leaf_index_tuple_tuple_per_simple_event,
        ) = self._sequential_event_to_quantized_abjad_container_converter.convert(
            sequential_event_to_convert.set_parameter(  # type: ignore
                "is_rest",
                lambda _: next(is_simple_event_rest_per_simple_event_iterator),
                set_unassigned_parameter=True,
                mutate=False,
            )
        )
        return quanitisized_abjad_leaf_voice, related_abjad_leaf_index_tuple_tuple_per_simple_event

    def _fill_abjad_container(
        self,
        abjad_container_to_fill: abjad.Voice,
        sequential_event_to_convert: events.basic.SequentialEvent[
            events.basic.SimpleEvent
        ],
    ):
        # tie rests before processing the event!
        sequential_event_to_convert = sequential_event_to_convert.tie_by(
            lambda event0, event1: self._is_simple_event_rest(event0)
            and self._is_simple_event_rest(event1),
            event_type_to_examine=events.basic.SimpleEvent,
            mutate=False,
        )

        # first, extract data from simple events and find rests
        extracted_data_per_simple_event = tuple(
            self._extract_data_from_simple_event(simple_event)
            for simple_event in sequential_event_to_convert
        )
        is_simple_event_rest_per_simple_event = tuple(
            self._is_simple_event_rest(simple_event)
            for simple_event in sequential_event_to_convert
        )

        # second, quantize the sequential event
        (
            quanitisized_abjad_leaf_voice,
            related_abjad_leaf_index_tuple_tuple_per_simple_event,
        ) = self._quantize_sequential_event(
            sequential_event_to_convert, is_simple_event_rest_per_simple_event
        )

        # third, apply pitches on Abjad voice
        self._apply_pitches_on_quantized_abjad_leaves(
            quanitisized_abjad_leaf_voice,
            related_abjad_leaf_index_tuple_tuple_per_simple_event,
            extracted_data_per_simple_event,
            is_simple_event_rest_per_simple_event,
        )

        # fourth, apply dynamics, tempos and playing_indicators on abjad voice
        attachments_per_type_per_event = (
            self._get_attachments_for_quantized_abjad_leaves(
                extracted_data_per_simple_event
            )
        )
        self._apply_tempos_on_quantized_abjad_leaves(quanitisized_abjad_leaf_voice)
        self._apply_attachments_on_quantized_abjad_leaves(
            quanitisized_abjad_leaf_voice,
            related_abjad_leaf_index_tuple_tuple_per_simple_event,
            attachments_per_type_per_event,
        )

        # fifth, replace rests lasting one bar with full measure rests
        if self._write_multimeasure_rests:
            SequentialEventToAbjadVoiceConverter._replace_rests_with_full_measure_rests(
                quanitisized_abjad_leaf_voice
            )

        # move leaves from 'quanitisized_abjad_leaf_voice' object to target container
        abjad.mutate.swap(quanitisized_abjad_leaf_voice, abjad_container_to_fill)

    # ###################################################################### #
    #               public methods for interaction with the user             #
    # ###################################################################### #

    def convert(
        self,
        sequential_event_to_convert: events.basic.SequentialEvent[
            events.basic.SimpleEvent
        ],
    ) -> abjad.Voice:
        """Convert passed :class:`~mutwo.events.basic.SequentialEvent`.

        :param sequential_event_to_convert: The
            :class:`~mutwo.events.basic.SequentialEvent` which shall
            be converted to the :class:`abjad.Voice` object.
        :type sequential_event_to_convert: mutwo.events.basic.SequentialEvent

        **Example:**

        >>> import abjad
        >>> from mutwo.events import basic, music
        >>> from mutwo.converters.frontends import abjad as mutwo_abjad
        >>> mutwo_melody = basic.SequentialEvent(
        >>>     [
        >>>         music.NoteLike(pitch, duration)
        >>>         for pitch, duration in zip("c a g e".split(" "), (1, 1 / 6, 1 / 6, 1 / 6))
        >>>     ]
        >>> )
        >>> converter = mutwo_abjad.SequentialEventToAbjadVoiceConverter()
        >>> abjad_melody = converter.convert(mutwo_melody)
        >>> abjad.lilypond(abjad_melody)
        \\new Voice
        {
            {
                \\tempo 4=120
                %%% \\time 4/4 %%%
                c'1
                \\mf
            }
            {
                \\times 2/3 {
                    a'4
                    g'4
                    e'4
                }
                r2
            }
        }
        """

        return super().convert(sequential_event_to_convert)


class _GraceNotesToAbjadVoiceConverter(SequentialEventToAbjadVoiceConverter):
    class GraceNotesToQuantizedAbjadContainerConverter(converters_abc.Converter):
        def convert(
            self, sequential_event_to_convert: events.basic.SequentialEvent
        ) -> abjad.Container:
            container = abjad.Container([], simultaneous=False)
            indices = []
            for nth_event, event in enumerate(sequential_event_to_convert):
                leaf = abjad.Note("c", event.duration)
                container.append(leaf)
                indices.append(((nth_event,),))
            return container, tuple(indices)

    def __init__(
        self,
        is_before: bool,
        simple_event_to_pitch_list: typing.Callable[
            [events.basic.SimpleEvent], list[parameters.abc.Pitch]
        ],
        simple_event_to_volume: typing.Callable[
            [events.basic.SimpleEvent], parameters.abc.Volume
        ],
        simple_event_to_playing_indicator_collection: typing.Callable[
            [events.basic.SimpleEvent],
            parameters.playing_indicators.PlayingIndicatorCollection,
        ],
        simple_event_to_notation_indicator_collection: typing.Callable[
            [events.basic.SimpleEvent],
            parameters.notation_indicators.NotationIndicatorCollection,
        ],
        is_simple_event_rest: typing.Callable[[events.basic.SimpleEvent], bool],
        mutwo_pitch_to_abjad_pitch_converter: MutwoPitchToAbjadPitchConverter,
    ):
        def raise_attribute_error(_):
            raise AttributeError

        if is_before:
            abjad_container_class = abjad.BeforeGraceContainer
        else:
            abjad_container_class = abjad.AfterGraceContainer

        super().__init__(
            sequential_event_to_quantized_abjad_container_converter=self.GraceNotesToQuantizedAbjadContainerConverter(),
            simple_event_to_pitch_list=simple_event_to_pitch_list,
            simple_event_to_volume=simple_event_to_volume,
            simple_event_to_playing_indicator_collection=simple_event_to_playing_indicator_collection,
            simple_event_to_notation_indicator_collection=simple_event_to_notation_indicator_collection,
            is_simple_event_rest=is_simple_event_rest,
            mutwo_pitch_to_abjad_pitch_converter=mutwo_pitch_to_abjad_pitch_converter,
            mutwo_volume_to_abjad_attachment_dynamic_converter=None,
            tempo_envelope_to_abjad_attachment_tempo_converter=None,
            simple_event_to_grace_note_sequential_event=raise_attribute_error,
            simple_event_to_after_grace_note_sequential_event=raise_attribute_error,
            write_multimeasure_rests=False,
            abjad_container_class=abjad_container_class,
            lilypond_type_of_abjad_container=None,
        )

    def _grace_note_sequential_event_to_abjad_attachment(
        self,
        grace_note_sequential_event_or_after_grace_note_sequential_event: events.basic.SequentialEvent[
            events.basic.SimpleEvent
        ],
        is_before: bool,
    ) -> dict[str, attachments.AbjadAttachment]:
        return {}

    def _get_tempo_attachment_tuple_for_quantized_abjad_leaves(
        self,
        abjad_voice: abjad.Voice,
    ) -> tuple[
        tuple[
            int,
            typing.Union[attachments.Tempo, attachments.DynamicChangeIndicationStop],
        ],
        ...,
    ]:
        return tuple([])


class NestedComplexEventToComplexEventToAbjadContainerConvertersConverter(
    converters_abc.Converter
):
    @abc.abstractmethod
    def convert(
        self, nested_complex_event_to_convert: events.abc.ComplexEvent
    ) -> tuple[ComplexEventToAbjadContainerConverter, ...]:
        raise NotImplementedError


class CycleBasedNestedComplexEventToComplexEventToAbjadContainerConvertersConverter(
    NestedComplexEventToComplexEventToAbjadContainerConvertersConverter
):
    def __init__(
        self,
        complex_event_to_abjad_container_converter_sequence: typing.Sequence[
            ComplexEventToAbjadContainerConverter
        ],
    ):
        self._complex_event_to_abjad_container_converters = (
            complex_event_to_abjad_container_converter_sequence
        )

    def convert(
        self, nested_complex_event_to_convert: events.abc.ComplexEvent
    ) -> tuple[ComplexEventToAbjadContainerConverter, ...]:
        complex_event_to_abjad_container_converters_cycle = itertools.cycle(
            self._complex_event_to_abjad_container_converters
        )
        complex_event_to_abjad_container_converter_list = []
        for _ in nested_complex_event_to_convert:
            complex_event_to_abjad_container_converter_list.append(
                next(complex_event_to_abjad_container_converters_cycle)
            )
        return tuple(complex_event_to_abjad_container_converter_list)


class TagBasedNestedComplexEventToComplexEventToAbjadContainerConvertersConverter(
    NestedComplexEventToComplexEventToAbjadContainerConvertersConverter
):
    def __init__(
        self,
        tag_to_complex_event_to_abjad_container_converter: dict[
            str, ComplexEventToAbjadContainerConverter
        ],
        complex_event_to_tag: typing.Callable[
            [events.abc.ComplexEvent], str
        ] = lambda complex_event: complex_event.tag,
    ):
        self._tag_to_complex_event_to_abjad_container_converter = (
            tag_to_complex_event_to_abjad_container_converter
        )
        self._complex_event_to_tag = complex_event_to_tag

    def convert(
        self, nested_complex_event_to_convert: events.abc.ComplexEvent
    ) -> tuple[ComplexEventToAbjadContainerConverter, ...]:
        complex_event_to_abjad_container_converter_list = []
        for complex_event in nested_complex_event_to_convert:
            tag = self._complex_event_to_tag(complex_event)
            try:
                complex_event_to_abjad_container_converter = (
                    self._tag_to_complex_event_to_abjad_container_converter[tag]
                )
            except KeyError:
                raise KeyError(
                    f"Found undefined tag '{tag}'."
                    " This object only knows the following tags:"
                    f" '{self._tag_to_complex_event_to_abjad_container_converter.keys()}'"
                )

            complex_event_to_abjad_container_converter_list.append(
                complex_event_to_abjad_container_converter
            )
        return tuple(complex_event_to_abjad_container_converter_list)


class NestedComplexEventToAbjadContainerConverter(
    ComplexEventToAbjadContainerConverter
):
    def __init__(
        self,
        nested_complex_event_to_complex_event_to_abjad_container_converters_converter: NestedComplexEventToComplexEventToAbjadContainerConvertersConverter,
        abjad_container_class: typing.Type[abjad.Container],
        lilypond_type_of_abjad_container: str,
        complex_event_to_abjad_container_name: typing.Callable[
            [events.abc.ComplexEvent], str
        ] = lambda complex_event: complex_event.tag,
        pre_process_abjad_container_routine_sequence: typing.Sequence[
            process_container_routines.ProcessAbjadContainerRoutine
        ] = tuple([]),
        post_process_abjad_container_routine_sequence: typing.Sequence[
            process_container_routines.ProcessAbjadContainerRoutine
        ] = tuple([]),
    ):
        super().__init__(
            abjad_container_class,
            lilypond_type_of_abjad_container,
            complex_event_to_abjad_container_name,
            pre_process_abjad_container_routine_sequence,
            post_process_abjad_container_routine_sequence,
        )
        self._nested_complex_event_to_complex_event_to_abjad_container_converters_converter = nested_complex_event_to_complex_event_to_abjad_container_converters_converter

    def _fill_abjad_container(
        self,
        abjad_container_to_fill: abjad.Container,
        nested_complex_event_to_convert: events.abc.ComplexEvent,
    ):
        complex_event_to_abjad_container_converter_tuple = self._nested_complex_event_to_complex_event_to_abjad_container_converters_converter.convert(
            nested_complex_event_to_convert
        )
        for complex_event, complex_event_to_abjad_container_converter in zip(
            nested_complex_event_to_convert, complex_event_to_abjad_container_converter_tuple
        ):
            converted_complex_event = (
                complex_event_to_abjad_container_converter.convert(complex_event)
            )
            abjad_container_to_fill.append(converted_complex_event)
