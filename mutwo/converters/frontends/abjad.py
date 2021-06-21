"""Build Lilypond scores via `Abjad <https://github.com/Abjad/abjad>`_ from Mutwo data.

The following converter classes help to quantize and translate Mutwo data to
Western notation. Due to the complex nature of this task, Mutwo tries to offer as
many optional arguments as possible through which the user can affect the conversion
routines. The most important class and best starting point for organising a conversion
setting is :class:`SequentialEventToAbjadVoiceConverter`.
"""

import abc
import typing
import warnings

try:
    import quicktions as fractions  # type: ignore
except ImportError:
    import fractions  # type: ignore

import abjad  # type: ignore
from abjadext import nauert  # type: ignore
import expenvelope  # type: ignore

from mutwo.converters import abc as converters_abc
from mutwo.converters.frontends import abjad_attachments
from mutwo.converters.frontends import abjad_constants
from mutwo.converters.frontends import ekmelily_constants

from mutwo import events
from mutwo import parameters

from mutwo.utilities import constants
from mutwo.utilities import tools

__all__ = (
    "MutwoPitchToAbjadPitchConverter",
    "MutwoPitchToHEJIAbjadPitchConverter",
    "MutwoVolumeToAbjadAttachmentDynamicConverter",
    "TempoEnvelopeToAbjadAttachmentTempoConverter",
    "ComplexTempoEnvelopeToAbjadAttachmentTempoConverter",
    "SequentialEventToQuantizedAbjadContainerConverter",
    "SequentialEventToDurationLineBasedQuantizedAbjadContainerConverter",
    "SequentialEventToAbjadVoiceConverter",
)


class MutwoPitchToAbjadPitchConverter(converters_abc.Converter):
    """Convert Mutwo Pitch objects to Abjad Pitch objects.

    This default class simply checks if the passed Mutwo object belongs to
    :class:`mutwo.parameters.pitches.WesternPitch`. If it does, Mutwo
    will initialise the Abjad Pitch from the :attr:`name` attribute.
    Otherwise Mutwo will simply initialise the Abjad Pitch from the
    objects :attr:`frequency` attribute.

    If users desire to make more complex conversions (for instance
    due to ``scordatura`` or transpositions of instruments), one can simply
    inherit from this class to define more complex cases.
    """

    def convert(self, pitch_to_convert: parameters.abc.Pitch) -> abjad.Pitch:
        if isinstance(pitch_to_convert, parameters.pitches.WesternPitch):
            return abjad.NamedPitch(pitch_to_convert.name)
        else:
            return abjad.NamedPitch.from_hertz(pitch_to_convert.frequency)


class _HEJIAccidental(object):
    """Fake abjad accidental

    Only for internal usage within the :class:`MutwoPitchToHEJIAbjadPitchConverter`.
    """

    def __init__(self, accidental: str):
        self._accidental = accidental

    def __str__(self) -> str:
        return self._accidental

    # necessary attributes, although they
    # won't be used at all
    semitones = 0
    arrow = None


