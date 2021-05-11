"""Build tuning files for `Lilypond <https://lilypond.org/>`_ extension `Ekmelily <http://www.ekmelic-music.org/en/extra/ekmelily.htm>`_.

By default the smallest step which Lilypond supports is one quartertone. With
the help of Ekmelily it is easily possible to add more complex micro- or
macrotonal tunings to Lilypond. The converter in this module aims to make it easier
to build tuning files to be used with the 'ekmel-main.ily' script from Thomas Richter.

**Disclaimer:**

For now the converters only support making notation tables for English note names.
"""

import dataclasses
import itertools
import typing
import warnings

try:
    import quicktions as fractions  # type: ignore
except ImportError:
    import fractions  # type: ignore

from mutwo.converters import abc as converters_abc
from mutwo.converters import frontends
from mutwo.parameters import pitches
from mutwo.parameters import pitches_constants
from mutwo.utilities import constants

__all__ = (
    "EkmelilyAccidental",
    "EkmelilyTuningFileConverter",
    "HEJIEkmelilyTuningFileConverter",
)


@dataclasses.dataclass(frozen=True)
class EkmelilyAccidental(object):
    """Representation of an Ekmelily accidental.

    :param accidental_name: The name of the accidental that
        follows after the diatonic pitch name (e.g. 's' or 'qf')
    :type accidental_name: str
    :param accidental_glyphs: The name of accidental glyphs that should
        appear before the notehead. For
        a list of available glyphs, check the documentation of
        `Ekmelos <http://www.ekmelic-music.org/en/extra/ekmelos.htm>`_.
        Furthermore one can find mappings from mutwo data to Ekmelos glyph
        names in :const:`~mutwo.converters.frontends.ekmelily_constants.PRIME_AND_EXPONENT_AND_TRADITIONAL_ACCIDENTAL_TO_ACCIDENTAL_GLYPH`
        and :const:`~mutwo.converters.frontends.ekmelily_constants.TEMPERED_ACCIDENTAL_TO_ACCIDENTAL_GLYPH`.
    :type accidental_glyphs: typing.Tuple[str, ...]
    :param deviation_in_cents: How many cents shall an altered pitch differ from
        its diatonic / natural counterpart.
    :type deviation_in_cents: float
    :param available_diatonic_pitch_indices: Sometimes one
        may want to define accidentals which are only available for certain
        diatonic pitches. For this case, one can use this argument
        and specify all diatonic pitches which should know this
        accidental. If this argument keeps undefined, the accidental
        will be added to all seven diatonic pitches.
    :type available_diatonic_pitch_indices: typing.Optional[typing.Tuple[int, ...]], optional

    **Example:**

    >>> from mutwo.converter.frontends import ekmelily
    >>> natural = ekmelily.EkmelilyAccidental('', ("#xE261",), 0)
    >>> sharp = ekmelily.EkmelilyAccidental('s', ("#xE262",), 100)
    >>> flat = ekmelily.EkmelilyAccidental('f', ("#xE260",), -100)
    """

    accidental_name: str
    accidental_glyphs: typing.Tuple[str, ...]
    deviation_in_cents: float
    available_diatonic_pitch_indices: typing.Optional[typing.Tuple[int, ...]] = None

    def __hash__(self) -> int:
        return hash(
            (
                self.accidental_name,
                self.accidental_glyphs,
                self.deviation_in_cents,
                self.available_diatonic_pitch_indices,
            )
        )


