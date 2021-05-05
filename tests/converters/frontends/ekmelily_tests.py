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


if __name__ == "__main__":
    unittest.main()
