import filecmp
import os
import unittest

try:
    import quicktions as fractions  # type: ignore
except ImportError:
    import fractions  # type: ignore

from mutwo.converters.frontends import ekmelily
from mutwo.converters.frontends import ekmelily_constants


class EkmelilyTuningFileConverterTest(unittest.TestCase):
    def test_correct_global_scale(self):
        test_global_scale = tuple(
            fractions.Fraction(f) for f in "12/11 1 2 5/2 7/2 9/2 10/2".split(" ")
        )
        corrected_global_scale = tuple(
            fractions.Fraction(f) for f in "0 1 2 5/2 7/2 9/2 10/2".split(" ")
        )
        self.assertEqual(
            ekmelily.EkmelilyTuningFileConverter._correct_global_scale(
                test_global_scale
            ),
            corrected_global_scale,
        )

    def test_deviation_in_cents_to_alteration_fraction(self):
        self.assertEqual(
            fractions.Fraction(1, 1),
            ekmelily.EkmelilyTuningFileConverter._deviation_in_cents_to_alteration_fraction(
                200
            ),
        )
        self.assertEqual(
            fractions.Fraction(2, 1),
            ekmelily.EkmelilyTuningFileConverter._deviation_in_cents_to_alteration_fraction(
                400
            ),
        )
        self.assertEqual(
            fractions.Fraction(1, 2),
            ekmelily.EkmelilyTuningFileConverter._deviation_in_cents_to_alteration_fraction(
                100
            ),
        )

    def test_alteration_fraction_to_deviation_in_cents(self):
        self.assertEqual(
            200,
            ekmelily.EkmelilyTuningFileConverter._alteration_fraction_to_deviation_in_cents(
                fractions.Fraction(1, 1),
            ),
        )
        self.assertEqual(
            -200,
            ekmelily.EkmelilyTuningFileConverter._alteration_fraction_to_deviation_in_cents(
                -fractions.Fraction(1, 1),
            ),
        )

    def test_accidental_index_to_alteration_code(self):
        self.assertEqual(
            "#x12",
            ekmelily.EkmelilyTuningFileConverter._accidental_index_to_alteration_code(
                18
            ),
        )

    def test_group_accidentals_by_deviations_in_cents(self):
        dummy_accidentals = (
            ekmelily.EkmelilyAccidental("s", ("#xE262",), 100),
            ekmelily.EkmelilyAccidental("f", ("#xE260",), -100),
            ekmelily.EkmelilyAccidental("sharp", ("#xE262",), 100),
            ekmelily.EkmelilyAccidental("flat", ("#xE260",), -100),
            ekmelily.EkmelilyAccidental("lonely", ("#xE265",), 1),
            ekmelily.EkmelilyAccidental("also_lonely", ("#xE266",), -20),
        )

        grouped_accidentals = (
            (1, (set([dummy_accidentals[-2]]), set([]))),
            (20, (set([]), set([dummy_accidentals[-1]]))),
            (
                100,
                (
                    set([dummy_accidentals[0], dummy_accidentals[2]]),
                    set([dummy_accidentals[1], dummy_accidentals[3]]),
                ),
            ),
        )

        result = ekmelily.EkmelilyTuningFileConverter._group_accidentals_by_deviations_in_cents(
            dummy_accidentals
        )
        # transform tuples to sets because order doesn't matter
        adjusted_result = tuple(
            (group[0], (set(group[1][0]), set(group[1][1]))) for group in result
        )

        self.assertEqual(grouped_accidentals, adjusted_result)

    def test_convert(self):
        # regression test with doc string example
        comparision_file_path = (
            "tests/converters/frontends/ekmelily_expected_conversion_output.ily"
        )

        test_file_path = "tests/converters/frontends/ekme-test.ily"
        natural = ekmelily.EkmelilyAccidental("", ("#xE261",), 0)
        sharp = ekmelily.EkmelilyAccidental("s", ("#xE262",), 100)
        flat = ekmelily.EkmelilyAccidental("f", ("#xE260",), -100)
        eigth_tone_sharp = ekmelily.EkmelilyAccidental("es", ("#xE2C7",), 25)
        eigth_tone_flat = ekmelily.EkmelilyAccidental("ef", ("#xE2C2",), -25)
        converter = ekmelily.EkmelilyTuningFileConverter(
            test_file_path, (natural, sharp, flat, eigth_tone_sharp, eigth_tone_flat)
        )
        converter.convert()

        self.assertTrue(filecmp.cmp(test_file_path, comparision_file_path))
        os.remove(test_file_path)