class EkmelilyTuningFileConverter(converters_abc.Converter):
    """Build Ekmelily tuning files from Ekmelily accidentals.

    :param path: Path where the new Ekmelily tuning file shall be written.
        The suffix '.ily' is recommended, but not necessary.
    :type path: str
    :param ekmelily_accidentals: A sequence which contains all
        :class:`EkmelilyAccidental` that shall be written to the tuning file,
    :type ekmelily_accidentals: typing.Sequence[EkmelilyAccidental]
    :param global_scale: From the `Lilypond documentation <https://lilypond.org/doc/v2.20/Documentation/notation/scheme-functions>`_:
        "This determines the tuning of pitches with no accidentals or key signatures.
        The first pitch is c. Alterations are calculated relative to this scale.
        The number of pitches in this scale determines the number of scale steps
        that make up an octave. Usually the 7-note major scale."
    :type global_scale: typing.Tuple[fractions.Fraction, ...], optional

    **Example:**

    >>> from mutwo.converter.frontends import ekmelily
    >>> natural = ekmelily.EkmelilyAccidental('', ("#xE261",), 0)
    >>> sharp = ekmelily.EkmelilyAccidental('s', ("#xE262",), 100)
    >>> flat = ekmelily.EkmelilyAccidental('f', ("#xE260",), -100)
    >>> eigth_tone_sharp = ekmelily.EkmelilyAccidental('es', ("#xE2C7",), 25)
    >>> eigth_tone_flat = ekmelily.EkmelilyAccidental('ef', ("#xE2C2",), -25)
    >>> converter = ekmelily.EkmelilyTuningFileConverter(
    >>>     'ekme-test.ily', (natural, sharp, flat, eigth_tone_sharp, eigth_tone_flat)
    >>> )
    >>> converter.convert()
    """

    def __init__(
        self,
        path: str,
        ekmelily_accidentals: typing.Sequence[EkmelilyAccidental],
        # should have exactly 7 fractions (one for each diatonic pitch)
        global_scale: typing.Optional[typing.Tuple[fractions.Fraction, ...]] = None,
    ):
        if global_scale is None:
            # set to default 12 EDO, a' = 440 Hertz
            global_scale = frontends.ekmelily_constants.DEFAULT_GLOBAL_SCALE

        global_scale = EkmelilyTuningFileConverter._correct_global_scale(global_scale)

        self._path = path
        self._global_scale = global_scale
        self._ekmelily_accidentals = ekmelily_accidentals
        (
            self._accidental_to_alteration_code_mapping,
            self._alteration_code_to_alteration_fraction_mapping,
        ) = EkmelilyTuningFileConverter._make_accidental_to_alteration_code_mapping_and_alteration_code_to_alteration_fraction_mapping(
            self._ekmelily_accidentals
        )

    # ###################################################################### #
    #                          static methods                                #
    # ###################################################################### #

    @staticmethod
    def _correct_global_scale(
        global_scale: typing.Tuple[fractions.Fraction, ...]
    ) -> typing.Tuple[fractions.Fraction, ...]:
        # Lilypond doesn't allow negative values for first item in global scale.
        # Therefore Mutwo makes sure that the first item isn't a negative number.
        corrected_global_scale = list(global_scale)
        if corrected_global_scale[0] != 0:
            message = (
                "Found value '{}' for first scale degree in global scale. Autoset value"
                " to 0 (Lilypond doesn't allow values != 0 for the first scale degree)"
                .format(corrected_global_scale[0])
            )
            warnings.warn(message)
            corrected_global_scale[0] = fractions.Fraction(0, 1)
        return tuple(corrected_global_scale)

    @staticmethod
    def _deviation_in_cents_to_alteration_fraction(
        deviation_in_cents: constants.Real, max_denominator: int = 1000
    ) -> fractions.Fraction:
        # simplify fraction to avoid too complex calculations during Lilyponds midi
        # render (otherwise Lilypond won't be able to render Midi / it will take
        # too long)
        return fractions.Fraction(deviation_in_cents / 200).limit_denominator(
            max_denominator
        )

    @staticmethod
    def _alteration_fraction_to_deviation_in_cents(
        alteration_fraction: fractions.Fraction,
    ) -> float:
        return float(alteration_fraction * 200)

    @staticmethod
    def _accidental_index_to_alteration_code(accidental_index: int) -> str:
        # convert index of accidental to hex code in a format that is
        # readable by Lilypond
        return "#x{}".format(str(hex(accidental_index))[2:].upper())

    @staticmethod
    def _find_and_group_accidentals_by_specific_deviation_in_cents(
        ekmelily_accidentals: typing.Sequence[EkmelilyAccidental],
        deviation_in_cents: float,
    ) -> typing.Tuple[
        typing.Tuple[EkmelilyAccidental, ...], typing.Tuple[EkmelilyAccidental, ...]
    ]:
        positive, negative = [], []
        for accidental in ekmelily_accidentals:
            if accidental.deviation_in_cents == deviation_in_cents:
                positive.append(accidental)
            elif (
                accidental.deviation_in_cents == -deviation_in_cents
                and deviation_in_cents != 0
            ):
                negative.append(accidental)

        return tuple(positive), tuple(negative)

    @staticmethod
    def _group_accidentals_by_deviations_in_cents(
        ekmelily_accidentals: typing.Sequence[EkmelilyAccidental],
    ) -> typing.Tuple[
        typing.Tuple[float, typing.Tuple[typing.Tuple[EkmelilyAccidental, ...], ...]],
        ...,
    ]:
        """Put all accidentals with the same absolute deviation to the same tuple.

        The first element of each tuple is the absolute deviation in cents,
        the second element is tuple with two elements where the first element
        contains all positive accidentals and the second tuple all negative
        accidentals.
        """

        available_deviations_in_cents = sorted(
            set(
                map(
                    lambda accidental: abs(accidental.deviation_in_cents),
                    ekmelily_accidentals,
                )
            )
        )
        accidentals_grouped_by_deviations_in_cents = tuple(
            (
                deviation_in_cents,
                EkmelilyTuningFileConverter._find_and_group_accidentals_by_specific_deviation_in_cents(
                    ekmelily_accidentals, deviation_in_cents
                ),
            )
            for deviation_in_cents in available_deviations_in_cents
        )

        return accidentals_grouped_by_deviations_in_cents

    @staticmethod
    def _process_single_accidental(
        accidental_to_alteration_code_mapping: typing.Dict[EkmelilyAccidental, str],
        alteration_code_to_alteration_fraction_mapping: typing.Dict[
            str, fractions.Fraction
        ],
        accidental: typing.Optional[EkmelilyAccidental],
        accidental_index: int,
        is_positive: bool,
        absolute_deviation_in_cents: float,
    ):
        alteration_code = EkmelilyTuningFileConverter._accidental_index_to_alteration_code(
            accidental_index
        )

        if accidental:
            accidental_to_alteration_code_mapping.update({accidental: alteration_code})

        if is_positive:
            alteration_fraction = EkmelilyTuningFileConverter._deviation_in_cents_to_alteration_fraction(
                absolute_deviation_in_cents
            )
            alteration_code_to_alteration_fraction_mapping.update(
                {alteration_code: alteration_fraction}
            )

    @staticmethod
    def _process_accidental_pair(
        accidental_to_alteration_code_mapping: typing.Dict[EkmelilyAccidental, str],
        alteration_code_to_alteration_fraction_mapping: typing.Dict[
            str, fractions.Fraction
        ],
        positive_accidental: typing.Optional[EkmelilyAccidental],
        positive_alteration_index: int,
        negative_accidental: typing.Optional[EkmelilyAccidental],
        negative_alteration_index: int,
        absolute_deviation_in_cents: float,
    ) -> None:
        # Add accidental data to accidental_to_alteration_code_mapping
        # and alteration_code_to_alteration_fraction_mapping.

        for is_positive, accidental, accidental_index in (
            (True, positive_accidental, positive_alteration_index),
            (False, negative_accidental, negative_alteration_index),
        ):
            EkmelilyTuningFileConverter._process_single_accidental(
                accidental_to_alteration_code_mapping,
                alteration_code_to_alteration_fraction_mapping,
                accidental,
                accidental_index,
                is_positive,
                absolute_deviation_in_cents,
            )

    @staticmethod
    def _get_accidental_from_accidental_iterator(
        accidental_iterator: typing.Iterator,
    ) -> typing.Optional[EkmelilyAccidental]:
        try:
            accidental = next(accidental_iterator)
        except StopIteration:
            accidental = None

        return accidental

    @staticmethod
    def _process_accidental_group(
        accidental_to_alteration_code_mapping: typing.Dict[EkmelilyAccidental, str],
        alteration_code_to_alteration_fraction_mapping: typing.Dict[
            str, fractions.Fraction
        ],
        nth_alteration: int,
        accidental_group: typing.Tuple[typing.Tuple[EkmelilyAccidental, ...], ...],
        absolute_deviation_in_cents: float,
    ) -> int:
        # Define alteration codes and alteration fractions for accidentals
        # in one accidental group and add the calculated data to both mappings.

        positive_accidentals, negative_accidentals = accidental_group
        positive_accidentals_iterator = iter(positive_accidentals)
        negative_accidentals_iterator = iter(negative_accidentals)
        for _ in range(max((len(positive_accidentals), len(negative_accidentals)))):
            positive_alteration_index, negative_alteration_index = (
                nth_alteration,
                nth_alteration + 1,
            )
            positive_accidental = EkmelilyTuningFileConverter._get_accidental_from_accidental_iterator(
                positive_accidentals_iterator
            )
            negative_accidental = EkmelilyTuningFileConverter._get_accidental_from_accidental_iterator(
                negative_accidentals_iterator
            )

            EkmelilyTuningFileConverter._process_accidental_pair(
                accidental_to_alteration_code_mapping,
                alteration_code_to_alteration_fraction_mapping,
                positive_accidental,
                positive_alteration_index,
                negative_accidental,
                negative_alteration_index,
                absolute_deviation_in_cents,
            )
            nth_alteration += 2

        return nth_alteration

    @staticmethod
    def _make_accidental_to_alteration_code_mapping_and_alteration_code_to_alteration_fraction_mapping(
        ekmelily_accidentals: typing.Sequence[EkmelilyAccidental],
    ) -> typing.Tuple[
        typing.Dict[EkmelilyAccidental, str], typing.Dict[str, fractions.Fraction]
    ]:
        accidentals_grouped_by_deviations_in_cents = EkmelilyTuningFileConverter._group_accidentals_by_deviations_in_cents(
            ekmelily_accidentals
        )
        accidental_to_alteration_code_mapping: typing.Dict[EkmelilyAccidental, str] = {}
        alteration_code_to_alteration_fraction_mapping: typing.Dict[
            str, fractions.Fraction
        ] = {}

        nth_alteration = 0
        for (
            absolute_deviation_in_cents,
            accidental_group,
        ) in accidentals_grouped_by_deviations_in_cents:
            nth_alteration = EkmelilyTuningFileConverter._process_accidental_group(
                accidental_to_alteration_code_mapping,
                alteration_code_to_alteration_fraction_mapping,
                nth_alteration,
                accidental_group,
                absolute_deviation_in_cents,
            )

        return (
            accidental_to_alteration_code_mapping,
            alteration_code_to_alteration_fraction_mapping,
        )

    # ###################################################################### #
    #                          private methods                               #
    # ###################################################################### #

    def _make_tuning_table(self) -> str:
        tuning_table_entries = [
            "  (-1 {})".format(" ".join((str(ratio) for ratio in self._global_scale)))
        ]
        for (
            alteration_code,
            alteration_fraction,
        ) in self._alteration_code_to_alteration_fraction_mapping.items():
            alteration = "({} . {})".format(alteration_code, alteration_fraction)
            tuning_table_entries.append(alteration)

        tuning_table = "ekmTuning = #'(\n{})".format("\n  ".join(tuning_table_entries))
        return tuning_table

    def _get_pitch_entry_from_accidental_and_diatonic_pitch(
        self,
        accidental: EkmelilyAccidental,
        nth_diatonic_pitch: int,
        diatonic_pitch: str,
    ) -> typing.Optional[str]:
        is_addable = True
        if accidental.available_diatonic_pitch_indices is not None:
            is_addable = (
                nth_diatonic_pitch in accidental.available_diatonic_pitch_indices
            )
        if is_addable:
            pitch_name = "{}{}".format(diatonic_pitch, accidental.accidental_name)
            alteration_code = self._accidental_to_alteration_code_mapping[accidental]
            pitch_entry = "({} {} . {})".format(
                pitch_name, nth_diatonic_pitch, alteration_code
            )
            return pitch_entry

        return None

    def _make_languages_table(self) -> str:
        language_table_entries = []

        for accidental in self._ekmelily_accidentals:
            for nth_diatonic_pitch, diatonic_pitch in enumerate(
                pitches_constants.ASCENDING_DIATONIC_PITCH_NAMES
            ):
                pitch_entry = self._get_pitch_entry_from_accidental_and_diatonic_pitch(
                    accidental, nth_diatonic_pitch, diatonic_pitch
                )
                if pitch_entry is not None:
                    language_table_entries.append(pitch_entry)

        # for now: only support english language
        languages_table = "ekmLanguages = #'(\n(english . (\n  {})))".format(
            "\n  ".join(language_table_entries)
        )
        return languages_table

    def _make_notations_table(self) -> str:
        notations_table_entries: typing.List[str] = []

        for accidental in self._ekmelily_accidentals:
            alteration_code = self._accidental_to_alteration_code_mapping[accidental]
            accidental_notation = "({} {})".format(
                alteration_code, " ".join(accidental.accidental_glyphs)
            )
            notations_table_entries.append(accidental_notation)

        notations_table = "ekmNotations = #'(\n(default .(\n  {})))".format(
            "\n  ".join(notations_table_entries)
        )
        return notations_table

    # ###################################################################### #
    #                          public api                                    #
    # ###################################################################### #

    def convert(self):
        """Render tuning file to :attr:`path`."""

        ekmelily_tuning_file = (
            self._make_tuning_table(),
            self._make_languages_table(),
            self._make_notations_table(),
            r'\include "ekmel-main.ily"',
        )

        ekmelily_tuning_file = "\n\n".join(ekmelily_tuning_file)

        with open(self._path, "w") as f:
            f.write(ekmelily_tuning_file)