class MutwoPitchToHEJIAbjadPitchConverter(MutwoPitchToAbjadPitchConverter):
    """Convert Mutwo :obj:`~mutwo.parameters.pitches.JustIntonationPitch` objects to Abjad Pitch objects.

    :param reference_pitch: The reference pitch (1/1). Should be a diatonic
        pitch name (see
        :const:`~mutwo.parameters.pitches_constants.ASCENDING_DIATONIC_PITCH_NAMES`)
        in English nomenclature. For any other reference pitch than 'c', Lilyponds
        midi rendering for pitches with the diatonic pitch 'c' will be slightly
        out of tune (because the first value of :arg:`global_scale`
        always have to be 0).
    :type reference_pitch: str, optional
    :param prime_to_heji_accidental_name: Mapping of a prime number
        to a string which indicates the respective prime number in the resulting
        accidental name. See
        :const:`~mutwo.converters.frontends.ekmelily_constants.DEFAULT_PRIME_TO_HEJI_ACCIDENTAL_NAME`
        for the default mapping.
    :type prime_to_heji_accidental_name: typing.Dict[int, str], optional
    :param otonality_indicator: String which indicates that the
        respective prime alteration is otonal. See
        :const:`~mutwo.converters.frontends.ekmelily_constants.DEFAULT_OTONALITY_INDICATOR`
        for the default value.
    :type otonality_indicator: str, optional
    :param utonality_indicator: String which indicates that the
        respective prime alteration is utonal. See
        :const:`~mutwo.converters.frontends.ekmelily_constants.DEFAULT_OTONALITY_INDICATOR`
        for the default value.
    :type utonality_indicator: str, optional
    :param exponent_to_exponent_indicator: Function to convert the
        exponent of a prime number to string which indicates the respective
        exponent. See
        :func:`~mutwo.converters.frontends.ekmelily_constants.DEFAULT_EXPONENT_TO_EXPONENT_INDICATOR`
        for the default function.
    :type exponent_to_exponent_indicator: typing.Callable[[int], str], optional
    :param tempered_pitch_indicator: String which indicates that the
        respective accidental is tempered (12 EDO). See
        :const:`~mutwo.converters.frontends.ekmelily_constants.DEFAULT_TEMPERED_PITCH_INDICATOR`
        for the default value.
    :type tempered_pitch_indicator: str, optional

    The resulting Abjad pitches are expected to be used in combination with tuning
    files that are generated by
    :class:`~mutwo.converters.frontends.ekmelily.HEJIEkmelilyTuningFileConverter`
    and with the Lilypond extension
    `Ekmelily <http://www.ekmelic-music.org/en/extra/ekmelily.htm>`_.
    You can find pre-generated tuning files
    `here <https://github.com/levinericzimmermann/ekme-heji.ily>`_.

    >>> from mutwo.parameters import pitches
    >>> from mutwo.converters.frontends import abjad
    >>> my_ji_pitch = pitches.JustIntonationPitch('5/4')
    >>> converter_on_a = abjad.MutwoPitchToHEJIAbjadPitchConverter(reference_pitch='a')
    >>> converter_on_c = abjad.MutwoPitchToHEJIAbjadPitchConverter(reference_pitch='c')
    >>> converter_on_a.convert(my_ji_pitch)
    NamedPitch("csoaa''")
    >>> converter_on_c.convert(my_ji_pitch)
    NamedPitch("eoaa'")
    """

    def __init__(
        self,
        reference_pitch: str = "a",
        prime_to_heji_accidental_name: typing.Optional[typing.Dict[int, str]] = None,
        otonality_indicator: str = None,
        utonality_indicator: str = None,
        exponent_to_exponent_indicator: typing.Callable[[int], str] = None,
        tempered_pitch_indicator: str = None,
    ):
        # set default values
        if prime_to_heji_accidental_name is None:
            prime_to_heji_accidental_name = (
                ekmelily_constants.DEFAULT_PRIME_TO_HEJI_ACCIDENTAL_NAME
            )

        if otonality_indicator is None:
            otonality_indicator = ekmelily_constants.DEFAULT_OTONALITY_INDICATOR

        if utonality_indicator is None:
            utonality_indicator = ekmelily_constants.DEFAULT_UTONALITY_INDICATOR

        if exponent_to_exponent_indicator is None:
            exponent_to_exponent_indicator = (
                ekmelily_constants.DEFAULT_EXPONENT_TO_EXPONENT_INDICATOR
            )

        if tempered_pitch_indicator is None:
            tempered_pitch_indicator = (
                ekmelily_constants.DEFAULT_TEMPERED_PITCH_INDICATOR
            )

        self._reference_pitch = reference_pitch
        self._otonality_indicator = otonality_indicator
        self._utonality_indicator = utonality_indicator
        self._exponent_to_exponent_indicator = exponent_to_exponent_indicator
        self._tempered_pitch_indicator = tempered_pitch_indicator
        self._reference_index = parameters.pitches_constants.ASCENDING_DIATONIC_PITCH_NAMES.index(
            reference_pitch
        )
        self._prime_to_heji_accidental_name = prime_to_heji_accidental_name

    def _convert_just_intonation_pitch(
        self, pitch_to_convert: parameters.pitches.JustIntonationPitch,
    ) -> abjad.Pitch:
        # find pythagorean pitch
        closest_pythagorean_pitch_name = pitch_to_convert.get_closest_pythagorean_pitch_name(
            self._reference_pitch
        )
        abjad_pitch_class = abjad.NamedPitchClass(closest_pythagorean_pitch_name)

        # find additional commas
        accidental_parts = [str(abjad_pitch_class.accidental)]
        prime_to_exponent = (
            pitch_to_convert.helmholtz_ellis_just_intonation_notation_commas.prime_to_exponent
        )
        for prime in sorted(prime_to_exponent.keys()):
            exponent = prime_to_exponent[prime]
            if exponent != 0:
                tonality = (
                    self._otonality_indicator
                    if exponent > 0
                    else self._utonality_indicator
                )
                heji_accidental_name = self._prime_to_heji_accidental_name[prime]
                exponent_indicator = self._exponent_to_exponent_indicator(
                    abs(exponent) - 1
                )
                accidental_parts.append(
                    "{}{}{}".format(tonality, heji_accidental_name, exponent_indicator)
                )

        accidental = _HEJIAccidental("".join(accidental_parts))
        abjad_pitch_class._accidental = accidental

        octave = pitch_to_convert.octave + 4
        closest_pythagorean_pitch_index = parameters.pitches_constants.ASCENDING_DIATONIC_PITCH_NAMES.index(
            closest_pythagorean_pitch_name[0]
        )
        if closest_pythagorean_pitch_index < self._reference_index:
            octave += 1

        # for pitches which are written with the same diatonic pitch as
        # the reference_pitch, but which are slightly deeper
        elif (
            closest_pythagorean_pitch_index == self._reference_index
            and pitch_to_convert.normalize(mutate=False).cents > 600  # type: ignore
        ):
            octave += 1

        abjad_pitch = abjad.NamedPitch(octave=octave)
        abjad_pitch._pitch_class = abjad_pitch_class
        return abjad_pitch

    def convert(self, pitch_to_convert: parameters.abc.Pitch) -> abjad.Pitch:
        if isinstance(pitch_to_convert, parameters.pitches.JustIntonationPitch):
            abjad_pitch = self._convert_just_intonation_pitch(pitch_to_convert)
        else:
            abjad_pitch = MutwoPitchToAbjadPitchConverter().convert(pitch_to_convert)

        return abjad_pitch


