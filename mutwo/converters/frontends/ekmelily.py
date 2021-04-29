"""Build tuning files for Lilypond extension `ekmelily <http://www.ekmelic-music.org/de/extra/ekmelily.htm>`_.

By default the smallest step which Lilypond supports is one quartertone. With
the help of Ekmelily it is easily possible to add more complex micro- or
macrotonal tunings to Lilypond. The converter in this module aims to make it easier
to build tuning files to be used with the 'ekmel-main.ily' script from Thomas Richter.
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


@dataclasses.dataclass(frozen=True)
class EkmelilyAccidental(object):
    """Representation of an Ekmelily accidental."""

    # TODO(add possibility to declare different languages)
    # typing.Union[str, typing.Dict[str, str]]
    accidental_name: str
    # TODO(add possibility for multiple accidentals)
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
    """Make Ekmelily tuning files from Ekmelily accidentals."""

    def __init__(
        self,
        name: str,
        ekmelily_accidentals: typing.Sequence[EkmelilyAccidental],
        # should have exactly 7 fractions (one for each diatonic pitch)
        global_scale: typing.Optional[typing.Tuple[fractions.Fraction, ...]] = None,
    ):
        if global_scale is None:
            # set to default 12 EDO, a' = 440 Hertz
            global_scale = frontends.ekmelily_constants.DEFAULT_GLOBAL_SCALE

        corrected_global_scale = []
        for nth_scale_degree, alteration_fraction in enumerate(global_scale):
            if alteration_fraction < 0:
                message = (
                    "Found negative value in global scale for scale degree {}. Value"
                    " has been set to 0 (no negative numbers are allowed).".format(
                        nth_scale_degree
                    )
                )
                warnings.warn(message)
                alteration_fraction = 0
            corrected_global_scale.append(alteration_fraction)

        self._path = "ekme-{}.ily".format(name)
        self._global_scale = tuple(corrected_global_scale)
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
    def _group_accidentals_by_deviations_in_cents(
        ekmelily_accidentals: typing.Sequence[EkmelilyAccidental],
    ) -> typing.Tuple[
        typing.Tuple[typing.Tuple[EkmelilyAccidental, ...], ...], ...,
    ]:
        available_deviations_in_cents = sorted(
            set(
                map(
                    lambda accidental: abs(accidental.deviation_in_cents),
                    ekmelily_accidentals,
                )
            )
        )
        accidentals_grouped_by_deviations_in_cents = tuple(
            tuple(
                tuple(
                    accidental
                    for accidental in ekmelily_accidentals
                    if value * accidental.deviation_in_cents == deviation_in_cents
                )
                for value in (1, -1)
            )
            for deviation_in_cents in available_deviations_in_cents
        )

        return accidentals_grouped_by_deviations_in_cents

    @staticmethod
    def _process_accidentals(
        accidental_to_alteration_code_mapping: typing.Dict[EkmelilyAccidental, str],
        alteration_code_to_alteration_fraction_mapping: typing.Dict[
            str, fractions.Fraction
        ],
        positive_accidental: typing.Optional[EkmelilyAccidental],
        positive_alteration_index: int,
        negative_accidental: typing.Optional[EkmelilyAccidental],
        negative_alteration_index: int,
    ) -> None:
        # Add accidental data to accidental_to_alteration_code_mapping
        # and alteration_code_to_alteration_fraction_mapping.
        is_positive = True
        for accidental, accidental_index in (
            (positive_accidental, positive_alteration_index),
            (negative_accidental, negative_alteration_index),
        ):
            alteration_code = "#x{}".format(str(hex(accidental_index))[2:].upper())
            if accidental:
                accidental_to_alteration_code_mapping.update(
                    {accidental: alteration_code}
                )

            if is_positive is True:
                try:
                    deviation_in_cents = accidental.deviation_in_cents  # type: ignore
                # if only negative accidental is defined
                except AttributeError:
                    deviation_in_cents = negative_accidental.deviation_in_cents  # type: ignore

                alteration_fraction = EkmelilyTuningFileConverter._deviation_in_cents_to_alteration_fraction(
                    deviation_in_cents
                )
                alteration_code_to_alteration_fraction_mapping.update(
                    {alteration_code: alteration_fraction}
                )
                is_positive = False

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
    ) -> int:
        # Define alteration codes and alteration fractions for accidentals
        # in accidental group and add the defined data to both mappings.
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

            EkmelilyTuningFileConverter._process_accidentals(
                accidental_to_alteration_code_mapping,
                alteration_code_to_alteration_fraction_mapping,
                positive_accidental,
                positive_alteration_index,
                negative_accidental,
                negative_alteration_index,
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

        # start with hex x12 like in ekmel.ily
        nth_alteration = 18
        for accidental_group in accidentals_grouped_by_deviations_in_cents:
            nth_alteration = EkmelilyTuningFileConverter._process_accidental_group(
                accidental_to_alteration_code_mapping,
                alteration_code_to_alteration_fraction_mapping,
                nth_alteration,
                accidental_group,
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
        # TODO(support more languages than English)
        language_table_entries = []

        # 1. Append pitches without accidentals
        for nth_diatonic_pitch, diatonic_pitch in enumerate(
            pitches_constants.ASCENDING_DIATONIC_PITCH_NAMES
        ):
            natural_pitch_entry = "({} {} . 0)".format(
                diatonic_pitch, nth_diatonic_pitch
            )
            language_table_entries.append(natural_pitch_entry)

        # 2. Append pitches with accidentals
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
        # TODO(only add natural accidental if no accidental with deviation_in_cents = 0
        #      has been defined!)

        # add natural accidental for diatonic pitches without alterations
        notations_table_entries = ["(#x00 #xE261)"]
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
    """Make Ekmelily tuning files for `Helmholtz-Ellis JI Pitch Notation <https://marsbat.space/pdfs/notation.pdf>`_."""

    def __init__(
        self,
        name: str = None,
        prime_to_highest_allowed_exponent: typing.Optional[
            typing.Dict[int, int]
        ] = None,
        prime_to_heji_accidental_name: typing.Optional[typing.Dict[int, str]] = None,
        reference_pitch: str = "a",
    ):
        if name is None:
            name = "heji-ref-{}".format(reference_pitch)

        if prime_to_highest_allowed_exponent is None:
            prime_to_highest_allowed_exponent = (
                frontends.ekmelily_constants.DEFAULT_PRIME_TO_HIGHEST_ALLOWED_EXPONENT
            )

        if prime_to_heji_accidental_name is None:
            prime_to_heji_accidental_name = (
                frontends.ekmelily_constants.DEFAULT_PRIME_TO_HEJI_ACCIDENTAL_NAME
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
        )
        super().__init__(name, ekmelily_accidentals, global_scale=global_scale)

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
        # TODO(don't hard code 700 cents for tempered fifth, or hard code it at least
        #      in constants file)
        difference_between_pythagorean_and_tempered_fifth = (
            pitches.JustIntonationPitch("3/2").cents - 700
        )

        for diatonic_pitch_name in pitches_constants.ASCENDING_DIATONIC_PITCH_NAMES:
            pitch_index = pitches_constants.DIATONIC_PITCH_NAME_CYCLE_OF_FIFTHS.index(
                diatonic_pitch_name
            )
            n_exponents_difference_from_reference = pitch_index - reference_pitch_index
            difference_from_tempered_diatonic_pitch = (
                difference_between_pythagorean_and_tempered_fifth
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
            if cents_deviation != 0:
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
    ) -> typing.Tuple[str, str, float]:
        glyph_key = (
            (prime, exponent, pythagorean_accidental)
            if prime == 5
            else (prime, exponent, None)
        )
        glyph = frontends.ekmelily_constants.PRIME_AND_EXPONENT_AND_TRADITIONAL_ACCIDENTAL_TO_ACCIDENTAL_GLYPH[
            glyph_key
        ]

        # TODO(don't hard code 'u' and 'o' or put it at least in constants)
        # TODO(don't hard code a->1, b->2, c->3 exponents, or put it at least
        #      in constants)
        accidental_name = "{}{}{}".format(
            ("o", "u")[exponent < 0],
            prime_to_heji_accidental_name[prime],
            "abc"[abs(exponent) - 1],
        )

        cents_deviation = pitches.JustIntonationPitch(
            pitches_constants.DEFAULT_PRIME_TO_COMMA[prime].ratio ** exponent
        ).cents
        return accidental_name, glyph, cents_deviation

    @staticmethod
    def _make_higher_prime_accidental(
        pythagorean_accidental: str,
        prime_to_highest_allowed_exponent: typing.Dict[int, int],
        prime_to_heji_accidental_name: typing.Dict[int, str],
        exponents: typing.Tuple[int, ...],
    ) -> EkmelilyAccidental:
        accidental_parts = ["{}".format(pythagorean_accidental)]
        cents_deviation = float(
            frontends.ekmelily_constants.PYTHAGOREAN_ACCIDENTAL_TO_CENT_DEVIATIONS[
                pythagorean_accidental
            ]
        )
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
                    pythagorean_accidental
                ) in (
                    frontends.ekmelily_constants.PYTHAGOREAN_ACCIDENTAL_TO_CENT_DEVIATIONS.keys()
                ):
                    accidental = HEJIEkmelilyTuningFileConverter._make_higher_prime_accidental(
                        pythagorean_accidental,
                        prime_to_highest_allowed_exponent,
                        prime_to_heji_accidental_name,
                        exponents,
                    )
                    accidentals.append(accidental)

        return tuple(accidentals)

    @staticmethod
    def _make_tempered_accidentals(
        difference_in_cents_from_tempered_pitch_class_for_diatonic_pitches: typing.Tuple[
            float, ...
        ],
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

                # TODO(don't hard code 't' or put it in constants)
                accidental_name = "{}t".format(tempered_accidental)
                deviation_in_cents = (
                    frontends.ekmelily_constants.TEMPERED_ACCIDENTAL_TO_CENT_DEVIATION[
                        tempered_accidental
                    ]
                    - difference_in_cents_from_tempered_pitch_class
                )
                if deviation_in_cents == 0:
                    deviation_in_cents = 0.2

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
    ) -> typing.Tuple[EkmelilyAccidental, ...]:

        # standard flat / sharp
        pythagorean_accidentals = (
            HEJIEkmelilyTuningFileConverter._make_pythagorean_accidentals()
        )

        # add accidentals with commas
        accidentals_for_higher_primes = HEJIEkmelilyTuningFileConverter._make_accidentals_for_higher_primes(
            prime_to_highest_allowed_exponent, prime_to_heji_accidental_name
        )

        # make tempered accidentals
        tempered_accidentals = HEJIEkmelilyTuningFileConverter._make_tempered_accidentals(
            difference_in_cents_from_tempered_pitch_class_for_diatonic_pitches
        )

        return (
            pythagorean_accidentals
            + accidentals_for_higher_primes
            + tempered_accidentals
        )