class HEJIEkmelilyTuningFileConverter(EkmelilyTuningFileConverter):
    """Build Ekmelily tuning files for `Helmholtz-Ellis JI Pitch Notation <https://marsbat.space/pdfs/notation.pdf>`_.

    :param path: Path where the new Ekmelily tuning file shall be written.
        The suffix '.ily' is recommended, but not necessary.
    :type path: str
    :param prime_to_highest_allowed_exponent: Mapping of prime number to
        highest exponent that should occur. Take care not to add
        higher exponents than the HEJI Notation supports. See
        :const:`~mutwo.converters.frontends.ekmelily_constants.DEFAULT_PRIME_TO_HIGHEST_ALLOWED_EXPONENT`
        for the default mapping.
    :type prime_to_highest_allowed_exponent: typing.Dict[int, int], optional
    :param reference_pitch: The reference pitch (1/1). Should be a diatonic
        pitch name (see
        :const:`~mutwo.parameters.pitches_constants.ASCENDING_DIATONIC_PITCH_NAMES`)
        in English nomenclature. For any other reference pitch than 'c', Lilyponds
        midi rendering for pitches with the diatonic pitch 'c' will be slightly
        out of tune (because the first value of `global_scale`
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
    """

    def __init__(
        self,
        path: str = None,
        prime_to_highest_allowed_exponent: typing.Optional[
            typing.Dict[int, int]
        ] = None,
        reference_pitch: str = "c",
        prime_to_heji_accidental_name: typing.Optional[typing.Dict[int, str]] = None,
        otonality_indicator: str = None,
        utonality_indicator: str = None,
        exponent_to_exponent_indicator: typing.Callable[[int], str] = None,
        tempered_pitch_indicator: str = None,
    ):
        # set default values
        if path is None:
            path = "ekme-heji-ref-{}.ily".format(reference_pitch)

        if prime_to_highest_allowed_exponent is None:
            prime_to_highest_allowed_exponent = (
                frontends.ekmelily_constants.DEFAULT_PRIME_TO_HIGHEST_ALLOWED_EXPONENT
            )

        if prime_to_heji_accidental_name is None:
            prime_to_heji_accidental_name = (
                frontends.ekmelily_constants.DEFAULT_PRIME_TO_HEJI_ACCIDENTAL_NAME
            )

        if otonality_indicator is None:
            otonality_indicator = (
                frontends.ekmelily_constants.DEFAULT_OTONALITY_INDICATOR
            )

        if utonality_indicator is None:
            utonality_indicator = (
                frontends.ekmelily_constants.DEFAULT_UTONALITY_INDICATOR
            )

        if exponent_to_exponent_indicator is None:
            exponent_to_exponent_indicator = (
                frontends.ekmelily_constants.DEFAULT_EXPONENT_TO_EXPONENT_INDICATOR
            )

        if tempered_pitch_indicator is None:
            tempered_pitch_indicator = (
                frontends.ekmelily_constants.DEFAULT_TEMPERED_PITCH_INDICATOR
            )

        difference_in_cents_from_tempered_pitch_class_for_diatonic_pitches = HEJIEkmelilyTuningFileConverter._find_difference_in_cents_from_tempered_pitch_class_for_diatonic_pitches(
            reference_pitch
        )
        global_scale = HEJIEkmelilyTuningFileConverter._make_global_scale(
            difference_in_cents_from_tempered_pitch_class_for_diatonic_pitches
        )
        ekmelily_accidentals = HEJIEkmelilyTuningFileConverter._make_ekmelily_accidentals(
            difference_in_cents_from_tempered_pitch_class_for_diatonic_pitches,
            prime_to_highest_allowed_exponent,
            prime_to_heji_accidental_name,
            otonality_indicator,
            utonality_indicator,
            exponent_to_exponent_indicator,
            tempered_pitch_indicator,
        )
        super().__init__(path, ekmelily_accidentals, global_scale=global_scale)

    # ###################################################################### #
    #                          static methods                                #
    # ###################################################################### #

    @staticmethod
    def _find_difference_in_cents_from_tempered_pitch_class_for_diatonic_pitches(
        reference_pitch: str,
    ) -> typing.Tuple[float, ...]:
        difference_in_cents_from_tempered_pitch_class_for_diatonic_pitches = []
        reference_pitch_index = pitches_constants.DIATONIC_PITCH_NAME_CYCLE_OF_FIFTHS.index(
            reference_pitch
        )
        for diatonic_pitch_name in pitches_constants.ASCENDING_DIATONIC_PITCH_NAMES:
            pitch_index = pitches_constants.DIATONIC_PITCH_NAME_CYCLE_OF_FIFTHS.index(
                diatonic_pitch_name
            )
            n_exponents_difference_from_reference = pitch_index - reference_pitch_index
            difference_from_tempered_diatonic_pitch = (
                frontends.ekmelily_constants.DIFFERENCE_BETWEEN_PYTHAGOREAN_AND_TEMPERED_FIFTH
                * n_exponents_difference_from_reference
            )
            difference_in_cents_from_tempered_pitch_class_for_diatonic_pitches.append(
                difference_from_tempered_diatonic_pitch
            )

        return tuple(difference_in_cents_from_tempered_pitch_class_for_diatonic_pitches)

    @staticmethod
    def _make_global_scale(
        difference_in_cents_from_tempered_pitch_class_for_diatonic_pitches: typing.Tuple[
            float, ...
        ],
    ) -> typing.Tuple[fractions.Fraction, ...]:
        new_global_scale = []

        for (
            nth_diatonic_pitch,
            difference_in_cents_from_tempered_pitch_class,
        ) in enumerate(
            difference_in_cents_from_tempered_pitch_class_for_diatonic_pitches
        ):
            default_cents_for_diatonic_pitch = EkmelilyTuningFileConverter._alteration_fraction_to_deviation_in_cents(
                frontends.ekmelily_constants.DEFAULT_GLOBAL_SCALE[nth_diatonic_pitch]
            )
            n_cents = (
                default_cents_for_diatonic_pitch
                + difference_in_cents_from_tempered_pitch_class
            )
            alteration_fraction = EkmelilyTuningFileConverter._deviation_in_cents_to_alteration_fraction(
                n_cents, max_denominator=1000
            )
            new_global_scale.append(alteration_fraction)

        return tuple(new_global_scale)

    @staticmethod
    def _make_pythagorean_accidentals() -> typing.Tuple[EkmelilyAccidental, ...]:
        accidentals = []
        for (
            alteration_name
        ) in (
            frontends.ekmelily_constants.PYTHAGOREAN_ACCIDENTAL_TO_CENT_DEVIATIONS.keys()
        ):
            glyph = frontends.ekmelily_constants.PRIME_AND_EXPONENT_AND_TRADITIONAL_ACCIDENTAL_TO_ACCIDENTAL_GLYPH[
                None, None, alteration_name
            ]
            cents_deviation = frontends.ekmelily_constants.PYTHAGOREAN_ACCIDENTAL_TO_CENT_DEVIATIONS[
                alteration_name
            ]
            accidental = EkmelilyAccidental(
                alteration_name, (glyph,), cents_deviation
            )
            accidentals.append(accidental)

        return tuple(accidentals)

    @staticmethod
    def _process_prime(
        prime_to_heji_accidental_name: typing.Dict[int, str],
        pythagorean_accidental: str,
        prime: int,
        exponent: int,
        otonality_indicator: str,
        utonality_indicator: str,
        exponent_to_exponent_indicator: typing.Callable[[int], str],
    ) -> typing.Tuple[str, str, float]:
        glyph_key = (
            (prime, exponent, pythagorean_accidental)
            if prime == 5
            else (prime, exponent, None)
        )
        glyph = frontends.ekmelily_constants.PRIME_AND_EXPONENT_AND_TRADITIONAL_ACCIDENTAL_TO_ACCIDENTAL_GLYPH[
            glyph_key
        ]

        accidental_name = "{}{}{}".format(
            (otonality_indicator, utonality_indicator)[exponent < 0],
            prime_to_heji_accidental_name[prime],
            exponent_to_exponent_indicator(abs(exponent) - 1),
        )

        cents_deviation = pitches.JustIntonationPitch(
            pitches_constants.DEFAULT_PRIME_TO_COMMA[prime].ratio ** exponent
        ).cents
        return accidental_name, glyph, cents_deviation

    @staticmethod
    def _make_higher_prime_accidental(
        pythagorean_accidental: str,
        pythagorean_accidental_cents_deviation: float,
        exponents: typing.Tuple[int, ...],
        prime_to_highest_allowed_exponent: typing.Dict[int, int],
        prime_to_heji_accidental_name: typing.Dict[int, str],
        otonality_indicator: str,
        utonality_indicator: str,
        exponent_to_exponent_indicator: typing.Callable[[int], str],
    ) -> EkmelilyAccidental:
        accidental_parts = ["{}".format(pythagorean_accidental)]
        cents_deviation = float(pythagorean_accidental_cents_deviation)
        glyphs = []
        for prime, exponent in zip(
            prime_to_highest_allowed_exponent.keys(), exponents,
        ):
            if exponent != 0:
                (
                    accidental_change,
                    glyph,
                    cents_deviation_change,
                ) = HEJIEkmelilyTuningFileConverter._process_prime(
                    prime_to_heji_accidental_name,
                    pythagorean_accidental,
                    prime,
                    exponent,
                    otonality_indicator,
                    utonality_indicator,
                    exponent_to_exponent_indicator,
                )
                accidental_parts.append(accidental_change)
                glyphs.append(glyph)
                cents_deviation += cents_deviation_change

        # add traditional accidentals (sharp, flat, etc.) if no syntonic
        # comma is available (if there is any syntonic comma there is
        # already the necessary pythagorean accidental)
        if exponents[0] == 0:
            glyphs.insert(
                0,
                frontends.ekmelily_constants.PRIME_AND_EXPONENT_AND_TRADITIONAL_ACCIDENTAL_TO_ACCIDENTAL_GLYPH[
                    (None, None, pythagorean_accidental)
                ],
            )

        # start with highest primes
        glyphs.reverse()

        accidental_name = "".join(accidental_parts)

        new_accidental = EkmelilyAccidental(
            accidental_name, tuple(glyphs), round(cents_deviation, 4)
        )
        return new_accidental

    @staticmethod
    def _make_accidentals_for_higher_primes(
        prime_to_highest_allowed_exponent: typing.Dict[int, int],
        prime_to_heji_accidental_name: typing.Dict[int, str],
        otonality_indicator: str,
        utonality_indicator: str,
        exponent_to_exponent_indicator: typing.Callable[[int], str],
    ) -> typing.Tuple[EkmelilyAccidental, ...]:
        allowed_exponents = tuple(
            tuple(range(-maxima_exponent, maxima_exponent + 1))
            for _, maxima_exponent in sorted(
                prime_to_highest_allowed_exponent.items(),
                key=lambda prime_to_maxima_exponent: prime_to_maxima_exponent[0],
            )
        )
        accidentals = []

        for exponents in itertools.product(*allowed_exponents):
            if any(tuple(exp != 0 for exp in exponents)):
                for (
                    pythagorean_accidental,
                    pythagorean_accidental_cents_deviation,
                ) in (
                    frontends.ekmelily_constants.PYTHAGOREAN_ACCIDENTAL_TO_CENT_DEVIATIONS.items()
                ):
                    accidental = HEJIEkmelilyTuningFileConverter._make_higher_prime_accidental(
                        pythagorean_accidental,
                        pythagorean_accidental_cents_deviation,
                        exponents,
                        prime_to_highest_allowed_exponent,
                        prime_to_heji_accidental_name,
                        otonality_indicator,
                        utonality_indicator,
                        exponent_to_exponent_indicator,
                    )
                    accidentals.append(accidental)

        return tuple(accidentals)

    @staticmethod
    def _make_tempered_accidentals(
        difference_in_cents_from_tempered_pitch_class_for_diatonic_pitches: typing.Tuple[
            float, ...
        ],
        tempered_pitch_indicator: str,
    ) -> typing.Tuple[EkmelilyAccidental, ...]:
        accidentals = []

        for (
            nth_diatonic_pitch,
            difference_in_cents_from_tempered_pitch_class,
        ) in enumerate(
            difference_in_cents_from_tempered_pitch_class_for_diatonic_pitches,
        ):
            for (
                tempered_accidental,
                accidental_glyph,
            ) in (
                frontends.ekmelily_constants.TEMPERED_ACCIDENTAL_TO_ACCIDENTAL_GLYPH.items()
            ):

                accidental_name = "{}{}".format(
                    tempered_accidental, tempered_pitch_indicator
                )
                deviation_in_cents = (
                    frontends.ekmelily_constants.TEMPERED_ACCIDENTAL_TO_CENT_DEVIATION[
                        tempered_accidental
                    ]
                    - difference_in_cents_from_tempered_pitch_class
                )

                accidental = EkmelilyAccidental(
                    accidental_name,
                    (accidental_glyph,),
                    deviation_in_cents,
                    available_diatonic_pitch_indices=(nth_diatonic_pitch,),
                )
                accidentals.append(accidental)

        return tuple(accidentals)

    @staticmethod
    def _make_ekmelily_accidentals(
        difference_in_cents_from_tempered_pitch_class_for_diatonic_pitches: typing.Tuple[
            float, ...
        ],
        prime_to_highest_allowed_exponent: typing.Dict[int, int],
        prime_to_heji_accidental_name: typing.Dict[int, str],
        otonality_indicator: str,
        utonality_indicator: str,
        exponent_to_exponent_indicator: typing.Callable[[int], str],
        tempered_pitch_indicator: str,
    ) -> typing.Tuple[EkmelilyAccidental, ...]:

        pythagorean_accidentals = (
            HEJIEkmelilyTuningFileConverter._make_pythagorean_accidentals()
        )

        accidentals_for_higher_primes = HEJIEkmelilyTuningFileConverter._make_accidentals_for_higher_primes(
            prime_to_highest_allowed_exponent,
            prime_to_heji_accidental_name,
            otonality_indicator,
            utonality_indicator,
            exponent_to_exponent_indicator,
        )

        tempered_accidentals = HEJIEkmelilyTuningFileConverter._make_tempered_accidentals(
            difference_in_cents_from_tempered_pitch_class_for_diatonic_pitches,
            tempered_pitch_indicator,
        )

        return (
            pythagorean_accidentals
            + accidentals_for_higher_primes
            + tempered_accidentals
        )