class MutwoVolumeToAbjadAttachmentDynamicConverter(converters_abc.Converter):
    """Convert Mutwo Volume objects to :class:`~mutwo.converters.frontends.abjad_attachments.Dynamic`.

    This default class simply checks if the passed Mutwo object belongs to
    :class:`mutwo.parameters.volumes.WesternVolume`. If it does, Mutwo
    will initialise the :class:`Tempo` object from the :attr:`name` attribute.
    Otherwise Mutwo will first initialise a :class:`WesternVolume` object via
    its py:method:`mutwo.parameters.volumes.WesternVolume.from_amplitude` method.

    Hairpins aren't notated with the aid of :class:`mutwo.parameters.abc.Volume`
    objects, but with :class:`mutwo.parameters.playing_indicators.Hairpin`.
    """

    def convert(
        self, volume_to_convert: parameters.abc.Volume
    ) -> typing.Optional[abjad_attachments.Dynamic]:
        if not isinstance(volume_to_convert, parameters.volumes.WesternVolume):
            if volume_to_convert.amplitude > 0:
                volume_to_convert = parameters.volumes.WesternVolume.from_amplitude(
                    volume_to_convert.amplitude
                )
            else:
                return None
        return abjad_attachments.Dynamic(dynamic_indicator=volume_to_convert.name)


class TempoEnvelopeToAbjadAttachmentTempoConverter(converters_abc.Converter):
    """Convert tempo envelope to :class:`~mutwo.converters.frontends.abjad_attachments.Tempo`.

    Abstract base class for tempo envelope conversion. See
    :class:`ComplexTempoEnvelopeToAbjadAttachmentTempoConverter` for a concrete
    class.
    """

    @abc.abstractmethod
    def convert(
        self, tempo_envelope_to_convert: expenvelope.Envelope
    ) -> typing.Tuple[typing.Tuple[constants.Real, abjad_attachments.Tempo], ...]:
        # return tuple filled with subtuples (leaf_index, abjad_attachments.Tempo)
        raise NotImplementedError()


