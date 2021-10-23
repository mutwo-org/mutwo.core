"""Module to quantize free :class:`SequentialEvent` to notation based abjad :class:`Container`"""

import abc
import typing
import warnings

try:
    import quicktions as fractions  # type: ignore
except ImportError:
    import fractions  # type: ignore

import abjad  # type: ignore
from abjadext import nauert  # type: ignore
from abjadext import rmakers  # type: ignore
import expenvelope  # type: ignore
import ranges  # type: ignore

from mutwo.converters import abc as converters_abc

from mutwo import events
from mutwo import parameters

from mutwo.utilities import tools

__all__ = (
    "SequentialEventToQuantizedAbjadContainerConverter",
    "ComplexSequentialEventToQuantizedAbjadContainerConverter",
    "ComplexSequentialEventToDurationLineBasedQuantizedAbjadContainerConverter",
    "FastSequentialEventToQuantizedAbjadContainerConverter",
    "FastSequentialEventToDurationLineBasedQuantizedAbjadContainerConverter",
)


class SequentialEventToQuantizedAbjadContainerConverter(converters_abc.Converter):
    """Quantize :class:`~mutwo.events.basic.SequentialEvent` objects.

    :param time_signatures: Set time signatures to divide the quantized abjad data
        in desired bar sizes. If the converted :class:`~mutwo.events.basic.SequentialEvent`
        is longer than the sum of all passed time signatures, the last time signature
        will be repeated for the remaining bars.
    :param tempo_envelope: Defines the tempo of the converted music. This is an
        :class:`expenvelope.Envelope` object which durations are beats and which
        levels are either numbers (that will be interpreted as beats per minute ('BPM'))
        or :class:`~mutwo.parameters.tempos.TempoPoint` objects. If no tempo envelope has
        been defined, Mutwo will assume a constant tempo of 1/4 = 120 BPM.
    """

    def __init__(
        self,
        time_signatures: typing.Sequence[abjad.TimeSignature] = (
            abjad.TimeSignature((4, 4)),
        ),
        tempo_envelope: expenvelope.Envelope = None,
    ):
        n_time_signatures = len(time_signatures)
        if n_time_signatures == 0:
            message = (
                "Found empty sequence for argument 'time_signatures'. Specify at least"
                " one time signature!"
            )
            raise ValueError(message)

        time_signatures = tuple(time_signatures)
        if tempo_envelope is None:
            tempo_envelope = expenvelope.Envelope.from_points(
                (0, parameters.tempos.TempoPoint(120)),
                (0, parameters.tempos.TempoPoint(120)),
            )

        self._time_signatures = time_signatures
        self._tempo_envelope = tempo_envelope

    @property
    def tempo_envelope(self) -> expenvelope.Envelope:
        return self._tempo_envelope

    # ###################################################################### #
    #               public methods for interaction with the user             #
    # ###################################################################### #

    @abc.abstractmethod
    def convert(
        self, sequential_event_to_convert: events.basic.SequentialEvent
    ) -> typing.Tuple[
        abjad.Container,
        typing.Tuple[typing.Tuple[typing.Tuple[int, ...], ...], ...],
    ]:
        raise NotImplementedError


