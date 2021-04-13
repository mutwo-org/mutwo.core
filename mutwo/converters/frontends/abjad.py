"""Build Lilypond scores via Abjad from Mutwo data.

**Disclaimer**:
    Only basic functionality works for now. This module
    is still in development.
"""

import typing
import warnings

import abjad  # type: ignore
from abjadext import nauert  # type: ignore
import expenvelope  # type: ignore

from mutwo.converters import abc as converters_abc
from mutwo.converters.frontends import abjad_attachments
from mutwo.converters.frontends import abjad_constants
from mutwo import events
from mutwo import parameters

__all__ = (
    "MutwoPitchToAbjadPitchConverter",
    "SequentialEventToQuantizedAbjadContainerConverter",
    "SequentialEventToAbjadVoiceConverter",
)


class MutwoPitchToAbjadPitchConverter(converters_abc.Converter):
    def convert(self, pitch_to_convert: parameters.abc.Pitch) -> abjad.Pitch:
        if isinstance(pitch_to_convert, parameters.pitches.WesternPitch):
            return abjad.NamedPitch(pitch_to_convert.name)
        else:
            return abjad.NumberedPitch.from_hertz(pitch_to_convert.frequency)


class SequentialEventToQuantizedAbjadContainerConverter(converters_abc.Converter):
    def __init__(
        self,
        time_signatures: typing.Optional[typing.Sequence[abjad.TimeSignature]] = None,
        duration_unit: str = "beats",  # for future: typing.Literal["beats", "miliseconds"]
        tempo_envelope: expenvelope.Envelope = None,
        attack_point_optimizer: typing.Optional[
            nauert.AttackPointOptimizer
        ] = nauert.MeasurewiseAttackPointOptimizer(),
    ):
        if duration_unit == "miliseconds":
            message = (
                "The current implementation can't apply tempo changes in the"
                " implementation yet!"
            )
            warnings.warn(message)

        if time_signatures is None:
            time_signatures = (abjad.TimeSignature(4, 4),)
        else:
            time_signatures = tuple(time_signatures)

        self._duration_unit = duration_unit
        self._time_signatures = time_signatures
        self._tempo_envelope = tempo_envelope
        self._attack_point_optimizer = attack_point_optimizer
        self._q_schema = SequentialEventToQuantizedAbjadContainerConverter._make_q_schema(
            self._time_signatures
        )

    # ###################################################################### #
    #                          static methods                                #
    # ###################################################################### #

    @staticmethod
    def _get_respective_q_event_from_abjad_leaf(
        abjad_leaf: typing.Union[abjad.Rest, abjad.Note]
    ) -> typing.Optional[nauert.QEvent]:
        # TODO(improve ugly code)
        try:
            return abjad.get.indicators(abjad_leaf)[0]["q_events"][0]
        except TypeError:
            return None
        except KeyError:
            return None
        except IndexError:
            return None

    @staticmethod
    def _process_abjad_leaf(
        indices: typing.List[int],
        abjad_leaf: abjad.Leaf,
        related_abjad_leaves_per_simple_event: typing.List[
            typing.List[typing.Tuple[int, ...]]
        ],
        q_event_sequence: nauert.QEventSequence,
        has_tie: bool,
        index_of_previous_q_event: int,
    ) -> typing.Tuple[bool, int]:
        q_event = SequentialEventToQuantizedAbjadContainerConverter._get_respective_q_event_from_abjad_leaf(
            abjad_leaf
        )

        if q_event and type(q_event) != nauert.TerminalQEvent:
            nth_q_event = q_event_sequence.sequence.index(q_event)
            related_abjad_leaves_per_simple_event[nth_q_event].append(tuple(indices))
            index_of_previous_q_event = nth_q_event
        elif has_tie:
            related_abjad_leaves_per_simple_event[index_of_previous_q_event].append(
                tuple(indices)
            )
        else:
            related_abjad_leaves_per_simple_event.append([tuple(indices)])

        has_tie = abjad.get.has_indicator(abjad_leaf, abjad.Tie)

        return has_tie, index_of_previous_q_event

    @staticmethod
    def _process_tuplet(
        indices: typing.List[int],
        tuplet: abjad.Tuplet,
        related_abjad_leaves_per_simple_event: typing.List[
            typing.List[typing.Tuple[int, ...]]
        ],
        q_event_sequence: nauert.QEventSequence,
        has_tie: bool,
        index_of_previous_q_event: int,
    ) -> typing.Tuple[bool, int]:
        for (nth_abjad_leaf_or_tuplet, abjad_leaf_or_tuplet,) in enumerate(tuplet):
            (
                has_tie,
                index_of_previous_q_event,
            ) = SequentialEventToQuantizedAbjadContainerConverter._process_abjad_leaf_or_tuplet(
                indices + [nth_abjad_leaf_or_tuplet],
                abjad_leaf_or_tuplet,
                related_abjad_leaves_per_simple_event,
                q_event_sequence,
                has_tie,
                index_of_previous_q_event,
            )

        return has_tie, index_of_previous_q_event

    @staticmethod
    def _process_abjad_leaf_or_tuplet(
        indices: typing.List[int],
        abjad_leaf_or_tuplet: typing.Union[abjad.Tuplet, abjad.Leaf],
        related_abjad_leaves_per_simple_event: typing.List[
            typing.List[typing.Tuple[int, ...]]
        ],
        q_event_sequence: nauert.QEventSequence,
        has_tie: bool,
        index_of_previous_q_event: int,
    ) -> typing.Tuple[bool, int]:
        if isinstance(abjad_leaf_or_tuplet, abjad.Tuplet):
            return SequentialEventToQuantizedAbjadContainerConverter._process_tuplet(
                indices,
                abjad_leaf_or_tuplet,
                related_abjad_leaves_per_simple_event,
                q_event_sequence,
                has_tie,
                index_of_previous_q_event,
            )

        else:
            return SequentialEventToQuantizedAbjadContainerConverter._process_abjad_leaf(
                indices,
                abjad_leaf_or_tuplet,
                related_abjad_leaves_per_simple_event,
                q_event_sequence,
                has_tie,
                index_of_previous_q_event,
            )

    @staticmethod
    def _make_related_abjad_leaves_per_simple_event(
        sequential_event: events.basic.SequentialEvent,
        q_event_sequence: nauert.QEventSequence,
        quanitisized_abjad_leaves: abjad.Voice,
    ) -> typing.Tuple[
        typing.Tuple[typing.Tuple[int, ...], ...], ...,
    ]:
        has_tie = False
        index_of_previous_q_event: int = 0
        related_abjad_leaves_per_simple_event: typing.List[
            typing.List[typing.Tuple[int, ...]]
        ] = [[] for _ in sequential_event]
        for nth_bar, bar in enumerate(quanitisized_abjad_leaves):
            for nth_abjad_leaf_or_tuplet, abjad_leaf_or_tuplet in enumerate(bar):
                (
                    has_tie,
                    index_of_previous_q_event,
                ) = SequentialEventToQuantizedAbjadContainerConverter._process_abjad_leaf_or_tuplet(
                    [nth_bar, nth_abjad_leaf_or_tuplet],
                    abjad_leaf_or_tuplet,
                    related_abjad_leaves_per_simple_event,
                    q_event_sequence,
                    has_tie,
                    index_of_previous_q_event,
                )

        return tuple(
            tuple(tuple(item) for item in pair)
            for pair in related_abjad_leaves_per_simple_event
        )

    @staticmethod
    def _make_q_schema(
        time_signatures: typing.Tuple[abjad.TimeSignature, ...]
    ) -> nauert.QSchema:
        formated_time_signatures = []
        for time_signature in time_signatures:
            formated_time_signatures.append({"time_signature": time_signature})

        return nauert.MeasurewiseQSchema(
            *formated_time_signatures,
            use_full_measure=True,
            tempo=abjad.MetronomeMark((1, 4), 60),
        )

    # ###################################################################### #
    #                         private methods                                #
    # ###################################################################### #

    def _sequential_event_to_q_event_sequence(
        self, sequential_event: events.basic.SequentialEvent
    ) -> nauert.QEventSequence:
        durations = list(sequential_event.get_parameter("duration"))

        for nth_simple_event, simple_event in enumerate(sequential_event):
            if simple_event.is_rest:
                durations[nth_simple_event] = -durations[nth_simple_event]

        if self._duration_unit == "beats":
            return nauert.QEventSequence.from_tempo_scaled_durations(
                durations, tempo=abjad.MetronomeMark((1, 4), 60)
            )

        elif self._duration_unit == "miliseconds":
            return nauert.QEventSequence.from_millisecond_durations(durations)

        else:
            message = (
                "Unknown duration unit '{}'. Use duration unit 'beats' or"
                " 'miliseconds'.".format(self._duration_unit)
            )
            raise NotImplementedError(message)

    def _q_event_sequence_to_quanitisized_abjad_leaves(
        self, q_event_sequence: nauert.QEventSequence
    ) -> abjad.Voice:
        quantizer = nauert.Quantizer()
        return quantizer(
            q_event_sequence,
            q_schema=self._q_schema,
            attach_tempos=True if self._duration_unit == "miliseconds" else False,
            attack_point_optimizer=self._attack_point_optimizer,
        )

    # ###################################################################### #
    #               public methods for interaction with the user             #
    # ###################################################################### #

    def convert(
        self, sequential_event_to_convert: events.basic.SequentialEvent
    ) -> typing.Tuple[
        abjad.Container, typing.Tuple[typing.Tuple[typing.Tuple[int, ...], ...], ...],
    ]:
        q_event_sequence = self._sequential_event_to_q_event_sequence(
            sequential_event_to_convert
        )
        quanitisized_abjad_leaves = self._q_event_sequence_to_quanitisized_abjad_leaves(
            q_event_sequence
        )

        related_abjad_leaves_per_simple_event = SequentialEventToQuantizedAbjadContainerConverter._make_related_abjad_leaves_per_simple_event(
            sequential_event_to_convert, q_event_sequence, quanitisized_abjad_leaves
        )
        return (
            quanitisized_abjad_leaves,
            related_abjad_leaves_per_simple_event,
        )


