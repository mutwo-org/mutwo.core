import unittest

try:
    import quicktions as fractions
except ImportError:
    import fractions

from mutwo.parameters import pitches


class JustIntonationPitchTest(unittest.TestCase):
    def test_constructor_from_string(self):
        self.assertEqual(
            pitches.JustIntonationPitch("3/2").ratio, fractions.Fraction(3, 2)
        )
        self.assertEqual(
            pitches.JustIntonationPitch("5/1").ratio, fractions.Fraction(5, 1)
        )
        self.assertEqual(
            pitches.JustIntonationPitch("1/17").ratio, fractions.Fraction(1, 17)
        )

    def test_constructor_from_ratio(self):
        ratio0 = fractions.Fraction(3, 2)
        ratio1 = fractions.Fraction(5, 1)
        ratio2 = fractions.Fraction(1, 17)
        self.assertEqual(pitches.JustIntonationPitch(ratio0).ratio, ratio0)
        self.assertEqual(pitches.JustIntonationPitch(ratio1).ratio, ratio1)
        self.assertEqual(pitches.JustIntonationPitch(ratio2).ratio, ratio2)

    def test_constructor_from_vector(self):
        ratio0 = fractions.Fraction(3, 2)
        ratio1 = fractions.Fraction(5, 1)
        ratio2 = fractions.Fraction(1, 17)
        self.assertEqual(pitches.JustIntonationPitch((-1, 1)).ratio, ratio0)
        self.assertEqual(pitches.JustIntonationPitch((0, 0, 1)).ratio, ratio1)
        self.assertEqual(
            pitches.JustIntonationPitch([0, 0, 0, 0, 0, 0, -1]).ratio, ratio2
        )

    def test_constructor_with_different_concert_pitch(self):
        concert_pitch0 = pitches.DirectPitch(300)
        concert_pitch1 = pitches.DirectPitch(200)
        self.assertEqual(
            pitches.JustIntonationPitch(concert_pitch=concert_pitch0).concert_pitch,
            concert_pitch0,
        )
        self.assertEqual(
            pitches.JustIntonationPitch(
                concert_pitch=concert_pitch1.frequency
            ).concert_pitch,
            concert_pitch1,
        )

    def test_property_exponents(self):
        ratio0 = fractions.Fraction(3, 2)
        ratio1 = fractions.Fraction(25, 1)
        ratio2 = fractions.Fraction(11, 9)
        self.assertEqual(pitches.JustIntonationPitch(ratio0).exponents, (-1, 1))
        self.assertEqual(pitches.JustIntonationPitch(ratio1).exponents, (0, 0, 2))
        self.assertEqual(
            pitches.JustIntonationPitch(ratio2).exponents, (0, -2, 0, 0, 1)
        )

    def test_property_primes(self):
        ratio0 = fractions.Fraction(3, 2)
        ratio1 = fractions.Fraction(25, 1)
        ratio2 = fractions.Fraction(11, 9)
        self.assertEqual(pitches.JustIntonationPitch(ratio0).primes, (2, 3))
        self.assertEqual(pitches.JustIntonationPitch(ratio1).primes, (2, 3, 5))
        self.assertEqual(pitches.JustIntonationPitch(ratio2).primes, (2, 3, 5, 7, 11))

    def test_property_occupied_primes(self):
        ratio0 = fractions.Fraction(3, 2)
        ratio1 = fractions.Fraction(25, 1)
        ratio2 = fractions.Fraction(11, 9)
        self.assertEqual(pitches.JustIntonationPitch(ratio0).occupied_primes, (2, 3))
        self.assertEqual(pitches.JustIntonationPitch(ratio1).occupied_primes, (5,))
        self.assertEqual(pitches.JustIntonationPitch(ratio2).occupied_primes, (3, 11))

    def test_property_frequency(self):
        ratio0 = fractions.Fraction(3, 2)
        concert_pitch0 = 200
        ratio1 = fractions.Fraction(25, 1)
        concert_pitch1 = 300
        ratio2 = fractions.Fraction(11, 9)
        concert_pitch2 = 10
        self.assertAlmostEqual(
            pitches.JustIntonationPitch(ratio0, concert_pitch0).frequency,
            ratio0 * concert_pitch0,
        )
        self.assertAlmostEqual(
            pitches.JustIntonationPitch(ratio1, concert_pitch1).frequency,
            ratio1 * concert_pitch1,
        )
        self.assertAlmostEqual(
            pitches.JustIntonationPitch(ratio2, concert_pitch2).frequency,
            ratio2 * concert_pitch2,
        )


if __name__ == "__main__":
    unittest.main()