class ComplexSequentialEventToQuantizedAbjadContainerConverter(
    SequentialEventToQuantizedAbjadContainerConverter
):
    """Quantize :class:`~mutwo.events.basic.SequentialEvent` objects via :mod:`abjadext.nauert`.

    :param time_signatures: Set time signatures to divide the quantized abjad data
        in desired bar sizes. If the converted :class:`~mutwo.events.basic.SequentialEvent`
        is longer than the sum of all passed time signatures, the last time signature
        will be repeated for the remaining bars.
    :param duration_unit: This defines the `duration_unit` of the passed
        :class:`~mutwo.events.basic.SequentialEvent` (how the
        :attr:`~mutwo.events.abc.Event.duration` attribute will be
        interpreted). Can either be 'beats' (default) or 'miliseconds'.
        WARNING: 'miliseconds' isn't working properly yet!
    :param tempo_envelope: Defines the tempo of the converted music. This is an
        :class:`expenvelope.Envelope` object which durations are beats and which
        levels are either numbers (that will be interpreted as beats per minute ('BPM'))
        or :class:`~mutwo.parameters.tempos.TempoPoint` objects. If no tempo envelope has
        been defined, Mutwo will assume a constant tempo of 1/4 = 120 BPM.
    :param attack_point_optimizer: Optionally the user can pass a
        :class:`nauert.AttackPointOptimizer` object. Attack point optimizer help to
        split events and tie them for better looking notation. The default attack point
        optimizer is :class:`nauert.MeasurewiseAttackPointOptimizer` which splits events
        to better represent metrical structures within bars. If no optimizer is desired
        this argument can be set to ``None``.

    Unlike :class:`FastSequentialEventToQuantizedAbjadContainerConverter` this converter
    supports nested tuplets and ties across tuplets. But this converter is much slower
    than the :class:`FastSequentialEventToQuantizedAbjadContainerConverter`. Because the
    converter depends on the abjad extension `nauert` its quality is dependent on the
    inner mechanism of the used package. Because the quantization made by the `nauert`
    package can be somewhat indeterministic a lot of tweaking may be necessary for
    complex musical structures.
    """

    # TODO(add proper miliseconds conversion: you will have to add the tempo_envelope
    # when building the QEventSequence. Furthermore you should auto write down the
    # metronome marks when initialising from miliseconds?)

    def __init__(
        self,
        time_signatures: typing.Sequence[abjad.TimeSignature] = (
            abjad.TimeSignature((4, 4)),
        ),
        duration_unit: str = "beats",  # for future: typing.Literal["beats", "miliseconds"]
        tempo_envelope: expenvelope.Envelope = None,
        attack_point_optimizer: typing.Optional[
            nauert.AttackPointOptimizer
        ] = nauert.MeasurewiseAttackPointOptimizer(),
        search_tree: typing.Optional[nauert.SearchTree] = None,
    ):
        if duration_unit == "miliseconds":
            # warning for not well implemented miliseconds conversion

            message = (
                "The current implementation can't apply tempo changes for duration unit"
                " 'miliseconds' yet! Furthermore to quantize via duration_unit"
                " 'miliseconds' isn't well tested yet and may return unexpected"
                " results."
            )
            warnings.warn(message)

        time_signatures = tuple(time_signatures)
        # nauert will raise an error if there is only one time signature
        if len(time_signatures) == 1:
            time_signatures += time_signatures

        super().__init__(time_signatures, tempo_envelope)

        self._duration_unit = duration_unit
        self._attack_point_optimizer = attack_point_optimizer
        self._q_schema = (
            ComplexSequentialEventToQuantizedAbjadContainerConverter._make_q_schema(
                self._time_signatures, search_tree
            )
        )

    # ###################################################################### #
    #                          static methods                                #
    # ###################################################################### #

    @staticmethod
    def _get_respective_q_event_from_abjad_leaf(
        abjad_leaf: typing.Union[abjad.Rest, abjad.Note]
    ) -> typing.Optional[nauert.QEvent]:
        # TODO(improve ugly, heuristic, unreliable code)
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
        q_event = ComplexSequentialEventToQuantizedAbjadContainerConverter._get_respective_q_event_from_abjad_leaf(
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
        # skip leaves without any links
        # else:
        #     related_abjad_leaves_per_simple_event.append([tuple(indices)])

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
        for (
            nth_abjad_leaf_or_tuplet,
            abjad_leaf_or_tuplet,
        ) in enumerate(tuplet):
            (
                has_tie,
                index_of_previous_q_event,
            ) = ComplexSequentialEventToQuantizedAbjadContainerConverter._process_abjad_leaf_or_tuplet(
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
            return ComplexSequentialEventToQuantizedAbjadContainerConverter._process_tuplet(
                indices,
                abjad_leaf_or_tuplet,
                related_abjad_leaves_per_simple_event,
                q_event_sequence,
                has_tie,
                index_of_previous_q_event,
            )

        else:
            return ComplexSequentialEventToQuantizedAbjadContainerConverter._process_abjad_leaf(
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
    ) -> typing.Tuple[typing.Tuple[typing.Tuple[int, ...], ...], ...,]:
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
                ) = ComplexSequentialEventToQuantizedAbjadContainerConverter._process_abjad_leaf_or_tuplet(
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
        time_signatures: typing.Tuple[abjad.TimeSignature, ...],
        search_tree: typing.Optional[nauert.SearchTree],
    ) -> nauert.QSchema:
        formated_time_signatures = []
        for time_signature in time_signatures:
            formated_time_signatures.append({"time_signature": time_signature})

        keyword_arguments = {
            "use_full_measure": True,
            "tempo": abjad.MetronomeMark((1, 4), 60),
        }

        if search_tree:
            keyword_arguments.update({"search_tree": search_tree})

        return nauert.MeasurewiseQSchema(*formated_time_signatures, **keyword_arguments)

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
        abjad.Container,
        typing.Tuple[typing.Tuple[typing.Tuple[int, ...], ...], ...],
    ]:
        q_event_sequence = self._sequential_event_to_q_event_sequence(
            sequential_event_to_convert
        )
        quanitisized_abjad_leaves = self._q_event_sequence_to_quanitisized_abjad_leaves(
            q_event_sequence
        )

        related_abjad_leaves_per_simple_event = ComplexSequentialEventToQuantizedAbjadContainerConverter._make_related_abjad_leaves_per_simple_event(
            sequential_event_to_convert, q_event_sequence, quanitisized_abjad_leaves
        )
        return (
            quanitisized_abjad_leaves,
            related_abjad_leaves_per_simple_event,
        )