class SequentialEventToAbjadVoiceConverter(converters_abc.Converter):
    def __init__(
        self,
        sequential_event_to_quantized_abjad_container_converter: SequentialEventToQuantizedAbjadContainerConverter,
        simple_event_to_pitches: typing.Callable[
            [events.basic.SimpleEvent], typing.List[parameters.abc.Pitch]
        ] = lambda simple_event: simple_event.pitch_or_pitches,  # type: ignore
        simple_event_to_volume: typing.Callable[
            [events.basic.SimpleEvent], parameters.abc.Volume
        ] = lambda simple_event: simple_event.volume,  # type: ignore
        simple_event_to_playing_indicators: typing.Callable[
            [events.basic.SimpleEvent],
            parameters.playing_indicators.PlayingIndicatorCollection,
        ] = lambda simple_event: simple_event.playing_indicators,  # type: ignore
        simple_event_to_notation_indicators: typing.Callable[
            [events.basic.SimpleEvent],
            parameters.notation_indicators.NotationIndicatorCollection,
        ] = lambda simple_event: simple_event.notation_indicators,  # type: ignore
        does_extracted_data_indicate_rest: typing.Callable[
            [
                typing.List[parameters.abc.Pitch],
                parameters.abc.Volume,
                parameters.playing_indicators.PlayingIndicatorCollection,
                parameters.notation_indicators.NotationIndicatorCollection,
            ],
            bool,
        ] = lambda pitches, volume, playing_indicators, notation_indicators: len(
            pitches
        )
        == 0,
        mutwo_pitch_to_abjad_pitch_converter: MutwoPitchToAbjadPitchConverter = MutwoPitchToAbjadPitchConverter(),
    ):
        self._sequential_event_to_quantized_abjad_container_converter = (
            sequential_event_to_quantized_abjad_container_converter
        )
        self._simple_event_to_pitches = simple_event_to_pitches
        self._simple_event_to_volume = simple_event_to_volume
        self._simple_event_to_playing_indicators = simple_event_to_playing_indicators
        self._simple_event_to_notation_indicators = simple_event_to_notation_indicators
        self._does_extracted_data_indicate_rest = does_extracted_data_indicate_rest
        self._mutwo_pitch_to_abjad_pitch_converter = (
            mutwo_pitch_to_abjad_pitch_converter
        )

    # ###################################################################### #
    #                          static methods                                #
    # ###################################################################### #

    @staticmethod
    def _detect_abjad_event_type(pitches: typing.List[parameters.abc.Pitch]) -> type:
        n_pitches = len(pitches)
        if n_pitches == 0:
            abjad_event_type = abjad.Rest
        elif n_pitches == 1:
            abjad_event_type = abjad.Note
        else:
            abjad_event_type = abjad.Chord
        return abjad_event_type

    @staticmethod
    def _get_item_from_indices(
        sequence: typing.Sequence, indices: typing.Tuple[int, ...]
    ) -> typing.Any:
        for index in indices:
            sequence = sequence[index]
        return sequence

    @staticmethod
    def _set_item_from_indices(
        sequence: typing.MutableSequence,
        indices: typing.Tuple[int, ...],
        item: typing.Any,
    ) -> None:
        n_indices = len(indices)
        for nth_index, index in enumerate(indices):
            if n_indices == nth_index + 1:
                sequence.__setitem__(index, item)
            else:
                sequence = sequence[index]

    @staticmethod
    def _indicator_collection_to_abjad_attachments(
        indicator_collection: parameters.abc.IndicatorCollection,
        indicator_name_to_abjad_attachment_mapping: typing.Dict[
            str, abjad_attachments.AbjadAttachment
        ],
    ) -> typing.Dict[str, abjad_attachments.AbjadAttachment]:
        attachments = {}
        for (
            indicator_name,
            indicator,
        ) in indicator_collection.get_indicator_dict().items():
            if indicator_name in indicator_name_to_abjad_attachment_mapping:
                new_attachment = indicator_name_to_abjad_attachment_mapping[
                    indicator_name
                ](**indicator.get_arguments_dict())
                attachments.update({indicator_name: new_attachment})

        return attachments

    @staticmethod
    def _playing_indicator_collection_to_abjad_attachments(
        playing_indicators: parameters.playing_indicators.PlayingIndicatorCollection,
    ) -> typing.Dict[str, abjad_attachments.AbjadAttachment]:
        return SequentialEventToAbjadVoiceConverter._indicator_collection_to_abjad_attachments(
            playing_indicators, abjad_constants.PLAYING_INDICATOR_TO_ABJAD_ATTACHMENT
        )

    @staticmethod
    def _notation_indicator_collection_to_abjad_attachments(
        notation_indicators: parameters.notation_indicators.NotationIndicatorCollection,
    ) -> typing.Dict[str, abjad_attachments.AbjadAttachment]:
        return SequentialEventToAbjadVoiceConverter._indicator_collection_to_abjad_attachments(
            notation_indicators, abjad_constants.NOTATION_INDICATOR_TO_ABJAD_ATTACHMENT
        )

    # ###################################################################### #
    #                          private methods                               #
    # ###################################################################### #

    def _get_attachments_for_quantized_abjad_leaves(
        self,
        extracted_data_per_simple_event: typing.Tuple[
            typing.Tuple[
                typing.List[parameters.abc.Pitch],
                parameters.abc.Volume,
                parameters.playing_indicators.PlayingIndicatorCollection,
                parameters.notation_indicators.NotationIndicatorCollection,
            ],
            ...,
        ],
    ) -> typing.Tuple[typing.Tuple[abjad_attachments.AbjadAttachment, ...], ...]:
        attachments_per_type_per_event = {
            attachment_name: [None for _ in extracted_data_per_simple_event]
            for attachment_name in abjad_constants.AVAILABLE_ABJAD_ATTACHMENTS
        }
        for nth_event, extracted_data in enumerate(extracted_data_per_simple_event):
            _, volume, playing_indicators, notation_indicators = extracted_data
            attachments = {}
            attachments.update(
                SequentialEventToAbjadVoiceConverter._playing_indicator_collection_to_abjad_attachments(
                    playing_indicators
                )
            )
            attachments.update(
                SequentialEventToAbjadVoiceConverter._notation_indicator_collection_to_abjad_attachments(
                    notation_indicators
                )
            )
            for attachment_name, attachment in attachments.items():
                attachments_per_type_per_event[attachment_name][nth_event] = attachment

        return tuple(
            attachments for attachments in attachments_per_type_per_event.values()
        )

    def _apply_attachments_on_quantized_abjad_leaves(
        self,
        quanitisized_abjad_leaves: abjad.Voice,
        related_abjad_leaves_per_simple_event: typing.Tuple[
            typing.Tuple[typing.Tuple[int, ...], ...], ...
        ],
        attachments_per_type_per_event: typing.Tuple[
            typing.Tuple[abjad_attachments.AbjadAttachment, ...], ...
        ],
    ) -> None:
        for attachments in attachments_per_type_per_event:
            previous_attachment = None
            for related_abjad_leaves_indices, attachment in zip(
                related_abjad_leaves_per_simple_event, attachments
            ):
                if attachment and attachment.is_active:
                    abjad_leaves = tuple(
                        SequentialEventToAbjadVoiceConverter._get_item_from_indices(
                            quanitisized_abjad_leaves, indices
                        )
                        for indices in related_abjad_leaves_indices
                    )
                    processed_abjad_leaves = attachment.process_leaves(
                        abjad_leaves, previous_attachment
                    )
                    for processed_abjad_leaf, indices in zip(
                        processed_abjad_leaves, related_abjad_leaves_indices
                    ):
                        SequentialEventToAbjadVoiceConverter._set_item_from_indices(
                            quanitisized_abjad_leaves, indices, processed_abjad_leaf
                        )

                    previous_attachment = attachment

    def _extract_data_from_simple_event(
        self, simple_event: events.basic.SimpleEvent
    ) -> typing.Tuple[
        typing.List[parameters.abc.Pitch],
        parameters.abc.Volume,
        parameters.playing_indicators.PlayingIndicatorCollection,
        parameters.notation_indicators.NotationIndicatorCollection,
    ]:
        try:
            pitches = self._simple_event_to_pitches(simple_event)
        except AttributeError:
            pitches = []

        try:
            volume = self._simple_event_to_volume(simple_event)
        except AttributeError:
            volume = parameters.volumes.DirectVolume(0)
            pitches = []

        try:
            playing_indicators = self._simple_event_to_playing_indicators(simple_event)
        except AttributeError:
            playing_indicators = (
                parameters.playing_indicators.PlayingIndicatorCollection()
            )

        try:
            notation_indicators = self._simple_event_to_notation_indicators(
                simple_event
            )
        except AttributeError:
            notation_indicators = (
                parameters.notation_indicators.NotationIndicatorCollection()
            )

        return pitches, volume, playing_indicators, notation_indicators

    def _apply_pitches_on_quantized_abjad_leaf(
        self,
        quanitisized_abjad_leaves: abjad.Voice,
        abjad_pitches: typing.List[abjad.Pitch],
        related_abjad_leaves_indices: typing.Tuple[typing.Tuple[int, ...], ...],
    ):
        if len(abjad_pitches) == 1:
            leaf_class = abjad.Note
        else:
            leaf_class = abjad.Chord

        for related_abjad_leaf_indices in related_abjad_leaves_indices:
            abjad_leaf = SequentialEventToAbjadVoiceConverter._get_item_from_indices(
                quanitisized_abjad_leaves, related_abjad_leaf_indices
            )
            if leaf_class == abjad.Note:
                abjad_leaf.note_head._written_pitch = abjad_pitches[0]

            else:
                new_abjad_leaf = leaf_class(
                    [abjad.NamedPitch() for _ in abjad_pitches],
                    abjad_leaf.written_duration,
                )
                for indicator in abjad.get.indicators(abjad_leaf):
                    if type(indicator) != dict:
                        abjad.attach(indicator, new_abjad_leaf)

                for abjad_pitch, note_head in zip(
                    abjad_pitches, new_abjad_leaf.note_heads
                ):
                    note_head._written_pitch = abjad_pitch

                SequentialEventToAbjadVoiceConverter._set_item_from_indices(
                    quanitisized_abjad_leaves,
                    related_abjad_leaf_indices,
                    new_abjad_leaf,
                )

    def _apply_pitches_on_quantized_abjad_leaves(
        self,
        quanitisized_abjad_leaves: abjad.Voice,
        related_abjad_leaves_per_simple_event: typing.Tuple[
            typing.Tuple[typing.Tuple[int, ...], ...], ...
        ],
        extracted_data_per_simple_event: typing.Tuple[
            typing.Tuple[
                typing.List[parameters.abc.Pitch],
                parameters.abc.Volume,
                parameters.playing_indicators.PlayingIndicatorCollection,
                parameters.notation_indicators.NotationIndicatorCollection,
            ],
            ...,
        ],
        is_simple_event_rest_per_simple_event: typing.Tuple[bool, ...],
    ):
        for is_simple_event_rest, extracted_data, related_abjad_leaves_indices in zip(
            is_simple_event_rest_per_simple_event,
            extracted_data_per_simple_event,
            related_abjad_leaves_per_simple_event,
        ):
            if not is_simple_event_rest:
                pitches = extracted_data[0]
                abjad_pitches = [
                    self._mutwo_pitch_to_abjad_pitch_converter.convert(pitch)
                    for pitch in pitches
                ]
                self._apply_pitches_on_quantized_abjad_leaf(
                    quanitisized_abjad_leaves,
                    abjad_pitches,
                    related_abjad_leaves_indices,
                )

    def _quantize_sequential_event(
        self,
        sequential_event_to_convert: events.basic.SequentialEvent[
            events.basic.SimpleEvent
        ],
        is_simple_event_rest_per_simple_event: typing.Tuple[bool, ...],
    ) -> typing.Tuple[
        abjad.Container, typing.Tuple[typing.Tuple[typing.Tuple[int, ...], ...], ...],
    ]:
        is_simple_event_rest_per_simple_event_iterator = iter(
            is_simple_event_rest_per_simple_event
        )
        (
            quanitisized_abjad_leaves,
            related_abjad_leaves_per_simple_event,
        ) = self._sequential_event_to_quantized_abjad_container_converter.convert(
            sequential_event_to_convert.set_parameter(  # type: ignore
                "is_rest",
                lambda _: next(is_simple_event_rest_per_simple_event_iterator),
                set_unassigned_parameter=True,
                mutate=False,
            )
        )
        return quanitisized_abjad_leaves, related_abjad_leaves_per_simple_event

    # ###################################################################### #
    #               public methods for interaction with the user             #
    # ###################################################################### #

    def convert(
        self,
        sequential_event_to_convert: events.basic.SequentialEvent[
            events.basic.SimpleEvent
        ],
    ) -> abjad.Voice:
        # first, extract data from simple events
        extracted_data_per_simple_event = tuple(
            self._extract_data_from_simple_event(simple_event)
            for simple_event in sequential_event_to_convert
        )
        is_simple_event_rest_per_simple_event = tuple(
            self._does_extracted_data_indicate_rest(*extracted_data)
            for extracted_data in extracted_data_per_simple_event
        )

        # second, quantize the sequential event
        (
            quanitisized_abjad_leaves,
            related_abjad_leaves_per_simple_event,
        ) = self._quantize_sequential_event(
            sequential_event_to_convert, is_simple_event_rest_per_simple_event
        )

        # third, apply pitches on abjad voice
        self._apply_pitches_on_quantized_abjad_leaves(
            quanitisized_abjad_leaves,
            related_abjad_leaves_per_simple_event,
            extracted_data_per_simple_event,
            is_simple_event_rest_per_simple_event,
        )

        # fourth, apply dynamics, tempos and playing_indicators on abjad voice
        # TODO(implement dynamic attachment, tempo attachment, pitch indicator
        # attachment)
        attachments_per_type_per_event = self._get_attachments_for_quantized_abjad_leaves(
            extracted_data_per_simple_event
        )
        self._apply_attachments_on_quantized_abjad_leaves(
            quanitisized_abjad_leaves,
            related_abjad_leaves_per_simple_event,
            attachments_per_type_per_event,
        )

        return quanitisized_abjad_leaves
