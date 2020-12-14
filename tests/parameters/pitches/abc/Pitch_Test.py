import unittest

try:
    import quicktions as fractions
except ImportError:
    import fractions

from mutwo.parameters import pitches


class PitchTest(unittest.TestCase):
    def test_abstract_error(self):
        self.assertRaises(TypeError, pitches.abc.Pitch)

    def test_hertz_to_cents(self):
        self.assertEqual(1200, pitches.abc.Pitch.hertz_to_cents(440, 880))
        self.assertEqual(-1200, pitches.abc.Pitch.hertz_to_cents(880, 440))
        self.assertEqual(0, pitches.abc.Pitch.hertz_to_cents(10, 10))
        self.assertEqual(702, round(pitches.abc.Pitch.hertz_to_cents(440, 440 * 3 / 2)))

    def test_ratio_to_cents(self):
        self.assertEqual(
            1200, pitches.abc.Pitch.ratio_to_cents(fractions.Fraction(2, 1))
        )
        self.assertEqual(
            -1200, pitches.abc.Pitch.ratio_to_cents(fractions.Fraction(1, 2))
        )
        self.assertEqual(0, pitches.abc.Pitch.ratio_to_cents(fractions.Fraction(1, 1)))
        self.assertEqual(
            702, round(pitches.abc.Pitch.ratio_to_cents(fractions.Fraction(3, 2)))
        )

    def test_cents_to_ratio(self):
        self.assertEqual(
            fractions.Fraction(2, 1), pitches.abc.Pitch.cents_to_ratio(1200)
        )
        self.assertEqual(
            fractions.Fraction(1, 2), pitches.abc.Pitch.cents_to_ratio(-1200)
        )
        self.assertEqual(fractions.Fraction(1, 1), pitches.abc.Pitch.cents_to_ratio(0))

    def test_hertz_to_midi_pitch_number(self):
        self.assertEqual(69, pitches.abc.Pitch.hertz_to_midi_pitch_number(440))
        self.assertEqual(60, round(pitches.abc.Pitch.hertz_to_midi_pitch_number(261)))


if __name__ == "__main__":
    unittest.main()