class ComplexTempoEnvelopeToAbjadAttachmentTempoConverter(
    TempoEnvelopeToAbjadAttachmentTempoConverter
):
    """Convert tempo envelope to :class:`~mutwo.converters.frontends.abjad_attachments.Tempo`.

    This object tries to intelligently set correct tempo attachments to an
    :class:`abjad.Voice` object, appropriate to Western notation standards.
    Therefore it will not repeat tempo indications if they are merely repetitions
    of previous tempo indications and it will write 'a tempo' when returning to the
    same tempo after ritardandi or accelerandi.
    """

    # ###################################################################### #
    #                     private static methods                             #
    # ###################################################################### #

    @staticmethod
    def _convert_tempo_points(
        tempo_points: typing.Tuple[
            typing.Union[constants.Real, parameters.tempos.TempoPoint], ...
        ]
    ) -> typing.Tuple[parameters.tempos.TempoPoint, ...]:
        return tuple(
            tempo_point
            if isinstance(tempo_point, parameters.tempos.TempoPoint)
            else parameters.tempos.TempoPoint(float(tempo_point))
            for tempo_point in tempo_points
        )

    @staticmethod
    def _find_dynamic_change_indication(
        tempo_point: parameters.tempos.TempoPoint,
        next_tempo_point: typing.Optional[parameters.tempos.TempoPoint],
    ) -> typing.Optional[str]:
        dynamic_change_indication = None
        if next_tempo_point:
            absolute_tempo_for_current_tempo_point = (
                tempo_point.absolute_tempo_in_beat_per_minute
            )
            absolute_tempo_for_next_tempo_point = (
                next_tempo_point.absolute_tempo_in_beat_per_minute
            )
            if (
                absolute_tempo_for_current_tempo_point
                > absolute_tempo_for_next_tempo_point
            ):
                dynamic_change_indication = "rit."
            elif (
                absolute_tempo_for_current_tempo_point
                < absolute_tempo_for_next_tempo_point
            ):
                dynamic_change_indication = "acc."

        return dynamic_change_indication

    @staticmethod
    def _shall_write_metronome_mark(
        tempo_envelope_to_convert: expenvelope.Envelope,
        nth_tempo_point: int,
        tempo_point: parameters.tempos.TempoPoint,
        tempo_points: typing.Tuple[parameters.tempos.TempoPoint, ...],
    ) -> bool:
        write_metronome_mark = True
        for previous_tempo_point, previous_tempo_point_duration in zip(
            reversed(tempo_points[:nth_tempo_point]),
            reversed(tempo_envelope_to_convert.durations[:nth_tempo_point]),
        ):
            # make sure the previous tempo point could have been written
            # down (longer duration than minimal duration)
            if previous_tempo_point_duration > 0:
                # if the previous writeable MetronomeMark has the same
                # beats per minute than the current event, there is no
                # need to write it down again
                if (
                    previous_tempo_point.absolute_tempo_in_beat_per_minute
                    == tempo_point.absolute_tempo_in_beat_per_minute
                ):
                    write_metronome_mark = False
                    break

                # but if it differs, we should definitely write it down
                else:
                    break

        return write_metronome_mark

    @staticmethod
    def _shall_stop_dynamic_change_indication(
        tempo_attachments: typing.Tuple[
            typing.Tuple[constants.Real, abjad_attachments.Tempo], ...
        ]
    ) -> bool:
        stop_dynamic_change_indicaton = False
        for _, previous_tempo_attachment in reversed(tempo_attachments):
            # make sure the previous tempo point could have been written
            # down (longer duration than minimal duration)
            if previous_tempo_attachment.dynamic_change_indication is not None:
                stop_dynamic_change_indicaton = True
            break

        return stop_dynamic_change_indicaton

    @staticmethod
    def _find_metronome_mark_values(
        write_metronome_mark: bool,
        tempo_point: parameters.tempos.TempoPoint,
        stop_dynamic_change_indicaton: bool,
    ) -> typing.Tuple[
        typing.Optional[typing.Tuple[int, int]],
        typing.Optional[typing.Union[int, typing.Tuple[int, int]]],
        typing.Optional[str],
    ]:
        if write_metronome_mark:
            textual_indication: typing.Optional[str] = tempo_point.textual_indication
            reference = fractions.Fraction(tempo_point.reference) * fractions.Fraction(
                1, 4
            )
            reference_duration: typing.Optional[typing.Tuple[int, int]] = (
                reference.numerator,
                reference.denominator,
            )
            units_per_minute: typing.Optional[
                typing.Union[int, typing.Tuple[int, int]]
            ] = (
                (
                    int(tempo_point.tempo_or_tempo_range_in_beats_per_minute[0]),
                    int(tempo_point.tempo_or_tempo_range_in_beats_per_minute[1]),
                )
                if isinstance(
                    tempo_point.tempo_or_tempo_range_in_beats_per_minute, tuple
                )
                else int(tempo_point.tempo_or_tempo_range_in_beats_per_minute)
            )

        else:
            reference_duration = None
            units_per_minute = None
            # check if you can write 'a tempo'
            if stop_dynamic_change_indicaton:
                textual_indication = "a tempo"
            else:
                textual_indication = None

        return reference_duration, units_per_minute, textual_indication

    @staticmethod
    def _process_tempo_event(
        tempo_envelope_to_convert: expenvelope.Envelope,
        nth_tempo_point: int,
        tempo_point: parameters.tempos.TempoPoint,
        tempo_points: typing.Tuple[parameters.tempos.TempoPoint, ...],
        tempo_attachments: typing.Tuple[
            typing.Tuple[constants.Real, abjad_attachments.Tempo], ...
        ],
    ) -> abjad_attachments.Tempo:
        try:
            next_tempo_point: typing.Optional[
                parameters.tempos.TempoPoint
            ] = tempo_points[nth_tempo_point + 1]
        except IndexError:
            next_tempo_point = None

        # check for dynamic_change_indication
        dynamic_change_indication = ComplexTempoEnvelopeToAbjadAttachmentTempoConverter._find_dynamic_change_indication(
            tempo_point, next_tempo_point
        )
        write_metronome_mark = ComplexTempoEnvelopeToAbjadAttachmentTempoConverter._shall_write_metronome_mark(
            tempo_envelope_to_convert, nth_tempo_point, tempo_point, tempo_points,
        )

        stop_dynamic_change_indicaton = ComplexTempoEnvelopeToAbjadAttachmentTempoConverter._shall_stop_dynamic_change_indication(
            tempo_attachments
        )

        (
            reference_duration,
            units_per_minute,
            textual_indication,
        ) = ComplexTempoEnvelopeToAbjadAttachmentTempoConverter._find_metronome_mark_values(
            write_metronome_mark, tempo_point, stop_dynamic_change_indicaton
        )

        # for writing 'a tempo'
        if textual_indication == "a tempo":
            write_metronome_mark = True

        converted_tempo_point = abjad_attachments.Tempo(
            reference_duration=reference_duration,
            units_per_minute=units_per_minute,
            textual_indication=textual_indication,
            dynamic_change_indication=dynamic_change_indication,
            stop_dynamic_change_indicaton=stop_dynamic_change_indicaton,
            print_metronome_mark=write_metronome_mark,
        )

        return converted_tempo_point

    # ###################################################################### #
    #                           public api                                   #
    # ###################################################################### #

    def convert(
        self, tempo_envelope_to_convert: expenvelope.Envelope
    ) -> typing.Tuple[typing.Tuple[constants.Real, abjad_attachments.Tempo], ...]:
        tempo_points = ComplexTempoEnvelopeToAbjadAttachmentTempoConverter._convert_tempo_points(
            tempo_envelope_to_convert.levels
        )

        tempo_attachments: typing.List[
            typing.Tuple[constants.Real, abjad_attachments.Tempo]
        ] = []
        for nth_tempo_point, absolute_time, duration, tempo_point in zip(
            range(len(tempo_points)),
            tools.accumulate_from_zero(tempo_envelope_to_convert.durations),
            tempo_envelope_to_convert.durations + (1,),
            tempo_points,
        ):

            if duration > 0:
                tempo_attachment = ComplexTempoEnvelopeToAbjadAttachmentTempoConverter._process_tempo_event(
                    tempo_envelope_to_convert,
                    nth_tempo_point,
                    tempo_point,
                    tempo_points,
                    tuple(tempo_attachments),
                )
                tempo_attachments.append((absolute_time, tempo_attachment))

        return tuple(tempo_attachments)


