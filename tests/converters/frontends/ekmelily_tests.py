import filecmp
import os
import unittest

try:
    import quicktions as fractions  # type: ignore
except ImportError:
    import fractions  # type: ignore

from mutwo.converters.frontends import ekmelily


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
        natural = ekmelily.EkmelilyAccidental('', ("#xE261",), 0)
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