class FastSequentialEventToQuantizedAbjadContainerConverter(
    SequentialEventToQuantizedAbjadContainerConverter
):
    """Quantize :class:`~mutwo.events.basic.SequentialEvent` object via abjad rmakers

    :param time_signatures: Set time signatures to divide the quantized abjad data
        in desired bar sizes. If the converted
        :class:`~mutwo.events.basic.SequentialEvent` is longer than the sum of
        all passed time signatures, the last time signature
        will be repeated for the remaining bars.
    :param tempo_envelope: Defines the tempo of the converted music. This is an
        :class:`expenvelope.Envelope` object which durations are beats and which
        levels are either numbers (that will be interpreted as beats per minute ('BPM'))
        or :class:`~mutwo.parameters.tempos.TempoPoint` objects. If no tempo envelope
        has been defined, Mutwo will assume a constant tempo of 1/4 = 120 BPM.

    This method is significantly faster than the
    :class:`ComplexSequentialEventToQuantizedAbjadContainerConverter`. But it also
    has several known limitations:

        1. :class:`FastSequentialEventToQuantizedAbjadContainerConverter` doesn't
           support nested tuplets.
        2. :class:`FastSequentialEventToQuantizedAbjadContainerConverter` doesn't
           support ties across tuplets with different prolation (or across tuplets
           and not-tuplet notation). If ties are desired the user has to build them
           manually before passing the :class:`~mutwo.events.basic.SequentialEvent`
           to the converter.
    """

    _maximum_dot_count = 1

    def __init__(
        self, *args, do_rewrite_meter: bool = True, add_beams: bool = True, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._do_rewrite_meter = do_rewrite_meter
        self._add_beams = add_beams

    # ###################################################################### #
    #                       static private methods                           #
    # ###################################################################### #

    @staticmethod
    def _find_offset_inventory(meter: abjad.Meter) -> tuple[abjad.Offset, ...]:
        for nth_offset_inventory, offset_inventory in enumerate(
            depthwise_offset_inventory := meter.depthwise_offset_inventory
        ):
            difference = offset_inventory[1] - offset_inventory[0]
            if difference == fractions.Fraction(1, 4):
                return offset_inventory
            elif difference <= fractions.Fraction(1, 4):
                return depthwise_offset_inventory[nth_offset_inventory - 1]
        return offset_inventory

    @staticmethod
    def _add_explicit_beams(
        bar: abjad.Container, meter: abjad.Meter, global_offset: abjad.Offset
    ) -> None:
        offset_inventory = FastSequentialEventToQuantizedAbjadContainerConverter._find_offset_inventory(
            meter
        )
        leaf_offsets = []
        # don't attach beams on tuplets
        relevant_bar_items = filter(
            lambda leaf_or_tuplet: isinstance(leaf_or_tuplet, abjad.Leaf)
            and leaf_or_tuplet.written_duration < fractions.Fraction(1, 4),
            bar,
        )
        leaves = abjad.select(relevant_bar_items).leaves()
        for leaf in leaves:
            offset = abjad.get.timespan(leaf).start_offset - global_offset
            leaf_offsets.append(offset)

        beam_ranges = []
        for start, end in zip(offset_inventory, offset_inventory[1:]):
            area = ranges.Range(start, end)
            offsets = tuple(filter(lambda offset: offset in area, leaf_offsets))
            n_elements = len(offsets)
            is_start_in_leaves = start in offsets

            # make new beam range
            if is_start_in_leaves and n_elements > 1:
                new_beam_range = [
                    leaf_offsets.index(offsets[0]),
                    leaf_offsets.index(offsets[-1]),
                ]
                beam_ranges.append(new_beam_range)

        for beam_range in beam_ranges:
            start, stop = beam_range
            abjad.attach(abjad.StartBeam(), leaves[start])
            abjad.attach(abjad.StopBeam(), leaves[stop])

        global_offset += offset_inventory[-1]
        return global_offset

    @staticmethod
    def _find_tuplet_indices(bar: abjad.Container) -> tuple[int, ...]:
        tuplet_indices = []
        for index, leaf_or_tuplet in enumerate(bar):
            if isinstance(leaf_or_tuplet, abjad.Tuplet):
                tuplet_indices.append(index)

        return tuple(tuplet_indices)

    @staticmethod
    def _group_tuplet_indices(tuplet_indices: tuple[int, ...]) -> list[list[int]]:
        """Put adjacent tuplet indices into groups."""

        grouped_tuplet_indices = [[]]
        last_tuplet_index = None
        for tuplet_index in tuplet_indices:
            if last_tuplet_index:
                difference = tuplet_index - last_tuplet_index
                if difference == 1:
                    grouped_tuplet_indices[-1].append(tuplet_index)
                else:
                    grouped_tuplet_indices.append([tuplet_index])
            else:
                grouped_tuplet_indices[-1].append(tuplet_index)
            last_tuplet_index = tuplet_index
        return grouped_tuplet_indices

    @staticmethod
    def _concatenate_adjacent_tuplets_for_one_group(
        bar: abjad.Container, group: list[int]
    ):
        implied_prolations = [bar[index].implied_prolation for index in group]
        common_prolation_groups = [[implied_prolations[0], [group[0]]]]
        for index, prolation in zip(group[1:], implied_prolations[1:]):
            if prolation == common_prolation_groups[-1][0]:
                common_prolation_groups[-1][1].append(index)
            else:
                common_prolation_groups.append([prolation, [index]])

        tuplets = []
        for prolation, tuplet_indices in common_prolation_groups:
            tuplet = abjad.Tuplet(prolation)
            for tuplet_index in tuplet_indices:
                for component in bar[tuplet_index]:
                    tuplet.append(abjad.mutate.copy(component))
            tuplets.append(tuplet)

        bar[group[0] : group[-1] + 1] = tuplets

    # ###################################################################### #
    #                       private methods                                  #
    # ###################################################################### #

    def _make_notes(
        self, sequential_event_to_convert: events.basic.SequentialEvent
    ) -> abjad.Selection:
        stack = rmakers.stack(
            rmakers.note(),
            rmakers.force_rest(
                lambda _: abjad.select(_)
                .logical_ties()
                .get(
                    [
                        index
                        for index, event in enumerate(sequential_event_to_convert)
                        if event.is_rest
                    ]
                ),
            ),
        )
        notes = stack(
            tuple(
                map(
                    lambda duration: (
                        fractions.Fraction(duration).numerator,
                        fractions.Fraction(duration).denominator,
                    ),
                    sequential_event_to_convert.get_parameter("duration"),
                )
            )
        )
        return notes

    def _concatenate_adjacent_tuplets_for_one_bar(self, bar: abjad.Container):
        tuplet_indices = (
            FastSequentialEventToQuantizedAbjadContainerConverter._find_tuplet_indices(
                bar
            )
        )
        if tuplet_indices:
            grouped_tuplet_indices = FastSequentialEventToQuantizedAbjadContainerConverter._group_tuplet_indices(
                tuplet_indices
            )
            for group in reversed(grouped_tuplet_indices):
                if len(group) > 1:
                    FastSequentialEventToQuantizedAbjadContainerConverter._concatenate_adjacent_tuplets_for_one_group(
                        bar, group
                    )

    def _concatenate_adjacent_tuplets(self, voice: abjad.Voice) -> abjad.Voice:
        for bar in voice:
            self._concatenate_adjacent_tuplets_for_one_bar(bar)

    def _rewrite_meter(self, voice: abjad.Voice):
        time_signatures = iter(self._time_signatures)
        last_time_signature = self._time_signatures[-1]
        # rewrite by meter
        global_offset = abjad.Offset((0, 1))
        previous_time_signature = None
        for bar in voice:
            try:
                time_signature = next(time_signatures)
            except StopIteration:
                time_signature = last_time_signature
            if time_signature != previous_time_signature:
                abjad.attach(time_signature, abjad.get.leaf(bar, 0))
            meter = abjad.Meter(time_signature)
            abjad.Meter.rewrite_meter(
                bar[:], time_signature, maximum_dot_count=self._maximum_dot_count
            )
            if self._add_beams:
                global_offset = self._add_explicit_beams(bar, meter, global_offset)
            previous_time_signature = time_signature

        last_bar = bar
        difference = time_signature.duration - abjad.get.duration(last_bar)
        if difference:

            stack = rmakers.stack(
                rmakers.note(),
                rmakers.force_rest(lambda _: abjad.select(_).logical_ties()[:]),
            )
            last_bar.extend(stack((difference,)))
            abjad.Meter.rewrite_meter(
                last_bar[:], time_signature, maximum_dot_count=self._maximum_dot_count
            )

    def _make_voice(
        self, sequential_event_to_convert: events.basic.SequentialEvent
    ) -> abjad.Voice:
        # first build notes
        notes = self._make_notes(sequential_event_to_convert)

        # split notes by time signatures
        notes_split_by_time_signatures = abjad.mutate.split(
            notes,
            [time_signature.duration for time_signature in self._time_signatures],
            cyclic=True,
        )
        bars = []
        for selection in notes_split_by_time_signatures:
            try:
                bar = abjad.Container(selection.items, simultaneous=False)
            except Exception:
                bar = abjad.Container(
                    abjad.mutate.copy(selection).items, simultaneous=False
                )
            bars.append(bar)
        voice = abjad.Voice(bars)
        if self._do_rewrite_meter:
            self._rewrite_meter(voice)
        self._concatenate_adjacent_tuplets(voice)
        return voice

    def _get_data_for_leaf(
        self, indices: typing.Tuple[int, ...], leaf: abjad.Leaf
    ) -> typing.Tuple[typing.Tuple[int, ...], bool, bool]:
        has_tie = abjad.get.indicator(leaf, abjad.Tie())
        is_rest = (
            isinstance(leaf, abjad.Rest)
            or isinstance(leaf, abjad.MultimeasureRest)
            or isinstance(leaf, abjad.Skip)
        )
        return indices, has_tie, is_rest

    def _get_data_for_tuplet_or_leaf(
        self,
        indices: typing.Tuple[int, ...],
        leaf_or_tuplet: typing.Union[abjad.Leaf, abjad.Tuplet],
    ) -> typing.Tuple[typing.Tuple[typing.Tuple[int, ...], bool], ...]:
        if isinstance(leaf_or_tuplet, abjad.Leaf):
            return (self._get_data_for_leaf(indices, leaf_or_tuplet),)
        else:
            data_per_leaf_or_tuplet = []
            for nth_leaf_or_tuplet_of_tuplet, sub_leaf_or_tuplet in enumerate(
                leaf_or_tuplet
            ):
                data_per_leaf_or_tuplet.extend(
                    self._get_data_for_tuplet_or_leaf(
                        indices + (nth_leaf_or_tuplet_of_tuplet,), sub_leaf_or_tuplet
                    )
                )
            return tuple(data_per_leaf_or_tuplet)

    def _make_related_abjad_leaves_per_simple_event(
        self, voice: abjad.Voice
    ) -> typing.Tuple[typing.Tuple[typing.Tuple[int, ...], ...], ...]:
        data_per_tuplet_or_leaf = []
        for nth_bar, bar in enumerate(voice):
            for nth_leaf_or_tuplet, leaf_or_tuplet in enumerate(bar):
                data_per_tuplet_or_leaf.extend(
                    self._get_data_for_tuplet_or_leaf(
                        (nth_bar, nth_leaf_or_tuplet), leaf_or_tuplet
                    )
                )

        related_abjad_leaves_per_simple_event = []
        related_abjad_leaves = []
        was_previous_note_rest = None
        has_previous_tie = None
        for indices, has_tie, is_rest in data_per_tuplet_or_leaf:
            if has_previous_tie or all((was_previous_note_rest, is_rest)):
                related_abjad_leaves.append(indices)
            else:
                if related_abjad_leaves:
                    related_abjad_leaves_per_simple_event.append(
                        tuple(related_abjad_leaves)
                    )
                related_abjad_leaves = [indices]

            has_previous_tie = has_tie
            was_previous_note_rest = is_rest

        if related_abjad_leaves:
            related_abjad_leaves_per_simple_event.append(tuple(related_abjad_leaves))

        return tuple(related_abjad_leaves_per_simple_event)

    def convert(
        self, sequential_event_to_convert: events.basic.SequentialEvent
    ) -> typing.Tuple[
        abjad.Container,
        typing.Tuple[typing.Tuple[typing.Tuple[int, ...], ...], ...],
    ]:
        voice = self._make_voice(sequential_event_to_convert)
        related_abjad_leaves_per_simple_event = (
            self._make_related_abjad_leaves_per_simple_event(voice)
        )
        return voice, related_abjad_leaves_per_simple_event


class ComplexSequentialEventToDurationLineBasedQuantizedAbjadContainerConverter(
    ComplexSequentialEventToQuantizedAbjadContainerConverter
):
    """Quantize :class:`~mutwo.events.basic.SequentialEvent` objects via :mod:`abjadext.nauert`.

    :param time_signatures: Set time signatures to divide the quantized abjad data
        in desired bar sizes. If the converted :class:`~mutwo.events.basic.SequentialEvent`
        is longer than the sum of all passed time signatures, the last time signature
        will be repeated for the remaining bars.
    :param duration_unit: This defines the `duration_unit` of the passed
        :class:`~mutwo.events.basic.SequentialEvent` (how the
        :attr:`~mutwo.events.abc.Event.duration` attribute will be
        interpreted). Can either be 'beats' (default) or 'miliseconds'.
    :param tempo_envelope: Defines the tempo of the converted music. This is an
        :class:`expenvelope.Envelope` object which durations are beats and which
        levels are either numbers (that will be interpreted as beats per minute ('BPM'))
        or :class:`~mutwo.parameters.tempos.TempoPoint` objects. If no tempo envelope has
        been defined, Mutwo will assume a constant tempo of 1/4 = 120 BPM.
    :param attack_point_optimizer: Optionally the user can pass a
        :class:`nauert.AttackPointOptimizer` object. Attack point optimizer help to
        split events and tie them for better looking notation. The default attack point
        optimizer is :class:`nauert.MeasurewiseAttackPointOptimizer` which splits events
        to better represent metrical structures within bars. If no optimizer is desired
        this argument can be set to ``None``.
    :param duration_line_minimum_length: The minimum length of a duration line.
    :type duration_line_minimum_length: int
    :param duration_line_thickness: The thickness of a duration line.
    :type duration_line_thickness: int

    This converter differs from
    :class:`SequentialEventToQuantizedAbjadContainerConverter` through
    the usage of duration lines for indicating rhythm instead of using
    flags, beams, dots and note head colors.

    **Note**:

    Don't forget to add the 'Duration_line_engraver' to the resulting
    abjad Voice, otherwise Lilypond won't be able to render the desired output.

    **Example:**

    >>> import abjad
    >>> from mutwo.converters.frontends import abjad as mutwo_abjad
    >>> from mutwo.events import basic, music
    >>> converter = frontends.abjad.SequentialEventToAbjadVoiceConverter(
    >>>     frontends.abjad.ComplexSequentialEventToDurationLineBasedQuantizedAbjadContainerConverter(
    >>>        )
    >>>    )
    >>> sequential_event_to_convert = basic.SequentialEvent(
    >>>     [music.NoteLike("c", 0.125), music.NoteLike("d", 1), music.NoteLike([], 0.125), music.NoteLike("e", 0.16666), music.NoteLike("e", 0.08333333333333333)]
    >>>    )
    >>> converted_sequential_event = converter.convert(sequential_event_to_convert)
    >>> converted_sequential_event.consists_commands.append("Duration_line_engraver")
    """

    def __init__(
        self,
        time_signatures: typing.Sequence[abjad.TimeSignature] = (
            abjad.TimeSignature((4, 4)),
        ),
        duration_unit: str = "beats",  # for future: typing.Literal["beats", "miliseconds"]
        tempo_envelope: expenvelope.Envelope = None,
        attack_point_optimizer: typing.Optional[
            nauert.AttackPointOptimizer
        ] = nauert.MeasurewiseAttackPointOptimizer(),
        search_tree: typing.Optional[nauert.SearchTree] = None,
        duration_line_minimum_length: int = 6,
        duration_line_thickness: int = 3,
    ):
        super().__init__(
            time_signatures,
            duration_unit,
            tempo_envelope,
            attack_point_optimizer,
            search_tree,
        )
        self._duration_line_minimum_length = duration_line_minimum_length
        self._duration_line_thickness = duration_line_thickness

    def _prepare_first_element(self, first_element: abjad.Leaf):
        # don't write rests (simply write empty space)
        abjad.attach(abjad.LilyPondLiteral("\\omit Staff.Rest"), first_element)
        abjad.attach(
            abjad.LilyPondLiteral("\\omit Staff.MultiMeasureRest"), first_element
        )
        # don't write stems (Rhythm get defined by duration line)
        abjad.attach(abjad.LilyPondLiteral("\\omit Staff.Stem"), first_element)
        # don't write flags (Rhythm get defined by duration line)
        abjad.attach(abjad.LilyPondLiteral("\\omit Staff.Flag"), first_element)
        # don't write beams (Rhythm get defined by duration line)
        abjad.attach(abjad.LilyPondLiteral("\\omit Staff.Beam"), first_element)
        # don't write dots (Rhythm get defined by duration line)
        abjad.attach(
            abjad.LilyPondLiteral("\\override Staff.Dots.dot-count = #0"),
            first_element,
        )
        # only write black note heads (Rhythm get defined by duration line)
        abjad.attach(
            abjad.LilyPondLiteral("\\override Staff.NoteHead.duration-log = 2"),
            first_element,
        )
        # set duration line properties
        abjad.attach(
            abjad.LilyPondLiteral(
                "\\override Staff.DurationLine.minimum-length = {}".format(
                    self._duration_line_minimum_length
                )
            ),
            first_element,
        )
        abjad.attach(
            abjad.LilyPondLiteral(
                "\\override Staff.DurationLine.thickness = {}".format(
                    self._duration_line_thickness
                )
            ),
            first_element,
        )

    def _adjust_quantisized_abjad_leaves(
        self,
        quanitisized_abjad_leaves: abjad.Container,
        related_abjad_leaves_per_simple_event: typing.Tuple[
            typing.Tuple[typing.Tuple[int, ...], ...], ...
        ],
    ):
        is_first = True

        for abjad_leaves_indices in related_abjad_leaves_per_simple_event:
            if abjad_leaves_indices:
                first_element = tools.get_nested_item_from_indices(
                    abjad_leaves_indices[0], quanitisized_abjad_leaves
                )
                if is_first:
                    self._prepare_first_element(first_element)
                    is_first = False

                is_active = bool(abjad.get.pitches(first_element))
                if is_active:
                    if len(abjad_leaves_indices) > 1:
                        abjad.detach(abjad.Tie(), first_element)

                    abjad.attach(
                        abjad.LilyPondLiteral("\\-", format_slot="after"), first_element
                    )

                    for indices in abjad_leaves_indices[1:]:
                        element = tools.get_nested_item_from_indices(
                            indices, quanitisized_abjad_leaves
                        )
                        tools.set_nested_item_from_indices(
                            indices,
                            quanitisized_abjad_leaves,
                            abjad.Skip(element.written_duration),
                        )

    def convert(
        self, sequential_event_to_convert: events.basic.SequentialEvent
    ) -> typing.Tuple[
        abjad.Container,
        typing.Tuple[typing.Tuple[typing.Tuple[int, ...], ...], ...],
    ]:

        (
            quanitisized_abjad_leaves,
            related_abjad_leaves_per_simple_event,
        ) = super().convert(sequential_event_to_convert)

        self._adjust_quantisized_abjad_leaves(
            quanitisized_abjad_leaves, related_abjad_leaves_per_simple_event
        )

        return quanitisized_abjad_leaves, related_abjad_leaves_per_simple_event


class FastSequentialEventToDurationLineBasedQuantizedAbjadContainerConverter(
    FastSequentialEventToQuantizedAbjadContainerConverter
):
    """Quantize :class:`~mutwo.events.basic.SequentialEvent` objects via :mod:`abjadext.nauert`.

    :param time_signatures: Set time signatures to divide the quantized abjad data
        in desired bar sizes. If the converted :class:`~mutwo.events.basic.SequentialEvent`
        is longer than the sum of all passed time signatures, the last time signature
        will be repeated for the remaining bars.
    :param duration_unit: This defines the `duration_unit` of the passed
        :class:`~mutwo.events.basic.SequentialEvent` (how the
        :attr:`~mutwo.events.abc.Event.duration` attribute will be
        interpreted). Can either be 'beats' (default) or 'miliseconds'.
    :param tempo_envelope: Defines the tempo of the converted music. This is an
        :class:`expenvelope.Envelope` object which durations are beats and which
        levels are either numbers (that will be interpreted as beats per minute ('BPM'))
        or :class:`~mutwo.parameters.tempos.TempoPoint` objects. If no tempo envelope has
        been defined, Mutwo will assume a constant tempo of 1/4 = 120 BPM.
    :param attack_point_optimizer: Optionally the user can pass a
        :class:`nauert.AttackPointOptimizer` object. Attack point optimizer help to
        split events and tie them for better looking notation. The default attack point
        optimizer is :class:`nauert.MeasurewiseAttackPointOptimizer` which splits events
        to better represent metrical structures within bars. If no optimizer is desired
        this argument can be set to ``None``.
    :param duration_line_minimum_length: The minimum length of a duration line.
    :type duration_line_minimum_length: int
    :param duration_line_thickness: The thickness of a duration line.
    :type duration_line_thickness: int

    This converter differs from
    :class:`SequentialEventToQuantizedAbjadContainerConverter` through
    the usage of duration lines for indicating rhythm instead of using
    flags, beams, dots and note head colors.

    **Note**:

    Don't forget to add the 'Duration_line_engraver' to the resulting
    abjad Voice, otherwise Lilypond won't be able to render the desired output.

    **Example:**

    >>> import abjad
    >>> from mutwo.converters.frontends import abjad as mutwo_abjad
    >>> from mutwo.events import basic, music
    >>> converter = frontends.abjad.SequentialEventToAbjadVoiceConverter(
    >>>     frontends.abjad.ComplexSequentialEventToDurationLineBasedQuantizedAbjadContainerConverter(
    >>>        )
    >>>    )
    >>> sequential_event_to_convert = basic.SequentialEvent(
    >>>     [music.NoteLike("c", 0.125), music.NoteLike("d", 1), music.NoteLike([], 0.125), music.NoteLike("e", 0.16666), music.NoteLike("e", 0.08333333333333333)]
    >>>    )
    >>> converted_sequential_event = converter.convert(sequential_event_to_convert)
    >>> converted_sequential_event.consists_commands.append("Duration_line_engraver")
    """

    def __init__(
        self,
        *args,
        duration_line_minimum_length: int = 6,
        duration_line_thickness: int = 3,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._duration_line_minimum_length = duration_line_minimum_length
        self._duration_line_thickness = duration_line_thickness

    def _prepare_first_element(self, first_element: abjad.Leaf):
        # don't write rests (simply write empty space)
        abjad.attach(abjad.LilyPondLiteral("\\omit Staff.Rest"), first_element)
        abjad.attach(
            abjad.LilyPondLiteral("\\omit Staff.MultiMeasureRest"), first_element
        )
        # don't write stems (Rhythm get defined by duration line)
        abjad.attach(abjad.LilyPondLiteral("\\omit Staff.Stem"), first_element)
        # don't write flags (Rhythm get defined by duration line)
        abjad.attach(abjad.LilyPondLiteral("\\omit Staff.Flag"), first_element)
        # don't write beams (Rhythm get defined by duration line)
        abjad.attach(abjad.LilyPondLiteral("\\omit Staff.Beam"), first_element)
        # don't write dots (Rhythm get defined by duration line)
        abjad.attach(
            abjad.LilyPondLiteral("\\override Staff.Dots.dot-count = #0"),
            first_element,
        )
        # only write black note heads (Rhythm get defined by duration line)
        abjad.attach(
            abjad.LilyPondLiteral("\\override Staff.NoteHead.duration-log = 2"),
            first_element,
        )
        # set duration line properties
        abjad.attach(
            abjad.LilyPondLiteral(
                "\\override Staff.DurationLine.minimum-length = {}".format(
                    self._duration_line_minimum_length
                )
            ),
            first_element,
        )
        abjad.attach(
            abjad.LilyPondLiteral(
                "\\override Staff.DurationLine.thickness = {}".format(
                    self._duration_line_thickness
                )
            ),
            first_element,
        )

    def _adjust_quantisized_abjad_leaves(
        self,
        quanitisized_abjad_leaves: abjad.Container,
        related_abjad_leaves_per_simple_event: typing.Tuple[
            typing.Tuple[typing.Tuple[int, ...], ...], ...
        ],
    ):
        is_first = True

        for abjad_leaves_indices in related_abjad_leaves_per_simple_event:
            if abjad_leaves_indices:
                first_element = tools.get_nested_item_from_indices(
                    abjad_leaves_indices[0], quanitisized_abjad_leaves
                )
                if is_first:
                    self._prepare_first_element(first_element)
                    is_first = False

                is_active = bool(abjad.get.pitches(first_element))
                if is_active:
                    if len(abjad_leaves_indices) > 1:
                        abjad.detach(abjad.Tie(), first_element)

                    abjad.attach(
                        abjad.LilyPondLiteral("\\-", format_slot="after"), first_element
                    )

                    for indices in abjad_leaves_indices[1:]:
                        element = tools.get_nested_item_from_indices(
                            indices, quanitisized_abjad_leaves
                        )
                        tools.set_nested_item_from_indices(
                            indices,
                            quanitisized_abjad_leaves,
                            abjad.Skip(element.written_duration),
                        )

    def convert(
        self, sequential_event_to_convert: events.basic.SequentialEvent
    ) -> typing.Tuple[
        abjad.Container,
        typing.Tuple[typing.Tuple[typing.Tuple[int, ...], ...], ...],
    ]:

        (
            quanitisized_abjad_leaves,
            related_abjad_leaves_per_simple_event,
        ) = super().convert(sequential_event_to_convert)

        self._adjust_quantisized_abjad_leaves(
            quanitisized_abjad_leaves, related_abjad_leaves_per_simple_event
        )

        # only assign first item to abjad leaves
        post_processed_releated_abjad_leaves_per_simple_event = []
        for related_abjad_leaves in related_abjad_leaves_per_simple_event:
            post_processed_releated_abjad_leaves_per_simple_event.append(
                (related_abjad_leaves[0],)
            )

        return (
            quanitisized_abjad_leaves,
            post_processed_releated_abjad_leaves_per_simple_event,
        )