class SequentialEventToQuantizedAbjadContainerConverter(converters_abc.Converter):
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

        n_time_signatures = len(time_signatures)
        if n_time_signatures == 0:
            message = (
                "Found empy sequence for argument 'time_signatures'. Specify at least"
                " one time signature!"
            )
            raise ValueError(message)

        time_signatures = tuple(time_signatures)
        # nauert will raise an error if there is only one time signature
        if n_time_signatures == 1:
            time_signatures += time_signatures

        if tempo_envelope is None:
            tempo_envelope = expenvelope.Envelope.from_points(
                (0, parameters.tempos.TempoPoint(120)),
                (0, parameters.tempos.TempoPoint(120)),
            )

        self._duration_unit = duration_unit
        self._time_signatures = time_signatures
        self._tempo_envelope = tempo_envelope
        self._attack_point_optimizer = attack_point_optimizer
        self._q_schema = SequentialEventToQuantizedAbjadContainerConverter._make_q_schema(
            self._time_signatures, search_tree
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


class SequentialEventToDurationLineBasedQuantizedAbjadContainerConverter(
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
    >>>     frontends.abjad.SequentialEventToDurationLineBasedQuantizedAbjadContainerConverter(
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
        abjad.attach(abjad.LilyPondLiteral("\\omit Rest"), first_element)
        abjad.attach(abjad.LilyPondLiteral("\\omit MultiMeasureRest"), first_element)
        # don't write stems (Rhythm get defined by duration line)
        abjad.attach(abjad.LilyPondLiteral("\\omit Stem"), first_element)
        # don't write flags (Rhythm get defined by duration line)
        abjad.attach(abjad.LilyPondLiteral("\\omit Flag"), first_element)
        # don't write beams (Rhythm get defined by duration line)
        abjad.attach(abjad.LilyPondLiteral("\\omit Beam"), first_element)
        # don't write dots (Rhythm get defined by duration line)
        abjad.attach(
            abjad.LilyPondLiteral("\\override Dots.dot-count = #0"), first_element,
        )
        # only write black note heads (Rhythm get defined by duration line)
        abjad.attach(
            abjad.LilyPondLiteral("\\override NoteHead.duration-log = 2"),
            first_element,
        )
        # set duration line properties
        abjad.attach(
            abjad.LilyPondLiteral(
                "\\override DurationLine.minimum-length = {}".format(
                    self._duration_line_minimum_length
                )
            ),
            first_element,
        )
        abjad.attach(
            abjad.LilyPondLiteral(
                "\\override DurationLine.thickness = {}".format(
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
        abjad.Container, typing.Tuple[typing.Tuple[typing.Tuple[int, ...], ...], ...],
    ]:

        (
            quanitisized_abjad_leaves,
            related_abjad_leaves_per_simple_event,
        ) = super().convert(sequential_event_to_convert)

        self._adjust_quantisized_abjad_leaves(
            quanitisized_abjad_leaves, related_abjad_leaves_per_simple_event
        )

        return quanitisized_abjad_leaves, related_abjad_leaves_per_simple_event


class SequentialEventToAbjadVoiceConverter(converters_abc.Converter):
    """Convert :class:`~mutwo.events.basic.SequentialEvent` to :class:`abjad.Voice`.

    :param sequential_event_to_quantized_abjad_container_converter: Class which
        defines how the Mutwo data will be quantized. See
        :class:`SequentialEventToQuantizedAbjadContainerConverter` for more information.
    :type sequential_event_to_quantized_abjad_container_converter: SequentialEventToQuantizedAbjadContainerConverter, optional
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
        extracted), mutwo will set :attr:`pitch_or_pitches` to an empty list and set
        volume to 0.
    :type simple_event_to_volume: typing.Callable[[events.basic.SimpleEvent], parameters.abc.Volume], optional
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
    :param simple_event_to_notation_indicators: Function to extract from a
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
    :type simple_event_to_notation_indicators: typing.Callable[[events.basic.SimpleEvent], parameters.notation_indicators.NotationIndicatorCollection,], optional
    :param is_simple_event_rest: Function to detect if the
        the inspected :class:`mutwo.events.basic.SimpleEvent` is a Rest. By
        default Mutwo simply checks if 'pitch_or_pitches' contain any objects. If not,
        the Event will be interpreted as a rest.
    :type is_simple_event_rest: typing.Callable[[events.basic.SimpleEvent], bool], optional
    :param mutwo_pitch_to_abjad_pitch_converter: Class which defines how to convert
        :class:`mutwo.parameters.abc.Pitch` objects to :class:`abjad.Pitch` objects.
        See :class:`MutwoPitchToAbjadPitchConverter` for more information.
    :type mutwo_pitch_to_abjad_pitch_converter: MutwoPitchToAbjadPitchConverter, optional
    :param mutwo_volume_to_abjad_attachment_dynamic_converter: Class which defines how
        to convert :class:`mutwo.parameters.abc.Volume` objects to
        :class:`mutwo.converters.frontends.abjad_attachments.Dynamic` objects.
        See :class:`MutwoVolumeToAbjadAttachmentDynamicConverter` for more information.
    :type mutwo_volume_to_abjad_attachment_dynamic_converter: MutwoVolumeToAbjadAttachmentDynamicConverter, optional
    :param tempo_envelope_to_abjad_attachment_tempo_converter: Class which defines how
        to convert tempo envelopes to
        :class:`mutwo.converters.frontends.abjad_attachments.Tempo` objects.
        See :class:`TempoEnvelopeToAbjadAttachmentTempoConverter` for more information.
    :type tempo_envelope_to_abjad_attachment_tempo_converter: TempoEnvelopeToAbjadAttachmentTempoConverter, optional
    :param abjad_attachment_classes: A tuple which contains all available abjad attachment classes
        which shall be used by the converter.
    :type abjad_attachment_classes: typing.Sequence[abjad_attachments.AbjadAttachment], optional
    """

    def __init__(
        self,
        sequential_event_to_quantized_abjad_container_converter: SequentialEventToQuantizedAbjadContainerConverter = SequentialEventToQuantizedAbjadContainerConverter(),
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
        is_simple_event_rest: typing.Callable[[events.basic.SimpleEvent], bool] = None,
        mutwo_pitch_to_abjad_pitch_converter: MutwoPitchToAbjadPitchConverter = MutwoPitchToAbjadPitchConverter(),
        mutwo_volume_to_abjad_attachment_dynamic_converter: MutwoVolumeToAbjadAttachmentDynamicConverter = MutwoVolumeToAbjadAttachmentDynamicConverter(),
        tempo_envelope_to_abjad_attachment_tempo_converter: TempoEnvelopeToAbjadAttachmentTempoConverter = ComplexTempoEnvelopeToAbjadAttachmentTempoConverter(),
        abjad_attachment_classes: typing.Sequence[
            typing.Type[abjad_attachments.AbjadAttachment]
        ] = None,
    ):
        if abjad_attachment_classes is None:
            abjad_attachment_classes = abjad_constants.DEFAULT_ABJAD_ATTACHMENT_CLASSES
        else:
            abjad_attachment_classes = tuple(abjad_attachment_classes)

        if is_simple_event_rest is None:

            def is_simple_event_rest(simple_event: events.basic.SimpleEvent) -> bool:
                try:
                    pitch_or_pitches = simple_event_to_pitches(simple_event)
                except AttributeError:
                    pitch_or_pitches = []

                return not bool(pitch_or_pitches)

        self._abjad_attachment_classes = abjad_attachment_classes

        self._available_abjad_attachments = tuple(
            abjad_attachment_class.get_class_name()
            for abjad_attachment_class in self._abjad_attachment_classes
        )

        self._sequential_event_to_quantized_abjad_container_converter = (
            sequential_event_to_quantized_abjad_container_converter
        )
        self._simple_event_to_pitches = simple_event_to_pitches
        self._simple_event_to_volume = simple_event_to_volume
        self._simple_event_to_playing_indicators = simple_event_to_playing_indicators
        self._simple_event_to_notation_indicators = simple_event_to_notation_indicators
        self._is_simple_event_rest = is_simple_event_rest
        self._mutwo_pitch_to_abjad_pitch_converter = (
            mutwo_pitch_to_abjad_pitch_converter
        )
        self._mutwo_volume_to_abjad_attachment_dynamic_converter = (
            mutwo_volume_to_abjad_attachment_dynamic_converter
        )
        self._tempo_attachments = tempo_envelope_to_abjad_attachment_tempo_converter.convert(
            self._sequential_event_to_quantized_abjad_container_converter._tempo_envelope
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
    def _indicator_collection_to_abjad_attachments_depr(
        indicator_collection: parameters.abc.IndicatorCollection,
        indicator_name_to_abjad_attachment_mapping: typing.Dict[
            str, typing.Type[abjad_attachments.AbjadAttachment]
        ],
    ) -> typing.Dict[str, abjad_attachments.AbjadAttachment]:
        attachments = {}
        for (
            indicator_name,
            indicator,
        ) in indicator_collection.get_indicator_dict().items():
            if indicator_name in indicator_name_to_abjad_attachment_mapping:
                new_attachment = indicator_name_to_abjad_attachment_mapping[  # type: ignore
                    indicator_name
                ](
                    **indicator.get_arguments_dict()
                )
                attachments.update({indicator_name: new_attachment})

        return attachments

    @staticmethod
    def _find_absolute_times_of_abjad_leaves(
        abjad_voice: abjad.Voice,
    ) -> typing.Tuple[fractions.Fraction, ...]:
        absolute_time_per_leaf: typing.List[fractions.Fraction] = []
        for leaf in abjad.select(abjad_voice).leaves():
            start, _ = abjad.get.timespan(leaf).offsets
            absolute_time_per_leaf.append(
                fractions.Fraction(start.numerator, start.denominator)
            )
        return tuple(absolute_time_per_leaf)

    @staticmethod
    def _replace_rests_with_full_measure_rests(abjad_voice: abjad.Voice) -> None:
        for bar in abjad_voice:
            if len(bar) == 1:
                if isinstance(bar[0], abjad.Rest):
                    abjad.mutate.replace(
                        bar[0],
                        abjad.MultimeasureRest(bar[0].written_duration),
                        wrappers=True,
                    )

    # ###################################################################### #
    #                          private methods                               #
    # ###################################################################### #

    def _indicator_collection_to_abjad_attachments(
        self, indicator_collection: parameters.abc.IndicatorCollection,
    ) -> typing.Dict[str, abjad_attachments.AbjadAttachment]:
        attachments = {}
        for abjad_attachment_class in self._abjad_attachment_classes:
            abjad_attachment = abjad_attachment_class.from_indicator_collection(
                indicator_collection
            )
            if abjad_attachment:
                attachments.update(
                    {abjad_attachment_class.get_class_name(): abjad_attachment}
                )

        return attachments

    def _volume_to_abjad_attachment(
        self, volume: parameters.abc.Volume
    ) -> typing.Dict[str, abjad_attachments.AbjadAttachment]:
        abjad_attachment_dynamic = self._mutwo_volume_to_abjad_attachment_dynamic_converter.convert(
            volume
        )
        if abjad_attachment_dynamic:
            return {"dynamic": abjad_attachment_dynamic}
        else:
            return {}

    def _get_tempo_attachments_for_quantized_abjad_leaves(
        self, abjad_voice: abjad.Voice,
    ) -> typing.Tuple[
        typing.Tuple[
            int,
            typing.Union[
                abjad_attachments.Tempo, abjad_attachments.DynamicChangeIndicationStop
            ],
        ],
        ...,
    ]:
        absolute_time_per_leaf = SequentialEventToAbjadVoiceConverter._find_absolute_times_of_abjad_leaves(
            abjad_voice
        )

        assert absolute_time_per_leaf == tuple(sorted(absolute_time_per_leaf))

        leaf_index_to_tempo_attachment_pairs: typing.List[
            typing.Tuple[
                int,
                typing.Union[
                    abjad_attachments.Tempo,
                    abjad_attachments.DynamicChangeIndicationStop,
                ],
            ]
        ] = []
        for absolute_time, tempo_attachment in self._tempo_attachments:
            closest_leaf = tools.find_closest_index(
                absolute_time, absolute_time_per_leaf
            )
            # special case:
            # check for stop dynamic change indication
            # (has to applied to the previous leaf for
            #  better looking results)
            if tempo_attachment.stop_dynamic_change_indicaton:
                leaf_index_to_tempo_attachment_pairs.append(
                    (closest_leaf - 1, abjad_attachments.DynamicChangeIndicationStop())
                )
            leaf_index_to_tempo_attachment_pairs.append(
                (closest_leaf, tempo_attachment)
            )

        return tuple(leaf_index_to_tempo_attachment_pairs)

    def _get_attachments_for_quantized_abjad_leaves(
        self,
        abjad_voice: abjad.Voice,
        extracted_data_per_simple_event: typing.Tuple[
            typing.Tuple[
                typing.List[parameters.abc.Pitch],
                parameters.abc.Volume,
                parameters.playing_indicators.PlayingIndicatorCollection,
                parameters.notation_indicators.NotationIndicatorCollection,
            ],
            ...,
        ],
    ) -> typing.Tuple[
        typing.Tuple[typing.Optional[abjad_attachments.AbjadAttachment], ...], ...
    ]:
        attachments_per_type_per_event: typing.Dict[
            str, typing.List[typing.Optional[abjad_attachments.AbjadAttachment]]
        ] = {
            attachment_name: [None for _ in extracted_data_per_simple_event]
            for attachment_name in self._available_abjad_attachments
        }
        for nth_event, extracted_data in enumerate(extracted_data_per_simple_event):
            _, volume, playing_indicators, notation_indicators = extracted_data
            attachments_for_nth_event = self._volume_to_abjad_attachment(volume)
            attachments_for_nth_event.update(
                self._indicator_collection_to_abjad_attachments(playing_indicators)
            )
            attachments_for_nth_event.update(
                self._indicator_collection_to_abjad_attachments(notation_indicators)
            )
            for attachment_name, attachment in attachments_for_nth_event.items():
                attachments_per_type_per_event[attachment_name][nth_event] = attachment

        return tuple(
            tuple(attachments)
            for attachments in attachments_per_type_per_event.values()
        )

    def _apply_tempos_on_quantized_abjad_leaves(
        self, quanitisized_abjad_leaves: abjad.Voice,
    ):
        leaves = abjad.select(quanitisized_abjad_leaves).leaves()
        tempo_attachment_data = self._get_tempo_attachments_for_quantized_abjad_leaves(
            quanitisized_abjad_leaves
        )
        for nth_event, tempo_attachment in tempo_attachment_data:
            tempo_attachment.process_leaves((leaves[nth_event],), None)

    def _apply_attachments_on_quantized_abjad_leaves(
        self,
        quanitisized_abjad_leaves: abjad.Voice,
        related_abjad_leaves_per_simple_event: typing.Tuple[
            typing.Tuple[typing.Tuple[int, ...], ...], ...
        ],
        attachments_per_type_per_event: typing.Tuple[
            typing.Tuple[typing.Optional[abjad_attachments.AbjadAttachment], ...], ...
        ],
    ) -> None:
        for attachments in attachments_per_type_per_event:
            previous_attachment = None
            for related_abjad_leaves_indices, attachment in zip(
                related_abjad_leaves_per_simple_event, attachments
            ):
                if attachment and attachment.is_active:
                    abjad_leaves = tuple(
                        tools.get_nested_item_from_indices(
                            indices, quanitisized_abjad_leaves,
                        )
                        for indices in related_abjad_leaves_indices
                    )
                    processed_abjad_leaves = attachment.process_leaves(
                        abjad_leaves, previous_attachment
                    )
                    for processed_abjad_leaf, indices in zip(
                        processed_abjad_leaves, related_abjad_leaves_indices
                    ):
                        tools.set_nested_item_from_indices(
                            indices, quanitisized_abjad_leaves, processed_abjad_leaf
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

        # TODO(Add option: no dynamic indicator if there aren't any pitches)
        try:
            if pitches:
                volume = self._simple_event_to_volume(simple_event)
            else:
                volume = parameters.volumes.DirectVolume(0)
        except AttributeError:
            volume = parameters.volumes.DirectVolume(0)
            pitches = []

        try:
            playing_indicators = self._simple_event_to_playing_indicators(simple_event)
        except AttributeError:
            playing_indicators = (
                events.music_constants.DEFAULT_PLAYING_INDICATORS_COLLECTION_CLASS()
            )

        try:
            notation_indicators = self._simple_event_to_notation_indicators(
                simple_event
            )
        except AttributeError:
            notation_indicators = (
                events.music_constants.DEFAULT_NOTATION_INDICATORS_COLLECTION_CLASS()
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
            abjad_leaf = tools.get_nested_item_from_indices(
                related_abjad_leaf_indices, quanitisized_abjad_leaves
            )
            if leaf_class == abjad.Note:
                # skip don't have note heads
                if hasattr(abjad_leaf, "note_head"):
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

                tools.set_nested_item_from_indices(
                    related_abjad_leaf_indices,
                    quanitisized_abjad_leaves,
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
            quanitisized_abjad_leaves,
            related_abjad_leaves_per_simple_event,
        ) = self._quantize_sequential_event(
            sequential_event_to_convert, is_simple_event_rest_per_simple_event
        )

        # third, apply pitches on Abjad voice
        self._apply_pitches_on_quantized_abjad_leaves(
            quanitisized_abjad_leaves,
            related_abjad_leaves_per_simple_event,
            extracted_data_per_simple_event,
            is_simple_event_rest_per_simple_event,
        )

        # fourth, apply dynamics, tempos and playing_indicators on abjad voice
        attachments_per_type_per_event = self._get_attachments_for_quantized_abjad_leaves(
            quanitisized_abjad_leaves, extracted_data_per_simple_event
        )
        self._apply_attachments_on_quantized_abjad_leaves(
            quanitisized_abjad_leaves,
            related_abjad_leaves_per_simple_event,
            attachments_per_type_per_event,
        )
        self._apply_tempos_on_quantized_abjad_leaves(quanitisized_abjad_leaves)

        # fifth, replace rests lasting one bar with full measure rests
        SequentialEventToAbjadVoiceConverter._replace_rests_with_full_measure_rests(
            quanitisized_abjad_leaves
        )

        return quanitisized_abjad_leaves