class HEJIEkmelilyTuningFileConverterTest(unittest.TestCase):
    def test_find_difference_in_cents_from_tempered_pitch_class_for_diatonic_pitches(
        self,
    ):
        diff_just_and_tempered_fifth = 1.955000865387433
        self.assertEqual(
            ekmelily.HEJIEkmelilyTuningFileConverter._find_difference_in_cents_from_tempered_pitch_class_for_diatonic_pitches(
                "c"
            ),
            (
                0,
                diff_just_and_tempered_fifth * 2,
                diff_just_and_tempered_fifth * 4,
                -diff_just_and_tempered_fifth,
                diff_just_and_tempered_fifth,
                diff_just_and_tempered_fifth * 3,
                diff_just_and_tempered_fifth * 5,
            ),
        )
        self.assertEqual(
            ekmelily.HEJIEkmelilyTuningFileConverter._find_difference_in_cents_from_tempered_pitch_class_for_diatonic_pitches(
                "a"
            ),
            (
                diff_just_and_tempered_fifth * -3,
                diff_just_and_tempered_fifth * -1,
                diff_just_and_tempered_fifth * 1,
                diff_just_and_tempered_fifth * -4,
                diff_just_and_tempered_fifth * -2,
                0,
                diff_just_and_tempered_fifth * 2,
            ),
        )

    def test_make_higher_prime_accidental(self):
        def round_deviation_in_cents(
            ekmelily_accidental: ekmelily.EkmelilyAccidental,
        ) -> ekmelily.EkmelilyAccidental:
            return ekmelily.EkmelilyAccidental(
                ekmelily_accidental.accidental_name,
                ekmelily_accidental.accidental_glyph_tuple,
                round(ekmelily_accidental.deviation_in_cents, 3),
                ekmelily_accidental.available_diatonic_pitch_index_tuple,
            )

        default_args = (
            ekmelily_constants.DEFAULT_PRIME_TO_HIGHEST_ALLOWED_EXPONENT_DICT,
            {5: "five", 7: "seven", 11: "eleven"},
            "o",
            "u",
            lambda exponent: ("one", "two", "three")[exponent],
        )

        self.assertEqual(
            round_deviation_in_cents(
                ekmelily.HEJIEkmelilyTuningFileConverter._make_higher_prime_accidental(
                    "", 0, (1, 0, 0), *default_args, True
                )
            ),
            round_deviation_in_cents(
                ekmelily.EkmelilyAccidental("ofiveone", ("#xE2C2",), -21.50628959671495)
            ),
        )

        self.assertEqual(
            round_deviation_in_cents(
                ekmelily.HEJIEkmelilyTuningFileConverter._make_higher_prime_accidental(
                    "", 0, (-2, 0, 0), *default_args, True
                )
            ),
            round_deviation_in_cents(
                ekmelily.EkmelilyAccidental(
                    "ufivetwo", ("#xE2D1",), 2 * 21.50628959671495
                )
            ),
        )

        self.assertEqual(
            round_deviation_in_cents(
                ekmelily.HEJIEkmelilyTuningFileConverter._make_higher_prime_accidental(
                    "", 0, (1, -1, 0), *default_args, True
                )
            ),
            round_deviation_in_cents(
                ekmelily.EkmelilyAccidental(
                    "ofiveoneusevenone",
                    ("#xE2DF", "#xE2C2",),
                    -21.50628959671495 + 27.264091800100235,
                )
            ),
        )

        self.assertEqual(
            round_deviation_in_cents(
                ekmelily.HEJIEkmelilyTuningFileConverter._make_higher_prime_accidental(
                    "s", 113.7, (0, 0, 1), *default_args, True
                )
            ),
            round_deviation_in_cents(
                ekmelily.EkmelilyAccidental(
                    "soelevenone", ("#xE2E3", "#xE262"), 53.27294323014408 + 113.7
                )
            ),
        )

        self.assertEqual(
            round_deviation_in_cents(
                ekmelily.HEJIEkmelilyTuningFileConverter._make_higher_prime_accidental(
                    "ss", 2 * 113.7, (3, 0, 0), *default_args, True
                )
            ),
            round_deviation_in_cents(
                ekmelily.EkmelilyAccidental(
                    "ssofivethree", ("#xE2D8",), (3 * -21.50628959671495) + (2 * 113.7)
                )
            ),
        )

    def test_convert(self):
        # regression test with doc string example
        comparision_file_path = (
            "tests/converters/frontends/ekmelily_heji_expected_conversion_output.ily"
        )

        test_file_path = "tests/converters/frontends/ekme-heji-test.ily"
        converter = ekmelily.HEJIEkmelilyTuningFileConverter(
            test_file_path,
            prime_to_highest_allowed_exponent={5: 2, 7: 1},
            reference_pitch="c",
            prime_to_heji_accidental_name={5: "five", 7: "seven"},
            exponent_to_exponent_indicator=lambda exponent: ("one", "two")[exponent],
        )
        converter.convert()

        self.assertTrue(filecmp.cmp(test_file_path, comparision_file_path))
        os.remove(test_file_path)


if __name__ == "__main__":
    unittest.main()
